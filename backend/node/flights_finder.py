from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool
from datetime import datetime

from models.model import FlightsInputSchema
from utils.flights_find import parse_flight_results

@tool(args_schema=FlightsInputSchema)
def flights_finder(params: FlightsInputSchema):
    '''
    Find flights using DuckDuckGo search.

    Returns:
        list: Flight search results.
    '''
    
    # Initialize DuckDuckGo search tool
    search_tool = DuckDuckGoSearchRun()
    
    # Format dates for readability
    try:
        outbound_date_obj = datetime.strptime(params.outbound_date, "%Y-%m-%d")
        outbound_date_formatted = outbound_date_obj.strftime("%B %d, %Y")
    except ValueError:
        outbound_date_formatted = params.outbound_date
    
    return_date_formatted = None
    if params.return_date:
        try:
            return_date_obj = datetime.strptime(params.return_date, "%Y-%m-%d")
            return_date_formatted = return_date_obj.strftime("%B %d, %Y")
        except ValueError:
            return_date_formatted = params.return_date
    
    # Build search query
    query = f"flights from {params.departure_airport} to {params.arrival_airport} "
    query += f"on {outbound_date_formatted} "
    
    if return_date_formatted:
        query += f"return {return_date_formatted} "
    
    passenger_info = []
    if params.adults > 0:
        passenger_info.append(f"{params.adults} adult{'s' if params.adults > 1 else ''}")
    if params.children > 0:
        passenger_info.append(f"{params.children} child{'ren' if params.children > 1 else ''}")
    if params.infants_in_seat > 0:
        passenger_info.append(f"{params.infants_in_seat} infant{'s' if params.infants_in_seat > 1 else ''} with seat")
    if params.infants_on_lap > 0:
        passenger_info.append(f"{params.infants_on_lap} infant{'s' if params.infants_on_lap > 1 else ''} on lap")
    
    if passenger_info:
        query += f"for {', '.join(passenger_info)} "
    
    query += "best flights with prices"
    
    # Execute search
    try:
        search_results = search_tool.invoke(query)
        flight_results = parse_flight_results(search_results)
        
        # Return empty list with message if no flights found
        if not flight_results:
            return [{"message": "No flight results could be extracted from the search. Try adjusting your search parameters."}]
        
        return flight_results
    except Exception as e:
        return [{"error": str(e)}]