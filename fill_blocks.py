#!/usr/bin/python

import sys, datetime, psycopg2, ast
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
            self.populate_sched_days()
        
        # 1) Populate classes/events
        if fill_dict['events']:
            self.populate_events()
        
        # 2) 5 days study plans
        if fill_dict['tests']:
            self.populate_tests()
        
        # 3) fill in assignments
        if fill_dict['assignments']:
            self.populate_assignments()
        
        
        if self.conn is not None:
            self.conn.close()
        return None
    
    
    def populate_sched_days(self):
        cur = self.conn.cursor()
        # current = self.start_date
        # while current <= self.end_date:
        #     print(current)
        #     for i in range(0, 24): # do we want 0 to 23 instead?
        #         if i < 7 or i >= 20:
        #             sql = f"insert into sched_days(local_date, local_hour, blocked) values ('{current}', {i}, true)"
        #         else:
        #             sql = f"insert into sched_days(local_date, local_hour, blocked) values ('{current}', {i}, false)"
        #         cur.execute(sql)
        #     current = current + datetime.timedelta(days=1)
            
        sql = f"insert into sched_days(local_date, local_hour, blocked) \
            SELECT date_trunc('hour', gs)::timestamp::date as local_date, \
            EXTRACT(hour from date_trunc('hour', gs)) as local_hour, \
            false as blocked \
            FROM generate_series('{self.start_date}'::timestamp, '{self.end_date}'::timestamp, '1 hour') as gs"
        cur.execute(sql)
        self.conn.commit()
        
        cur.close()
        
    def populate_events(self):
        cur = self.conn.cursor()
        # days = {'SU':[], 'MO':[], 'TU':[], 'WE':[], 'TH':[], 'FR':[], 'SA':[]}
        day_key = {'SU':0, 'MO':1, 'TU':2, 'WE':3, 'TH':4, 'FR':5, 'SA':6}
        # days = [[] for _ in range(0,7)]
        # print(days)
        
        sql = f"select uid, summary, start_time::date, EXTRACT(hour from start_time), EXTRACT(epoch from (end_time - start_time)) / 60,   vrecur from events where action = 'DISPLAY'"
        cur.execute(sql)
        events = unpack_cursor(cur)
        
        for event in events:
            id = event[0]
            name = event[1]
            start_time = event[2]
            start_hour = event[3]
            minute_time = int(event[4])
            recur = event[5]
            
            # ceiling to hours
            e_len = minute_time // 60
            e_len += 1 if (e_len % 60) > 0 else 0
            # print(e_len)
            # print(recur)
            # recur = recur.replace("vRecur(", "")[:-1]
            # print(dict(recur))
            
            recur = recur.split("'BYDAY': ")[1].split("}")[0]
            # print(recur, type(recur))
            recur = ast.literal_eval(recur)
            # print(recur, type(recur))
            dows = ','.join([str(day_key[x]) for x in recur])
            # print(dows)
            
            #calculate class length and ceiling it
            # (let's just block off sleeping)
            sql = f"UPDATE sched_days SET blocked = true FROM \
                generate_series('{start_time}'::date, '{self.end_date}'::date, '1 day') AS ds(date), \
                generate_series(0, {e_len - 1}) AS h(hour) \
                WHERE sched_days.local_date = date_trunc('day', ds.date + interval '{start_hour} hour' + interval '1 hour' * h.hour) \
                AND sched_days.local_hour = EXTRACT(HOUR FROM ds.date + interval '{start_hour} hour' + interval '1 hour' * h.hour) \
                AND EXTRACT(DOW FROM ds.date) IN ({dows})"
            print(sql, "\n")
            cur.execute(sql)
        # sql = f"update sched_days set blocked = false"
        # cur.execute(sql)
        self.conn.commit()
        
        cur.close()
        
    def populate_tests(self):
        cur = self.conn.cursor()
        
        
        
        
        cur.close()
    
    def populate_assignments(self):
        # Get semester objects by date desc
        
        cur = self.conn.cursor()
        
        
        # Get all assignments by due date desc
        # TODO: only get assignments that are due in our timeframe 
        # Extract hour for ordering purposes (?)
        # sql = f"select EXTRACT(DAY FROM due) as day, description, uid, EXTRACT(HOUR FROM due) as hour from assignments where \
        #     type = 'hw' or type = 'lab' order by hour asc, day desc"
        sql = f"select date_trunc('day', due) as day, description, uid, EXTRACT(HOUR FROM due) as hour from assignments where \
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
                cur.execute(sql)
                ass_date = ass_date - datetime.timedelta(days=2)
            
                
                
        
        sql = f"select assignment_id, due_date, chunk_no from chunks order by due_date desc" #might switch order?
        cur.execute(sql)
        chunks = unpack_cursor(cur)
        # Go through chunks by due date desc and then block num desc
        # Assign chunk to alternating days (or just lower block number?)
        # chunks = []
        for chunk in chunks:
            # sql = f"update chunk set start_time = (select coalesce(min(local_hour) from sched_days where blocked is false and local_date = '{chunk[1]}'), \
            #     min(local_hour) from sched_days where blocked is false and \
            #         local_date = (select max(local_date) from sched_days where blocked is false and local_date <= '{chunk[1]}') ), \
            #     stop_time = (start_time + interval '1 hour') \
            #     where assignment_id = '{chunk[0]}' and chunk_no = {chunk[2]}"
            
            # change chunks to have days and hours separate to line up with sched_days?
            sql = f"update chunks set start_time = coalesce( \
                (select '{chunk[1]}' + interval '1 hour' * (select min(local_hour) from sched_days where blocked is false and local_date = '{chunk[1]}')), \
                (select min(local_hour) from sched_days where blocked is false and \
                    local_date = (select max(local_date) from sched_days where blocked is false and local_date <= '{chunk[1]}'))) , \
                stop_time = (start_time + interval '1 hour') \
                where assignment_id = '{chunk[0]}' and chunk_no = {chunk[2]}"
            cur.execute(sql)
                
            # Also update sched_days to be blocked
            sql = f"update sched_days set blocked = true where \
                local_date = (select due_date from chunks where assignment_id = '{chunk[0]}' and chunk_no = {chunk[2]}) \
                    and local_time = (select start_time from chunks where assignment_id = '{chunk[0]}' and chunk_no = {chunk[2]})"
            cur.execute(sql)
        
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
    
    to_fill = {"semester":False, "tests":False, "events":False, "assignments":True}
    
    bf = BlockFiller(supabase, datetime.date.fromisoformat('2024-01-01'),datetime.date.fromisoformat('2024-06-01'))
    bf.main(to_fill)