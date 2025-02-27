from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uuid
from typing import Optional

from models.model import (
    TravelQuery, 
    SearchFlightsRequest, 
    SearchHotelsRequest,
    EmailRequest
)
from workflow.agent import Agent

app = FastAPI(title="Travel Agent API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agent as a global variable
agent = Agent()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Travel Agent API is running"}

@app.post("/query")
async def process_travel_query(query: TravelQuery):
    """Process a natural language travel query"""
    try:
        thread_id = str(uuid.uuid4())
        messages = [{"role": "user", "content": query.query}]
        config = {'configurable': {'thread_id': thread_id}}
        
        result = agent.graph.invoke({'messages': messages}, config=config)
        
        return {
            "thread_id": thread_id,
            "response": result['messages'][-1].content,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search/flights")
async def search_flights(request: SearchFlightsRequest):
    """Search for flights using specific criteria"""
    try:
        params = {
            "departure_airport": request.departure_airport,
            "arrival_airport": request.arrival_airport,
            "outbound_date": request.outbound_date,
            "return_date": request.return_date,
            "adults": request.adults,
            "children": request.children,
            "infants_in_seat": request.infants_in_seat,
            "infants_on_lap": request.infants_on_lap
        }
        
        results = agent._tools['flights_finder'].invoke(params)
        return {"flights": results, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search/hotels")
async def search_hotels(request: SearchHotelsRequest):
    """Search for hotels using specific criteria"""
    try:
        params = {
            "q": request.location,
            "check_in_date": request.check_in_date,
            "check_out_date": request.check_out_date,
            "adults": request.adults,
            "children": request.children,
            "rooms": request.rooms,
            "sort_by": request.sort_by,
            "hotel_class": request.hotel_class
        }
        
        results = agent._tools['hotels_finder'].invoke(params)
        return {"hotels": results, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/email")
async def send_email(request: EmailRequest):
    """Send travel information via email"""
    try:
        thread_id = str(uuid.uuid4())
        config = {
            'configurable': {
                'thread_id': thread_id,
                'from_email': request.from_email,
                'to_email': request.to_email,
                'subject': request.subject
            }
        }
        
        agent.graph.invoke({'content': request.content}, config=config)
        return {"status": "success", "message": "Email sent successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)