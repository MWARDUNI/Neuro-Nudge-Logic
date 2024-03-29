from icalendar import Calendar
from dateutil.rrule import *
from dateutil.parser import parse
import pytz




def parse_ics(file_path):
    with open(file_path, 'rb') as f:
        gcal = Calendar.from_ical(f.read())

    events = []
    assignments = []

    for component in gcal.walk():
        if component.name == "VEVENT":
            # Initialize the event dictionary with default values
            event = {
                'summary': str(component.get('summary', 'No summary provided')),
                'start': component.get('dtstart').dt if component.get('dtstart') else None,
                'end': component.get('dtend').dt if component.get('dtend') else None,
                'location': str(component.get('location', 'No location provided')),
                'description': str(component.get('description', 'No description provided'))
            }

            # Handle cases where 'dtstart' or 'dtend' is None
            if event['start'] is None or event['end'] is None:
                continue  # Skip this event if essential datetime info is missing

            if component.get('rrule'):
                event['recurrence'] = str(component.get('rrule'))
            else:
                keywords = ['homework', 'project', 'quiz', 'midterm', 'final', 'lab']
                if any(keyword in event['summary'].lower() for keyword in keywords) or \
                   any(keyword in event['description'].lower() for keyword in keywords):
                    assignment_type = next((keyword for keyword in keywords if keyword in event['summary'].lower()), 'unknown')
                    assignment = {
                        'due_date': event['start'],
                        'type': assignment_type,
                        'class': event['summary'].split('-')[0].strip() if '-' in event['summary'] else 'Unknown',
                        'description': event['description']
                    }
                    assignments.append(assignment)
                    continue  # Skip adding to events if it's an assignment

            events.append(event)

    # Convert event and assignment dates to UTC timezone, if they're not None
    for event in events:
        if event['start']:
            event['start'] = event['start'].astimezone(pytz.utc)
        if event['end']:
            event['end'] = event['end'].astimezone(pytz.utc)

    for assignment in assignments:
        if assignment['due_date']:
            assignment['due_date'] = assignment['due_date'].astimezone(pytz.utc)

    return events, assignments



# def parse_ics(file_path):
#     with open(file_path, 'rb') as f:
#         gcal = Calendar.from_ical(f.read())

#     events = []
#     assignments = []

#     for component in gcal.walk():
#         if component.name == "VEVENT":
#             event = {
#                 'summary': str(component.get('summary')),
#                 'start': component.get('dtstart').dt,
#                 'end': component.get('dtend').dt,
#                 'location': str(component.get('location')),
#                 'description': str(component.get('description'))
#             }

#             # recurring event
#             if component.get('rrule'):
#                 event['recurrence'] = str(component.get('rrule'))
#                 events.append(event)
#             else:
#                 # assignment based on keywords in summary or description
#                 keywords = ['homework', 'project', 'quiz', 'midterm', 'final', 'lab']
#                 if any(keyword in event['summary'].lower() for keyword in keywords) or \
#                    any(keyword in event['description'].lower() for keyword in keywords):
#                     assignment_type = next((keyword for keyword in keywords if keyword in event['summary'].lower()), 'unknown')
#                     assignment = {
#                         'due_date': event['start'],
#                         'type': assignment_type,
#                         'class': event['summary'].split('-')[0].strip() if '-' in event['summary'] else 'Unknown',
#                         'description': event['description']
#                     }
#                     assignments.append(assignment)
#                 else:
#                     events.append(event)


#     for event in events:
#         event['start'] = event['start'].astimezone(pytz.utc)
#         event['end'] = event['end'].astimezone(pytz.utc)

#     for assignment in assignments:
#         assignment['due_date'] = assignment['due_date'].astimezone(pytz.utc)

#     return events, assignments


events, assignments = parse_ics('testcal.ics')
print(events)
print(assignments)
