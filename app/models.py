from pydantic import BaseModel, Field
from datetime import datetime

# from enum import Enum
import pytz


class Tag(BaseModel):
    name: str
    url: str


class UserInfo(BaseModel):
    name: str
    id: str
    url: str


class Content(BaseModel):
    type: str
    text: str | None = None
    img_alt: str | None = None
    img_url: str | None = None


class Comment(Content):
    # seq: str
    # create_time: datetime
    user: UserInfo
    like_counts: str = "0"


class Reel(BaseModel):
    url: str
    user: UserInfo
    text: str
    tags: list[Tag] = []
    like_counts: str = "0"
    comment_counts: str = "0"
    share_counts: str = "0"
    comments: list[Comment]
    create_time: datetime = Field(
        default_factory=lambda: datetime.now(tz=pytz.timezone("Asia/Taipei"))
    )

    def get_answer(self):
        pass
