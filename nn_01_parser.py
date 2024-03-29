from icalendar import Calendar
from dateutil.rrule import *
from dateutil.parser import parse
import pytz


# from nn_01_parser import parse_assignments
# from nn_02_categorizer import categorize_assignments
# from nn_03_prioritizer import calculate_impact, prioritize_assignments
# from nn_03_1_5day_study import create_study_plans_for_tests
# from nn_04_time_blocker import find_time_blocks

from nn_01_parser import *
from nn_02_categorizer import *
from nn_03_prioritizer import *
from nn_03_1_5day_study import *
from nn_04_time_blocker import *


def parse_ics(file_path):
    with open(file_path, 'rb') as f:
        gcal = Calendar.from_ical(f.read())

    events = []
    assignments = []

    for component in gcal.walk():
        if component.name == "VEVENT":
            event = {
                'summary': str(component.get('summary')),
                'start': component.get('dtstart').dt,
                'end': component.get('dtend').dt,
                'location': str(component.get('location')),
                'description': str(component.get('description'))
            }

            # recurring event
            if component.get('rrule'):
                event['recurrence'] = str(component.get('rrule'))
                events.append(event)
            else:
                # assignment based on keywords in summary or description
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
                else:
                    events.append(event)


    for event in events:
        event['start'] = event['start'].astimezone(pytz.utc)
        event['end'] = event['end'].astimezone(pytz.utc)

    for assignment in assignments:
        assignment['due_date'] = assignment['due_date'].astimezone(pytz.utc)

    return events, assignments


events, assignments = parse_ics('testcal.ics')
print(events)
print(assignments)
