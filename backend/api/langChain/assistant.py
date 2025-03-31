from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.tools import tool
#from langchain_core.memory import ConversationBufferMemory
from typing import Optional
from pydantic import BaseModel, Field
from ..models import Event


class ChatEvent(BaseModel):
    """Structured representation of an event"""
    date: str = Field(description="The date of the event in YYYY-MM-DD format")
    title: str = Field(description="The title of the event")
    start_time: str = Field(description="The start time of the event in HH:MM format")
    end_time: str = Field(description="The end time of the event in HH:MM format")

class Response(BaseModel):
    """Structured response for the assistant"""
    description: str = Field(description="A basic description of the human message and the assistant approach")
    events: Optional[list[ChatEvent]] = Field(description="A list of events that should be created to satisfy the user request")
    modify_calendar: bool = Field(description="A boolean indicating if the calendar should be modified, should be true if the user request is to add or modify an event, false otherwise")
    response: str = Field(description="The response to the user request")

class CalendarAssistant:
    def __init__(self):   
        self.llm = ChatOpenAI(model="gpt-4o-mini")
        self.structured_llm = self.llm.with_structured_output(Response)
     #   self.memory = ConversationBufferMemory(memory_key="chat_history")
     
    def handle_request(self, chat_response, user):
        print(chat_response)
        if chat_response.modify_calendar:
            for event in chat_response.events:
                try:
                    e = Event.objects.create(
                        title=event.title,
                        date=event.date,
                        start_time=event.start_time,
                        end_time=event.end_time,
                        author=user,
                    )
                    e.save()
                    print(f"Event created: {e.title} on {e.date} from {e.start_time} to {e.end_time}")
                except Exception as e:
                    print (f"Error creating event: {e}")
        return
        
    def respond(self, user_input, user):
    #    chat_history = self.memory.load_memory_variables({})    
        response = self.structured_llm.invoke([
            SystemMessage(content="You are a helpful calendar assistant"),
            HumanMessage(content=user_input)
        ])
        self.handle_request(response, user)
        
       # self.memory.save_context({"input": user_input}, {"output": response.content})
        return {
            "desription": response.description,
            "events": [event.dict() for event in response.events] if response.events else [],
            "modify_calendar": response.modify_calendar,
            "response": response.response
        }

