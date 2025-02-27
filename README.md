# Flightpy

Flightpy is a travel agent API that helps users find flights and hotels, and send travel information via email. It uses various tools and APIs to provide accurate and up-to-date information.

## **Features**

- **Stateful Interactions**: The agent remembers user interactions and continues from where it left off, ensuring a smooth user experience.
- **Human-in-the-Loop**: Users have control over critical actions, like reviewing travel plans before emails are sent.
- **Dynamic LLM Usage**: The agent intelligently switches between different LLMs for various tasks, like tool invocation and email generation.
- **Email Automation**: Automatically generates and sends detailed travel plans to users via email.

## Setup

1. Clone the repository:
    ```bash
    git clone https://github.com/rahulsamant37/Flightpy.git
    cd Flightpy
    ```

2. Create a virtual environment and activate it:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Set up environment variables:
    Create a `.env` file in the root directory and add the following variables:
    ```
    OPENAI_API_KEY=your_openai_api_key
    SERPAPI_API_KEY=your_serpapi_api_key
    SENDGRID_API_KEY=your_sendgrid_api_key

    # Observability variables
    LANGCHAIN_API_KEY=your_langchain_api_key
    LANGCHAIN_TRACING_V2=true
    LANGCHAIN_PROJECT=ai_travel_agent
    ```

## Usage

1. Run the FastAPI server:
    ```bash
    uvicorn backend.main:app --reload
    ```

2. Access the API documentation at `http://127.0.0.1:8000/docs`.

3. To start the chatbot, run the following command:
```
streamlit run app.py
```

### Using the Chatbot
Once launched, simply enter your travel request. For example:
> I want to travel to Amsterdam from Madrid from October 1st to 7th. Find me flights and 4-star hotels.


![photo1](https://github.com/rahulsamant37/Flightpy/blob/main/assets/Four-Star%20Hotel%20Options%20in%20Amsterdam%20(March%201-7%2C%202025)%20(2).png)

The chatbot will generate results that include logos and links for easy navigation.

> **Note**: The data is fetched via Google Flights and Google Hotels APIs. There’s no affiliation or promotion of any particular brand.


#### Example Outputs

- Flight and hotel options with relevant logos and links for easy reference:

![photo2](https://github.com/user-attachments/assets/741e010c-22cf-4d31-a518-441b076ec58f)

![photo3](https://github.com/user-attachments/assets/a29173c7-852d-41ab-b3fe-94e6cca83c78)


#### Email Integration
The email integration is implemented using the **human-in-the-loop** feature, allowing you to stop the agent execution and return control back to the user, providing flexibility in managing the travel data before sending it via email.

![photo4](https://github.com/rahulsamant37/Flightpy/blob/main/assets/Four-Star%20Hotel%20Options%20in%20Amsterdam%20(March%201-7%2C%202025)%20(3).png)

- Travel data formatted in HTML, delivered straight to your inbox:
![photo5](https://github.com/rahulsamant37/Flightpy/blob/main/assets/Four-Star%20Hotel%20Options%20in%20Amsterdam%20(March%201-7%2C%202025)%20(1).png)
![photo6](https://github.com/rahulsamant37/Flightpy/blob/main/assets/Four-Star%20Hotel%20Options%20in%20Amsterdam%20(March%201-7%2C%202025).png)


## Endpoints

- `GET /` - Health check endpoint
- `POST /query` - Process a natural language travel query
- `POST /search/flights` - Search for flights using specific criteria
- `POST /search/hotels` - Search for hotels using specific criteria
- `POST /email` - Send travel information via email

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any changes.

## License

This project is licensed under the MIT License.
