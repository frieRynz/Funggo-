from elasticsearch import Elasticsearch, helpers, exceptions
from dotenv import load_dotenv
import json
import os
import sys
import urllib3

load_dotenv()
# Suppress InsecureRequestWarning since we are using self-signed certs (verify_certs=False)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- CONFIGURATION ---
# Ensure these match your actual Elasticsearch setup
ES_HOST = "https://localhost:9200" 
ES_USER = os.getenv("es_user")
ES_PASSWORD = os.getenv("es_password")

DATASET_PATH = "songdb.ndjson"
INDEX_NAME = "songs" 

# -------------------------------
# 1. Connect to Elasticsearch
# -------------------------------
try:
    print(f" Connecting to {ES_HOST}...")
    es = Elasticsearch(
        ES_HOST,
        basic_auth=(ES_USER, ES_PASSWORD),
        verify_certs=False, 
        ssl_show_warn=False
    )

    if not es.ping():
        raise exceptions.ConnectionError(" Cannot connect to Elasticsearch!")
    print("Connected successfully!")

except Exception as e:
    print(f"Connection failed: {e}")
    sys.exit(1)

# -------------------------------
# 2. Define Index Mapping
# -------------------------------
# logical fix: Actually USE the analyzers defined in settings
mapping = {
    "settings": {
        "analysis": {
            "analyzer": {
                "thai_analyzer": {"type": "thai"},
                "english_analyzer": {"type": "standard"}
            }
        }
    },
    "mappings": {
        "properties": {
            "title": {
                "type": "text",
                "analyzer": "standard", # Default to standard
                "fields": {
                    "th": {"type": "text", "analyzer": "thai_analyzer"}, # Sub-field for Thai logic
                    "raw": {"type": "keyword"}
                }
            },
            "artist": {
                "type": "text",
                "analyzer": "standard",
                "fields": {
                    "th": {"type": "text", "analyzer": "thai_analyzer"},
                    "raw": {"type": "keyword"}
                }
            },
            "lyrics": {
                "type": "text", 
                "analyzer": "standard",
                "fields": {
                    "th": {"type": "text", "analyzer": "thai_analyzer"}
                }
            },
            "views": {"type": "integer"},
            "album": {"type": "text"},
            "duration": {"type": "keyword"},
            "year": {"type": "integer"}
        }
    }
}

# -------------------------------
# 3. Create Index
# -------------------------------
if es.indices.exists(index=INDEX_NAME):
    print(f"Index '{INDEX_NAME}' already exists. Skipping creation.")
else:
    es.indices.create(index=INDEX_NAME, body=mapping)
    print(f"Index '{INDEX_NAME}' created.")

# -------------------------------
# 4. Upload Data
# -------------------------------
if not os.path.exists(DATASET_PATH):
    print(f"Dataset file '{DATASET_PATH}' not found. Skipping upload.")
    sys.exit(0)

print("Uploading dataset...")

def generate_actions():
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                doc = json.loads(line.strip())

                # Data Cleaning: Convert year safely
                if "year" in doc and doc["year"]:
                    try:
                        # Handle cases where year might be ["2020"] or "2020"
                        val = doc["year"][0] if isinstance(doc["year"], list) else doc["year"]
                        doc["year"] = int(val)
                    except (ValueError, IndexError, TypeError):
                        doc["year"] = None
                
                # Remove junk fields
                for redundant in ["lyrics_clean", "lyrics_clean.keyword", "features.keyword", "year.keyword"]:
                    doc.pop(redundant, None)

                yield {
                    "_index": INDEX_NAME,
                    "_source": doc
                }

try:
    success, failed = helpers.bulk(
        es,
        generate_actions(),
        chunk_size=2000,
        max_retries=5,
        request_timeout=60,
        stats_only=True
    )
    print(f"Upload complete {success} documents indexed.")
except Exception as e:
    print(f"Bulk upload error: {e}")