import os
import uuid
import requests
import streamlit as st
from langchain_core.messages import HumanMessage

def render_custom_css():
    """Render custom CSS styles"""
    st.markdown(
        '''
        <style>
        .main-title {
            font-size: 2.5em;
            color: #333;
            text-align: center;
            margin-bottom: 0.5em;
            font-weight: bold;
        }
        .sub-title {
            font-size: 1.2em;
            color: #333;
            text-align: left;
            margin-bottom: 0.5em;
        }
        .center-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            width: 100%;
        }
        .query-box {
            width: 80%;
            max-width: 600px;
            margin-top: 0.5em;
            margin-bottom: 1em;
        }
        .query-container {
            width: 80%;
            max-width: 600px;
            margin: 0 auto;
        }
        </style>
        ''', unsafe_allow_html=True
    )

def render_ui():
    """Render the main UI components"""
    st.markdown('<div class="center-container">', unsafe_allow_html=True)
    st.markdown('<div class="main-title">✈️🌍 FlightPy Travel Agent 🏨🗺️</div>', unsafe_allow_html=True)
    st.markdown('<div class="query-container">', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Enter your travel query and get flight and hotel information:</div>', unsafe_allow_html=True)
    
    # Travel Query Input
    user_input = st.text_area(
        'Travel Query',
        height=200,
        key='query',
        placeholder='Example: Find flights from NYC to London from March 15-22 and hotels near Big Ben',
    )
    
    # Advanced Search Options
    with st.expander("Advanced Search Options"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Flight Options")
            departure = st.text_input("Departure Airport (e.g., JFK)")
            arrival = st.text_input("Arrival Airport (e.g., LHR)")
            outbound = st.date_input("Outbound Date")
            return_date = st.date_input("Return Date")
            adults = st.number_input("Adults", min_value=1, value=1)
            children = st.number_input("Children", min_value=0, value=0)
        
        with col2:
            st.subheader("Hotel Options")
            location = st.text_input("Location")
            check_in = st.date_input("Check-in Date")
            check_out = st.date_input("Check-out Date")
            rooms = st.number_input("Rooms", min_value=1, value=1)
            hotel_class = st.multiselect("Hotel Class", options=[3, 4, 5], default=[4])

    st.markdown('</div>', unsafe_allow_html=True)
    
    return {
        'query': user_input,
        'flight_options': {
            'departure': departure,
            'arrival': arrival,
            'outbound': outbound,
            'return_date': return_date,
            'adults': adults,
            'children': children
        },
        'hotel_options': {
            'location': location,
            'check_in': check_in,
            'check_out': check_out,
            'rooms': rooms,
            'hotel_class': hotel_class
        }
    }

def process_query(query_data, api_url="http://localhost:8000"):
    """Process the travel query through the API"""
    if query_data['query']:
        try:
            # Natural language query
            response = requests.post(
                f"{api_url}/travel/query",
                json={"query": query_data['query']}
            )
            result = response.json()
            
            st.subheader('Travel Information')
            
            # Handle the response content properly
            if result.get('response') and result['response'].get('messages'):
                content = result['response']['messages'][0].get('content', '')
                st.write(content)
                st.session_state.travel_info = content
            else:
                st.write("No results found")
            
        except Exception as e:
            st.error(f'Error: {e}')

def render_email_form():
    """Render the email form"""
    send_email_option = st.radio('Do you want to send this information via email?', ('No', 'Yes'))
    if send_email_option == 'Yes':
        with st.form(key='email_form'):
            sender_email = st.text_input('Gmail Address', help="Enter your Gmail address")
            app_password = st.text_input('Gmail App Password', type='password', help="Enter your Gmail App Password")
            receiver_email = st.text_input('Receiver Email')
            subject = st.text_input('Email Subject', 'Travel Information')
            submit_button = st.form_submit_button(label='Send Email')

            if submit_button:
                if sender_email and receiver_email:
                    try:
                        # Send email request to backend
                        response = requests.post(
                            "http://localhost:8000/travel/email",
                            json={
                                "from_email": sender_email,
                                "to_email": receiver_email,
                                "subject": subject,
                                "content": st.session_state.travel_info
                            }
                        )
                        
                        if response.status_code == 200:
                            st.success('Email sent successfully!')
                            # Clear session state
                            for key in ['travel_info']:
                                st.session_state.pop(key, None)
                        else:
                            st.error(f'Failed to send email: {response.json().get("detail", "Unknown error")}')
                    except Exception as e:
                        st.error(f'Error sending email: {e}')
                else:
                    st.error('Please fill out both sender and receiver email addresses.')

def main():
    # Page config
    st.set_page_config(
        page_title="FlightPy Travel Assistant",
        page_icon="✈️",
        layout="wide"
    )
    
    # Render CSS
    render_custom_css()
    
    # Render main UI
    query_data = render_ui()
    
    # Process query button
    if st.button('Search Travel Options'):
        process_query(query_data)
    
    # Render email form if results are available
    if 'travel_info' in st.session_state:
        render_email_form()

if __name__ == '__main__':
    main()