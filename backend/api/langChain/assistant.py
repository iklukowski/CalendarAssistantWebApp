from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.tools import tool
#from langchain_core.memory import ConversationBufferMemory
from typing import Optional, Annotated, Literal
from typing_extensions import TypedDict
from pydantic import BaseModel, Field
from ..models import Event
from dotenv import load_dotenv
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from datetime import datetime
from django.contrib.auth.models import User
from langgraph.graph import MessagesState, END, StateGraph, START
from langgraph.types import Command
from langchain.prompts import ChatPromptTemplate

class ChatEvent(BaseModel):
    """Structure of the event"""
    date: str = Field(description="date of the event in the YYYY-MM-DD format")
    title: str = Field(description="title of the event")
    start_time: str = Field(description="start time of the event in the HH:MM format")
    end_time: str = Field(description="end time of the event in the HH:MM format")


members = ["researcher", "scheduler", "conversation"]
options = members + ["FINISH"]

class UserSchema(BaseModel):
    id: int = 0
    username: str = ""
    
    @classmethod
    def from_django_user(cls,user : User):
        return cls(
            id=user.id,
            username=user.username
        )

class CurrentUser:
    user: User
    
    def setUser(self, user: User):
        self.user = user
    def getUser(self):
        return self.user
    
current_user = CurrentUser()

class Router(TypedDict):
    """Worker to route to next. If no workers needed, route to FINISH.
        Use instructions to provide additional information to the agent."""
    next: Literal[*options]
    instructions: Optional[str] = None
    
system_prompt = (
    "You are a supervisor to calendar managing a system of Agents. "
    f"Here is the list of agents: {members}. "
    "Given the user request respond with the agent to act next. "
    "Each agent will perform a task connected to the calendar and respond with their results and status except the conversation agent who will end the process. "
    "based on each agent's response, write the instructions for the next agent. "
    "When finished call the conversation agent. ONLY CALL THE CONVERSATION AGENT AT THE END OR WHEN USER INFO IS NEEDED. "
    "Use the conversation agent to finish the processing of a request. It will end the graph. Avoid looping. "
    f"Today is {datetime.now().strftime('%Y-%m-%d')}, {datetime.now().strftime('%H:%M')}, {datetime.now().strftime('%A')}. "
    "In case of updating or deleting an event, provide the id of the event to be updated or deleted. "
    "Remember to give detailed instructions to the agents like exact dates, times, titles, and other information. "
    "You can assume missing details of events if not provided by the user, some default values are: date - today, start time - 10:00, end time - 12:00, title - 'Event. "
    "When not sure about the time details assume the user is meaning about an event close to the current time."
)

llm = ChatOpenAI(model="gpt-4.1-mini")


class State(MessagesState):
    next: str

def supervisor_node(state: State) -> Command[Literal[*members, "__end__" ]]:
    messages = [
        {"role": "system", "content": system_prompt},
    ] + state["messages"]
    response = llm.with_structured_output(Router).invoke(messages)
    goto = response["next"]
    if goto == "FINISH":
        goto = END
        
    return Command(goto=goto, update={"next": goto, 
                                      "messages": [HumanMessage(content=response["instructions"], name="supervisor")]
                                      })



@tool
def getEvents() -> list[dict]:
    """Get events from the calendar and format them for the LLM."""
    try:
        events = Event.objects.filter(author=current_user.getUser())
        formatted_events = [
            {
                "id": event.id,
                "title": event.title,
                "date": event.date.strftime("%Y-%m-%d"),
                "start_time": event.start_time.strftime("%H:%M"),
                "end_time": event.end_time.strftime("%H:%M"),
            }
            for event in events
        ]
        return formatted_events
    except Exception as e:
        return [{"error": f"Error retrieving events: {e}"}]


research_prompt = ChatPromptTemplate.from_messages([
    SystemMessage(content="You are a calendar information exctractor agent. After extracting the information about the user calendar, respond with the plan for the scheduler agent."
            "The plan should be a list of events to create, a list of events to update, and a list of events to delete."
            "The plan should be in the format: {'create': [], 'update': [], 'delete': []}"
            "Try to follow supervisor instructions and not question them too much."
            "Cancel means delete, and reschedule means update."
            "Do not get stuck calling the tool indefnitely, you only need to call it once."),
])

research_agent = create_react_agent(
    model=llm,
    tools=[getEvents],
    prompt="You are a calendar information exctractor agent. After extracting the information about the user calendar, respond with the plan for the scheduler agent."
            "The plan should be a list of events to create, a list of events to update, and a list of events to delete."
            "The plan should be in the format: {'create': [], 'update': [], 'delete': []}"
            "Try to follow supervisor instructions and not question them too much."
            "Cancel means delete, and reschedule means update."
            "Do not get stuck calling the tool indefnitely, you only need to call it once.",
)


def research_node(state: State) -> Command[Literal["supervisor"]]:
    result = research_agent.invoke(state)
    return Command(
        update={
            "messages": [
                HumanMessage(content=result["messages"][-1].content, name="researcher"),
            ]
        },
        goto="supervisor",
    )
 

@tool
def createEvent(event: Annotated[ChatEvent, Field(description="Event to create")]):
    '''Create an event in the calendar'''
    try:
        event = Event(
            author=current_user.getUser(),
            title=event.title,
            date=datetime.strptime(event.date, "%Y-%m-%d").date(),
            start_time=datetime.strptime(event.start_time, "%H:%M").time(),
            end_time=datetime.strptime(event.end_time, "%H:%M").time(),
        )
        event.save()
       #print(f"Event created: {event}")
    except Exception as e:
        return f"Error creating event: {e}"
    return f"Event created successfully {event}"

@tool
def updateEvent(update_id: Annotated[int, Field(description="Id of the event that should be updated")], updated_event: Annotated[ChatEvent, Field(description="Event to update")]):
    '''Update an event in the calendar'''
    try:
        event = Event.objects.get(id=update_id, author=current_user.getUser())
        event.title = updated_event.title
        event.date = datetime.strptime(updated_event.date, "%Y-%m-%d").date()
        event.start_time = datetime.strptime(updated_event.start_time, "%H:%M").time()
        event.end_time = datetime.strptime(updated_event.end_time, "%H:%M").time()
        event.save()
       #print(f"Event updated: {event}")
    except Exception as e:
        return f"Error updating event: {e}"
    return f"Event updated successfully {updated_event}"

@tool
def deleteEvent(delete_id: Annotated[int, Field(description="Id of the event that should be deleted")]):
    '''Delete an event in the calendar'''
    try:
        event = Event.objects.get(id=delete_id, author=current_user.getUser())
        event.delete()
       #print(f"Event deleted: {event}")
    except Exception as e:
        return f"Error deleting event: {e}"
    return f"Event deleted successfully {event}"
    
scheduler_agent = create_react_agent(
    model=llm,
    tools=[createEvent, updateEvent, deleteEvent],
    prompt="You are a calendar event scheduler agent. After receiving the plan from the researcher agent, you will use available tools modify the calendar in accordance to the plan."
            "In case of any errors, you will respond with the issues to the supervisor agent."
            "Try to follow supervisor instructions and not question them too much."
            "If you do not finish all tasks at once, respond with done tasks and notify the supervisor of the remaining tasks."
            "If you finish all tasks, respond with the summary of the tasks and notify the supervisor."
) 
        
def scheduler_node(state: State) -> Command[Literal["supervisor"]]:
    result = scheduler_agent.invoke(state)
    return Command(
        update={
            "messages": [
                HumanMessage(content=result["messages"][-1].content, name="scheduler")
            ]
        },
        goto="supervisor",
    )

class ConversationResponse(TypedDict):
    """Structure of the conversation response"""
    message: str
    next: Literal["supervisor", "FINISH"]


conversation_prompt = ("You are a conversation agent. You will be used to have a conversation with the user. "
                    "Your task will be to summarize the actions of the agents and provide the user with the final summary to the request. "
        "Your answer should be short and concise but friendly. "
        "If the supervisor agent need additional information from the user, you will ask the user for it by ending the conversation. "
        "Almost always next should be FINISH."
)


def conversation_node(state: State) -> Command[Literal["__end__"]]:
    messages = [
        {"role": "system", "content": conversation_prompt},
    ] + state["messages"]
    result = llm.with_structured_output(ConversationResponse).invoke(messages)
    goto = END
    #if result["next"] == "FINISH":
    #    goto = END
    #else:
    #    goto = "supervisor"
    return Command(
        update={
            "next": goto,
            "messages": [
                HumanMessage(content=result["message"], name="conversation")
            ]
        },
        goto=goto,
    )
# Create the state graph

memory = MemorySaver()
config = {"configurable": {"thread_id": "abc123"}}

builder = StateGraph(State)
builder.add_edge(START, "supervisor")
builder.add_node("supervisor", supervisor_node)
builder.add_node("researcher", research_node)
builder.add_node("scheduler", scheduler_node)
builder.add_node("conversation", conversation_node)
graph = builder.compile(checkpointer=memory)
#try:
#    graph.get_graph().draw_mermaid_png(output_file_path="graph.png")
#except Exception as e:
#    print(f"Error drawing graph: {e}")
#graph.get_graph().draw_mermaid_png(output_file_path="graph.png")

    
class CalendarAssistant:
    def __init__(self, user: User):
        load_dotenv()
        #self.user = UserSchema.from_django_user(user)
        self.graph = graph
        self.state = {"messages": [], "next": "supervisor"}
        current_user.setUser(user)
        #self.graph.get_graph().draw_mermaid_png(output_file_path="graph.png")
        #self.state.start()  # Start the state machine

    def run(self, message: str):
        self.state["messages"].append({"role": "user", "content": message})
        for s in self.graph.stream(self.state, subgraphs=True, stream_mode="updates", config=config):
            # Access the state update
            state_update = s[1]
            for agent_name, agent_state in state_update.items():
                # Print the agent name and its state
                #print(f"Agent: {agent_name}")
                #print(f"State: {agent_state}")
                #print(f"Message: {agent_state.get("messages", [])[-1].content}")
                messages = agent_state.get("messages", [])[-1]
                self.state["messages"].append(messages)
                #print("---")
            
        # Return the last message content
        #print(f"Last message: {self.state['messages'][-1]}")
        return {"response": self.state["messages"][-1].content}
        