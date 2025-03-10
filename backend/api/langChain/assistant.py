from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
#from langchain_core.memory import ConversationBufferMemory

class CalendarAssistant:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4")
     #   self.memory = ConversationBufferMemory(memory_key="chat_history")
        
    def respond(self, user_input):
    #    chat_history = self.memory.load_memory_variables({})    
        response = self.llm([
            SystemMessage(content="You are a helpful calendar assistant"),
            HumanMessage(content=user_input)
        ])
       # self.memory.save_context({"input": user_input}, {"output": response.content})
        return response.content

