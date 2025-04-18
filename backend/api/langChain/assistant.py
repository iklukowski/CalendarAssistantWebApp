from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.tools import tool
#from langchain_core.memory import ConversationBufferMemory
from typing import Optional, Annotated
from pydantic import BaseModel, Field
from ..models import Event
from dotenv import load_dotenv
from langgraph.prebuilt import InjectedState, create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from datetime import datetime

class ChatEvent(BaseModel):
    """Structured representation of an event"""
    id: str = Field(description="The unique identifier of the event (use string + number)")
    date: str = Field(description="The date of the event in YYYY-MM-DD format")
    title: str = Field(description="The title of the event")
    start_time: str = Field(description="The start time of the event in HH:MM format")
    end_time: str = Field(description="The end time of the event in HH:MM format")

    
class CreateEventResponse(BaseModel):
    """Response for creating an event"""
    event: Optional[list[ChatEvent]] = Field(description="The created list of events")
    success: bool = Field(description="Indicates if the event was successfully created")
    message: str = Field(description="A message indicating the result of the event creation")

class CalendarAssistant:
    def __init__(self):
        load_dotenv()   
        self.payload = {
            "description": "",
            "new_events": None,
            "modified_events": None,
            "deleted_events": None,
            "modify_calendar": False,
            "response": None
        }
        self.tools = [self.generate_events_agent]
        self.model = ChatOpenAI(model="gpt-4o-mini")
        self.memory = MemorySaver()
        self.supervisor = create_react_agent(
            model=self.model,
            tools=self.tools,
            prompt="You are a helpful calendar assistant that supervises other agents to create, update and modify events in the calendar of the user",
            checkpointer=self.memory,
        )
        self.config = {"configurable": {"thread_id": "abc235"}}
        
     #   self.memory = ConversationBufferMemory(memory_key="chat_history")
    
    
    def generate_events_agent(self, state: Annotated[dict, InjectedState]):
        ''' An agent that only creates events based on the user request, he does not update or delete events
            He handles multiples events in the same request
        '''
        llm = ChatOpenAI(model="gpt-4o-mini")
        structured_llm = llm.with_structured_output(CreateEventResponse)
        # Extract the last human message from the state
        human_messages = [msg for msg in state["messages"] if isinstance(msg, HumanMessage)]
        last_human_message = human_messages[-1].content if human_messages else ""

        response = structured_llm.invoke([
            SystemMessage(content=f"You are an event creating assistant agent in the calendar domain, your task is to create events in the calendar based on the user request. "
                  f"Today's date is {datetime.today().strftime('%Y-%m-%d')}, the current time is {datetime.now().strftime('%H:%M')}."),
            HumanMessage(content=last_human_message),
        ])
        if response.success:
            self.payload["new_events"] = response.event
            self.payload["modify_calendar"] = True
        return response
            
        
    def respond(self, user_input, user):
    #    chat_history = self.memory.load_memory_variables({})
        last_message = ""    
        for chunk in self.supervisor.stream(
            {"messages": [user_input]}, self.config, stream_mode="values"
        ):
            message = chunk["messages"][-1]
            message.pretty_print()
            if isinstance(message, AIMessage):
               last_message = message.content
            #print(chunk)
            #print("---------------------")
        print("Final payload")
        print(self.payload)
        print("---------------------")
        print("Last message")
        print(last_message)
        return {
            "description": self.payload["description"],
            "new_events": [event.dict() for event in self.payload["new_events"]] if self.payload["new_events"] else None,
            "modify_calendar": self.payload["modify_calendar"],
            "response": last_message,
        }
