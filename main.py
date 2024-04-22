from fastapi import FastAPI
import uvicorn, datetime
from fill_blocks import BlockFiller
from nn_00_main import nn_main

# CMD TO RUN: uvicorn main:app --reload

app = FastAPI()

ICS_FILE = "all_in_one"

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/load-ics")
async def get_ics():
    nn_main()
    
    
    to_fill = {"semester":True, "tests":True, "events":True, "assignments":True, "reset":False}
    
    bf = BlockFiller(datetime.date.fromisoformat('2024-01-01'),datetime.date.fromisoformat('2024-06-01'))
    bf.main(to_fill)
    
    return "Success"


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)