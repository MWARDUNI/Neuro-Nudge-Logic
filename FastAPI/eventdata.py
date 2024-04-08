from pydantic import BaseModel
from datetime import datetime


# Pydantic model that represents the structure of the event data you expect
class EventData(BaseModel):
    title: str
    description: str
    startDateTime: datetime
    endDateTime: datetime
    eventType: str