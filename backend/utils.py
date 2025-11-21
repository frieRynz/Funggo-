import string

# Expanded Stopwords list for better accuracy
STOPWORDS = {
    "the", "be", "you", "i", "to", "and", "we", "me", "a", "in", "on",
    "of", "my", "our", "your", "at", "is", "it", "that", "for", "with", 
    "this", "are", "was", "im", "so", "oh", "baby", "yeah"
}

def is_lyric_query(query: str) -> bool:
    """
    Heuristic to determine if a user is searching for lyrics 
    vs a specific Song Title / Artist.
    """
    if not query:
        return False

    # Remove punctuation and lowercase
    clean = query.translate(str.maketrans("", "", string.punctuation)).lower()
    tokens = clean.split()

    # Rule 1: Query length
    # Titles are usually short (1-3 words). Lyrics are longer phrases.
    if len(tokens) >= 4:
        return True

    # Rule 2: Stopwords
    # Titles (e.g., "Thriller", "Havana") rarely have many stopwords compared to lyrics.
    # If > 30% of the query is stopwords, it's likely natural language (lyrics).
    stopword_count = sum(1 for t in tokens if t in STOPWORDS)
    if len(tokens) > 0 and (stopword_count / len(tokens)) > 0.3:
        return True

    return False