from icalendar import Calendar
from datetime import date, datetime, timedelta
import csv

with open('nn_all_events.ics', 'r') as file:
    ical_data = file.read()

cal = Calendar.from_ical(ical_data)

events = []

for component in cal.walk():
    if component.name == "VEVENT":
        summary = component.get('summary', '')
        description = component.get('description', '')

        # Extract start time and assume it always exists
        start = component.get('dtstart').dt
        if isinstance(start, datetime):
            start_str = start.isoformat()
        else:
            # Handle all-day events or unexpected formats
            start_str = str(start)
        
        # Attempt to extract end time
        end = component.get('dtend')
        if end:
            end = end.dt
        else:
            # Default to 1 hour after start time if end time is missing
            # This assumes start is a datetime object; adjust if necessary for your data
            end = start + timedelta(hours=1)

        if isinstance(end, datetime):
            end_str = end.isoformat()
        else:
            # Handle all-day events or unexpected formats
            end_str = str(end)

        # Extract RRULE directly as a string
        rrule = component.get('rrule')
        if rrule:
            rrule_str = rrule.to_ical().decode('utf-8')  # Convert bytes to string
        else:
            rrule_str = ''

        is_all_day = isinstance(start, date) and not isinstance(start, datetime)
        location = component.get('location', '')
        profile_id = '6931c08c-c2e9-427f-9d3c-75c48e87b4ec'

        events.append([profile_id,summary, description, start_str, end_str, rrule_str, is_all_day, location])




with open('events.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['profileid','title', 'description', 'starttime', 'endtime', 'recurrencerule', 'isallday', 'location'])
    writer.writerows(events)