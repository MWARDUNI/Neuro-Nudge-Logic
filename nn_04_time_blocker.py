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

        # check for available time block at the end of the day
        if end_of_day > current_time + timedelta(hours=1):
            available_blocks.append((current_time, current_time + timedelta(hours=1)))

        return available_blocks

    except Exception as e:
        print(f"Error: {str(e)}")
        return []



def allocate_time_blocks(assignments):
    # alloc TB based on: due date, priority, impact
    # sort assignments by due date, priority (ascending), and impact (descending)
    sorted_assignments = sorted(assignments, key=lambda x: (parse_datetime(x['due']), -int(x['priority']), -int(x['impact'])))

    current_time = datetime.now()
    tb_schedule = []

    for assignment in sorted_assignments:
        # assign number of time blocks based on impact
        num_blocks = 3 if int(assignment['impact']) >= 10 else 2
        
        for _ in range(num_blocks):
            # schedule each block 1 hour apart, starting from the current time
            start_time = current_time
            end_time = start_time + timedelta(hours=1)
            schedule.append({
                'assignment_uid': assignment['uid'],
                'start': start_time,
                'end': end_time
            })
            # update current time to the end of the last scheduled block
            current_time = end_time

    return tb_schedule



if __name__ == "__main__":
    # Initialize the Supabase client
    url = "https://fgocfoakntmlhgtftrzh.supabase.co"
    key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZnb2Nmb2FrbnRtbGhndGZ0cnpoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTE2ODkyMTUsImV4cCI6MjAyNzI2NTIxNX0.s5dAWy-DSa1EBfKjhpGOOcax6S7QUsh7xCHPFgKlBn8"
    supabase: Client = create_client(url, key)
    find_available_time_blocks(supabase, 4, )



