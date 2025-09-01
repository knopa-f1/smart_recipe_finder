import spacy

nlp = spacy.load("en_core_web_sm")

CUSTOM_STOPWORDS = {"less", "under", "with", "minute", "minutes", "recipe", "recipes"}

def parse_natural_query(text: str) -> dict:
    doc = nlp(text.lower())
    filters = {}
    keywords = []

    for token in doc:
        # cooking_time
        if token.like_num:
            next_token = doc[token.i + 1] if token.i + 1 < len(doc) else None
            if next_token and next_token.text in {"minute", "minutes"}:
                filters["cooking_time"] = {"lte": int(token.text)}
                continue

        # difficulty
        if token.lemma_ in {"easy", "beginner"}:
            filters["difficulty"] = "easy"
            continue
        if token.lemma_ in {"medium", "intermediate"}:
            filters["difficulty"] = "medium"
            continue
        if token.lemma_ in {"hard", "difficult"}:
            filters["difficulty"] = "hard"
            continue

        # skip stopwords
        if token.lemma_ in CUSTOM_STOPWORDS or token.is_stop:
            continue

        if token.is_alpha:
            keywords.append(token.lemma_)

    return {
        "fts": " ".join(keywords),
        **filters
    }
