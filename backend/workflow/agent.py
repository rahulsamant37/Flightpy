from langchain_openai import ChatOpenAI
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from langchain_core.messages import AnyMessage, HumanMessage, SystemMessage, ToolMessage
from langgraph.graph import START, END, StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import MessagesState

from prompt.prompt import EMAILS_SYSTEM_PROMPT, TOOLS_SYSTEM_PROMPT
from node.flights_finder import flights_finder
from node.hotels_finder import hotels_finder

TOOLS = [flights_finder, hotels_finder]

load_dotenv()
os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')

class Agent:

    def __init__(self):
        self._tools = {t.name: t for t in TOOLS}
        self._tools_llm = ChatOpenAI(model='gpt-4o').bind_tools(TOOLS)

        builder = StateGraph(MessagesState)
        builder.add_node('call_tools_llm', self.call_tools_llm)
        builder.add_node('invoke_tools', self.invoke_tools)
        builder.add_node('email_sender', self.email_sender)
        builder.set_entry_point('call_tools_llm')

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

    def email_sender(self, state: MessagesState):
        print('Sending email')
        email_llm = ChatOpenAI(model='gpt-4o', temperature=0.1)  # Instantiate another LLM
        email_message = [SystemMessage(content=EMAILS_SYSTEM_PROMPT), HumanMessage(content=state['messages'][-1].content)]
        email_response = email_llm.invoke(email_message)
        print('Email content:', email_response.content)

        message = Mail(from_email=os.environ['FROM_EMAIL'], to_emails=os.environ['TO_EMAIL'], subject=os.environ['EMAIL_SUBJECT'],
                       html_content=email_response.content)
        try:
            sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
            response = sg.send(message)
            print(response.status_code)
            print(response.body)
            print(response.headers)
        except Exception as e:
            print(str(e))

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