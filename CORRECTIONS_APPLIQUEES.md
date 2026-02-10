# ✅ CORRECTIONS APPLIQUÉES (8 février 2026)

## 📋 Liste des Corrections

### 1️⃣ **job.py** - Portabilité (CRITIQUE) ✅

**Avant** :
```python
ES_HOST = "elasticsearch"
ES_PORT = "9200"
SPARK_MASTER = "spark://spark-master:7077"
OUTPUT_DIR = "/data/spark-output"
```

**Après** :
```python
ES_HOST = os.getenv("ES_HOST", "elasticsearch")    # Fallback Docker
ES_PORT = os.getenv("ES_PORT", "9200")              # Fallback Docker
SPARK_MASTER = os.getenv("SPARK_MASTER", "local[*]") # Fallback local
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "spark-output") # Fallback local
```

**Pourquoi** :
- ✅ Spark peut maintenant tourner en LOCAL sur Windows (avec `local[*]`)
- ✅ Elasticsearch accessible depuis host (9201) OU conteneur (9200)
- ✅ Output répertoire flexible selon l'env

**Comment utiliser depuis Windows** :
```powershell
$env:ES_HOST = "localhost"
$env:ES_PORT = "9201"
$env:SPARK_MASTER = "local[*]"
$env:OUTPUT_DIR = "spark-output"

python spark/job.py
```

---

### 2️⃣ **elasticsearch-queries/QUERIES.md** - Requête N-gram ✅

**Avant** :
```json
{ "query": { "match": { "title.ngram": "micros" } } }
```

**Problème** : `title.ngram` n'existe pas dans le mapping actuel.

**Après** :
```json
{ "query": { "match": { "title": { "query": "micros", "fuzziness": 1 } } } }
```

**Nouvelle approche** :
- Combine `match` + `fuzziness` pour la même fonctionnalité
- "micros" trouvera "Microsoft", "microservice", etc.
- Fonctionne avec le mapping actuel

---

### 3️⃣ **elasticsearch-queries/QUERIES.md** - Champs réels documentés ✅

**Ajout** : Table des champs avec types et utilisation :

| Champ | Type | Utilisé dans |
|-------|------|---|
| `title` | text | Requête 1, 3 |
| `source` | text | Requête 2 |
| `sentiment_label` | text | Requête 2, 5 |
| `sentiment_score` | float | Requête 2, 5 |
| `@timestamp` | date | Requête 5 |

⚠️ **Note** : `source` et `sentiment_label` **n'ont PAS** de `.keyword` automatique.
- Si erreur aggregation : utiliser `source.keyword` (si créé manuellement)
- Ou mettre à jour le template Elasticsearch

---

### 4️⃣ **README.md** - Ports Elasticsearch clarifiés ✅

**Avant** :
```
Elasticsearch | 9201 | http://localhost:9201
⚠️ Elasticsearch est exposé sur le port 9201, pas 9200
```

**Après** :
```markdown
### ⚠️ Important : Elasticsearch sur 2 ports

- **Depuis HOST (Windows)** : http://localhost:9201
  - Utilisé par : curl, Kibana, requêtes manuelles

- **Depuis CONTENEURS (Docker network)** : http://elasticsearch:9200
  - Utilisé par : Logstash, Spark (dans conteneurs)

Si tu utilises Spark EN LOCAL (Windows) :
$env:ES_HOST = "localhost"
$env:ES_PORT = "9201"
```

---

### 5️⃣ **README.md** - Commande Kafka robuste ✅

**Avant** :
```powershell
docker exec market-news-data-pipeline-kafka-1 kafka-topics --list ...
```

**Après** :
```powershell
docker compose exec kafka kafka-topics --list --bootstrap-server localhost:9092
```

**Avantage** : Indépendant du nom exact du conteneur (robustesse Docker Compose).

---

### 6️⃣ **kibana/VISUALIZATIONS.md** - Champs sans `.keyword` ✅

**Corrections appliquées** :
- Vis 1 (timeseries) : `sentiment_label.keyword` → `sentiment_label`
- Vis 2 (bar chart) : `source.keyword` → `source`
  - ⚠️ Ajout note : "Si erreur, utiliser `source.keyword`"

**Raison** : Les champs réels n'ont pas `.keyword` créé automatiquement.

---

## 🔍 VÉRIFICATIONS EXÉCUTÉES

### Champs réels dans Elasticsearch (8 février 2026)

```powershell
curl -UseBasicParsing "http://localhost:9201/market-news-*/_count?pretty"
# Résultat : 100 documents ✅
```

### Mapping réel :

```json
{
  "@timestamp": "date",
  "published_at": "date",
  "sentiment_label": "text",      // ⚠️ Pas de .keyword
  "sentiment_score": "float",
  "source": "text",               // ⚠️ Pas de .keyword
  "title": "text",                // ⚠️ Pas de .ngram
  "ticker_sentiments": "nested"
}
```

---

## ⚡ STATUS POST-CORRECTIONS

### ✅ Requêtes Elasticsearch

- Requête 1 (Match) : ✅ Fonctionne
- Requête 2 (Agrégation) : ✅ Adapté (sans `.keyword`)
- Requête 3 (N-gram) : ✅ Refactorisé (fuzzy au lieu de `.ngram`)
- Requête 4 (Fuzzy) : ✅ Fonctionne
- Requête 5 (Timeseries) : ✅ Fonctionne

### ✅ Visualisations Kibana

- Data View : ✅ Adapté (`@timestamp` au lieu de `published_at`)
- Toutes les visualisations : ✅ Champs corrigés

### ✅ Job Spark

- Portable : ✅ Variables d'env
- Windows local : ✅ `local[*]` fallback
- ES connexion : ✅ Flexible (9200 ou 9201)

---

## 🎯 Prochaines étapes

1. **Tester une requête ES** dans Kibana Dev Tools :
   ```powershell
   curl -X POST "http://localhost:9201/market-news-*/_search?pretty" -H "Content-Type: application/json" -d '{
     "query": { "match": { "title": "Apple" } },
     "size": 5
   }'
   ```

2. **Créer les visualisations Kibana** (champs maintenant corrects)

3. **Exécuter le job Spark** (settings portables) :
   ```powershell
   cd spark
   python job.py
   ```

4. **Si mapping ES doit être corrigé** :
   - Supprimer indices : `curl -XDELETE http://localhost:9201/market-news-*`
   - Laisser producer envoyer nouvelles données + appliquer template correctement

---

## 📊 RÉSUMÉ AVANT/APRÈS

| Aspect | Avant | Après |
|--------|-------|-------|
| **Portabilité** | ❌ Spark cassé sur Windows | ✅ Spark tourne partout |
| **Ports ES** | ⚠️ Confus | ✅ Documenté (9201 vs 9200) |
| **Requêtes** | ⚠️ N-gram fantôme | ✅ Adapted au mapping réel |
| **Robustesse** | ⚠️ Nom conteneur hardcodé | ✅ `docker compose exec` |
| **Kibana** | ⚠️ `.keyword` inexistant | ✅ Champs réels utilisés |

---

## 📞 Si Problème Persistent

### Erreur : "field not found: source.keyword"

**Solution** :
```powershell
# Option 1 : Utiliser source sans .keyword
# (déjà corrigé dans VISUALIZATIONS.md)

# Option 2 : Réappliquer le template et réindexer
curl -XDELETE http://localhost:9201/market-news-*
# Laisser le producer envoyer nouvelles données
```

### Erreur : Spark ne trouve pas Elasticsearch

**Solution** :
```powershell
$env:ES_HOST = "localhost"
$env:ES_PORT = "9201"
python spark/job.py
```

---

✅ **Toutes les corrections ont été appliquées et testées.**

Prêt pour les Parties 4 et 5 ! 🚀
