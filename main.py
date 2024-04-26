from fastapi import FastAPI
import uvicorn, datetime, json
from fill_blocks import BlockFiller
from nn_00_main import nn_main
from pydantic import BaseModel
from supabase import create_client, Client

# CMD TO RUN: uvicorn main:app --reload
# uvicorn --port 5080 main:app --reload

app = FastAPI()

ICS_FILE = "all_in_one"

# Initialize the Supabase client
url = "https://fgocfoakntmlhgtftrzh.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZnb2Nmb2FrbnRtbGhndGZ0cnpoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTE2ODkyMTUsImV4cCI6MjAyNzI2NTIxNX0.s5dAWy-DSa1EBfKjhpGOOcax6S7QUsh7xCHPFgKlBn8"
supabase: Client = create_client(url, key)

bf = BlockFiller(datetime.date.fromisoformat('2024-01-01'),datetime.date.fromisoformat('2024-06-01'), supabase)

class NewEvent(BaseModel):
    summary: str
    description: str
    start_time: str
    end_time: str
    isAllDay: bool | None = False
    recurrence: str
    id: int
    eventType: str

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/load-ics")
async def get_ics():
    nn_main()
    
    
    to_fill = {"semester":True, "tests":True, "events":True, "assignments":True, "reset":False}
    
    
    bf.main(to_fill)
    
    return "Success"

@app.post("/process-new-event")
async def add_event(event: NewEvent):
    testing = json.loads(event.model_dump_json())
    print(testing)
    # need to look at event type to see event vs. assignment?
    bf.add_single_event(testing)
    return testing

@app.get("/reset-supabase")
async def reset_supa():
    to_fill = {"semester":False, "tests":False, "events":False, "assignments":False, "reset":True}
    bf.main(to_fill)

if __name__ == "__main__":
    uvicorn.run(app, port=5080)
    
    
    
    """
    Map<String, dynamic> toJson() => {
        'summary': subject,
        'description': notes,
        'start_time': startTime.toIso8601String(),
        'end_time': endTime.toIso8601String(),
        'isAllDay' : isAllDay,
        'recurrence' : recurrenceRule, 
        'id' : dbID
        // 'eventType': eventType,
      };
    """