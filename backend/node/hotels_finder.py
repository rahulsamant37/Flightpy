from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool

from models.model import HotelsInputSchema
from utils.hotel_find import parse_hotel_results

@tool(args_schema=HotelsInputSchema)
def hotels_finder(params: HotelsInputSchema):
    '''
    Find hotels using DuckDuckGo search.
    
    Returns:
        list: Top 5 hotel search results.
    '''
    
    # Initialize DuckDuckGo search tool
    search_tool = DuckDuckGoSearchRun()
    
    # Build search query
    query = f"hotels {params.q} check in {params.check_in_date} check out {params.check_out_date} "
    query += f"{params.adults} adults "
    
    if params.children and params.children > 0:
        query += f"{params.children} children "
    
    if params.rooms and params.rooms > 1:
        query += f"{params.rooms} rooms "
    
    if params.hotel_class:
        stars = " ".join([f"{star}-star" for star in params.hotel_class])
        query += f"{stars} "
    
    if params.sort_by and params.sort_by != "relevance":
        query += f"sort by {params.sort_by} "
    
    # Execute search
    search_results = search_tool.invoke(query)
    hotel_results = parse_hotel_results(search_results)
    
    return hotel_results[:5]
