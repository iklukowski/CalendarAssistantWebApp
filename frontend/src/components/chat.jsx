import { useState } from "react"
import api from "../api"
import '../styles/Chat.css'

const ChatComponent = ({refreshEvents}) => {
    const [message, setMessage] = useState("")
    const [response, setResponse] = useState("")

    const ChatWithAssistant = async (message) => {
        const chat_response = await api.get(`/api/assistant/chat/?message=${encodeURIComponent(message)}`)
        console.log(chat_response.data.response)
        return chat_response.data.response
    }

    const SendMessage = async () => {
        const assistantResponse = await ChatWithAssistant(message)
        setResponse(assistantResponse.response)
        refreshEvents()
    }

    return (
        <div className="chat-container">
            <h2>Chat with Assistant</h2>
            <textarea className="chat-input" value={message} onChange={(e) => setMessage(e.target.value)}/>
            <p/>
            <button className="send-button" onClick={SendMessage}>Send Message</button>
            <p>Assistant response: {response}</p>
        </div>
    )

}

export default ChatComponent
