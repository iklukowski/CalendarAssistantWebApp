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
from django.contrib.auth.models import User

class ChatEvent(BaseModel):
    """Structured representation of an event"""
    id: str = Field(description="The unique identifier of the event (use string + number) unless its an already exsiting event than use the id of the event")
    date: str = Field(description="The date of the event in YYYY-MM-DD format")
    title: str = Field(description="The title of the event")
    start_time: str = Field(description="The start time of the event in HH:MM format")
    end_time: str = Field(description="The end time of the event in HH:MM format")

    
class CreateEventResponse(BaseModel):
    """Response for creating event(s)"""
    event: Optional[list[ChatEvent]] = Field(description="The created list of events")
    success: bool = Field(description="Indicates if the event was successfully created")
    message: str = Field(description="A message indicating the result of the event creation")
    
class UpdateEventResponse(BaseModel):
    """Response for updating event(s)"""
    updated_events: Optional[list[ChatEvent]] = Field(description="The list of updated events, keep the id's the same as the original events")
    success: bool = Field(description="Indicates if the event(s) was(were) successfully updated")
    message: str = Field(description="A message indicating the result of the event(s) update")



class CalendarAssistant:
    def __init__(self):
        load_dotenv()   
        self.payload = {
            "description": "",
            "new_events": None,
            "events_to_change": None,
            "updated_events": None,
            "deleted_events": None,
            "modify_calendar": False,
            "response": None
        }
        self.tools = [self.generate_events_agent, self.get_events_tool, self.update_events_agent, self.delete_events_agent]
        self.model = ChatOpenAI(model="gpt-4o-mini")
        self.memory = MemorySaver()
        self.supervisor = create_react_agent(
            model=self.model,
            tools=self.tools,
            prompt="You are a helpful calendar assistant that supervises other agents to create, update and delete events in the calendar of the user"
                    f"Today's date is {datetime.today().strftime('%Y-%m-%d')}, the current time is {datetime.now().strftime('%H:%M')}."
                    "Do not call the agents with any parameters unless they need specific ones."
                    "Agents are given to you with the help of tool-calling, you can call them with the help of the tool-calling system."
                    "Call the get_events tool if the request of the user will require you create, udpdate or delete events."
                    "if the tool has the word agent in it, call it once unless it comes back with an error. We want to prevent calling an agent twice which could lead to problems",
            checkpointer=self.memory,
        )
        self.user = None
        self.config = {"configurable": {"thread_id": "abc235"}}
        self.retrieved_events = None
        
     #   self.memory = ConversationBufferMemory(memory_key="chat_history")
    
    
    def get_events_tool(self):
        ''' 
        A tool to retrieve events from the database that belong to the user
        '''
        try:
            #user_id = state.get("user")
            #print(f"User ID: {user_id}")
            #user = User.objects.get(id=user_id)
            #print(f"User: {user}")
            user = self.user 
            events = Event.objects.filter(author=user)  # Replace with your actual query logic
            formatted_events = [
                {
                    "id": event.id,
                    "date": event.date.strftime('%Y-%m-%d'),
                    "title": event.title,
                    "start_time": event.start_time.strftime('%H:%M'),
                    "end_time": event.end_time.strftime('%H:%M'),
                }
                for event in events
            ]

            # Update the state with the retrieved events
            self.retrieved_events = formatted_events
            return {
                "success": True,
                "events": formatted_events,
                "message": "Events retrieved successfully."
            }
        except Exception as e:
            return {
                "success": False,
                "events": None,
                "message": f"Failed to retrieve events: {str(e)}"
            }
        
    def generate_events_agent(self, state: Annotated[dict, InjectedState]):
        ''' An agent that only creates events based on the user request, he does not update or delete events
            He handles multiples events in the same request, do not call this agent if update_agent doen not work
        '''
        prompt = (
            "You are an event creating assistant agent in the calendar domain, your task is to create events in the calendar based on the user request. "
            "Only list an event to create if the user request is clear, do not update or delete events, that is a job for another agent. Ignore the part of the request that is not suitable for you purpose"
            f"Here's the list of events that belong to the user: {self.retrieved_events}\n\n. Choose the events that need to be created based on the user request."
            "Use this list to create the events using the generate_events tool, if there is a problem, return the error to the supervisor agent only try calling the tool once."
            f"Today's date is {datetime.today().strftime('%Y-%m-%d')}, the current time is {datetime.now().strftime('%H:%M')}."
            "Time is provided for you so that you can assess word like today or tomorrow, even if events are in the past you can create them."
            "Make sure that you actually create the events, meaning that if you have not received a success message from the tool, return an error."
            "Generate an ID for the event, it should be unique and not the same as any other event in the database."
            "Before returning any messages, proceed with the creation of the events, and return the success message to the supervisor agent, unless there are no events to create."
        )
        llm = create_react_agent(
            model = self.model,
            tools = [self.generate_events],
            prompt=prompt,
        )
        # Extract the last human message from the state
        human_messages = [msg for msg in state["messages"] if isinstance(msg, HumanMessage)]
        last_human_message = human_messages[-1].content if human_messages else ""
        response = llm.invoke({"messages": HumanMessage(content=last_human_message)})
        print(response["messages"])
        return response["messages"][-1].content
    
    def generate_events(self, new_events: list[dict[str, str]]):
        '''A tool for the creating events agent to create the events in the database
            args: new_events: list of events to create
            events are to be structured like this:
            id: the same as the original event (give as string)
            date: in the format YYYY-MM-DD
            title: The same unless the user wants to change it
            start_time: in the format HH:MM
            end_time: in the format HH:MM
            returns: success: bool, message: str
        '''
        print("Tool Reached")
        for new_event in new_events:
            try:
                # Create a new event instance
                event = Event(
                    author=self.user,
                    title=new_event["title"],
                    date=datetime.strptime(new_event["date"], '%Y-%m-%d').date(),
                    start_time=datetime.strptime(new_event["start_time"], '%H:%M').time(),
                    end_time=datetime.strptime(new_event["end_time"], '%H:%M').time()
                )
                # Save the event to the database
                event.save()
                print("Event Saved")
            except Exception as e:
                return {
                    "success": False,
                    "message": f"Failed to create event: {str(e)}"
                }
        return {
            "success": True,
            "message": "Events created successfully."
        }
    
    def update_events_agent(self, state: Annotated[dict, InjectedState]):
        ''' An agent that only updates events based on the user request, he does not create events
            He handles multiples events in the same request
            args: NO ARGS, the agent will use the retrieved events from the get_events_tool
        '''
        #llm = ChatOpenAI(model="gpt-4o-mini")
        #llm_with_tools = llm.bind_tools([self.update_events])
        prompt = (
            f"You are an event updating assistant agent in the calendar domain, your task is to update events in the calendar based on the user request. "
                                    "Only list an event to updated or edited if the user request is clear, do not create or delete events, that is a job for another agent. Ignore the part of the request that is not suitable for you purpose"
                                    f"Here's the list of events that belong to the user: {self.retrieved_events}\n\n. Choose the events that need to be updated based on the user request."
                                    "Try your best to choose the event that the user request is referring to. If the request mentions the title or date, make sure you choose the correct event from the calendar."
                                    "Use this list to update the events using the update_events tool, if there is a problem, return the error to the supervisor agent only try calling the tool once."
                                    f"Today's date is {datetime.today().strftime('%Y-%m-%d')}, the current time is {datetime.now().strftime('%H:%M')}."
                                    "Time is provided for you so that you can assess word like today or tomorrow, even if events are in the past you can update them."
                                    "Before returning any messages, proceed with the update of the events, and return the success message to the supervisor agent, unless there are no events to modify."
        )
        llm = create_react_agent(
            model = self.model,
            tools = [self.update_events],
            prompt=prompt,
        )
        # Extract the last human message from the state
        human_messages = [msg for msg in state["messages"] if isinstance(msg, HumanMessage)]
        last_human_message = human_messages[-1].content if human_messages else ""

        response = llm.invoke({"messages": HumanMessage(content=last_human_message)})  
        print(response)
        return response["messages"][-1].content
    
    def update_events(self, new_events: list[dict[str, str]]):
        '''A tool for the updating events agent to update the events in the database
            args: new_events: list of events to update (the changed events)
            events are to be structured like this:
            id: the same as the original event (give as string)
            date: in the format YYYY-MM-DD
            title: The same unless the user wants to change it
            start_time: in the format HH:MM
            end_time: in the format HH:MM
            returns: success: bool, message: str
        '''
        print("Tool Reached")
        for new_event in new_events:
            try:
                    # Fetch the event by ID
                    event = Event.objects.get(id=new_event["id"], author=self.user)
                    
                    # Update the event fields
                    event.title = new_event.get("title", event.title)
                    event.date = datetime.strptime(new_event.get("date", event.date.strftime('%Y-%m-%d')), '%Y-%m-%d').date()
                    event.start_time = datetime.strptime(new_event.get("start_time", event.start_time.strftime('%H:%M')), '%H:%M').time()
                    event.end_time = datetime.strptime(new_event.get("end_time", event.end_time.strftime('%H:%M')), '%H:%M').time()
                    
                    # Save the updated event
                    event.save()
                    print("Event Saved")
            except Event.DoesNotExist:
                    return {
                        "success": False,
                        "message": f"Event with ID {new_event['id']} does not exist or does not belong to the user."
                    }
            except Exception as e:
                    return {
                        "success": False,
                        "message": f"Failed to update event with ID {new_event['id']}: {str(e)}"
                    }
            
            return {
                "success": True,
                "message": "Events updated successfully."
            }
    
    
    def delete_events_agent(self, state: Annotated[dict, InjectedState]):
        ''' An agent that only deletes events based on the user request, he does not create or update events
            He handles multiples events in the same request
            args: NO ARGS, the agent will use the retrieved events from the get_events_tool
        '''
        prompt = (
            "You are an event deleting assistant agent in the calendar domain, your task is to delete events in the calendar based on the user request. "
            "Only list an event to delete if the user request is clear, do not create or update events, that is a job for another agent. Ignore the part of the request that is not suitable for you purpose"
            f"Here's the list of events that belong to the user: {self.retrieved_events}\n\n. Choose the events that need to be deleted based on the user request."
            "Try your best to choose the event that the user request is referring to. If the request mentions the title or date, make sure you choose the correct event from the calendar."
            "Use this list to delete the events using the delete_events tool, if there is a problem, return the error to the supervisor agent only try calling the tool once."
            f"Today's date is {datetime.today().strftime('%Y-%m-%d')}, the current time is {datetime.now().strftime('%H:%M')}."
            "Use the id of the event to delete it, if the user wants to delete an event that does not exist, return an error."
            "Time is provided for you so that you can assess word like today or tomorrow, even if events are in the past you can delete them."
            "Make sure that you actually delete the events, meaning that if you have not received a success message from the tool, return an error."
            "Before returning any messages, proceed with the deletion of the events, and return the success message to the supervisor agent, unless there are no events to delete."
        )
        llm = create_react_agent(
            model = self.model,
            tools = [self.delete_events],
            prompt=prompt,
        )
        # Extract the last human message from the state
        human_messages = [msg for msg in state["messages"] if isinstance(msg, HumanMessage)]
        last_human_message = human_messages[-1].content if human_messages else ""

        response = llm.invoke({"messages": HumanMessage(content=last_human_message)}) 
        return response["messages"][-1].content

    def delete_events(self, events_to_delete: list[dict[str, str]]):
        '''A tool for the deleting events agent to delete the events in the database
            args: events_to_delete: list of events to delete
            events are to be structured like this:
            id: the same as the original event (give as string)
            returns: success: bool, message: str
        '''
        print("Tool Reached")
        for event_to_delete in events_to_delete:
            try:
                # Fetch the event by ID
                event = Event.objects.get(id=event_to_delete["id"], author=self.user)
                
                # Delete the event
                event.delete()
                print("Event Deleted")
            except Event.DoesNotExist:
                return {
                    "success": False,
                    "message": f"Event with ID {event_to_delete['id']} does not exist or does not belong to the user."
                }
            except Exception as e:
                return {
                    "success": False,
                    "message": f"Failed to delete event with ID {event_to_delete['id']}: {str(e)}"
                }
        return {
            "success": True,
            "message": "Events deleted successfully."
        }
    
        
        
    def respond(self, user_input, user):
    #    chat_history = self.memory.load_memory_variables({})
        last_message = "" 
        self.user = user
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
            #"events_to_change": [event.dict() for event in self.payload["events_to_change"]] if self.payload["events_to_change"] else None,
            #"updated_events": [event.dict() for event in self.payload["updated_events"]] if self.payload["updated_events"] else None,
            #"deleted_events": self.payload["deleted_events"],
            "modify_calendar": self.payload["modify_calendar"],
            "response": last_message,
        }
