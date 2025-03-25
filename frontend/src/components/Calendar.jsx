import React, {useState} from 'react';
import "../styles/Calendar.css";


const Calendar = ({ events }) => {
    const [currentWeek, setCurrentWeek] = useState(new Date());

    const days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
    const hours = Array.from({ length: 24 }, (_, i) => `${i}:00`);

    const startOfWeek = (date) => {
        const start = new Date(date);
        const day = start.getDay();
        const diff = start.getDate() - day + (day === 0 ? -6 : 1);
        return new Date(start.setDate(diff));
    };

    const getWeekDates = (date) => {
        const start = startOfWeek(date);
        return Array.from({ length: 7 }, (_, i) => {
          const d = new Date(start);
          d.setDate(start.getDate() + i);
          return d;
        });
      };   

    const weekDates = getWeekDates(currentWeek);
    
    const handlePreviousWeek = () => {
        const newDate = new Date(currentWeek);
        newDate.setDate(currentWeek.getDate() - 7);
        setCurrentWeek(newDate);
      };

    const handleNextWeek = () => {
        const newDate = new Date(currentWeek);
        newDate.setDate(currentWeek.getDate() + 7);
        setCurrentWeek(newDate);
      };

    return (
        <div className="calendar-container">
        <div className="calendar-navigation">
            <h2>
                {weekDates[0].toLocaleDateString()} - {weekDates[6].toLocaleDateString()}
            </h2>
            <br />
            <button onClick={handlePreviousWeek}>Previous Week</button>
            <button onClick={handleNextWeek}>Next Week</button>   
        </div>
        <div className="calendar-header">
            {weekDates.map((date, index) => (
            <div key={index} className="calendar-day-header">
                {days[index]} <br /> {date.toLocaleDateString()}
            </div>
          ))}
        </div>
        <div className="calendar-body">
          {hours.map((hour, index) => (
            <div key={index} className="calendar-hour-row">
              <div className="calendar-hour">{hour}</div>
                {weekDates.map((date, dayIndex) => (
                <div key={dayIndex} className="calendar-cell">
                    {events
                    .filter(event => new Date(event.date).toDateString() === date.toDateString())
                    .map(event => {
                        const eventStartHour = parseInt(event.start_time.split(":")[0], 10);
                        const eventStartMinute = parseInt(event.start_time.split(":")[1], 10);
                        const eventEndHour = parseInt(event.end_time.split(":")[0], 10);
                        const eventEndMinute = parseInt(event.end_time.split(":")[1], 10);
                        if(eventStartHour <= index && eventEndHour > index || (eventStartHour === index && eventEndHour === index)) {
                            const eventDuration = (eventEndHour + eventEndMinute/60)  - (eventStartHour + eventStartMinute/60);
                            return (
                                <div key={event.id} className="calendar-event"
                                    style={{
                                      top: `${(eventStartHour - index) * 100}%`,
                                      minHeight: `${eventDuration * 100}%`,
                                    }}>
                                    {event.title} {event.start_time}-{event.end_time}
                                </div>
                            );
                        }
                        else return null;
                })}
                </div>
              ))}
            </div>
          ))}
        </div>
      </div>
    ); 
}

export default Calendar;