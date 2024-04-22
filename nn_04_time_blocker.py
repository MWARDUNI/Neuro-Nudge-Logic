from datetime import datetime, timezone, timedelta
from icalendar import Calendar, Event, Alarm
from dateutil.rrule import *
from dateutil.parser import parse
from supabase import create_client, Client
from datetime import datetime, timedelta




async def find_available_blocks(supabase: Client):
    available_blocks = await supabase.table("timeblocks").select("*").eq("filled", False).execute()
    return available_blocks.data

# available_blocks and sorted_assignments
# for each assignment find three 1-hr blocks, beginning 2 weeks before due date
# check for conflicting blocks in "events" table
# if no conflicts, add to "timeblocks" table and mapping table
# if conflicts, find next available block
async def allocate_time_blocks(sorted_assignments, available_blocks):
    two_wks = timedelta(weeks=2)
    for assignment in sorted_assignments:
        due_date = assignment['due']
        starter_block = due_date - two_wks
        allocated_blocks = []


        for _ in range(3):
            for block in available_blocks:
                block_start = block['start']
                if block_start >= starter_block and not is_block_confilcted(block, assignment['uid']):
                    allocate_one_block(assignment['uid'], block_start, allocated_blocks)
                    allocated_blocks.append(block)
                    starter_block += block_start + timedelta(days=2)
                    break


async def is_block_confilcted(block, assignment_uid):
    start = block['start']
    end = block['end']
    response = await supabase.table("events")\
    .select("*").eq("class_id", assignment_uid)\
    .gte("start_time", start)\
    .lte("end_time", end)\
    .execute()

    return len(response.data) > 0


async def allocate_one_block(assignment_uid, block_start, allocated_blocks):
    await supabase.table("timeblocks")\
    .update({"filled": True})\
    .eq("start", block_start)\
    .execute()

    await supabase.table("timeblock_assignments")\
    .insert({"assignment_uid": assignment_uid, "block_start": block_start})\
    .execute()




if __name__ == "__main__":
    # Initialize the Supabase client
    url = "https://fgocfoakntmlhgtftrzh.supabase.co"
    key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZnb2Nmb2FrbnRtbGhndGZ0cnpoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTE2ODkyMTUsImV4cCI6MjAyNzI2NTIxNX0.s5dAWy-DSa1EBfKjhpGOOcax6S7QUsh7xCHPFgKlBn8"
    supabase: Client = create_client(url, key)




