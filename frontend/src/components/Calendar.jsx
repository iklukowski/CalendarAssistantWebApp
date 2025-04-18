import FullCalendar from '@fullcalendar/react';
import dayGridPlugin from '@fullcalendar/daygrid';
import timeGridPlugin from '@fullcalendar/timegrid';

function Calendar({events, chat_events=[], eventClick}) {
    const calendar_events = [...events, ...chat_events];

    function renderEventContent(eventInfo) {
        return(
          <>
          <div>
            <b>{eventInfo.timeText}</b>
            <button>+</button>
            <br />
            <i>{eventInfo.event.title}</i>
          </div>
          <b>{eventInfo.event.extendedProps.note}</b>
          </>
        )
      }

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
            slotMinTime="08:00:00"
            slotMaxTime="21:00:00"
            expandRows={true}
            eventMouseEnter= { (info) => {
                info.el.style.cursor = "pointer";
            }}
            eventClick={eventClick}
            eventContent={renderEventContent}
        />
    );
}

export default Calendar;