from icalendar import Calendar
from dateutil.rrule import *
from dateutil.parser import parse
import pytz, json
import copy
import pandas as pd
from supabase import create_client, Client





def parse_ics(file_path):
    with open(file_path, 'rb') as f:
        gcal = Calendar.from_ical(f.read())

    events = []
    assignments = []

    for component in gcal.walk():
        if component.name == "VEVENT": # timebound event
            # init event dictionary w/ default vals
            event = {
                'summary': str(component.get('summary', 'No summary provided')),                # title of event
                'start_time': component.get('dtstart').dt if component.get('dtstart') else None,     # start time
                'end_time': component.get('dtend').dt if component.get('dtend') else None,           # end time
                'description': str(component.get('description', 'No description provided')),    # details of event
                'category': str(component.get('category', 'No category provided')),             # category for filtering
                'status': str(component.get('status', 'No status provided')),                   # VEVENT: 'confirmed' [default], 'cancelled', 'tentative'  
                'due': component.get('due').dt if component.get('due') else None,               # due date
                'uid': str(component.get('uid', 'No UID provided')),                            # unique identifier
                'alarm': component.get('alarm'),                                                # reminder/alarm
                'trigger': component.get('trigger'),                                            # trigger alarm
                'action': str(component.get('action', 'DISPLAY')),                              # action for alarm
                'impact': component.get('impact', 0),                                           # impact on final grade
                'display_name': str(component.get('summary', 'No summary provided')),
                'color' : "ffa500"
            }
            
            if "lunch" in event['summary'].lower():
                event['color'] = "008080"
            if "<br>" in event['description']:
                event['description'] = event['description'].split('<br>')[0]

            # if 'dtstart' or 'dtend' is None: TODO: adjust ics 
            if event['start_time'] is None or event['end_time'] is None:
                print(f"{event['summary']} is missing essential datetime information. Skipping.")
                continue  

            if component.get('rrule'):
                rrule = component.get('rrule')
                if rrule.get('UNTIL'):
                    rrule['UNTIL'] = [x.isoformat() for x in rrule.get('UNTIL')]
                
                rrule = str(rrule).removeprefix("vRecur(")[:-1]
                # FREQ=WEEKLY;WKST=SU;UNTIL=2024-05-10T05:59:59+00:00;BYDAY=MO,WE
                rrule = rrule.replace("{", "").replace("}", "").replace("[", "").replace("]", "")
                rrule = rrule.replace(":", "=").replace(",", ";").replace("'", "").replace(" ", "")
                if "BYDAY" in rrule:
                    temp = rrule.split("BYDAY")
                    temp[1] = temp[1].replace(";", ",")
                    rrule = "BYDAY".join(temp)
                
                event['recurrence'] = rrule
            else:
                keywords = ['homework', 'project', 'quiz', 'midterm', 'final', 'lab', 'HW', 'hw']
                if any(keyword in event['summary'].lower() for keyword in keywords) or \
                   any(keyword in event['description'].lower() for keyword in keywords):
                    assignment_type = next((keyword for keyword in keywords if keyword in event['summary'].lower()), 'unknown')
                    
                    # assignments are VTODO components, not VEVENT
                    assignment = {
                        'class': event['summary'].split('-')[0].strip() if '-' in event['summary'] else 'Unknown',
                        'due': event['end_time'],
                        'type': assignment_type,
                        'description': event['description'],
                        'status': str(component.get('status', 'NEEDS-ACTION')), # VTODO: 'NEEDS-ACTION' [default], 'COMPLETED', 'IN-PROCESS', 'CANCELLED'
                        'priority': str(component.get('priority', '0')), # VTODO: '0' [default], '1' = HIGH, '9' = LOW
                        'uid': event['uid'],
                        'alarm': event['alarm'],
                        'trigger': event['trigger'],
                        'action': event['action'],
                        'category': event['category'],
                        'impact': event['impact'], # default impact value
                        'display_name': event['summary']
                    }
                    assignments.append(assignment)
                    continue  # skip adding to events if it's an assignment

            events.append(event)


    # convert event/assignment dates to UTC timezone, if not None
    for event in events:
        if event['start_time']:
            event['start_time'] = event['start_time'].astimezone(pytz.utc)
        if event['end_time']:
            event['end_time'] = event['end_time'].astimezone(pytz.utc)


    for assignment in assignments:
        if assignment['due']:
            assignment['due'] = assignment['due'].astimezone(pytz.utc)

    return events, assignments



# events, assignments = parse_ics('class_cal.ics')
events, assignments = parse_ics('all_in_one.ics')












# # make copies of events and assignments data by value.
# copy_events = copy.deepcopy(events)



# print("\n type of events: ")
# print(type(events))
# for event in copy_events:
#     print("\n")
#     # print the type(event) to see what type of object it is
#     print(type(event))

# copy_assignments = copy.deepcopy(assignments)


# print("\n")
# print("============================================================\n")
# print("Events:\n")
# print("\tThese are recurring events, such as classes, meetings, etc. that are time bounded.\n")
# for event in events:
#     print(event)
#     print("\n") 


# print("\n")
# print("============================================================\n")
# print("Assignments:\n")
# print("\tThese are tasks/todos with due dates.\n")
# for assignment in assignments:
#     print(assignment)
#     print("\n") 


