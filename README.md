# Market News Data Pipeline

> Pipeline de données temps réel pour l'analyse de sentiment des actualités financières  
> **M2 DataScale — Université de Versailles Saint-Quentin-en-Yvelines**

---

## Architecture

```
Alpha Vantage API → Kafka → Logstash → Elasticsearch → Kibana
                                              ↓
                                           Spark
```

| Composant | Technologie | Rôle |
|-----------|-------------|------|
| Collecte | Python + Alpha Vantage API | Récupération des actualités financières avec scores de sentiment |
| Streaming | Apache Kafka + Zookeeper | Transport fiable et découplé des messages |
| Transformation | Logstash | Parsing JSON, typage, normalisation des dates |
| Indexation | Elasticsearch 8.12.2 | Stockage, recherche et agrégations |
| Visualisation | Kibana | Dashboards et analyses interactives |
| Traitement distribué | Apache Spark 3.4.2 | Agrégations distribuées sur le corpus indexé |

---

## Structure du Projet

```
market-news-data-pipeline/
├── docker-compose.yml              # Stack complète (Kafka, ES, Kibana, Logstash, Spark)
├── README.md
│
├── producer/
│   ├── producer.py                 # Collecte API Alpha Vantage → Kafka
│   ├── requirements.txt
│   └── .env                        # Clé API (non versionné)
│
├── elastic/
│   └── index-template.json         # Mapping Elasticsearch avec N-gram analyzer
│
├── logstash/
│   └── pipeline.conf               # Pipeline Kafka → Elasticsearch
│
├── spark/
│   ├── job.py                      # Job d'agrégations distribuées
│   └── output/                     # Exports CSV des résultats
│
├── elasticsearch-queries/
│   └── QUERIES.md                  # 5 requêtes Elasticsearch documentées
│
└── kibana/
    └── VISUALIZATIONS.md           # Guide des visualisations et du dashboard
```

---

## Prérequis

- Docker Desktop 24.x
- Python 3.11+
- Clé API Alpha Vantage (gratuite : https://www.alphavantage.co/support/#api-key)

---

## Installation et Lancement

### 1. Configuration

Créer le fichier `.env` dans `producer/` :
```env
ALPHAVANTAGE_API_KEY=VOTRE_CLE_ICI
```

Installer les dépendances Python :
```bash
cd producer
python -m venv .venv
source .venv/bin/activate        # Linux / Git Bash
# OU
.\.venv\Scripts\Activate.ps1     # PowerShell

pip install -r requirements.txt
```

### 2. Lancer la stack Docker

```bash
docker compose up -d
```

Vérifier que les 6 conteneurs sont actifs :
```bash
docker compose ps
```

Les services suivants doivent être en état **Up** : `zookeeper`, `kafka`, `elasticsearch`, `kibana`, `logstash`, `spark`.

### 3. Lancer le producer

```bash
cd producer
python producer.py
```

Sortie attendue :
```
API returned 50 articles
published 50 docs to market_news
```

### 4. Exécuter le job Spark

```bash
docker-compose exec spark /opt/spark/bin/spark-submit \
  --master local[*] \
  --jars /tmp/spark-deps/es-spark.jar \
  /opt/spark-jobs/job.py
```

### 5. Accéder à Kibana

Ouvrir : http://localhost:5601

---

## Configuration Réseau

| Service | Port (hôte) | Port (conteneur) | URL d'accès |
|---------|-------------|------------------|-------------|
| Kafka | 9092 | 9092 | `localhost:9092` |
| Zookeeper | 2181 | 2181 | `localhost:2181` |
| Elasticsearch | 9201 | 9200 | http://localhost:9201 |
| Kibana | 5601 | 5601 | http://localhost:5601 |
| Logstash | 9600 | 9600 | `localhost:9600` |

> **Important** : Elasticsearch est exposé sur le port **9201** depuis l'hôte, mais accessible sur le port **9200** depuis les conteneurs Docker (Logstash, Spark) via `http://elasticsearch:9200`.

---

## Résultats

### Données collectées
- **50 articles** financiers indexés sur 19 jours (25 janvier — 14 février 2026)
- **24 sources** médiatiques distinctes
- Score de sentiment moyen global : **0.151** (légèrement positif)

### Distribution des sentiments

| Label | Articles | Pourcentage |
|-------|----------|-------------|
| Somewhat-Bullish | 21 | 42% |
| Neutral | 20 | 40% |
| Bullish | 6 | 12% |
| Somewhat-Bearish | 3 | 6% |

### Indices Elasticsearch produits par Spark
- `market-news-stats-daily` : agrégations journalières
- `market-news-stats-by-source` : agrégations par source médiatique
- `market-news-stats-by-sentiment` : distribution par catégorie de sentiment

---

## Dépannage

**Erreur `NoBrokersAvailable`**  
Kafka n'est pas encore prêt. Attendre 30 secondes après `docker compose up -d` et réessayer.

**`Connection refused` sur Elasticsearch**  
Vérifier que le conteneur tourne avec `docker compose ps`. Utiliser le port **9201** depuis l'hôte.

**Aucune donnée dans Elasticsearch**  
Vérifier les logs Logstash : `docker compose logs logstash -f`

**Conteneur Kafka crash au démarrage**  
```bash
docker compose down -v
docker compose up -d
```

---

## Références

- [Alpha Vantage API Documentation](https://www.alphavantage.co/documentation/)
- [Apache Kafka Documentation](https://kafka.apache.org/documentation/)
- [Elasticsearch Reference Guide](https://www.elastic.co/guide/en/elasticsearch/reference/)
- [Kibana User Guide](https://www.elastic.co/guide/en/kibana/current/)
- [PySpark SQL API](https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql.html)

---

**Projet** : M2 DataScale — UE Indexation et Visualisation de Données Massives  
**Université** : Université de Versailles Saint-Quentin-en-Yvelines  
**Année universitaire** : 2025–2026
