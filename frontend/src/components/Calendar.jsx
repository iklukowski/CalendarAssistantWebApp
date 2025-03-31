import FullCalendar from '@fullcalendar/react';
import dayGridPlugin from '@fullcalendar/daygrid';
import timeGridPlugin from '@fullcalendar/timegrid';

function Calendar({events, chat_events=[], eventClick}) {
    const calendar_events = [...events, ...chat_events];
    return (
        <FullCalendar
            plugins={[timeGridPlugin]}
            initialView="timeGridWeek"
            headerToolbar={{
                left: 'prev,next today',
                center: 'title',
                right: 'timeGridWeek,timeGridDay'
            }}
            events={calendar_events}
            firstDay={1}
            slotMinTime="06:00:00"
            slotMaxTime="24:00:00"
            expandRows={true}
            eventMouseEnter= { (info) => {
                info.el.style.cursor = "pointer";
            }}
            eventClick={eventClick}
        />
    );
}

export default Calendar;