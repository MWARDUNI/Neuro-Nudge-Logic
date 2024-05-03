from fastapi import FastAPI
import uvicorn, datetime, json
from fill_blocks import BlockFiller
from nn_00_main import nn_main
from pydantic import BaseModel
from supabase import create_client, Client
from openai import OpenAI
from fastapi.responses import JSONResponse
import json

# CMD TO RUN: uvicorn main:app --reload
# uvicorn --port 8000 --host 0.0.0.0 main:app --reload

app = FastAPI()

ICS_FILE = "all_in_one"

# Initialize the Supabase client
url = "https://fgocfoakntmlhgtftrzh.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZnb2Nmb2FrbnRtbGhndGZ0cnpoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTE2ODkyMTUsImV4cCI6MjAyNzI2NTIxNX0.s5dAWy-DSa1EBfKjhpGOOcax6S7QUsh7xCHPFgKlBn8"
supabase: Client = create_client(url, key)
string_to_event = OpenAI(api_key="sk-proj-9DyhQpPtK1Lm0fccEdL3T3BlbkFJKRoKglT8STd5B36OuBs8")
thread_id = "thread_i1iA8WbkmxqISKiJtNH9XPcr"
assistant_id = "asst_lDPbXSYKGtywyuHIyY2Tzmq5"

bf = BlockFiller(datetime.date.fromisoformat('2024-01-01'),datetime.date.fromisoformat('2024-06-01'), supabase)

class NewEvent(BaseModel):
    summary: str
    description: str
    start_time: str
    end_time: str
    isAllDay: bool | None = False
    recurrence: str | None = ""
    id: int | None = 0
    eventType: str | None = ""

class Input(BaseModel):
    inputString : str

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

@app.post("/smart-add-process")
async def smart_add(input: Input):
    # url = "https://api.openai.com/v1/threads//messages"
    message = string_to_event.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=input.inputString
    )

    run = string_to_event.beta.threads.runs.create_and_poll(
          thread_id=thread_id,
          assistant_id=assistant_id,
    )

    if run.status == 'completed': 
        messages = string_to_event.beta.threads.messages.list(
            thread_id=thread_id
        )
    theResponse = messages.data[0].content[0].text.value

    response = json.loads(theResponse)

    meeting = NewEvent(
        summary=response.get("subject"),
        description="",
        start_time=response.get("start_time"),
        end_time=response.get("end_time"),
        isAllDay=response.get('isAllDay'),
        recurrence=response.get('recurrence'),
        id=0,
        eventType=response.get('eventType'),
    )

    print(response)
    return JSONResponse(content=meeting.model_dump_json())

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