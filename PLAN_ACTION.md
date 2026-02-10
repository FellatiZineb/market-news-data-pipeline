# 🎯 PLAN D'ACTION - Parties 4 et 5

## 📌 Contexte

Ta binôme a terminé les **Parties 1, 2 et 3** (Collecte API, Kafka, Logstash, Elasticsearch).

**Tes responsabilités** :
- ✅ **Partie 4** : Requêtes Elasticsearch + Visualisations Kibana (40 pts)
- ✅ **Partie 5** : Traitement distribué Spark (20 pts)

---

## ⏱️ Timeline Recommandée (8-10h de travail)

### Jour 1 (3h) : Configuration + Collecte de Données
- [x] Démarrer Docker Compose ✅
- [x] Lancer le producer Python ✅
- [ ] **Laisser tourner 2-3 heures** pour collecter assez de données (~100-200 articles)
- [ ] Vérifier l'indexation Elasticsearch

### Jour 2 (3h) : Partie 4 - Elasticsearch + Kibana
- [ ] Tester les 5 requêtes Elasticsearch
- [ ] Créer le Data View dans Kibana
- [ ] Créer les 6 visualisations
- [ ] Assembler le dashboard
- [ ] Prendre les captures d'écran

### Jour 3 (2h) : Partie 5 - Spark
- [ ] Exécuter le job Spark
- [ ] Vérifier les exports CSV/JSON
- [ ] Prendre les captures d'écran
- [ ] Rédiger la justification technique

### Jour 4 (2h) : Rapport Final
- [ ] Compiler toutes les captures
- [ ] Rédiger les explications
- [ ] Relire et structurer le document
- [ ] Soumettre avant le 27 février

---

## 🚀 ÉTAPES CONCRÈTES

### MAINTENANT : Collecte de Données (30 min - 3h)

Le producer Python tourne et collecte des données. **Il faut attendre 2-3 heures** pour avoir assez de données (100-200 articles minimum).

#### Action immédiate :

1. **Vérifier que le producer tourne** (fenêtre PowerShell ouverte avec `producer.py`)
   - Si pas lancé : `cd producer` → `python producer.py`
   - Ne PAS fermer la fenêtre

2. **Pendant que ça tourne, lire les guides :**
   - [elasticsearch-queries/QUERIES.md](elasticsearch-queries/QUERIES.md)
   - [kibana/VISUALIZATIONS.md](kibana/VISUALIZATIONS.md)
   - [spark/README.md](spark/README.md)

3. **Vérifier toutes les 30 min** que des données arrivent :
   ```powershell
   curl "http://localhost:9201/market-news-*/_count?pretty"
   ```
   
   **Objectif** : avoir au moins **50-100 documents** avant de commencer les visualisations.

---

### ÉTAPE 1 : Partie 4.1 - Requêtes Elasticsearch (1h)

**Prérequis** : Au moins 50 documents indexés

#### 1.1 Ouvrir Kibana Dev Tools

- URL : http://localhost:5601
- Menu → **Dev Tools**

#### 1.2 Copier-coller les 5 requêtes

Depuis [elasticsearch-queries/QUERIES.md](elasticsearch-queries/QUERIES.md) :

1. **Requête textuelle** (Match query)
2. **Agrégation** (Sentiment moyen par source)
3. **N-gram** (Recherche partielle)
4. **Fuzzy** (Tolérance fautes)
5. **Série temporelle** (Date histogram)

#### 1.3 Captures d'écran

Pour **chaque requête** :
- ✅ Capture de la requête JSON dans Dev Tools
- ✅ Capture du résultat JSON (au moins les premiers éléments)

**Format** : PNG, haute résolution

---

### ÉTAPE 2 : Partie 4.2 - Visualisations Kibana (2h)

Suivre le guide complet : [kibana/VISUALIZATIONS.md](kibana/VISUALIZATIONS.md)

#### 2.1 Créer le Data View (5 min)
- Stack Management → Data Views
- Nom : `Market News`
- Index pattern : `market-news-*`
- Timestamp : `@timestamp`

#### 2.2 Créer 6 visualisations (1h)

1. **Line chart** : Sentiment over time
2. **Horizontal bar** : Avg sentiment by source
3. **Pie chart** : Sentiment distribution
4. **Vertical bar** : Top sources by volume
5. **Metric** : KPIs (total articles, avg sentiment)
6. **Data table** : Latest news

#### 2.3 Créer le Dashboard (30 min)
- Dashboard → Create new
- Add from library → sélectionner les 6 visualisations
- Organiser la disposition
- Ajouter des filtres (Time range, Tickers, etc.)

#### 2.4 Captures d'écran (15 min)
- ✅ Chaque visualisation individuellement
- ✅ Dashboard complet
- ✅ Dashboard avec différents filtres appliqués

---

### ÉTAPE 3 : Partie 5 - Spark (1h30)

Suivre le guide : [spark/README.md](spark/README.md)

#### 3.1 Vérifier l'environnement Spark

Selon ta fiche technique, tu as déjà Spark installé. Vérifier :

```powershell
# Si Spark via Docker
docker ps | Select-String spark

# Si Spark local
python -c "import pyspark; print(pyspark.__version__)"
```

#### 3.2 Exécuter le job Spark (30 min)

```powershell
cd spark
python job.py
```

**Sortie attendue** :
- Connexion à Elasticsearch réussie
- 5 analyses complétées
- Exports CSV/JSON créés

#### 3.3 Vérifier les résultats (15 min)

**Emplacement** : Selon ton `OUTPUT_DIR` dans `job.py`

Fichiers attendus :
```
spark-output/
├── global_stats/
├── sentiment_by_source_csv/
├── sentiment_by_source_json/
├── sentiment_distribution/
├── ticker_analysis/
├── positive_news/
└── negative_news/
```

Ouvrir au moins 2 fichiers CSV avec Excel ou VSCode pour vérifier le contenu.

#### 3.4 Captures d'écran (15 min)
- ✅ Commande d'exécution `python job.py`
- ✅ Logs de sortie (5 analyses)
- ✅ Explorateur de fichiers montrant les CSV/JSON
- ✅ Contenu d'au moins 2 fichiers (ex: `sentiment_by_source.csv`, `ticker_analysis.csv`)

#### 3.5 Justification technique (30 min)

Créer un document `spark/JUSTIFICATION.md` qui explique :

1. **Pourquoi Spark ?**
   - Calculs distribués (même si données faibles, démontre la capacité à scaler)
   - Connecteur natif Elasticsearch
   - Transformations puissantes (`explode`, `groupBy`, `agg`)

2. **Alternatives considérées**
   - Hadoop MapReduce : trop verbeux
   - Pandas : pas de distribution
   - **Spark ✅** : meilleur compromis

3. **Choix techniques**
   - PySpark (Python) plutôt que Scala : plus accessible
   - Lecture directe depuis ES via `elasticsearch-spark`
   - Export multi-format (CSV pour Excel, JSON pour réingestion)

---

### ÉTAPE 4 : Compilation du Rapport (2h)

#### Structure recommandée :

```
RAPPORT_PROJET_MARKET_NEWS.pdf

1. Introduction
   - Objectif du projet
   - Architecture globale

2. Partie 1-3 (Travail de ta binôme)
   - Collecte API
   - Kafka (producteur/consommateur)
   - Logstash + Elasticsearch

3. Partie 4 : Requêtes Elasticsearch + Kibana
   - 5 requêtes JSON + résultats
   - 6 visualisations
   - Dashboard complet
   - Captures d'écran

4. Partie 5 : Traitement Spark
   - Description du job
   - 5 analyses effectuées
   - Résultats CSV/JSON
   - Justification technique
   - Captures d'écran

5. Documentation & Organisation
   - Structure du projet
   - README
   - Commentaires code
   - Choix techniques

6. Conclusion
   - Résultats obtenus
   - Difficultés rencontrées
   - Améliorations possibles

Annexes :
   - Lien GitHub
   - Fichiers de configuration
   - Résultats complets (CSV/JSON)
```

---

## 📋 Checklist Barème (100 pts)

### Partie 1 : Collecte API (10 pts) ✅ Binôme
- [x] Script producer.py
- [x] Exemple de données extraites

### Partie 2 : Kafka (15 pts) ✅ Binôme
- [x] Topic `market_news` créé
- [x] Producteur configuré
- [x] Consommateur (Logstash) configuré
- [x] Captures d'écran

### Partie 3 : Logstash & Elasticsearch (25 pts) ✅ Binôme
- [x] Fichier `pipeline.conf`
- [x] Mapping avec analyzers + n-gram
- [x] Données indexées
- [x] 5 requêtes préparées

### Partie 4 : Kibana (20 pts) ⚠️ TOI
- [ ] Data View créé
- [ ] 6 visualisations créées
- [ ] Dashboard complet
- [ ] Captures d'écran haute qualité
- [ ] Requêtes ES testées

### Partie 5 : Spark (20 pts) ⚠️ TOI
- [ ] Job Spark exécuté
- [ ] 5 analyses complétées
- [ ] Résultats CSV/JSON exportés
- [ ] Justification technique rédigée
- [ ] Captures d'écran

### Documentation (10 pts) ⚠️ TOI + Binôme
- [ ] README complet
- [ ] Structure claire
- [ ] Commentaires code
- [ ] Rapport PDF final

---

## 🎯 RÉSUMÉ : Ce qui a été FAIT pour Toi

✅ **5 requêtes Elasticsearch prêtes à l'emploi**
   → Fichier : [elasticsearch-queries/QUERIES.md](elasticsearch-queries/QUERIES.md)

✅ **Job Spark complet (300+ lignes)**
   → Fichier : [spark/job.py](spark/job.py)

✅ **Guide visualisations Kibana étape par étape**
   → Fichier : [kibana/VISUALIZATIONS.md](kibana/VISUALIZATIONS.md)

✅ **Documentation Spark complète**
   → Fichier : [spark/README.md](spark/README.md)

✅ **README principal mis à jour**
   → Fichier : [README.md](README.md)

---

## 🚨 Points d'Attention

### ⚠️ Port Elasticsearch : 9201 (pas 9200)
Dans tous les scripts et commandes curl, utiliser **9201**.

### ⚠️ Attendre assez de données
Ne pas créer les visualisations Kibana avec seulement 10 documents. Minimum recommandé : **50-100 documents**.

### ⚠️ Time Range dans Kibana
Par défaut, Kibana affiche seulement les 15 dernières minutes. Penser à élargir à **Last 30 days** en haut à droite.

### ⚠️ Spark Master URL
Si erreur de connexion Spark, vérifier dans `job.py` ligne 30 :
```python
SPARK_MASTER = "spark://spark-master:7077"  # Adapter selon ton env
```

---

## 📞 Si Problème

### Le producer ne démarre pas
→ Vérifier Kafka : `docker compose ps`  
→ Nettoyer : `docker compose down -v` puis `docker compose up -d`

### Pas de données dans Elasticsearch
→ Vérifier Logstash : `docker compose logs logstash -f`  
→ Attendre plus longtemps (le producer poll toutes les heures)

### Kibana affiche "No data"
→ Vérifier le Time Range (Last 30 days)  
→ Recharger le Data View : Management → Data Views → Refresh

### Spark ne trouve pas Elasticsearch
→ Vérifier que le conteneur ES tourne : `docker compose ps`  
→ Dans `job.py`, ES_HOST doit être `"elasticsearch"` (nom du service Docker)

---

## ✅ Tu es Prêt !

Tout est en place. Il ne te reste plus qu'à :

1. **Attendre 2-3h** que le producer collecte des données
2. **Tester les 5 requêtes ES** → 30 min
3. **Créer les visualisations Kibana** → 2h
4. **Exécuter le job Spark** → 1h
5. **Compiler le rapport** → 2h

**Total estimé** : 5-6h de travail effectif (hors temps de collecte des données)

---

## 🎓 Bon Courage !

Si tu suis ce plan étape par étape, tu auras **60 points sur 60** pour tes parties 4 et 5.

N'oublie pas de **capturer les écrans** au fur et à mesure, c'est plus facile que de tout refaire à la fin ! 📸
