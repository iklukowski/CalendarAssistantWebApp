from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.tools import tool
#from langchain_core.memory import ConversationBufferMemory
from typing import Optional, Annotated, Literal
from typing_extensions import TypedDict
from pydantic import BaseModel, Field
from ..models import Event
from dotenv import load_dotenv
from langgraph.prebuilt import InjectedState, create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from datetime import datetime
from django.contrib.auth.models import User
from langgraph.graph import MessagesState, END
from langgraph.types import Command

members = ["Creator", "Updater", "Deleter", "Conversation"]
membersL = Literal["Creator", "Updater", "Deleter", "Conversation"]

class Router(TypedDict):
    """Worker to route to next. If no workers needed, route to FINISH."""
    next: Literal["Creator", "Updater", "Deleter", "Conversation", "FINISH"]
    
system_prompt = (
    "You are a supervisor to calendar managing system of Agents"
    f"Here is the list of agents: {members}"
    "Given the user request respond with the agent to act next"
    "Each agent will perform a task connected to the calendar and respond with their results and status"
    "When finished respond with FINISH."
)

llm = ChatOpenAI(model="gpt-4o-mini")
class State(MessagesState):
    next: str

def supervisor_node(state: State) -> Command[Literal[membersL, "__end__" ]]:
    messages = [
        {"role": "system", "content": system_prompt},
    ] + state["messages"]
    response = llm.with_structured_output(Router).invoke(messages)
    goto = response["next"]
    if goto == "FINISH":
        goto = END
        
    return Command(goto=goto, update={"next": goto})
    
