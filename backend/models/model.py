from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr

class HotelsInput(BaseModel):
    q: str = Field(..., description="Search query for hotels")
    check_in_date: str = Field(..., description="Check-in date in YYYY-MM-DD format")
    check_out_date: str = Field(..., description="Check-out date in YYYY-MM-DD format")
    adults: int = Field(2, description="Number of adults")
    children: Optional[int] = Field(0, description="Number of children")
    rooms: Optional[int] = Field(1, description="Number of rooms")
    sort_by: Optional[str] = Field("relevance", description="Sort results by: relevance, price, rating")
    hotel_class: Optional[List[int]] = Field(None, description="Hotel class/star rating (1-5)")

class HotelsInputSchema(BaseModel):
    params: HotelsInput

class FlightsInput(BaseModel):
    departure_airport: str = Field(..., description="Departure airport code (e.g., LAX)")
    arrival_airport: str = Field(..., description="Arrival airport code (e.g., JFK)")
    outbound_date: str = Field(..., description="Outbound date in YYYY-MM-DD format")
    return_date: Optional[str] = Field(None, description="Return date in YYYY-MM-DD format for round trips")
    adults: int = Field(1, description="Number of adult passengers")
    children: Optional[int] = Field(0, description="Number of children passengers")
    infants_in_seat: Optional[int] = Field(0, description="Number of infants requiring a seat")
    infants_on_lap: Optional[int] = Field(0, description="Number of infants on lap")

class EmailRequest(BaseModel):
    from_email: EmailStr
    to_email: EmailStr
    subject: str
    content: str
class FlightsInputSchema(BaseModel):
    params: FlightsInput

class TravelQuery(BaseModel):
    query: str

class SearchFlightsRequest(BaseModel):
    departure_airport: str
    arrival_airport: str
    outbound_date: str
    return_date: Optional[str] = None
    adults: int = 1
    children: int = 0
    infants_in_seat: int = 0
    infants_on_lap: int = 0

class SearchHotelsRequest(BaseModel):
    location: str
    check_in_date: str
    check_out_date: str
    adults: int = 2
    children: int = 0
    rooms: int = 1
    sort_by: str = "relevance"
    hotel_class: Optional[List[int]] = None