#!/usr/bin/python

import sys, datetime, psycopg2, ast
from utils import unpack_cursor

OPEN_BLOCKS_DAILY = 8
NUM_OF_CHUNKS = 3

conn_str = "user=postgres.fgocfoakntmlhgtftrzh password=RkTM2EYlp93mnld6 host=aws-0-us-west-1.pooler.supabase.com port=5432 dbname=postgres"


class BlockFiller():
    def __init__(self, start_date: datetime, end_date: datetime) -> None:
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
            self.block_off_events()
        
        # 2) 5 days study plans
        if fill_dict['tests']:
            self.block_off_single_events()
        
        # 3) fill in assignments
        if fill_dict['assignments']:
            self.populate_assignments()
            
        if fill_dict['reset']:
            self.reset_tables()
        
        
        if self.conn is not None:
            self.conn.close()
        return None
    
    
    def populate_sched_days(self):
        cur = self.conn.cursor()
        
        # Populate the sched_days table with unblocked hour rows    
        sql = f"insert into sched_days(local_date, local_hour, blocked) \
            SELECT date_trunc('hour', gs)::timestamp::date as local_date, \
            EXTRACT(hour from date_trunc('hour', gs)) as local_hour, \
            false as blocked \
            FROM generate_series('{self.start_date}'::timestamp, '{self.end_date}'::timestamp, '1 hour') as gs"
        cur.execute(sql)
        self.conn.commit()
        
        cur.close()
        
    def block_off_events(self):
        cur = self.conn.cursor()
        
        # Key for changes vRecur days into psql friendly DOWs
        day_key = {'SU':0, 'MO':1, 'TU':2, 'WE':3, 'TH':4, 'FR':5, 'SA':6}
        
        # Get all recurring events
        sql = f"select uid, summary, start_time::date, EXTRACT(hour from start_time), \
            EXTRACT(epoch from (end_time - start_time)) / 60,   vrecur from events \
            where action = 'DISPLAY' and vrecur is not null"
        cur.execute(sql)
        events = unpack_cursor(cur)
        
        for event in events:
            id = event[0]
            name = event[1]
            start_time = event[2]
            start_hour = event[3]
            minute_time = int(event[4])
            recur = event[5]
            
            # ceiling to hours - need to block off entire hour if event runs over the hour mark
            e_len = minute_time // 60
            e_len += 1 if (e_len % 60) > 0 else 0
            
            # Split up and parse the recurrance values
            recur = recur.split("'BYDAY': ")[1].split("}")[0]
            recur = ast.literal_eval(recur)
            dows = ','.join([str(day_key[x]) for x in recur])
            
            # Block off sched_days blocks where the recurring events happen
            sql = f"UPDATE sched_days SET blocked = true FROM \
                generate_series('{start_time}'::date, '{self.end_date}'::date, '1 day') AS ds(date), \
                generate_series(0, {e_len - 1}) AS h(hour) \
                WHERE sched_days.local_date = date_trunc('day', ds.date + interval '{start_hour} hour' + interval '1 hour' * h.hour) \
                AND sched_days.local_hour = EXTRACT(HOUR FROM ds.date + interval '{start_hour} hour' + interval '1 hour' * h.hour) \
                AND EXTRACT(DOW FROM ds.date) IN ({dows})"
            cur.execute(sql)
            
        self.conn.commit()
        
        cur.close()
        
    def block_off_single_events(self):
        cur = self.conn.cursor()
        
        # put in events with no recurrence
        sql = f"select uid, summary, start_time::date, EXTRACT(hour from start_time), EXTRACT(epoch from (end_time - start_time)) / 60 from events \
            where action = 'DISPLAY' and vrecur is null"
        cur.execute(sql)
        events = unpack_cursor(cur)
        
        for event in events:
            id = event[0]
            name = event[1]
            start_time = event[2]
            start_hour = event[3]
            minute_time = int(event[4])
            
            # ceiling to hours - need to block off entire hour if event runs over the hour mark
            e_len = minute_time // 60
            e_len += 1 if (e_len % 60) > 0 else 0
            
            
            
            # Block off sched_days blocks where the non-recurring events happen
            sql = f"UPDATE sched_days SET blocked = true FROM \
                generate_series('{start_time}'::date, '{self.end_date}'::date, '1 day') AS ds(date), \
                generate_series(0, {e_len - 1}) AS h(hour) \
                WHERE sched_days.local_date = date_trunc('day', ds.date + interval '{start_hour} hour' + interval '1 hour' * h.hour) \
                AND sched_days.local_hour = EXTRACT(HOUR FROM ds.date + interval '{start_hour} hour' + interval '1 hour' * h.hour)"
            cur.execute(sql)
            
        self.conn.commit()
        
        cur.close()
    
    def populate_assignments(self):
        cur = self.conn.cursor()
        
        # Get all assignments by due date desc
        # Extract hour for ordering purposes (?)
        sql = f"select date_trunc('day', due) as day, description, uid, EXTRACT(HOUR FROM due) as hour from assignments where \
            (type = 'hw' or type = 'lab') AND due BETWEEN '{self.start_date}'::timestamp AND '{self.end_date}'::timestamp \
            order by hour asc, day desc"
        cur.execute(sql)
        ass = unpack_cursor(cur)
        
        for a in ass:
            ass_date = a[0]
            description = a[1]
            id = a[2]
            
            # Break assignments into chucks/blocks
            for i in range(NUM_OF_CHUNKS, 0, -1):
                sql = f"insert into chunks(assignment_id, due_date, chunk_no, summary) values('{id}', '{ass_date}', {i}, '{description}')"
                cur.execute(sql)
                ass_date = ass_date - datetime.timedelta(days=2)
            
        self.conn.commit()       
                
        
        sql = f"select assignment_id, due_date, chunk_no from chunks order by due_date desc" #might switch order?
        cur.execute(sql)
        chunks = unpack_cursor(cur)
        # Go through chunks by due date desc and then block num desc
        # Assign chunk to alternating days
        for idx, chunk in enumerate(chunks):
            print(f"Chunk {idx+1} of {len(chunks)}\r", end="")
            
            # TODO: check this order by is right
            sql = f"select local_hour, local_date from sched_days where blocked is false and local_date <= '{chunk[1]}' order by local_date desc, local_hour asc limit 1"
            cur.execute(sql)
            times = unpack_cursor(cur)
            
            start_time = datetime.datetime.combine(times[1], datetime.time(hour=times[0]))
            stop_time = start_time + datetime.timedelta(hours=1)
            
            sql = f"update chunks set start_time = '{start_time}', end_time = '{stop_time}' where assignment_id = '{chunk[0]}' and chunk_no = {chunk[2]}"
            cur.execute(sql)
                
            # Also update sched_days to be blocked
            sql = f"update sched_days set blocked = true where \
                local_date = date_trunc('day', '{start_time}'::timestamp) and local_hour = {times[0]}"
            cur.execute(sql)
        
        
        self.conn.commit()
        
        cur.close()
        
        
    def reset_tables(self):
        cur = self.conn.cursor()
        
        TABLES = ['chunks', 'sched_days', 'assignments', 'events']
        
        for table in TABLES:
            sql = f"delete from {table}"
            print(sql)
            cur.execute(sql)
        
        self.conn.commit()
        
        cur.close()
        
            

if __name__ == "__main__":
    
    
    to_fill = {"semester":True, "tests":True, "events":True, "assignments":True, "reset":False}
    
    bf = BlockFiller(datetime.date.fromisoformat('2024-01-01'),datetime.date.fromisoformat('2024-06-01'))
    bf.main(to_fill)