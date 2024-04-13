#!/usr/bin/python

import sys, datetime, psycopg2
from supabase import create_client, Client

OPEN_BLOCKS_DAILY = 8
NUM_OF_CHUNKS = 3

conn_str = "user=postgres.fgocfoakntmlhgtftrzh password=RkTM2EYlp93mnld6 host=aws-0-us-west-1.pooler.supabase.com port=5432 dbname=postgres"

def unpack_cursor(cur):
    res = cur.fetchall()
    if len(res) == 1:
        if len(res[0]) == 1:
            return res[0][0]
        else:
            return list(res[0])
        
    else:
        output = []
        for r in res:
            if len(r) == 1:
                output.append(r[0])
            else:
                output.append(list(r))
        
        return output

class BlockFiller():
    def __init__(self, supabase: Client, start_date: datetime, end_date: datetime) -> None:
        self.supabase = supabase
        self.start_date = start_date
        self.end_date = end_date
        self.conn = psycopg2.connect(conn_str)
    
    def main(self, **kwargs):
        # kwargs pattern just for testing
        
        # 0) Populate semester?
        if "semester" in kwargs:
            self.populate_semester()
        
        # 1) Populate classes/events
        if "events" in kwargs:
            ...
        
        # 2) 5 days study plans
        if "tests" in kwargs:
            ...
        
        # 3) fill in assignments
        if "assignments" in kwargs:
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
            
        return None
    
    def populate_assignments(self):
        # Get semester objects by date desc
        # days = self.supabase.table("semester").select("*").eq("filled", False).execute()
        
        cur = self.conn.cursor()
        
        # Maybe we just don't need to actually pull them?
        sql = f"select local_date, open_blocks from semester where open_blocks > 0 order by local_date desc"
        cur.execute(sql)
        dates = unpack_cursor(cur)
        # myDict = { k:v for (k,v) in zip(keys, values)}
        dates = {k:v for k,v in dates}
        # COULD STORE SEMESTER BLOCKS AS OFFSET FROM START (or back?)
        # what about a list of these days

        
        
        # Get all assignments by due date desc
        sql = f"select due, description from assignments where type = 'hw' or type = 'lab' order by due_date desc"
        cur.execute(sql)
        ass = unpack_cursor(cur)
        
        for a in ass:
            # change these to line up
            ass_date = a['due_date']
            description = a['des']
            id = a['id']
            
            # Break assignments into chucks/blocks
            for i in range(1, NUM_OF_CHUNKS, -1):
                sql = f"insert into chunks(assignment_id, due_date, chunk_no, title) values('{id}', '{ass_date}', {i}, '{description}')"
                # chunk = f"{i}"
                ass_date = ass_date - datetime.timedelta(days=2)
            
                
                
        
        sql = f"select * from chunks order by due_date desc" #might switch order?
        
        # Go through chunks by due date desc and then block num desc
        # Assign chunk to alternating days (or just lower block number?)
        #COULD MARK CHUNK DUE DATE AS 2 DAYS BACK
        chunks = []
        for chunk in chunks:
            # Grab dates and then grab chunks that are due that date???
            sql = f"update chunk set start_time = (select min(local_hour) from sched_days where blocked is false and local_date = {chunk['due_date']}), \
                stop_time = (start_time + interval '1 hour') \
                where assignment_id = '{chunk['id']}' and chunk_no = {chunk['chunk_no']}"
            
        
        start = self.start_date
        current = self.end_date
        while current >= start:
            sql = f"select * from chunks where due_date = '{current}' order by chunk_no desc"
            
            sql = f"select "
            
            current = current - datetime.timedelta(days=1)
        
        
        
        # after assignment, update semester blocks??
        cur.close()
        
    # def build_chunks(self, assignments):
    #     for assignment in assignments:
    #         ...
            

if __name__ == "__main__":
    
    # Init supabase client
    url = "https://fgocfoakntmlhgtftrzh.supabase.co"
    key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZnb2Nmb2FrbnRtbGhndGZ0cnpoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTE2ODkyMTUsImV4cCI6MjAyNzI2NTIxNX0.s5dAWy-DSa1EBfKjhpGOOcax6S7QUsh7xCHPFgKlBn8"
    
    supabase: Client = create_client(url, key)
    
    bf = BlockFiller(supabase)
    bf.main()