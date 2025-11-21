from elasticsearch import Elasticsearch
from typing import List, Dict, Any
from dotenv import load_dotenv
import os
import urllib3

# Use absolute import
from utils import is_lyric_query

# Suppress warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
load_dotenv()

# --- CONFIGURATION ---
ES_HOST = "https://localhost:9200"
ES_USER = os.getenv("es_user")
ES_PASSWORD = os.getenv("es_password")
INDEX_NAME = "songs" 

# Connect
es = Elasticsearch(
    ES_HOST,
    basic_auth=(ES_USER, ES_PASSWORD),
    verify_certs=False
)

def search_songs(query: str, is_artist_search: bool = False) -> List[Dict[str, Any]]:
    """
    Main search logic with HYBRID SCORING (Multiplier):
    
    Formula: Final Score = Text_Match_Score * (1 + log10(views + 1))
    
    Why this works:
    - Irrelevant songs (Text Score ~1) * High Views (Multiplier 10) = 10 (Low Rank)
    - Relevant Covers (Text Score ~20) * Low Views (Multiplier 2) = 40 (Mid Rank)
    - Relevant Originals (Text Score ~20) * High Views (Multiplier 10) = 200 (Top Rank)
    """
    
    # 1. Determine Settings based on Query Type
    if is_artist_search:
         boosts = {"title": 1.5, "artist": 3.0, "lyrics": 1.5}
         min_match = "2<-1"
         score_cutoff = 1.0
        
    elif is_lyric_query(query):
        # LYRIC MODE (Natural Language)
        boosts = {"title": 1.5, "artist": 1.5, "lyrics": 3.0}
        min_match = "65%" 
        score_cutoff = 0.5 
        
    else:
        # TITLE/ARTIST MODE
        boosts = {"title": 3.0, "artist": 2.0, "lyrics": 1.0}
        min_match = "2<-1" 
        score_cutoff = 1.0

    # 2. Construct Query
    body = {
        "size": 20,
        "min_score": score_cutoff,

        "query": {
            "function_score": {
                "query": {
                    "multi_match": {
                        "query": query,
                        "fields": [
                            f"title^{boosts['title']}",
                            f"artist^{boosts['artist']}",
                            f"lyrics^{boosts['lyrics']}",
                            f"title.th^{boosts['title']}",
                            f"artist.th^{boosts['artist']}",
                            f"lyrics.th^{boosts['lyrics']}"
                        ],
                        "type": "most_fields", 
                        "fuzziness": "AUTO",
                        "minimum_should_match": min_match
                    }
                },
                
                # --- CRITICAL CHANGE: Multiplier Logic ---
                # We use a script to calculate a safe multiplier.
                # If views = 0, multiplier = 1 (Score is unchanged).
                # If views = 1M, multiplier ~= 7 (Score boosted 7x).
                "script_score": {
                    "script": {
                        "source": "Math.log10(doc['views'].value + 1) + 1"
                    }
                },
                
                # Multiply the Text Score by the Script Result
                "boost_mode": "multiply", 
                "score_mode": "max",
            }
        }
    }

    # Execute Search
    try:
        result = es.search(index=INDEX_NAME, body=body)
        
        hits = []
        for hit in result["hits"]["hits"]:
            source = hit["_source"]
            source["id"] = hit["_id"]
            # Debugging info
            source["score"] = hit["_score"]
            hits.append(source)
            
        return hits
        
    except Exception as e:
        print(f"Search Error: {e}")
        return []