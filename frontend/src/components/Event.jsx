import React from "react";
import "../styles/Event.css"

function Event({ event, onDelete, onUpdate}) {
    const [isEditing, setIsEditing] = React.useState(false)
    const [note, setNote] = React.useState(event.note)

    const handleEditClick= () => {
        setIsEditing(true);
    };

    const handleNoteChange = (e) => {
        setNote(e.target.value)
    };

    const handleNoteSubmit = (e) => {
        e.preventDefault();
        onUpdate(event.id, note);
        setIsEditing(false);
    };
    //const formattedDate = new Date(note.created_at).toLocaleDateString("en-US")

    return (
        <div className="event-container">
            <p className="event-date">{event.date}</p>
            <p className="event-title">Title: {event.title}</p>
            <p className="event-start-time">Start: {event.start_time}</p>
            <p className="event-end-time">End: {event.end_time}</p>
            {isEditing ? (
                <form onSubmit={handleNoteSubmit}>
                    <textarea
                        className="note-textarea"
                        value={note}
                        onChange={handleNoteChange}
                    />
                    <button className="save-button" type="submit">
                        Save
                    </button>
                </form>
            ) : (
                <p className="event-note">
                    {event.note && `Note: ${event.note}`}
                </p>
            )}
            <button className="delete-button" onClick={() => onDelete(event.id)}>
                Delete
            </button>
            <button className="edit-button" onClick={handleEditClick}>
                Note
            </button>
        </div>
    );
}

export default Event