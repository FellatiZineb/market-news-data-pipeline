# 📊 Market News Data Pipeline

> Pipeline de données temps réel pour l'analyse de sentiments financiers  
> **M2 DataScale - Université Paris-Saclay**

## 🏗️ Architecture

```
Alpha Vantage API → Kafka → Logstash → Elasticsearch → Kibana
                                              ↓
                                           Spark
```

**Technologies** :
- 📡 **Producer** : Python + Kafka Producer
- 🚀 **Streaming** : Apache Kafka + Zookeeper
- 🔄 **Transformation** : Logstash
- 🔍 **Indexation** : Elasticsearch (8.12.2)
- 📊 **Visualisation** : Kibana
- ⚡ **Traitement Distribué** : Apache Spark

---

## 📋 État du Projet

### ✅ Parties Complètes (Binôme)

- **Partie 1** : Collecte API Alpha Vantage ✅
- **Partie 2** : Transmission Kafka (producteur/consommateur) ✅
- **Partie 3** : Transformation Logstash + Indexation Elasticsearch ✅

### 🚧 Parties en Cours

- **Partie 4** : Requêtes Elasticsearch + Visualisations Kibana (voir [kibana/VISUALIZATIONS.md](kibana/VISUALIZATIONS.md))
- **Partie 5** : Traitement distribué Spark (voir [spark/README.md](spark/README.md))

---

## 🚀 Démarrage Rapide

### 1️⃣ Prérequis

- Docker Desktop installé et démarré
- Python 3.11+ avec pip
- Clé API Alpha Vantage (gratuite : https://www.alphavantage.co/support/#api-key)

### 2️⃣ Configuration

**Créer le fichier `.env` dans `producer/` :**
```env
ALPHAVANTAGE_API_KEY=VOTRE_CLE_ICI
```

**Installer les dépendances Python :**
```powershell
cd producer
python -m venv .venv
.\.venv\Scripts\Activate.ps1  # PowerShell
# OU
source .venv/bin/activate      # Git Bash

pip install -r requirements.txt
```

### 3️⃣ Lancer la Stack Docker

```powershell
# Depuis la racine du projet
docker compose up -d
```

**Vérifier que tout tourne :**
```powershell
docker compose ps
```

Vous devriez voir 5 conteneurs **Up** :
- `zookeeper`
- `kafka`
- `elasticsearch`
- `kibana`
- `logstash`

**Attendre 30 secondes** que tous les services démarrent complètement.

### 4️⃣ Lancer le Producer

```powershell
cd producer
python producer.py
```

**Sortie attendue :**
```
API returned 50 articles
published 15 docs to market_news
```

Le producer tourne en continu (polling toutes les heures). Laisser tourner **au moins 10 minutes** pour accumuler des données.

---

## 🔍 Vérification des Données

### Vérifier Kafka
```powershell
docker compose exec kafka kafka-topics --list --bootstrap-server localhost:9092
```

Doit afficher : `market_news`

### Vérifier Elasticsearch
```powershell
curl "http://localhost:9201/market-news-*/_count?pretty"
```

Doit retourner un count > 0.

### Vérifier Kibana
Ouvrir : http://localhost:5601

---

## 📊 Partie 4 : Requêtes + Visualisations Kibana

**Guide complet** : [kibana/VISUALIZATIONS.md](kibana/VISUALIZATIONS.md)  
**Requêtes Elasticsearch** : [elasticsearch-queries/QUERIES.md](elasticsearch-queries/QUERIES.md)

### Requêtes à Réaliser (5 obligatoires)

1. ✅ **Requête textuelle** : Match query sur `title`
2. ✅ **Agrégation** : Sentiment moyen par source
3. ✅ **N-gram** : Recherche avec `title.ngram`
4. ✅ **Fuzzy** : Tolérance aux fautes de frappe
5. ✅ **Série temporelle** : Évolution du sentiment par jour

### Visualisations à Créer

- Line chart : évolution temporelle
- Bar chart : sentiment par source
- Pie chart : distribution Bullish/Bearish/Neutral
- Métriques : KPIs globaux
- Data table : derniers articles

**Dashboard final** : combiner toutes les visualisations.

---

## ⚡ Partie 5 : Traitement Spark

**Guide complet** : [spark/README.md](spark/README.md)

### Ce que fait le Job Spark

Le script `spark/job.py` effectue **5 analyses distribuées** :

1. **Statistiques globales** : avg, min, max du sentiment
2. **Sentiment par source** : agrégation par média
3. **Distribution des labels** : Bullish vs Bearish vs Neutral
4. **Analyse par ticker** : AAPL, MSFT, GOOGL
5. **Top articles** : plus positifs et plus négatifs

### Exécution

```powershell
cd spark
python job.py
```

**Résultats exportés** en CSV + JSON dans `.venv/spark-tp/spark-output/` (à adapter selon ton environnement).

---

## 📂 Structure du Projet

```
market-news-data-pipeline/
├── docker-compose.yml              # Stack complète (Kafka, ES, Kibana, Logstash)
├── README.md                       # Ce fichier
│
├── producer/
│   ├── producer.py                 # Collecte API → Kafka
│   ├── requirements.txt            # Dépendances Python
│   └── .env                        # Clé API (non versionné)
│
├── elastic/
│   └── index-template.json         # Mapping ES avec n-gram analyzer
│
├── logstash/
│   └── pipeline.conf               # Kafka → Elasticsearch
│
├── spark/
│   ├── job.py                      # Analyses distribuées
│   └── README.md                   # Guide d'utilisation Spark
│
├── elasticsearch-queries/
│   └── QUERIES.md                  # 5 requêtes ES obligatoires
│
└── kibana/
    └── VISUALIZATIONS.md           # Guide visualisations + dashboard
```

---

## 🔧 Configuration Système

### Ports Utilisés

| Service         | Port Host | Port Container | Accès |
|-----------------|-----------|---|----------|
| Kafka           | 9092      | 9092 | `localhost:9092` |
| Zookeeper       | 2181      | 2181 | `localhost:2181` |
| **Elasticsearch** | **9201** | **9200** | http://localhost:9201 (host) / http://elasticsearch:9200 (Docker) |
| Kibana          | 5601      | 5601 | http://localhost:5601 |
| Logstash        | 9600      | 9600 | `localhost:9600` |

### ⚠️ Important : Elasticsearch sur 2 ports

- **Depuis HOST (Windows)** : `http://localhost:9201`
  - Utilisé par : curl, Kibana, requêtes manuelles
  - Exemple : `curl http://localhost:9201/market-news-*/_count?pretty`

- **Depuis CONTENEURS (Docker network)** : `http://elasticsearch:9200`
  - Utilisé par : Logstash, Spark (dans leurs conteneurs)
  - Exemple dans `job.py` : `ES_HOST = "elasticsearch"`, `ES_PORT = "9200"`

**Résumé** : Si tu utilises Spark / Logstash EN LOCAL (Windows), définis les variables d'environnement :
```powershell
$env:ES_HOST = "localhost"
$env:ES_PORT = "9201"
```

---

## 🐛 Dépannage

### ❌ Erreur "NoBrokersAvailable"
→ Kafka n'est pas démarré. Lancer `docker compose up -d` et attendre 30s.

### ❌ "Connection refused" Elasticsearch
→ Vérifier que le conteneur tourne : `docker compose ps`  
→ Utiliser le bon port : **9201**

### ❌ Pas de données dans Elasticsearch
→ Laisser tourner le producer au moins 10 minutes  
→ Vérifier les logs Logstash : `docker compose logs logstash -f`

### ❌ Conteneur Kafka crash au démarrage
→ Nettoyer et redémarrer :
```powershell
docker compose down -v
docker compose up -d
```

---

## 📸 Livrables pour le Rapport

### Partie 1-3 (Déjà fait par ta binôme)
- Captures des topics Kafka
- Logs du producer
- Mapping Elasticsearch
- Données indexées

### Partie 4 (À faire)
- [ ] 5 requêtes Elasticsearch exécutées + résultats JSON
- [ ] Captures des visualisations Kibana
- [ ] Dashboard complet

### Partie 5 (À faire)
- [ ] Logs d'exécution du job Spark
- [ ] Fichiers CSV/JSON exportés
- [ ] Justification technique (pourquoi Spark ?)

### Documentation
- [ ] README complet (ce fichier)
- [ ] Commentaires dans le code
- [ ] Explications des choix techniques

---

## 📚 Ressources

- [Alpha Vantage API Docs](https://www.alphavantage.co/documentation/)
- [Kafka Python Client](https://kafka-python.readthedocs.io/)
- [Elasticsearch Python Client](https://elasticsearch-py.readthedocs.io/)
- [Kibana Lens](https://www.elastic.co/guide/en/kibana/current/lens.html)
- [PySpark SQL](https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql.html)

---

## 👥 Contributeurs

- **Binôme** : Parties 1, 2, 3 (Collecte, Kafka, Logstash, Elasticsearch)
- **Toi** : Parties 4, 5 (Requêtes, Kibana, Spark)

**Projet** : M2 DataScale - Université Paris-Saclay  
**Date limite** : 27 février 2026

---

## ✅ Checklist Finale

- [x] Partie 1 : API + Producer Kafka
- [x] Partie 2 : Topics Kafka + Consommation
- [x] Partie 3 : Logstash + Mapping ES
- [ ] Partie 4 : 5 requêtes ES + Visualisations Kibana
- [ ] Partie 5 : Job Spark + Export résultats
- [ ] Documentation complète + Captures

---

## 🎯 Prochaines Étapes IMMÉDIATES

1. **Laisser tourner le producer** 10-15 minutes pour collecter des données
2. **Vérifier l'indexation** : `curl "http://localhost:9201/market-news-*/_count?pretty"`
3. **Tester les 5 requêtes ES** : voir [elasticsearch-queries/QUERIES.md](elasticsearch-queries/QUERIES.md)
4. **Créer les visualisations Kibana** : voir [kibana/VISUALIZATIONS.md](kibana/VISUALIZATIONS.md)
5. **Exécuter le job Spark** : voir [spark/README.md](spark/README.md)
6. **Capturer les résultats** pour le rapport final
