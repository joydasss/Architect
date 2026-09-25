"""
Section 4.1 / 4.5 companion example: create an index with an explicit
mapping and a custom analyzer, avoiding the dynamic-mapping pitfall
described in Section 4.5 of CH20_ElasticSearch.md.

Requires: pip install elasticsearch
Assumes a local ElasticSearch instance reachable at http://localhost:9200.
"""

from elasticsearch import Elasticsearch

INDEX_NAME = "support-tickets"

# Custom analyzer: char_filter -> tokenizer -> token_filter pipeline
# (Section 4.1). Strips HTML from ticket bodies, splits on the standard
# Unicode text-segmentation rules, lowercases, removes English stop words,
# and stems remaining terms so "cancelled"/"cancelling" both match "cancel".
CUSTOM_ANALYZER_SETTINGS = {
    "settings": {
        "analysis": {
            "analyzer": {
                "ticket_body_analyzer": {
                    "type": "custom",
                    "char_filter": ["html_strip"],
                    "tokenizer": "standard",
                    "filter": ["lowercase", "english_stop", "english_stemmer"],
                }
            },
            "filter": {
                "english_stop": {"type": "stop", "stopwords": "_english_"},
                "english_stemmer": {"type": "stemmer", "language": "english"},
            },
        }
    },
    "mappings": {
        "properties": {
            # Free text: analyzed for full-text relevance search.
            "body": {"type": "text", "analyzer": "ticket_body_analyzer"},
            # Exact match / aggregation / sorting: never analyzed.
            "status": {"type": "keyword"},
            "assignee_email": {"type": "keyword"},
            # Multi-field: one value, two purpose-built representations
            # (Section 4.1's text/keyword multi-field pattern).
            "subject": {
                "type": "text",
                "analyzer": "ticket_body_analyzer",
                "fields": {"raw": {"type": "keyword"}},
            },
            "created_at": {"type": "date"},
        }
    },
}


def create_explicit_mapping(client: Elasticsearch) -> None:
    """Explicit mapping avoids the dynamic-mapping type-lock-in pitfall
    (Section 4.5): every field's type and analyzer is declared up front
    rather than guessed from whichever document arrives first."""
    if client.indices.exists(index=INDEX_NAME):
        client.indices.delete(index=INDEX_NAME)
    client.indices.create(index=INDEX_NAME, body=CUSTOM_ANALYZER_SETTINGS)
    print(f"Created index '{INDEX_NAME}' with explicit mapping.")


def verify_analyzer_output(client: Elasticsearch) -> None:
    """Use the _analyze API to confirm the exact terms the custom analyzer
    produces before ever indexing real data — the practice Section 16
    (Testing) recommends for any custom analyzer."""
    sample_text = "Customer requested cancelling <b>Order #4821</b> today."
    result = client.indices.analyze(
        index=INDEX_NAME,
        body={"analyzer": "ticket_body_analyzer", "text": sample_text},
    )
    terms = [token["token"] for token in result["tokens"]]
    print(f"Input:  {sample_text!r}")
    print(f"Terms:  {terms}")


def index_sample_documents(client: Elasticsearch) -> None:
    client.index(
        index=INDEX_NAME,
        document={
            "subject": "Cancel my subscription",
            "body": "I would like to cancel my subscription immediately.",
            "status": "open",
            "assignee_email": "support@example.com",
            "created_at": "2026-09-01T10:00:00Z",
        },
        refresh="wait_for",
    )
    client.index(
        index=INDEX_NAME,
        document={
            "subject": "Order was cancelled by mistake",
            "body": "My order got cancelled and I never asked for that.",
            "status": "closed",
            "assignee_email": "support@example.com",
            "created_at": "2026-09-02T09:30:00Z",
        },
        refresh="wait_for",
    )
    print("Indexed 2 sample tickets.")


if __name__ == "__main__":
    es = Elasticsearch("http://localhost:9200")
    create_explicit_mapping(es)
    verify_analyzer_output(es)
    index_sample_documents(es)

    # Stemming means a query for "cancel" matches both "cancelling" and
    # "cancelled" documents (Section 4.1).
    hits = es.search(
        index=INDEX_NAME,
        query={"match": {"body": "cancel"}},
    )
    print(f"Matches for 'cancel': {hits['hits']['total']['value']}")
