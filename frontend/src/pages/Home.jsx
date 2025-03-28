import { useState, useEffect } from "react";
import api from "../api";
import Event from "../components/Event"
import ChatComponent from "../components/chat";
import Calendar from "../components/Calendar";
import "../styles/Home.css"
import DemoCalendar from "../components/demoCalendar";

function Home() {
    const [events, setEvents] = useState([]);
    const [title, setTitle] = useState("");
    const [date, setDate] = useState("now");
    const [start_time, setStart_time] = useState("8:00");
    const [end_time, setEnd_time] = useState("10:00");


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
                        title: `${event.title} ${event.note}`,
                        start: `${event.date} ${event.start_time}`,
                        end: `${event.date} ${event.end_time}`,
                        author: event.author
                    };
                });
                setEvents(calendar_events);
                console.log(data);
                console.log({calendar_events});
            })
            .catch((err) => alert(err));
    };

    const deleteEvent = (id) => {
        api
            .delete(`/api/event/delete/${id}/`)
            .then((res) => {
                if (res.status === 204) alert("Event deleted!");
                else alert("Failed to delete event.");
                getEvents();
            })
            .catch((error) => alert(error));
    };

    const createEvent = (e) => {
        e.preventDefault();
        api
            .post("/api/event/", {date, title, start_time, end_time })
            .then((res) => {
                if (res.status === 201) alert("Event created!");
                else alert("Failed to make event.");
                getEvents();
            })
            .catch((err) => alert(err));
    };

    const updateEventNote = (id, note) => {
        api
            .patch(`api/event/update/${id}/`, { note })
            .then((res) => {
                if (res.status === 200) console.log("Note updated!");
                else console.log("Failed to update note.");
                getEvents();
            })
            .catch((err) => alert(err));
    }

    return (
        <div>
            <div>
                <h2>Calendar</h2>
                {/*<Calendar events={events} />*/}
                <DemoCalendar events={events} chat_events={[{id: 100, title:"Test potential chat event", start:"2025-03-26 17:00:00", end:"2025-03-26 19:00:00", color:"green"}]}/>
            </div>
            <h2>Create an Event</h2>
            <form onSubmit={createEvent}>
                <label htmlFor="title">Title:</label>
                <br />
                <input
                    type="text"
                    id="title"
                    name="title"
                    required
                    onChange={(e) => setTitle(e.target.value)}
                    value={title}
                />
                <br />
                <label htmlFor="date">Date:</label>
                <input 
                    type="date"
                    id="date"
                    name="date"
                    required
                    onChange={(e) => setDate(e.target.value)}
                />
                <br />
                <label htmlFor="start_time">Start:</label>
                <input 
                    type="time"
                    id="start_time"
                    name="start_time"
                    required
                    onChange={(e) => setStart_time(e.target.value)}
                />
                <br />
                <label htmlFor="end_time">End:</label>
                <input 
                    type="time"
                    id="end_time"
                    name="end_time"
                    required
                    onChange={(e) => setEnd_time(e.target.value)}
                />
                <input type="submit" value="Submit"></input>
            </form>
            <ChatComponent />
        </div>
    );
}

export default Home;