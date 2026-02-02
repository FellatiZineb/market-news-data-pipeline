import os
import time
import json
import requests
from kafka import KafkaProducer
from dotenv import load_dotenv

load_dotenv()

# ========================
# CONFIGURATION APPLICATIVE
# ========================

# Kafka
KAFKA_BOOTSTRAP = "localhost:9092"
KAFKA_TOPIC = "market_news"

# Alpha Vantage (secret dans .env)
API_KEY = os.getenv("ALPHAVANTAGE_API_KEY")
if not API_KEY:
    raise SystemExit("ALPHAVANTAGE_API_KEY manquant dans .env")

# Liste de tickers (modifiable facilement)
TICKERS = [
    "AAPL", "MSFT", "GOOGL"
]

TICKERS_QUERY = ",".join(TICKERS)

# Fréquence et timeout
POLL_SECONDS = 3600
HTTP_TIMEOUT = 30

# ========================
# KAFKA PRODUCER
# ========================

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BOOTSTRAP,
    value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode("utf-8"),
)

seen = set()

# ========================
# FONCTIONS
# ========================

def fetch_news():
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "NEWS_SENTIMENT",
        "tickers": TICKERS_QUERY,
        "sort": "LATEST",
        "limit": 50,
        "apikey": API_KEY,
    }
    r = requests.get(url, params=params, timeout=HTTP_TIMEOUT)
    r.raise_for_status()
    data = r.json()

    # gestion quota / erreurs API
    if "Note" in data or "Information" in data or "Error Message" in data:
        raise RuntimeError(data.get("Note") or data.get("Information") or data.get("Error Message"))

    return data.get("feed", [])

def to_iso8601(time_published):
    if not time_published or len(time_published) < 15:
        return None
    return (
        f"{time_published[0:4]}-{time_published[4:6]}-{time_published[6:8]}"
        f"T{time_published[9:11]}:{time_published[11:13]}:{time_published[13:15]}Z"
    )

def normalize(item):
    published_iso = to_iso8601(item.get("time_published"))

    doc_id = item.get("url") or (
        (item.get("title", "") + "|" + str(item.get("time_published")))
    )

    doc = {
        "published_at": published_iso,
        "title": item.get("title"),
        "summary": item.get("summary"),
        "source": item.get("source"),
        "url": item.get("url"),
        "sentiment": item.get("overall_sentiment_label"),
        "sentiment_score": float(item.get("overall_sentiment_score", 0.0) or 0.0),
        "ticker_sentiments": item.get("ticker_sentiment", []),
        "provider": "alphavantage",
        "tickers_query": TICKERS_QUERY
    }
    return doc_id, doc

# ========================
# BOUCLE PRINCIPALE
# ========================

while True:
    try:
        feed = fetch_news()
        print(f"API returned {len(feed)} articles")
        sent = 0

        for item in feed:
            doc_id, doc = normalize(item)

            if doc_id in seen:
                continue

            seen.add(doc_id)
            producer.send(KAFKA_TOPIC, doc)
            sent += 1

        producer.flush()
        print(f"published {sent} docs to {KAFKA_TOPIC}")

    except Exception as e:
        print(f"error: {e}")

    time.sleep(POLL_SECONDS)
