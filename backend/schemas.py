from pydantic import BaseModel
from typing import List, Optional

class Song(BaseModel):
    id: Optional[str] = None
    title: str
    artist: str
    lyrics: Optional[str] = "Lyrics not available"
    album: Optional[str] = None
    duration: Optional[str] = None
    views: Optional[int] = 0
    score: Optional[float] = 0.0
    year: Optional[int] = None

class SearchResponse(BaseModel):
    results: List[Song]