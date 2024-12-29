from pydantic import BaseModel


class VideoData(BaseModel):
    video_url: str
    start_time: float = None  # Optional start time in seconds
    end_time: float = None  # Optional end time in seconds
    resize_factor: float = 1.0
