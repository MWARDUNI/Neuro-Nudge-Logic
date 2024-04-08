
# from eventdata import EventData
from pydantic import BaseModel
from datetime import datetime
from fastapi import FastAPI, HTTPException
import uvicorn

# Pydantic model that represents the structure of the event data you expect
class EventData(BaseModel):
    title: str
    description: str
    startDateTime: datetime
    endDateTime: datetime
    eventType: str

# Handler functions for different event types
def handle_exam(event_data):
    print("Processing a meeting event")
    # Add your logic here for meeting events

# Handler functions for different event types
def handle_meeting(event_data):
    print("Processing a meeting event")
    # Add your logic here for meeting events


# Dispatch table mapping event types to handler functions
event_handlers = {
    "Meeting": handle_meeting,
    "Exam" : handle_exam
}

def process_event_based_on_type(event_data: EventData):
    # Get the handler function from the dispatch table and invoke it
    handler = event_handlers.get(event_data.eventType)
    if handler:
        handler(event_data)
    else:
        print("Unknown event type")


app = FastAPI()

# Define the /process-new-event endpoint that accepts a POST request
@app.post("/process-new-event")
async def process_new_event(event_data: EventData):
    # Here, you would add your logic to process the event data
    # For this example, we'll just return the received data as JSON
    print(event_data)
    return {
        "message": "Event received successfully!",
        "eventData": event_data
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=5080, reload=True)