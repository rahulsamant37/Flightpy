from langchain_core.tools import tool
from datetime import datetime
import serpapi
import os

from models.model import FlightsInputSchema, FlightsInput
from utils.flights_find import parse_flight_results

@tool(args_schema=FlightsInputSchema)
def flights_finder(params: FlightsInput):
    '''
    Find flights using the Google Flights engine.

    Returns:
        dict: Flight search results.
    '''

    params = {
        'api_key': os.environ.get('SERPAPI_API_KEY'),
        'engine': 'google_flights',
        'hl': 'en',
        'gl': 'us',
        'departure_id': params.departure_airport,
        'arrival_id': params.arrival_airport,
        'outbound_date': params.outbound_date,
        'return_date': params.return_date,
        'currency': 'USD',
        'adults': params.adults,
        'infants_in_seat': params.infants_in_seat,
        'stops': '1',
        'infants_on_lap': params.infants_on_lap,
        'children': params.children
    }

    try:
        search = serpapi.search(params)
        results = search.data['best_flights']
    except Exception as e:
        results = str(e)
    return results