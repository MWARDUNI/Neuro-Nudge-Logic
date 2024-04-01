from datetime import datetime, timezone, timedelta
from icalendar import Calendar, Event, Alarm
from dateutil.rrule import *
from dateutil.parser import parse


def parse_timeblock_ics():

    with open('nn_timeblocks.ics', 'rb') as f:
        tblockscal = Calendar.from_ical(f.read())

    timeblocks = []

    for block in tblockscal.walk():
        if block.name == "VEVENT":
            timeblock = {
                'summary': str(block.get('summary', 'No summary provided')),
                'start': block.get('dtstart').dt if block.get('dtstart') else None,
                'end': block.get('dtend').dt if block.get('dtend') else None,
                'location': str(block.get('location', 'No location provided')),
                'description': str(block.get('description', 'No description provided')),
                'category': str(block.get('category', 'No category provided')),
                'status': str(block.get('status', 'No status provided')),
                'uid': str(block.get('uid', 'No UID provided')),
                'alarm': block.get('alarm'),
                'trigger': block.get('trigger'),
                'action': str(block.get('action', 'DISPLAY')),
                'related-to': str(block.get('related-to', 'TODO: via UID')),
                'impact': block.get('impact', 0),
            }

            if timeblock['start'] is None or timeblock['end'] is None:
                print(f"{timeblock['summary']} is missing essential datetime information. Skipping.")
                continue

            if block.get('rrule'):
                timeblock['recurrence'] = str(block.get('rrule'))
            else:
                timeblocks.append(timeblock)






# def find_available_time_blocks(ical_data, search_start, search_end, min_duration_hours=1):
#     """
#     Find available time blocks within the specified search period.
#     """
#     events = parse_ical(ical_data)
#     # Ensure events are sorted by start time
#     events.sort(key=lambda x: x[0])

#     available_blocks = []
#     current_time = search_start

#     for start, end in events:
#         # Skip events that end before the search period or start after the search period
#         if end < search_start or start > search_end:
#             continue
#         # If there's a gap of at least `min_duration_hours` between the current time and the next event, record it
#         if start >= current_time + timedelta(hours=min_duration_hours):
#             available_blocks.append((current_time, start))
#         current_time = max(current_time, end)

#     # Check for availability after the last event until the search end
#     if current_time + timedelta(hours=min_duration_hours) <= search_end:
#         available_blocks.append((current_time, search_end))

#     return available_blocks

# # Usage
# ical_data = """
# BEGIN:VCALENDAR
# VERSION:2.0
# BEGIN:VEVENT
# SUMMARY:Event 1
# DTSTART;VALUE=DATE-TIME:20230412T090000Z
# DTEND;VALUE=DATE-TIME:20230412T100000Z
# END:VEVENT
# BEGIN:VEVENT
# SUMMARY:Event 2
# DTSTART;VALUE=DATE-TIME:20230412T110000Z
# DTEND;VALUE=DATE-TIME:20230412T120000Z
# END:VEVENT
# END:VCALENDAR
# """
# # Define the search period in UTC for simplicity
# search_start = datetime(2023, 4, 12, 8, 0, tzinfo=timezone.utc)
# search_end = datetime(2023, 4, 12, 18, 0, tzinfo=timezone.utc)

# available_blocks = find_available_time_blocks(ical_data, search_start, search_end, 1)  # Looking for 1-hour blocks
# for start, end in available_blocks:
#     print(f"Available: {start.strftime('%Y-%m-%d %H:%M')} to {end.strftime('%Y-%m-%d %H:%M')}")