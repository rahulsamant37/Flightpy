from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import HumanMessage
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
import uuid
import os

from workflow.agent import Agent
from models.model import FlightsInput, HotelsInput
from models.model import SearchFlightsRequest, SearchHotelsRequest, TravelQuery, EmailRequest

app = FastAPI(
    title="FlightPy API",
    description="A travel agency API for finding flights and hotels",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Initialize agent with error handling
agent = Agent()

@app.get("/", status_code=status.HTTP_200_OK)
async def root():
    """Root endpoint to verify API is running"""
    return {"message": "Welcome to FlightPy API", "status": "active"}

@app.post("/travel/query", status_code=status.HTTP_200_OK)
async def process_travel_query(query: TravelQuery):
    """Process a natural language travel query"""
    if not query.query:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query cannot be empty"
        )
    # Create a human message from the query
    message = HumanMessage(content=query.query)
    
    # Add configuration for checkpointing
    thread_id = str(uuid.uuid4())
    config = {'configurable': {'thread_id': thread_id}}
    
    # Process the query through the agent with config
    result = agent.graph.invoke({"messages": [message]}, config=config)
    
    # Format the response properly
    response_content = result.get('messages', [])[-1].content if result.get('messages') else str(result)
    return {
        "response": {
            "messages": [{
                "content": response_content
            }]
        }, 
        "status": "success"
    }

@app.post("/flights/search", status_code=status.HTTP_200_OK)
async def search_flights(request: SearchFlightsRequest):
    """Search for flights based on specific criteria"""
    if request.return_date and request.return_date < request.outbound_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Return date cannot be before outbound date"
        )
    flight_input = FlightsInput(
        departure_airport=request.departure_airport,
        arrival_airport=request.arrival_airport,
        outbound_date=request.outbound_date,
        return_date=request.return_date,
        adults=request.adults,
        children=request.children,
        infants_in_seat=request.infants_in_seat,
        infants_on_lap=request.infants_on_lap
    )
    
    # Add configuration for checkpointing
    thread_id = str(uuid.uuid4())
    config = {'configurable': {'thread_id': thread_id}}
    
    # Create a human message that will trigger flight search
    query = f"Find flights from {request.departure_airport} to {request.arrival_airport} on {request.outbound_date}"
    if request.return_date:
        query += f" returning on {request.return_date}"
    
    message = HumanMessage(content=query)
    result = agent.graph.invoke({"messages": [message]}, config=config)
    return {"results": result, "status": "success"}

@app.post("/hotels/search", status_code=status.HTTP_200_OK)
async def search_hotels(request: SearchHotelsRequest):
    """Search for hotels based on specific criteria"""
    if request.check_out_date < request.check_in_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Check-out date cannot be before check-in date"
        )
    hotel_input = HotelsInput(
        q=request.location,
        check_in_date=request.check_in_date,
        check_out_date=request.check_out_date,
        adults=request.adults,
        children=request.children,
        rooms=request.rooms,
        sort_by=request.sort_by,
        hotel_class=request.hotel_class
    )
    
    # Add configuration for checkpointing
    thread_id = str(uuid.uuid4())
    config = {'configurable': {'thread_id': thread_id}}
    
    # Create a human message that will trigger hotel search
    query = f"Find hotels in {request.location} from {request.check_in_date} to {request.check_out_date}"
    message = HumanMessage(content=query)
    result = agent.graph.invoke({"messages": [message]}, config=config)
    return {"results": result, "status": "success"}

@app.post("/travel/email", status_code=status.HTTP_200_OK)
async def send_email(request: EmailRequest):
    """Send travel information via email"""
    
    # Set environment variables for email
    os.environ['FROM_EMAIL'] = request.from_email
    os.environ['TO_EMAIL'] = request.to_email
    os.environ['EMAIL_SUBJECT'] = request.subject
    
    # Validate Gmail App Password is set
    if not os.getenv('GMAIL_APP_PASSWORD'):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gmail App Password not configured"
        )
    
    # Create a message for the agent
    message = HumanMessage(content=request.content)
    
    # Add configuration for checkpointing
    thread_id = str(uuid.uuid4())
    config = {'configurable': {'thread_id': thread_id}}
    
    # Process through agent's email sender
    result = agent.graph.invoke({"messages": [message]}, config=config)
    return {"status": "success", "message": "Email sent successfully"}

@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "services": {
            "agent": "online",
            "flights_finder": "online",
            "hotels_finder": "online"
        }
    }

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Global exception handler for HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "status": "error"}
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )