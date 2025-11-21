from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import uvicorn

from search_engine import search_songs
from schemas import SearchResponse

app = FastAPI(title="Song Search API")

# Allow Flutter front-end
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Song Search API with Elasticsearch is running!"}

@app.get("/search", response_model=SearchResponse)
def search_endpoint(
    q: str = Query(..., min_length=1, description="Search for songs by title, artist, or lyrics"),
    is_artist_search: bool = Query(False, description="Boost artist field if true")
):
    # results = search_songs(q)
    results = search_songs(q, is_artist_search)
    return SearchResponse(results=results)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)