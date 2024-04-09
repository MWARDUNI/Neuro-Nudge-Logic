from datetime import datetime, timezone, timedelta
from icalendar import Calendar, Event, Alarm
from dateutil.rrule import *
from dateutil.parser import parse
from supabase import create_client, Client
from datetime import datetime, timedelta


def find_available_time_blocks(supabase: Client, class_id, date):

    try:
        # query database to get the schedule for the given date
        response = supabase.table("events").select("start_time, end_time").eq("class_id", class_id).eq("date", date).order("start_time").execute()


        schedule = response.data

        start_of_day = datetime.combine(date, datetime.min.time(), tzinfo=timezone.utc)
        end_of_day = datetime.combine(date, datetime.max.time(), tzinfo=timezone.utc)

        available_blocks = []
        current_time = start_of_day

        # iterate through schedule
        for event in schedule:
            start_time = datetime.fromisoformat(event["start_time"])
            end_time = datetime.fromisoformat(event["end_time"])

            # Check if there is a gap between the current time and the start of the next scheduled event
            if start_time > current_time + timedelta(hours=1):
                # Add the available time block to the list
                available_blocks.append((current_time, current_time + timedelta(hours=1)))

            # Update the current time to the end of the scheduled event
            current_time = end_time

        # Check if there is an available time block at the end of the day
        if end_of_day > current_time + timedelta(hours=1):
            available_blocks.append((current_time, current_time + timedelta(hours=1)))

        return available_blocks

    except Exception as e:
        print(f"Error: {str(e)}")
        return []

 

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

if __name__ == "__main__":
    # Initialize the Supabase client
    url = "https://fgocfoakntmlhgtftrzh.supabase.co"
    key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZnb2Nmb2FrbnRtbGhndGZ0cnpoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTE2ODkyMTUsImV4cCI6MjAyNzI2NTIxNX0.s5dAWy-DSa1EBfKjhpGOOcax6S7QUsh7xCHPFgKlBn8"
    supabase: Client = create_client(url, key)
    find_available_time_blocks(supabase, 4, )