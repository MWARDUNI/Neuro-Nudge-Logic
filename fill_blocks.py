#!/usr/bin/python

import sys, datetime, psycopg2
from supabase import create_client, Client
from utils import unpack_cursor

OPEN_BLOCKS_DAILY = 8
NUM_OF_CHUNKS = 3

conn_str = "user=postgres.fgocfoakntmlhgtftrzh password=RkTM2EYlp93mnld6 host=aws-0-us-west-1.pooler.supabase.com port=5432 dbname=postgres"


class BlockFiller():
    def __init__(self, supabase: Client, start_date: datetime, end_date: datetime) -> None:
        self.supabase = supabase
        self.start_date = start_date
        self.end_date = end_date
        self.conn = psycopg2.connect(conn_str)
    
    def main(self, fill_dict: dict):
        # Can turn on/off fill flags for testing
        
        # 0) Populate semester?
        if fill_dict['semester']:
            # self.populate_semester()
            self.populate_sched_days()
        
        # 1) Populate classes/events
        if fill_dict['events']:
            ...
        
        # 2) 5 days study plans
        if fill_dict['tests']:
            ...
        
        # 3) fill in assignments
        if fill_dict['assignments']:
            self.populate_assignments()
        
        
        if self.conn is not None:
            self.conn.close()
        return None
    
    def populate_semester(self):
        dates = []
        current = self.start_date
        while current <= self.end_date:
            dates.append({"local_date": current, "open_blocks": OPEN_BLOCKS_DAILY})
            current = current + datetime.timedelta(days=1)
            
        # need to populate blocked off times
            
        return None
    
    def populate_sched_days(self):
        cur = self.conn.cursor()
        current = self.start_date
        while current <= self.end_date:
            for i in range(1, 25): # do we want 0 to 23 instead?
                sql = f"insert into sched_days(local_date, local_hour, blocked) values ('{current}', {i}, false)"
                cur.execute(sql)
                current = current + datetime.timedelta(days=1)
        cur.close()
    
    def populate_assignments(self):
        # Get semester objects by date desc
        
        cur = self.conn.cursor()
        
        
        # Get all assignments by due date desc
        # Extract hour for ordering purposes (?)
        sql = f"select EXTRACT(DAY FROM due) as day, description, uid, EXTRACT(HOUR FROM due) as hour from assignments where \
            type = 'hw' or type = 'lab' order by hour asc, day desc"
        cur.execute(sql)
        ass = unpack_cursor(cur)
        
        for a in ass:
            # change these to line up
            ass_date = a[0]
            description = a[1]
            id = a[2]
            
            # Break assignments into chucks/blocks
            for i in range(NUM_OF_CHUNKS, 0, -1):
                sql = f"insert into chunks(assignment_id, due_date, chunk_no, title) values('{id}', '{ass_date}', {i}, '{description}')"
                
                ass_date = ass_date - datetime.timedelta(days=2)
            
                
                
        
        sql = f"select assignment_id, due_date, chunk_no from chunks order by due_date desc" #might switch order?
        
        # Go through chunks by due date desc and then block num desc
        # Assign chunk to alternating days (or just lower block number?)
        chunks = []
        for chunk in chunks:
            sql = f"update chunk set start_time = (select coalesce(min(local_hour) from sched_days where blocked is false and local_date = '{chunk[1]}'), \
                min(local_hour) from sched_days where blocked is false and \
                    local_date = (select max(local_date) from sched_days where blocked is false and local_date <= '{chunk[1]}') ), \
                stop_time = (start_time + interval '1 hour') \
                where assignment_id = '{chunk[0]}' and chunk_no = {chunk[2]}"
                
            # Also update sched_days to be blocked
            sql = f"update sched_days set blocked = true where \
                local_date = (select due_date from chunks where assignment_id = '{chunk[0]}' and chunk_no = {chunk[2]}) \
                    and local_time = (select start_time from chunks where assignment_id = '{chunk[0]}' and chunk_no = {chunk[2]})"
        
        # start = self.start_date
        # current = self.end_date
        # while current >= start:
        #     sql = f"select * from chunks where due_date = '{current}' order by chunk_no desc"
            
        #     sql = f"select "
            
        #     current = current - datetime.timedelta(days=1)
        
        
        
        # after assignment, update semester blocks??
        cur.close()
        
            

if __name__ == "__main__":
    
    # Init supabase client
    url = "https://fgocfoakntmlhgtftrzh.supabase.co"
    key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZnb2Nmb2FrbnRtbGhndGZ0cnpoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTE2ODkyMTUsImV4cCI6MjAyNzI2NTIxNX0.s5dAWy-DSa1EBfKjhpGOOcax6S7QUsh7xCHPFgKlBn8"
    
    supabase: Client = create_client(url, key)
    
    to_fill = {"semester":False, "tests":False, "events":False, "assignments":False}
    
    bf = BlockFiller(supabase)
    bf.main(to_fill)