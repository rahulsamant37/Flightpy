from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr

class HotelsInput(BaseModel):
    q: str = Field(description='Location of the hotel')
    check_in_date: str = Field(description='Check-in date. The format is YYYY-MM-DD. e.g. 2024-06-22')
    check_out_date: str = Field(description='Check-out date. The format is YYYY-MM-DD. e.g. 2024-06-28')
    sort_by: Optional[str] = Field(8, description='Parameter is used for sorting the results. Default is sort by highest rating')
    adults: Optional[int] = Field(1, description='Number of adults. Default to 1.')
    children: Optional[int] = Field(0, description='Number of children. Default to 0.')
    rooms: Optional[int] = Field(1, description='Number of rooms. Default to 1.')
    hotel_class: Optional[str] = Field(
        None, description='Parameter defines to include only certain hotel class in the results. for example- 2,3,4')

class HotelsInputSchema(BaseModel):
    params: HotelsInput

class FlightsInput(BaseModel):
    departure_airport: Optional[str] = Field(description='Departure airport code (IATA)')
    arrival_airport: Optional[str] = Field(description='Arrival airport code (IATA)')
    outbound_date: Optional[str] = Field(description='Parameter defines the outbound date. The format is YYYY-MM-DD. e.g. 2024-06-22')
    return_date: Optional[str] = Field(description='Parameter defines the return date. The format is YYYY-MM-DD. e.g. 2024-06-28')
    adults: Optional[int] = Field(1, description='Parameter defines the number of adults. Default to 1.')
    children: Optional[int] = Field(0, description='Parameter defines the number of children. Default to 0.')
    infants_in_seat: Optional[int] = Field(0, description='Parameter defines the number of infants in seat. Default to 0.')
    infants_on_lap: Optional[int] = Field(0, description='Parameter defines the number of infants on lap. Default to 0.')

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

class EmailRequest(BaseModel):
    from_email: EmailStr
    to_email: EmailStr
    subject: str
    content: str