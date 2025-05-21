import { useState } from "react"
import api from "../api"
import '../styles/Chat.css'

const ChatComponent = ({refreshEvents, setChatEvents, setUpdatedChatEvents}) => {
    const [message, setMessage] = useState("")
    const [responseHistory, setResponseHistory] = useState([])

    const ChatWithAssistant = async (message) => {
        const chat_response = await api.get(`/api/assistant/chat/?message=${encodeURIComponent(message)}`)
        console.log(chat_response.data.response)
        return chat_response.data.response
    }

    const SendMessage = async () => {
        setResponseHistory((prev) => [
            ...prev,
            {user: message, assistant: null}
       ])
        const assistantResponse = await ChatWithAssistant(message)
        setResponseHistory((prev) => [
            ...prev,
            {user: null, assistant: assistantResponse.response}
        ])
        setMessage("")
        //if(assistantResponse.new_events) setChatEvents(assistantResponse.new_events)
        //if (assistantResponse.updated_events) setUpdatedChatEvents(assistantResponse.updated_events, assistantResponse.events_to_change)
        refreshEvents()
    }

    return (
        <div className="chat-container">
            <h2 className="chat-header">Calendar Assistant</h2>
            <div className="chat-history">
                {responseHistory.map((chat, index) => (
                    <div key={index} className="chat-message">
                        {chat.user != null ? <div className="user-message">You: {chat.user}</div> : null}
                        {chat.assistant != null ? <div className="assistant-message">Assistant: {chat.assistant}</div> : null}
                    </div>
                ))}
            </div>
            <div className="chat-input-container">
                <textarea
                    className="chat-input"
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    placeholder="Type your message here..."
                />
                <button className="send-button" onClick={SendMessage}>
                    Send
                </button>
            </div>
        </div>
    )

}

export default ChatComponent
