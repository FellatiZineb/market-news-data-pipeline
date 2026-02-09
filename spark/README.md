# 🚀 Spark Job - Guide d'Utilisation

## 📋 Prérequis

1. ✅ Docker Desktop lancé
2. ✅ Stack Docker Compose active (`docker compose up -d`)
3. ✅ Données indexées dans Elasticsearch (via producer → Kafka → Logstash)
4. ✅ Conteneurs Spark disponibles (selon ta fiche technique)

---

## 🔧 Configuration

Le job Spark se connecte à :
- **Elasticsearch** : `elasticsearch:9200` (conteneur Docker)
- **Spark Master** : `spark://spark-master:7077`
- **Répertoire de sortie** : `/data/spark-output` (monté sur Windows : `C:\Users\benal\spark-tp`)

---

## 🎯 Ce que fait le Job

Le script `job.py` effectue **5 analyses distribuées** :

### 1. **Statistiques Globales**
- Nombre total d'articles
- Score moyen de sentiment
- Min/Max des scores

### 2. **Sentiment par Source de Presse**
- Agrégation par source (Reuters, Bloomberg, etc.)
- Moyenne des scores par source
- Nombre d'articles par source

### 3. **Distribution des Labels**
- Compte des articles Bullish / Bearish / Neutral
- Score moyen par label

### 4. **Analyse par Ticker**
- Sentiments pour AAPL, MSFT, GOOGL
- Score moyen et relevance par ticker
- Nombre de mentions

### 5. **Top Articles Positifs/Négatifs**
- 5 articles les plus positifs
- 5 articles les plus négatifs

---

## 🚀 Exécution du Job

### Option A : Depuis Windows (Recommandé)

Si tu as Python + PySpark installé localement :

```powershell
cd C:\Users\benal\OneDrive\Bureau\M2 DataScale\Partie 2\indexation\Projet\market-news-data-pipeline\spark

# Exécuter le job
python job.py
```

### Option B : Dans le Conteneur Spark

```powershell
# Copier le script dans le conteneur (si pas déjà monté)
docker cp job.py spark-master:/opt/spark/work-dir/

# Exécuter dans le conteneur
docker exec -it spark-master bash

# Puis dans le conteneur :
/opt/spark/bin/spark-submit \
  --master spark://spark-master:7077 \
  --packages org.elasticsearch:elasticsearch-spark-30_2.12:8.12.0 \
  /opt/spark/work-dir/job.py
```

---

## 📂 Récupération des Résultats

Les résultats sont exportés dans `/data/spark-output/` (conteneur) = `C:\Users\benal\spark-tp\spark-output\` (Windows).

### Structure des fichiers :

```
C:\Users\benal\spark-tp\spark-output\
├── global_stats/
│   └── *.json
├── sentiment_by_source_csv/
│   └── *.csv
├── sentiment_by_source_json/
│   └── *.json
├── sentiment_distribution/
│   └── *.csv
├── ticker_analysis/
│   └── *.csv
├── positive_news/
│   └── *.csv
└── negative_news/
    └── *.csv
```

### Copier depuis le conteneur (si nécessaire) :

```powershell
docker cp spark-master:/data/spark-output C:\Users\benal\spark-tp\
```

---

## 📊 Visualisation des Résultats

### Avec Pandas (Python)

```python
import pandas as pd

# Charger un résultat CSV
df = pd.read_csv(r"C:\Users\benal\spark-tp\spark-output\sentiment_by_source_csv\part-00000-*.csv")
print(df.head())
```

### Avec Excel

Ouvrir directement les fichiers `.csv` depuis `C:\Users\benal\spark-tp\spark-output\`.

---

## 🐛 Dépannage

### ❌ Erreur "No module named 'pyspark'"

PySpark manquant → Installer :
```powershell
pip install pyspark==3.5.0
```

### ❌ "Connection refused" à Elasticsearch

Vérifier que les conteneurs tournent :
```powershell
docker compose ps
```

Vérifier que Elasticsearch est accessible :
```powershell
curl http://localhost:9201/_cluster/health?pretty
```

### ❌ "Index not found" ou "0 documents"

Le producer n'a pas encore envoyé de données. Attendre quelques minutes ou vérifier :
```powershell
curl "http://localhost:9201/market-news-*/_count?pretty"
```

### ❌ Spark Master inaccessible

Vérifier le nom du master dans `job.py` ligne 30 :
```python
SPARK_MASTER = "spark://spark-master:7077"  # Nom selon docker-compose
```

---

## 📸 Captures d'écran pour le Rapport

Pour le livrable Partie 5 (20 pts), capturer :

1. ✅ Commande d'exécution du job Spark
2. ✅ Logs de sortie (5 analyses)
3. ✅ Fichiers CSV/JSON générés
4. ✅ Contenu d'au moins 2 fichiers (ex: sentiment_by_source, ticker_analysis)
5. ✅ Graphiques depuis Excel ou Pandas (optionnel mais valorisé)

---

## 🎯 Intégration avec Kibana (Partie 4)

Les résultats Spark peuvent être **réindexés dans Elasticsearch** pour visualisation dans Kibana :

```python
# Dans job.py, ajouter à la fin :
sentiment_by_source.write \
    .format("org.elasticsearch.spark.sql") \
    .option("es.nodes", ES_HOST) \
    .option("es.port", ES_PORT) \
    .option("es.resource", "spark-analysis/_doc") \
    .mode("overwrite") \
    .save()
```

Puis créer un nouveau Data View dans Kibana : `spark-analysis`.

---

## 📝 Justification Technique (pour le rapport)

### Pourquoi Spark ?

1. **Traitement distribué** : même si les données sont faibles, Spark démontre la capacité à scaler
2. **Connecteur natif** : `elasticsearch-spark` permet lecture/écriture directe
3. **Transformations puissantes** : `explode`, `groupBy`, `agg` pour analyses complexes
4. **Export multi-format** : JSON (réingestion), CSV (Excel, Pandas)

### Alternatives considérées

- **Hadoop MapReduce** : plus verbeux, moins adapté aux analyses interactives
- **Pandas** : limité au single-node, pas de distribution
- **Spark** ✅ : compromis idéal pour le TP

---

## ✅ Checklist Partie 5

- [ ] Job Spark exécuté sans erreur
- [ ] 5 analyses complétées
- [ ] Résultats exportés en CSV + JSON
- [ ] Captures d'écran prises
- [ ] Documentation technique rédigée
- [ ] Justification des choix techniques (pourquoi Spark ?)

---

## 📞 Support

En cas de problème, vérifier :
1. Logs Docker : `docker compose logs -f`
2. Logs Spark : dans la sortie de `spark-submit`
3. État Elasticsearch : `curl http://localhost:9201/_cat/indices?v`

**Environnement validé** : Windows 10/11 + Docker Desktop + Git Bash
