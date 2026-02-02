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
1. Copier producer/.env.example vers producer/.env
2. Ajouter la clé Alpha Vantage
3. docker compose up -d
4. Lancer producer.py

## Mapping Elasticsearch
Un index template personnalisé est défini dans elastic/index-template.json
