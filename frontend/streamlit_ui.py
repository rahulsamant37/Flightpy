# pylint: disable = invalid-name
import os
import requests
import streamlit as st

# API endpoint configuration
API_BASE_URL = "http://localhost:8000"

def process_query(user_input: str):
    """Send travel query to backend API"""
    if user_input:
        try:
            response = requests.post(
                f"{API_BASE_URL}/query",
                json={"query": user_input}
            )
            response.raise_for_status()
            result = response.json()
            
            st.session_state.thread_id = result["thread_id"]
            st.session_state.travel_info = result["response"]
            
            st.subheader('Travel Information')
            st.write(st.session_state.travel_info)
            
        except Exception as e:
            st.error(f'Error: {e}')
    else:
        st.error('Please enter a travel query.')

def send_email(sender_email: str, receiver_email: str, subject: str):
    """Send email through backend API"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/email",
            json={
                "from_email": sender_email,
                "to_email": receiver_email,
                "subject": subject,
                "content": st.session_state.travel_info
            }
        )
        response.raise_for_status()
        st.success('Email sent successfully!')
        
        # Clear session state
        for key in ['travel_info', 'thread_id']:
            st.session_state.pop(key, None)
            
    except Exception as e:
        st.error(f'Error sending email: {e}')

def render_custom_css():
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
        ''', unsafe_allow_html=True)

def render_ui():
    st.markdown('<div class="center-container">', unsafe_allow_html=True)
    st.markdown('<div class="main-title">✈️🌍 AI Travel Agent 🏨🗺️</div>', unsafe_allow_html=True)
    st.markdown('<div class="query-container">', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Enter your travel query and get flight and hotel information:</div>', unsafe_allow_html=True)
    user_input = st.text_area(
        'Travel Query',
        height=200,
        key='query',
        placeholder='Type your travel query here...',
    )
    st.markdown('</div>', unsafe_allow_html=True)

    return user_input

def render_email_form():
    send_email_option = st.radio('Do you want to send this information via email?', ('No', 'Yes'))
    if send_email_option == 'Yes':
        with st.form(key='email_form'):
            sender_email = st.text_input('Sender Email')
            receiver_email = st.text_input('Receiver Email')
            subject = st.text_input('Email Subject', 'Travel Information')
            submit_button = st.form_submit_button(label='Send Email')

        if submit_button:
            if sender_email and receiver_email and subject:
                send_email(sender_email, receiver_email, subject)
            else:
                st.error('Please fill out all email fields.')

def main():
    render_custom_css()
    user_input = render_ui()

    if st.button('Get Travel Information'):
        process_query(user_input)

    if 'travel_info' in st.session_state:
        render_email_form()

if __name__ == '__main__':
    main()