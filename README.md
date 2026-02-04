# Market News Data Pipeline

Pipeline de données temps réel basé sur :
- Alpha Vantage API
- Kafka
- Logstash
- Elasticsearch
- Kibana

## Architecture
API → Kafka → Logstash → Elasticsearch → Kibana

## Lancement
1. Cree .env dans dossier producer et mets dedans ta clé : ALPHAVANTAGE_API_KEY= (insere ta cle comme ça) 
2. Ajouter la clé Alpha Vantage
3. demarre le .venv tjrs dans dossier producer python -m venv .venv
4. pip install -r requirements.txt
5. docker compose up -d
6. cd producer
7. Lancer producer.py

## Mapping Elasticsearch
Un index template personnalisé est défini dans elastic/index-template.json
