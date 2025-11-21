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

def search_songs(query: str) -> List[Dict[str, Any]]:
    """
    Main search logic with THRESHOLDS:
    - Detect lyric query
    - Apply dynamic field boosting
    - Apply 'minimum_should_match' to filter weak matches
    - Apply 'min_score' to remove low-quality results
    """
    
    # 1. Determine Settings based on Query Type
    if is_lyric_query(query):
        # LYRIC MODE
        boosts = {"title": 1.5, "artist": 1.5, "lyrics": 3.0}
        
        # User must get at least 65% of the words right.
        # Prevents random songs appearing just because they share 1 common word like "love".
        min_match = "65%" 
        
        # Lower cutoff for lyrics because natural language matches can sometimes have lower individual term scores
        score_cutoff = 1.0 
    else:
        # TITLE/ARTIST MODE
        boosts = {"title": 3.0, "artist": 2.0, "lyrics": 1.0}
        
        # "2<-1": If 1 or 2 words, match all. If >2 words, allow 1 missing word.
        # Perfect for "Taylor Swift" (2 matches needed) vs "Taylor Sift" (typo allowed)
        min_match = "2<-1" 
        
        # Higher cutoff: Title matches should be very strong
        score_cutoff = 2.0

    # 2. Construct Query
    body = {
        "size": 20,
        # GLOBAL THRESHOLD: If the final score is below this, drop the result.
        "min_score": score_cutoff, 
        
        "sort":[
            {"views": {"order": "desc", "missing": 0}},
            "_score"
        ],

        
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
                        
                        # FILTER: Only show results that match X% of the query terms
                        "minimum_should_match": min_match
                    }
                },
                "boost_mode": "sum",
                "score_mode": "sum",
                
                "functions": [
                    {
                        "field_value_factor": {
                            "field": "views",
                            "factor": 50, 
                            "modifier": "log1p",
                            "missing": 0
                        }
                    }
                ],
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
            source["score"] = hit["_score"]
            hits.append(source)
            
        return hits
        
    except Exception as e:
        print(f"Search Error: {e}")
        return []


# from elasticsearch import Elasticsearch
# from typing import List, Dict, Any
# from dotenv import load_dotenv
# import os
# import urllib3

# # Use absolute import
# from utils import is_lyric_query

# # Suppress warnings
# urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# load_dotenv()

# # --- CONFIGURATION ---
# ES_HOST = "https://localhost:9200"
# ES_USER = os.getenv("es_user", "elastic") # Added defaults for safety
# ES_PASSWORD = os.getenv("es_password")

# # CRITICAL FIX: Ensure this matches your load_dataset.py
# # If your loader used "songs_v2", this MUST be "songs_v2"
# INDEX_NAME = "songs" 

# # Connect
# es = Elasticsearch(
#     ES_HOST,
#     basic_auth=(ES_USER, ES_PASSWORD),
#     verify_certs=False
# )

# def search_songs(query: str) -> List[Dict[str, Any]]:
#     """
#     Main search logic with RESCORING:
#     1. Fetch Top 50 matches based on Text Relevance (BM25) + Field Boosting.
#     2. Rescore those Top 50 primarily by Popularity (Views).
#     This ensures "Originals" (High Views) beat "Covers" (Low Views) 
#     even if the Cover has a slightly better text match.
#     """
    
#     # 1. Determine Settings based on Query Type
#     if is_lyric_query(query):
#         # LYRIC MODE
#         boosts = {"title": 1.5, "artist": 1.5, "lyrics": 3.0}
#         min_match = "65%" 
#         score_cutoff = 1.0 
#     else:
#         # TITLE/ARTIST MODE
#         boosts = {"title": 3.0, "artist": 2.0, "lyrics": 1.0}
#         min_match = "2<-1" 
#         score_cutoff = 2.0

#     # 2. Construct Query
#     body = {
#         "size": 20,
#         "min_score": score_cutoff,
        
#         # PHASE 1: GET RELEVANT SONGS (Text Match)
#         "query": {
#             "multi_match": {
#                 "query": query,
#                 "fields": [
#                     f"title^{boosts['title']}",
#                     f"artist^{boosts['artist']}",
#                     f"lyrics^{boosts['lyrics']}",
#                     f"title.th^{boosts['title']}",
#                     f"artist.th^{boosts['artist']}",
#                     f"lyrics.th^{boosts['lyrics']}"
#                 ],
#                 "type": "most_fields", 
#                 "fuzziness": "AUTO",
#                 "minimum_should_match": min_match
#             }
#         },
        
#         # PHASE 2: RESCORE THE TOP 50 BY POPULARITY
#         # This re-sorts the best text matches specifically by view count.
#         "rescore": {
#             "window_size": 50, # Apply to top 50 text hits
#             "query": {
#                 "rescore_query": {
#                     "function_score": {
#                         "query": { "match_all": {} },
#                         "functions": [
#                             {
#                                 "field_value_factor": {
#                                     "field": "views",
#                                     "factor": 50, # High factor makes views dominant
#                                     "modifier": "log1p",
#                                     "missing": 0
#                                 }
#                             }
#                         ],
#                         "boost_mode": "replace" # Replace dummy match_all score with View Score
#                     }
#                 },
#                 # Final Score = (Text_Score * 1.0) + (View_Score * 2.0)
#                 # This weighting ensures popularity breaks ties and overtakes minor text differences.
#                 "query_weight": 1.0,
#                 "rescore_query_weight": 2.0
#             }
#         }
#     }

#     # Execute Search
#     try:
#         result = es.search(index=INDEX_NAME, body=body)
        
#         hits = []
#         for hit in result["hits"]["hits"]:
#             source = hit["_source"]
#             source["id"] = hit["_id"]
#             source["score"] = hit["_score"]
#             hits.append(source)
            
#         return hits
        
#     except Exception as e:
#         print(f"Search Error: {e}")
#         return []