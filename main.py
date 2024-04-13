from fastapi import FastAPI
from pydantic import BaseModel
from supabase import create_client, Client
from nn_01_parser import parse_ics
import json

# CMD TO RUN: uvicorn main:app --reload

app = FastAPI()
# Initialize the Supabase client
# url = "https://fgocfoakntmlhgtftrzh.supabase.co"
# key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZnb2Nmb2FrbnRtbGhndGZ0cnpoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTE2ODkyMTUsImV4cCI6MjAyNzI2NTIxNX0.s5dAWy-DSa1EBfKjhpGOOcax6S7QUsh7xCHPFgKlBn8"
# supabase: Client = create_client(url, key)

# class CalendarJson(BaseModel):
#     data: list



@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/load-ics")
async def get_ics():
    return parse_ics("class_cal.ics")

# @app.get("/load-calendar")
# async def load_ics(cal: CalendarJson):
#     for row in cal.data:
#         print(row)
#     return