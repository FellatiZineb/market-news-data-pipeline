# 📊 Kibana - Guide de Visualisation (Partie 4)

## 🎯 Objectif

Créer des **visualisations pertinentes** dans Kibana basées sur les 5 requêtes Elasticsearch de la Partie 4.

**Barème** : 20 points
- Visualisations créées : 15 pts
- Pertinence et lisibilité : 5 pts

---

## 🚀 Accès à Kibana

**URL** : http://localhost:5601

Attendre 1-2 minutes après `docker compose up` pour que Kibana soit complètement démarré.

---

## 📋 Étape 1 : Créer un Data View

1. **Menu** → **Stack Management** → **Data Views**
2. Cliquer **Create data view**
3. Remplir :
   - **Name** : `Market News`
   - **Index pattern** : `market-news-*`
   - **Timestamp field** : `@timestamp`
4. Cliquer **Save data view to Kibana**

✅ Le Data View est maintenant disponible pour toutes les visualisations.

---

## 📊 Étape 2 : Créer les Visualisations

### 🟢 Visualisation 1 : Évolution du Sentiment dans le Temps

**Type** : **Line chart** (courbe temporelle)

**Basée sur** : Requête 5 (Série temporelle)

**Création** :
1. **Menu** → **Visualize Library** → **Create visualization**
2. Choisir **Lens** (éditeur visuel)
3. Sélectionner le Data View `Market News`
4. Configuration :
   - **Axe X** : `@timestamp` (Date Histogram, intervalle : 1 day)
   - **Axe Y** : `Average of sentiment_score`
   - **Break down by** : `sentiment_label` (optionnel, pour séparer par label)
5. **Save** → Nom : `Sentiment Score Over Time`

**Résultat attendu** : Courbe montrant l'évolution du sentiment moyen par jour.

---

### 🟢 Visualisation 2 : Sentiment Moyen par Source

**Type** : **Horizontal Bar Chart**

**Basée sur** : Requête 2 (Agrégation par source)

**Création** :
1. **Lens** → Nouveau
2. Configuration :
   - **Axe Y (vertical)** : `source` (Top 10 values)
     - ⚠️ Si erreur "field not found", utiliser `source.keyword`
   - **Axe X (horizontal)** : `Average of sentiment_score`
   - **Couleur** : `sentiment_label` (optionnel)
3. **Save** → Nom : `Average Sentiment by Source`

**Résultat attendu** : Barres horizontales comparant le sentiment moyen entre Reuters, Bloomberg, etc.

---

### 🟢 Visualisation 3 : Distribution des Sentiments

**Type** : **Pie Chart** (camembert)

**Basée sur** : Distribution des labels

**Création** :
1. **Lens** → Nouveau
2. Configuration :
   - **Slice by** : `sentiment_label`
   - **Size by** : `Count of records`
3. **Save** → Nom : `Sentiment Distribution (Bullish/Bearish/Neutral)`

**Résultat attendu** : Camembert montrant la proportion d'articles positifs/négatifs/neutres.

---

### 🟢 Visualisation 4 : Top 10 Sources (Volume)

**Type** : **Vertical Bar Chart**

**Basée sur** : Agrégation par source (nombre d'articles)

**Création** :
1. **Lens** → Nouveau
2. Configuration :
   - **Axe X** : `source.keyword` (Top 10)
   - **Axe Y** : `Count of records`
   - **Couleur** : gradient ou fixe
3. **Save** → Nom : `Top Sources by Article Count`

**Résultat attendu** : Histogramme des sources les plus prolifiques.

---

### 🟢 Visualisation 5 : Métriques Clés (KPIs)

**Type** : **Metric** (nombre unique)

**Création** :
1. **Lens** → Nouveau → **Metric**
2. Créer 3 métriques :
   - **Total Articles** : `Count of records`
   - **Average Sentiment** : `Average of sentiment_score`
   - **Sources Count** : `Unique count of source.keyword`
3. **Save** → Nom : `Key Metrics`

**Résultat attendu** : Grands chiffres affichant les métriques globales.

---

### 🟢 Visualisation 6 : Table des Derniers Articles

**Type** : **Data Table**

**Basée sur** : Requête 1 (Recherche textuelle)

**Création** :
1. **Discover** → Sélectionner Data View `Market News`
2. Ajouter les colonnes :
   - `title`
   - `sentiment_label`
   - `sentiment_score`
   - `source`
   - `published_at`
3. **Filtrer** (optionnel) : `sentiment_label: Bullish OR Bearish`
4. **Save** → Nom : `Latest Market News`

**Résultat attendu** : Table interactive des derniers articles.

---

## 📊 Étape 3 : Créer un Dashboard

1. **Menu** → **Dashboard** → **Create dashboard**
2. Cliquer **Add from library**
3. Sélectionner les 6 visualisations créées
4. Organiser la disposition :

```
┌─────────────────────────────────────────────────┐
│  Key Metrics (3 métriques côte à côte)          │
├─────────────────────────────────────────────────┤
│  Sentiment Score Over Time (ligne temporelle)   │
├───────────────────────┬─────────────────────────┤
│  Sentiment Distribution│ Top Sources by Volume  │
│  (Pie Chart)           │ (Bar Chart)            │
├───────────────────────┴─────────────────────────┤
│  Average Sentiment by Source (Horizontal Bars)  │
├─────────────────────────────────────────────────┤
│  Latest Market News (Data Table)                │
└─────────────────────────────────────────────────┘
```

5. **Save** → Nom : `Market News Sentiment Dashboard`

---

## 🔍 Étape 4 : Tester les Requêtes dans Dev Tools

**Menu** → **Dev Tools**

Copier-coller les 5 requêtes depuis [elasticsearch-queries/QUERIES.md](../elasticsearch-queries/QUERIES.md).

**Exemple** :
```json
POST /market-news-*/_search
{
  "query": {
    "match": {
      "title": "Apple Microsoft"
    }
  },
  "size": 5
}
```

Cliquer sur ▶️ pour exécuter.

---

## 📸 Captures d'écran à Faire

Pour le rapport (Partie 4 - 20 pts), capturer :

1. ✅ **Data View** créé (`market-news-*`)
2. ✅ **5 visualisations** individuelles
3. ✅ **Dashboard complet** avec toutes les visualisations
4. ✅ **Dev Tools** avec les 5 requêtes + résultats JSON
5. ✅ **Table "Discover"** montrant les derniers articles

**Format recommandé** : PNG ou JPEG, haute résolution

---

## 🛠️ Filtres et Interactions (Bonus)

### Ajouter un filtre temporel global :
1. Dans le Dashboard, cliquer **Add filter**
2. Choisir `@timestamp` → **Last 7 days**
3. Toutes les visualisations se mettent à jour automatiquement

### Ajouter un filtre par ticker :
1. **Add filter** → `title` : `contains` : `AAPL`
2. Filtrer uniquement les articles mentionnant Apple

### Drill-down :
Cliquer sur une barre/slice → ajoute automatiquement un filtre à tout le dashboard.

---

## 🎨 Personnalisation Avancée

### Changer les couleurs :
- Dans Lens → **Appearance** → Palette de couleurs
- Utiliser des couleurs sémantiques :
  - **Vert** : Bullish (positif)
  - **Rouge** : Bearish (négatif)
  - **Gris** : Neutral

### Ajouter des seuils :
- Dans une visualisation métrique → **Threshold**
- Exemple :
  - `sentiment_score > 0.2` → Vert
  - `sentiment_score < -0.2` → Rouge

---

## ✅ Checklist Partie 4

### Requêtes Elasticsearch (voir QUERIES.md)
- [ ] Requête 1 : Textuelle (match)
- [ ] Requête 2 : Agrégation (avg par source)
- [ ] Requête 3 : N-gram (title.ngram)
- [ ] Requête 4 : Fuzzy (tolérance fautes)
- [ ] Requête 5 : Série temporelle (date_histogram)

### Visualisations Kibana
- [ ] Data View créé
- [ ] Visualisation : Line chart (évolution temporelle)
- [ ] Visualisation : Bar chart (sentiment par source)
- [ ] Visualisation : Pie chart (distribution)
- [ ] Visualisation : Métriques (KPIs)
- [ ] Dashboard complet créé

### Livrables
- [ ] Captures d'écran haute qualité
- [ ] Requêtes JSON copiées dans le rapport
- [ ] Explications des choix de visualisation

---

## 🐛 Dépannage

### ❌ "No matching indices found"
→ Vérifier que des données sont indexées :
```powershell
curl "http://localhost:9201/market-news-*/_count?pretty"
```

### ❌ Kibana n'affiche pas de données
→ Vérifier le **Time Range** (en haut à droite) : mettre **Last 30 days**

### ❌ Champ non disponible pour visualisation
→ Recharger le Data View : **Management** → **Data Views** → **Refresh field list**

---

## 📚 Ressources

- [Kibana Lens Documentation](https://www.elastic.co/guide/en/kibana/current/lens.html)
- [Elasticsearch Query DSL](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl.html)

---

## 🎯 Validation Finale

Ton dashboard est prêt si tu peux répondre à ces questions :

1. ✅ Quelle source de presse a le sentiment le plus positif ?
2. ✅ Combien d'articles Bearish vs Bullish ?
3. ✅ Évolution du sentiment cette semaine : hausse ou baisse ?
4. ✅ Quel ticker (AAPL/MSFT/GOOGL) est le plus mentionné ?

Si oui → **Partie 4 complète !** 🎉
