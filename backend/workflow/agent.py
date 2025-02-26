from langchain_groq import ChatGroq
from langchain_core.messages import AnyMessage, HumanMessage, SystemMessage, ToolMessage
from langgraph.graph import START, END, StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import MessagesState

from prompt.prompt import EMAILS_SYSTEM_PROMPT, TOOLS_SYSTEM_PROMPT
from node.flights_finder import flights_finder
from node.hotels_finder import hotels_finder

TOOLS = [flights_finder, hotels_finder]

import os
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()
os.environ['GROQ_API_KEY'] = os.getenv('GROQ_API_KEY')

class Agent:

    def __init__(self):
        self._tools = {t.name: t for t in TOOLS}
        self._tools_llm = ChatGroq(model='gemma2-9b-it').bind_tools(TOOLS)

        builder = StateGraph(MessagesState)
        builder.add_node('call_tools_llm', self.call_tools_llm)
        builder.add_node('invoke_tools', self.invoke_tools)
        builder.add_node('email_sender', self.email_sender)

        builder.add_edge(START,'call_tools_llm')
        builder.add_conditional_edges('call_tools_llm', Agent.exists_action, {'more_tools': 'invoke_tools', 'email_sender': 'email_sender'})
        builder.add_edge('invoke_tools', 'call_tools_llm')
        builder.add_edge('email_sender', END)
        memory = MemorySaver()
        self.graph = builder.compile(checkpointer=memory, interrupt_before=['email_sender'])

        print(self.graph.get_graph().draw_mermaid())

    @staticmethod
    def exists_action(state: MessagesState):
        result = state['messages'][-1]
        if len(result.tool_calls) == 0:
            return 'email_sender'
        return 'more_tools'

    def send_email_with_smtp(from_email: str, to_email: str, subject: str, html_content: str, app_password: str):
        """Send email using Gmail SMTP"""
        try:
            # Create message
            message = MIMEMultipart('alternative')
            message['Subject'] = subject
            message['From'] = from_email
            message['To'] = to_email

            # Add HTML content
            html_part = MIMEText(html_content, 'html')
            message.attach(html_part)

            # Create SMTP connection
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(from_email, app_password)
                server.send_message(message)

            return True
        except Exception as e:
            print(f"Failed to send email: {str(e)}")
            raise e

    def email_sender(self, state: MessagesState):
        """Send email with travel information"""
        try:
            print('Preparing email')
            email_llm = ChatGroq(model='gemma2-9b-it', temperature=0.1)
            email_message = [
                SystemMessage(content=EMAILS_SYSTEM_PROMPT), 
                HumanMessage(content=state['messages'][-1].content)
            ]
            email_response = email_llm.invoke(email_message)

            # Get email details from environment
            from_email = os.getenv('FROM_EMAIL')
            to_email = os.getenv('TO_EMAIL')
            subject = os.getenv('EMAIL_SUBJECT', 'Travel Information')
            app_password = os.getenv('GMAIL_APP_PASSWORD')  # Gmail App Password

            # Send email using SMTP
            self.send_email_with_smtp(
                from_email=from_email,
                to_email=to_email,
                subject=subject,
                html_content=email_response.content,
                app_password=app_password
            )

            print('Email sent successfully')
            return {'messages': state['messages']}

        except Exception as e:
            print(f'Error in email_sender: {str(e)}')
            raise Exception(f'Error in email_sender: {str(e)}')

    def call_tools_llm(self, state: MessagesState):
        messages = state['messages']
        messages = [SystemMessage(content=TOOLS_SYSTEM_PROMPT)] + messages
        message = self._tools_llm.invoke(messages)
        return {'messages': [message]}

    def invoke_tools(self, state: MessagesState):
        tool_calls = state['messages'][-1].tool_calls
        results = []
        for t in tool_calls:
            print(f'Calling: {t}')
            if not t['name'] in self._tools:  # check for bad tool name from LLM
                print('\n ....bad tool name....')
                result = 'bad tool name, retry'  # instruct LLM to retry if bad
            else:
                result = self._tools[t['name']].invoke(t['args'])
            results.append(ToolMessage(tool_call_id=t['id'], name=t['name'], content=str(result)))
        print('Back to the model!')
        return {'messages': results}