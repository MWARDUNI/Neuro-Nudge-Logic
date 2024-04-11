from icalendar import Calendar
from datetime import date, datetime, timedelta
import csv
from supabase import Client, create_client


url = "https://fgocfoakntmlhgtftrzh.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZnb2Nmb2FrbnRtbGhndGZ0cnpoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTE2ODkyMTUsImV4cCI6MjAyNzI2NTIxNX0.s5dAWy-DSa1EBfKjhpGOOcax6S7QUsh7xCHPFgKlBn8"
supabase: Client = create_client(url, key)

auth_response = supabase.auth.sign_in_with_password({"email": "neuro.nudger@gmail.com", "password": "Vatican1-Cameos3"})

user = auth_response.user
profileid = user.id

with open('nn_all_events.ics', 'r') as file:
    ical_data = file.read()

cal = Calendar.from_ical(ical_data)

events = []

for component in cal.walk():
    if component.name == "VEVENT":
        event_data = {
            "profileid": profileid,
            "title": component.get('summary', ''),
            "description": component.get('description', ''),
            "location": component.get('location', '')
        }

        # Extract the start time
        start = component.get('dtstart').dt
        if isinstance(start, datetime):
            start_str = start.isoformat()
        else:
            # Handle all-day events or unexpected formats
            start_str = str(start)

        # Extract the end time
        end_component = component.get('dtend')
        if end_component:
            end = end_component.dt
        else:
            # Default to 1 hour after start time if end time is missing
            end = start + timedelta(hours=1)

        if isinstance(end, datetime):
            end_str = end.isoformat()
        else:
            # Handle all-day events or unexpected formats
            end_str = str(end)

        event_data["starttime"] = start.isoformat() if isinstance(start, datetime) else start_str
        event_data["endtime"] = end.isoformat() if isinstance(end, datetime) else end_str


        # Handle recurrence rule
        rrule = component.get('rrule')
        event_data["recurrencerule"] = rrule.to_ical().decode('utf-8') if rrule else ''

        # Check for all-day events
        event_data["isallday"] = isinstance(start, date) and not isinstance(start, datetime)

        # Insert the event into the Supabase table
        insert_response = supabase.table("appointments").insert(event_data).execute()
        events.append(event_data)





with open('events.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['profileid','title', 'description', 'starttime', 'endtime', 'recurrencerule', 'isallday', 'location'])
    for event in events:
        writer.writerow([
            event['profileid'],
            event['title'],
            event['description'],
            event['starttime'],
            event['endtime'],
            event['recurrencerule'],
            event['isallday'],
            event['location']
        ])