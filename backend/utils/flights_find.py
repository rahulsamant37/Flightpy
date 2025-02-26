import re

def parse_flight_results(search_results: str) -> list:
    """
    Parse flight information from DuckDuckGo search results.
    
    Args:
        search_results: Raw text results from DuckDuckGo
        
    Returns:
        list: List of dictionaries containing flight information
    """
    flights = []
    
    # Pattern matching for potential flight information
    # Looking for patterns like: "Airline - $Price - Duration - Stops"
    airline_pattern = r"([\w\s]+Airlines|[\w\s]+Airways|Delta|United|American|Southwest|JetBlue|Alaska|Spirit)"
    price_pattern = r"\$(\d+(?:,\d+)?(?:\.\d+)?)"
    time_pattern = r"(\d+h\s*\d+m|\d+\s*hours?\s*(?:\d+\s*minutes?)?)"
    
    # Split by new lines to process each result separately
    lines = search_results.split('\n')
    current_flight = {}
    
    for line in lines:
        # Skip empty lines
        if not line.strip():
            if current_flight and len(current_flight) >= 2:  # At least airline and price
                flights.append(current_flight)
                current_flight = {}
            continue
        
        # Look for airline names
        airline_match = re.search(airline_pattern, line)
        if airline_match and 'airline' not in current_flight:
            current_flight['airline'] = airline_match.group(0).strip()
            
        # Look for prices
        price_match = re.search(price_pattern, line)
        if price_match and 'price' not in current_flight:
            current_flight['price'] = price_match.group(0).strip()
            
        # Look for flight times/duration
        time_match = re.search(time_pattern, line)
        if time_match and 'duration' not in current_flight:
            current_flight['duration'] = time_match.group(0).strip()
            
        # Look for stops information
        if 'nonstop' in line.lower() and 'stops' not in current_flight:
            current_flight['stops'] = 'Nonstop'
        elif '1 stop' in line.lower() and 'stops' not in current_flight:
            current_flight['stops'] = '1 stop'
        elif '2 stop' in line.lower() and 'stops' not in current_flight:
            current_flight['stops'] = '2 stops'
        
        # Look for departure/arrival times
        if re.search(r'\d{1,2}:\d{2}\s*[APap][Mm]', line) and 'times' not in current_flight:
            current_flight['times'] = line.strip()
    
    # Add the last flight if it exists
    if current_flight and len(current_flight) >= 2:
        flights.append(current_flight)
    
    # If no structured data could be extracted, create general results
    if not flights:
        # Create some best guess results based on keywords in the search results
        segments = re.split(r'\.\s+', search_results)
        for i, segment in enumerate(segments[:5]):  # Limit to 5 results
            if any(keyword in segment.lower() for keyword in ['flight', 'airline', 'airport', '$', 'ticket']):
                flights.append({
                    "information": segment.strip(),
                    "note": "This is an extracted text segment that may contain flight information."
                })
    
    # Return the top 5 results or fewer if less are found
    return flights[:5]