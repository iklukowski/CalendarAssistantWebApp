import { useState, useEffect } from "react";
import api from "../api";
import Event from "../components/Event"
import ChatComponent from "../components/chat";
import "../styles/Home.css"
import Calendar from "../components/Calendar";

function Home() {
    const [events, setEvents] = useState([]);
    const [title, setTitle] = useState("");
    
    const [start_time, setStart_time] = useState("08:00");
    const [end_time, setEnd_time] = useState("10:00");
    const [isAddOpen, setIsAddOpen] = useState(false);
    const [ifEdit, setifEdit] = useState(false);
    const [eventId, setEventId] = useState(null);
    const [note, setNote] = useState("");

    const currentDate = new Date();
    const [date, setDate] = useState(currentDate.toLocaleDateString("en-CA"));
    
    useEffect(() => {
        getEvents();
    }, []);

    const getEvents = () => {
        api
            .get("/api/event/")
            .then((res) => res.data)
            .then((data) => {
                const calendar_events = data.map((event) => {
                    return {
                        id: event.id,
                        title: `${event.title} \n ${event.note}`,
                        start: `${event.date} ${event.start_time}`,
                        end: `${event.date} ${event.end_time}`,
                        author: event.author
                    };
                });
                setEvents(calendar_events);
                console.log(data);
                console.log({calendar_events});
            })
            .catch((err) => console.log(err));
    };

    const deleteEvent = (e, id) => {
        e.preventDefault();
        api
            .delete(`/api/event/delete/${id}/`)
            .then((res) => {
                if (res.status === 204) console.log("Event deleted!");
                else alert("Failed to delete event.");
                getEvents();
            })
            .catch((error) => alert(error));
        handleEventClickAway();
    };

    const handleSave = (e) => {
        e.preventDefault();
        if (start_time >= end_time) {
            alert("Start time must be before end time.");
            return
        }
        else {
            if(ifEdit) 
                updateEvent(eventId)
            else
                createEvent(e);
            handleEventClickAway();
        }
    }  
    
    const createEvent = (e) => {
        e.preventDefault();
        api
            .post("/api/event/", {date, title, start_time, end_time })
            .then((res) => {
                if (res.status === 201) console.log("Event created!");
                else alert("Failed to make event.");
                getEvents();
            })
            .catch((err) => alert(err));
    };

    const updateEvent = (id) => {
        api
            .patch(`api/event/update/${id}/`, {date, title, start_time, end_time, note})
            .then((res) => {
                if (res.status === 200) console.log("Event updated!");
                else alert("Failed to update event.");
                getEvents();
            })
            .catch((err) => alert(err));
    }

    const handleEventClick = (info) => {
        setIsAddOpen(!isAddOpen);
        setifEdit(true);
        setTitle(info.event.title.split('\n')[0]);
        setEventId(info.event.id);
        setDate(info.event.start.toLocaleDateString("en-CA"));
        setStart_time(info.event.start.toTimeString().split(" ")[0]);
        setEnd_time(info.event.end.toTimeString().split(" ")[0]);
        console.log(info.event.title.split('\n')[1]);
        setNote(info.event.title.split('\n')[1]);
    }

    const handleEventClickAway = () => {
        setifEdit(false);
        setIsAddOpen(false);
        setTitle("");
        setDate(currentDate.toLocaleDateString("en-CA"));
        setStart_time("08:00");
        setEnd_time("10:00");
        setEventId(null);
        setNote("");
    }

    return (
        <div>
            <div>
                <h2>Calendar</h2>
                <button className="add-event-button" onClick={() => setIsAddOpen(!isAddOpen)}>
                    +
                </button>
            </div>
            <Calendar 
                    events={events} 
                    chat_events={[{id: 100, title:"Test potential chat event", start:"2025-04-04 09:00:00", end:"2025-04-04 14:00:00", color:"green"}]}
                    eventClick={handleEventClick}
                    />
            {isAddOpen && (
                <div className="modal">
                    <div className="modal-content">
                        <span className="close-button" onClick={() => {handleEventClickAway();}}>
                            &times;
                        </span>
                        {ifEdit ? <h2>Edit Event</h2> : <h2>Add Event</h2>}
                        <form>
                            <input
                                type="text"
                                placeholder="Title"
                                value={title}
                                required
                                onChange={(e) => setTitle(e.target.value)}
                            />
                            <input
                                type="date"
                                value={date}
                                required
                                onChange={(e) => setDate(e.target.value)}
                            />
                            <input
                                type="time"
                                value={start_time}
                                required
                                onChange={(e) => setStart_time(e.target.value)}
                            />
                            <input
                                type="time"
                                value={end_time}
                                required
                                onChange={(e) => setEnd_time(e.target.value)}
                            />
                            {ifEdit && <input
                                type="textfield"
                                placeholder="Note"
                                value={note}
                                onChange={(e) => setNote(e.target.value)}
                            />}
                            <button className="submit-button" onClick={(e) => handleSave(e)}>Save</button>
                            <button className="delete-button" onClick={(e) => deleteEvent(e, eventId)}>Delete</button>
                        </form>
                    </div>
                </div>
            )}
            <ChatComponent refreshEvents={getEvents} />
        </div>
    );
}

export default Home;