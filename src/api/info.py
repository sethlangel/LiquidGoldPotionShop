from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional  # Import Optional
from src.api import auth

router = APIRouter(
    prefix="/info",
    tags=["info"],
    dependencies=[Depends(auth.get_api_key)],
)

class Timestamp(BaseModel):
    day: str
    hour: int

cur_time: Optional[Timestamp] = None

def get_timestamp():
    if cur_time is not None:
        return f"{cur_time.day} {cur_time.hour}"
    else:
        return "Unknown"

@router.post("/current_time")
def post_time(timestamp: Timestamp):

    global cur_time
    cur_time = timestamp
    print(timestamp)

    return "OK"
