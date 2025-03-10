import React from "react";
import "../styles/Event.css"

function Event({ event, onDelete }) {
    //const formattedDate = new Date(note.created_at).toLocaleDateString("en-US")

    return (
        <div className="event-container">
            <p className="event-date">{event.date}</p>
            <p className="event-title">Title: {event.title}</p>
            <p className="event-start-time">Start: {event.start_time}</p>
            <p className="event-end-time">End: {event.end_time}</p>
            <button className="delete-button" onClick={() => onDelete(event.id)}>
                Delete
            </button>
        </div>
    );
}

export default Event