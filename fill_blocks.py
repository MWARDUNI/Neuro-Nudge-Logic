#!/usr/bin/python

import uuid, datetime, psycopg2, ast, atexit
from utils import unpack_cursor
from nn_03_1_5day_study import create_study_plan
from supabase import create_client, Client

OPEN_BLOCKS_DAILY = 8
NUM_OF_CHUNKS = 3

conn_str = "user=postgres.fgocfoakntmlhgtftrzh password=RkTM2EYlp93mnld6 host=aws-0-us-west-1.pooler.supabase.com port=5432 dbname=postgres"


class BlockFiller():
    def __init__(self, start_date: datetime, end_date: datetime, supabase: Client) -> None:
        self.start_date = start_date
        self.end_date = end_date
        self.conn = psycopg2.connect(conn_str)
        self.supabase = supabase
        
        def close():
            print("closing connection.")
            self.conn.close()
            
        atexit.register(close)
    
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
        sql = f"select class_id, summary, start_time::date, EXTRACT(hour from start_time), \
            EXTRACT(epoch from (end_time - start_time)) / 60,   recurrence from events \
            where action = 'DISPLAY' and recurrence is not null"
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
            if "BYDAY" in recur:
                # recur = recur.split("'BYDAY': ")[1].split("}")[0]
                recur = recur.split("BYDAY=")[1].split(',')
                # recur = ast.literal_eval(recur)
                dows = ','.join([str(day_key[x]) for x in recur])
            else:
                dows = ','.join([str(v) for _, v in day_key.items()])
            
            # Block off sched_days blocks where the recurring events happen
            sql = f"UPDATE sched_days SET blocked = true FROM \
                generate_series('{start_time}'::date, '{self.end_date}'::date, '1 day') AS ds(date), \
                generate_series(0, {e_len - 1}) AS h(hour) \
                WHERE sched_days.local_date = date_trunc('day', ds.date + interval '{start_hour} hour' + interval '1 hour' * h.hour) \
                AND sched_days.local_hour = EXTRACT(HOUR FROM ds.date + interval '{start_hour} hour' + interval '1 hour' * h.hour) \
                AND EXTRACT(DOW FROM ds.date) IN ({dows})"
            cur.execute(sql)
            
            sql = f"UPDATE events set scheduled = true where class_id = {id}"
            cur.execute(sql)
            
        self.conn.commit()
        
        cur.close()
        
    def block_off_single_events(self):
        cur = self.conn.cursor()
        
        # put in events with no recurrence
        sql = f"select class_id, summary, start_time::date, EXTRACT(hour from start_time), EXTRACT(epoch from (end_time - start_time)) / 60, trigger from events \
            where action = 'DISPLAY' and recurrence is null and scheduled is false"
        cur.execute(sql)
        events = unpack_cursor(cur)
        
        #TODO: deal with "events" being len() == 1?
        
        for event in events:
            id = event[0]
            name = event[1]
            start_time = event[2]
            start_hour = event[3]
            minute_time = int(event[4])
            fkey = event[5]
            
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
            
            sql = f"UPDATE events set scheduled = true where class_id = {id}"
            cur.execute(sql)
            
            sql = f"UPDATE assignments set scheduled = true where uid = '{fkey}'"
            cur.execute(sql)
            
        self.conn.commit()
        
        cur.close()
    
    def populate_assignments(self, color=None):
        cur = self.conn.cursor()
        
        # Get all assignments by due date desc
        # Extract hour for ordering purposes (?)
        sql = f"select date_trunc('day', due) as day, display_name, uid, EXTRACT(HOUR FROM due) as hour from assignments where \
            (type = 'hw' or type = 'lab') AND due BETWEEN '{self.start_date}'::timestamp AND '{self.end_date}'::timestamp \
            and scheduled is false order by hour asc, day desc"
        cur.execute(sql)
        ass = unpack_cursor(cur)
        if isinstance(ass, list) and not isinstance(ass[0], list):
            ass = [ass]
        for a in ass:
            ass_date = a[0]
            description = a[1]
            id = a[2]
            
            # Break assignments into chucks/blocks
            for i in range(NUM_OF_CHUNKS, 0, -1):
                if color is not None:
                    sql = f"insert into chunks(assignment_id, due_date, chunk_no, summary, color) values('{id}', '{ass_date}', {i}, '{description}', '{color}')"
                else:
                    sql = f"insert into chunks(assignment_id, due_date, chunk_no, summary) values('{id}', '{ass_date}', {i}, '{description}')"
                cur.execute(sql)
                ass_date = ass_date - datetime.timedelta(days=2)
            sql = f"update assignments set scheduled = true where uid = '{id}'"
            cur.execute(sql)
            
        self.conn.commit()       
                
        
        sql = f"select assignment_id, due_date, chunk_no, summary from chunks where scheduled is false order by due_date desc" #might switch order?
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
            
            dname = f"{chunk[3]} - chunk {chunk[2]}"
            
            sql = f"update chunks set start_time = '{start_time}', end_time = '{stop_time}', scheduled = true, \
                display_name = '{dname}' where assignment_id = '{chunk[0]}' and chunk_no = {chunk[2]}"
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
        
    def add_single_event(self, e: dict):
        cur = self.conn.cursor()      
        
        
        """
        class NewEvent(BaseModel):
            summary: str
            description: str
            start_time: str
            end_time: str
            isAllDay: bool | None = False
            recurrence: str
            id: str
            eventType: str
            
            # changing keys of dictionary
            ini_dict['akash'] = ini_dict.pop('akshat')
        """
        
        if (e['recurrence'] == "null" or e['recurrence'] == "None") and e['eventType'] in ['midterm', 'final']:
            sql = f"insert into assignments(class, due, type, description, uid, action, impact, display_name) \
                values ('{e['summary']}', '{e['end_time']}', '{e['eventType']}', '{e['description']}', \
                    '{uuid.uuid4()}@nn.com', 'DISPLAY', 0, '{e['summary']}')"
            cur.execute(sql)
            self.conn.commit()
            # insert into assignments
            
            # run study plans
            
            create_study_plan(self.supabase)
            
            
            # pull unscheduled events
            sql = f"select class_id, summary, start_time::date, EXTRACT(hour from start_time), EXTRACT(epoch from (end_time - start_time)) / 60, start_time from events \
            where action = 'DISPLAY' and recurrence is null and scheduled is false"
            cur.execute(sql)
            events = unpack_cursor(cur)
            
            for event in events:
                id = event[0]
                name = event[1]
                start_time = event[2]
                start_hour = event[3]
                minute_time = int(event[4])
                fkey = event[5]
                
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
                
                sql = f"UPDATE chunks set scheduled = false where start_time = '{fkey}'"
                cur.execute(sql)
                
                sql = f"UPDATE events set scheduled = true where class_id = {id}"
                cur.execute(sql)
            
            
            # insert into sched days (try on conflict w/ returning??)
            sql = f"select assignment_id, due_date, chunk_no, summary from chunks where scheduled is false order by due_date desc" #might switch order?
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
                
                dname = f"{chunk[3]} - chunk {chunk[2]}"
                
                sql = f"update chunks set start_time = '{start_time}', end_time = '{stop_time}', scheduled = true, \
                    display_name = '{dname}', color = '800080' where assignment_id = '{chunk[0]}' and chunk_no = {chunk[2]}"
                cur.execute(sql)
                    
                # Also update sched_days to be blocked
                sql = f"update sched_days set blocked = true where \
                    local_date = date_trunc('day', '{start_time}'::timestamp) and local_hour = {times[0]}"
                cur.execute(sql)       
        
        if e['eventType'] in ['hw', 'lab']:
            sql = f"insert into assignments(class, due, type, description, uid, action, impact, display_name) \
                values ('{e['summary']}', '{e['end_time']}', '{e['eventType']}', '{e['description']}', \
                    '{uuid.uuid4()}@nn.com', 'DISPLAY', 0, '{e['summary']}')"
            cur.execute(sql)
            self.conn.commit()
            
            self.populate_assignments(color="800080")
        
            
        else:
            pass
            #TODO? Implement new recurring events
        
        self.conn.commit()
        
        cur.close()
            
    def add_single_assignment(self):
        cur = self.conn.cursor()    
        
        
        
        cur.close()
        
            

if __name__ == "__main__":
    # Initialize the Supabase client
    url = "https://fgocfoakntmlhgtftrzh.supabase.co"
    key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZnb2Nmb2FrbnRtbGhndGZ0cnpoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTE2ODkyMTUsImV4cCI6MjAyNzI2NTIxNX0.s5dAWy-DSa1EBfKjhpGOOcax6S7QUsh7xCHPFgKlBn8"
    supabase: Client = create_client(url, key)
    
    to_fill = {"semester":True, "tests":True, "events":True, "assignments":True, "reset":False}
    
    bf = BlockFiller(datetime.date.fromisoformat('2024-01-01'),datetime.date.fromisoformat('2024-06-01'), supabase)
    bf.main(to_fill)