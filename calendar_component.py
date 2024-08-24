import streamlit as st
import streamlit_calendar as st_calendar
from datetime import datetime, timedelta
from database import Database

def calendar_page():
    st.title("Calendar")

    db = Database()

    col1, col2 = st.columns([2, 3])

    with col1:
        st.subheader("Existing Events")
        dates_with_notes = db.get_dates_with_notes()
        for date in dates_with_notes:
            notes = db.get_notes(date)
            st.write(f"**{date.strftime('%Y-%m-%d')}**")
            for note in notes:
                col_note, col_delete = st.columns([4, 1])
                with col_note:
                    st.markdown(f"<span style='color:{note['color']};'>- {note['text']}</span>", unsafe_allow_html=True)
                with col_delete:
                    if st.button("Delete", key=f"delete_{date}_{note['id']}"):
                        db.delete_note(note['id'])
                        st.rerun()
            st.write("---")

        st.subheader("Add New Event")
        with st.form("add_event_form"):
            event_title = st.text_input("Event Title")
            event_date = st.date_input("Date")
            event_color = st.color_picker("Event Color", "#3DD56D")
            if st.form_submit_button("Add Event"):
                db.add_note(event_date, event_title, event_color)
                st.rerun()

    with col2:
        events = []
        for date in dates_with_notes:
            notes = db.get_notes(date)
            for note in notes:
                events.append({
                    "title": note['text'],
                    "start": date.isoformat(),
                    "backgroundColor": note['color'],
                    "borderColor": note['color']
                })

        calendar = st_calendar.calendar(
            events=events,
            options={
                "initialView": "dayGridMonth",
                "headerToolbar": {
                    "left": "prev,next today",
                    "center": "title",
                    "right": "dayGridMonth,timeGridWeek,timeGridDay"
                },
            },
            callbacks=["eventClick", "select"]
        )

        if calendar.get("eventClick"):
            clicked_event = calendar["eventClick"]["event"]
            st.write(f"Event clicked: {clicked_event['title']}")

        if calendar.get("select"):
            st.write("Date range selected:", calendar["select"]["startStr"], "to", calendar["select"]["endStr"])