#!/usr/bin/env python3
"""
===========================================
SPARK JOB - Analyse de Sentiments Market News
===========================================
Objectif : Charger les données depuis Elasticsearch et effectuer
des transformations distribuées avec Spark.

Barème Partie 5 (20 pts) :
- Charger les données depuis Elasticsearch
- Appliquer des transformations (calculs, agrégations)
- Exporter les résultats en JSON et CSV

Auteur : M2 DataScale - Université Paris-Saclay
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, avg, count, sum as spark_sum, max as spark_max, 
    min as spark_min, round as spark_round, explode, 
    from_json, to_date, year, month, dayofmonth
)
from pyspark.sql.types import StructType, StructField, StringType, FloatType, ArrayType
import os

# ========================================
# CONFIGURATION
# ========================================

# Elasticsearch (avec fallback pour portabilité)
ES_HOST = os.getenv("ES_HOST", "elasticsearch")  # Nom du conteneur / host (localhost pour Windows)
ES_PORT = os.getenv("ES_PORT", "9200")           # Port interne Docker (9200) ou 9201si sur host
ES_INDEX = "market-news-*"

# Spark Master (cluster Docker ou local[*] pour tests)
SPARK_MASTER = os.getenv("SPARK_MASTER", "local[*]")

# Répertoire de sortie (adapté à ton env : /data ou ./spark-output)
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "spark-output")

# ========================================
# INITIALISATION SPARK
# ========================================

print("=" * 60)
print("📊 SPARK JOB - Analyse de Sentiments Market News")
print("=" * 60)

spark = SparkSession.builder \
    .appName("MarketNewsSentimentAnalysis") \
    .master(SPARK_MASTER) \
    .config("spark.es.nodes", ES_HOST) \
    .config("spark.es.port", ES_PORT) \
    .config("spark.es.nodes.wan.only", "false") \
    .config("spark.es.index.read.missing.as.empty", "true") \
    .config("spark.jars.packages", "org.elasticsearch:elasticsearch-spark-30_2.12:8.12.0") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

print(f"✅ Spark Session créée : {spark.version}")
print(f"🔗 Elasticsearch : {ES_HOST}:{ES_PORT}")
print(f"📂 Index : {ES_INDEX}\n")

# ========================================
# 1. CHARGEMENT DES DONNÉES
# ========================================

print("📥 Chargement des données depuis Elasticsearch...")

df = spark.read \
    .format("org.elasticsearch.spark.sql") \
    .option("es.nodes", ES_HOST) \
    .option("es.port", ES_PORT) \
    .option("es.read.field.as.array.include", "ticker_sentiments") \
    .load(ES_INDEX)

total_count = df.count()
print(f"✅ {total_count} documents chargés\n")

if total_count == 0:
    print("⚠️  AUCUNE DONNÉE TROUVÉE - Vérifier que le producer a envoyé des données")
    spark.stop()
    exit(1)

# Affichage du schéma
print("📋 Schéma des données :")
df.printSchema()

# Aperçu des données
print("\n📄 Aperçu des 3 premiers documents :")
df.select("title", "sentiment_label", "sentiment_score", "source", "published_at").show(3, truncate=False)

# ========================================
# 2. TRANSFORMATIONS ET ANALYSES
# ========================================

print("\n" + "=" * 60)
print("🔬 ANALYSE 1 : Statistiques Globales du Sentiment")
print("=" * 60)

global_stats = df.select(
    count("*").alias("total_articles"),
    spark_round(avg("sentiment_score"), 4).alias("avg_sentiment_score"),
    spark_round(spark_min("sentiment_score"), 4).alias("min_sentiment"),
    spark_round(spark_max("sentiment_score"), 4).alias("max_sentiment")
).collect()[0]

print(f"""
📊 Statistiques Globales :
   - Nombre total d'articles : {global_stats['total_articles']}
   - Score moyen de sentiment : {global_stats['avg_sentiment_score']}
   - Score minimum : {global_stats['min_sentiment']}
   - Score maximum : {global_stats['max_sentiment']}
""")

# Sauvegarde JSON
global_stats_df = df.select(
    count("*").alias("total_articles"),
    spark_round(avg("sentiment_score"), 4).alias("avg_sentiment_score"),
    spark_round(spark_min("sentiment_score"), 4).alias("min_sentiment"),
    spark_round(spark_max("sentiment_score"), 4).alias("max_sentiment")
)

global_stats_df.coalesce(1).write.mode("overwrite").json(f"{OUTPUT_DIR}/global_stats")
print(f"💾 Résultats sauvegardés : {OUTPUT_DIR}/global_stats/")

# ========================================
print("\n" + "=" * 60)
print("🔬 ANALYSE 2 : Sentiment par Source de Presse")
print("=" * 60)

sentiment_by_source = df.groupBy("source") \
    .agg(
        count("*").alias("article_count"),
        spark_round(avg("sentiment_score"), 4).alias("avg_sentiment"),
        spark_round(spark_min("sentiment_score"), 4).alias("min_sentiment"),
        spark_round(spark_max("sentiment_score"), 4).alias("max_sentiment")
    ) \
    .orderBy(col("article_count").desc())

print("📰 Top 10 Sources par nombre d'articles :")
sentiment_by_source.show(10, truncate=False)

# Sauvegarde CSV + JSON
sentiment_by_source.coalesce(1).write.mode("overwrite") \
    .option("header", "true") \
    .csv(f"{OUTPUT_DIR}/sentiment_by_source_csv")

sentiment_by_source.coalesce(1).write.mode("overwrite") \
    .json(f"{OUTPUT_DIR}/sentiment_by_source_json")

print(f"💾 Résultats sauvegardés :")
print(f"   - CSV : {OUTPUT_DIR}/sentiment_by_source_csv/")
print(f"   - JSON : {OUTPUT_DIR}/sentiment_by_source_json/")

# ========================================
print("\n" + "=" * 60)
print("🔬 ANALYSE 3 : Distribution des Labels de Sentiment")
print("=" * 60)

sentiment_distribution = df.groupBy("sentiment_label") \
    .agg(
        count("*").alias("count"),
        spark_round(avg("sentiment_score"), 4).alias("avg_score")
    ) \
    .orderBy(col("count").desc())

print("🏷️  Distribution des sentiments :")
sentiment_distribution.show(truncate=False)

# Sauvegarde
sentiment_distribution.coalesce(1).write.mode("overwrite") \
    .option("header", "true") \
    .csv(f"{OUTPUT_DIR}/sentiment_distribution")

print(f"💾 Résultats sauvegardés : {OUTPUT_DIR}/sentiment_distribution/")

# ========================================
print("\n" + "=" * 60)
print("🔬 ANALYSE 4 : Sentiments par Ticker (AAPL, MSFT, GOOGL)")
print("=" * 60)

# Schéma pour parser ticker_sentiments
ticker_schema = ArrayType(StructType([
    StructField("ticker", StringType(), True),
    StructField("relevance_score", StringType(), True),
    StructField("ticker_sentiment_score", StringType(), True),
    StructField("ticker_sentiment_label", StringType(), True)
]))

# Exploser le tableau ticker_sentiments
df_exploded = df.select(
    "title",
    explode("ticker_sentiments").alias("ticker_data")
).select(
    "title",
    col("ticker_data.ticker").alias("ticker"),
    col("ticker_data.ticker_sentiment_score").cast("float").alias("ticker_sentiment_score"),
    col("ticker_data.ticker_sentiment_label").alias("ticker_sentiment_label"),
    col("ticker_data.relevance_score").cast("float").alias("relevance_score")
)

# Agrégation par ticker
ticker_analysis = df_exploded.groupBy("ticker") \
    .agg(
        count("*").alias("mention_count"),
        spark_round(avg("ticker_sentiment_score"), 4).alias("avg_sentiment"),
        spark_round(avg("relevance_score"), 4).alias("avg_relevance")
    ) \
    .orderBy(col("mention_count").desc())

print("📈 Analyse par Ticker :")
ticker_analysis.show(10, truncate=False)

# Sauvegarde
ticker_analysis.coalesce(1).write.mode("overwrite") \
    .option("header", "true") \
    .csv(f"{OUTPUT_DIR}/ticker_analysis")

print(f"💾 Résultats sauvegardés : {OUTPUT_DIR}/ticker_analysis/")

# ========================================
print("\n" + "=" * 60)
print("🔬 ANALYSE 5 : Articles Positifs vs Négatifs")
print("=" * 60)

positive_news = df.filter(col("sentiment_label") == "Bullish") \
    .select("title", "sentiment_score", "source", "published_at") \
    .orderBy(col("sentiment_score").desc())

negative_news = df.filter(col("sentiment_label") == "Bearish") \
    .select("title", "sentiment_score", "source", "published_at") \
    .orderBy(col("sentiment_score").asc())

print(f"\n📈 Top 5 Articles POSITIFS (Bullish) :")
positive_news.show(5, truncate=False)

print(f"\n📉 Top 5 Articles NÉGATIFS (Bearish) :")
negative_news.show(5, truncate=False)

# Sauvegarde
positive_news.coalesce(1).write.mode("overwrite") \
    .option("header", "true") \
    .csv(f"{OUTPUT_DIR}/positive_news")

negative_news.coalesce(1).write.mode("overwrite") \
    .option("header", "true") \
    .csv(f"{OUTPUT_DIR}/negative_news")

print(f"\n💾 Résultats sauvegardés :")
print(f"   - Positifs : {OUTPUT_DIR}/positive_news/")
print(f"   - Négatifs : {OUTPUT_DIR}/negative_news/")

# ========================================
# RÉCAPITULATIF
# ========================================

print("\n" + "=" * 60)
print("✅ TRAITEMENT SPARK TERMINÉ AVEC SUCCÈS")
print("=" * 60)
print(f"""
📊 Résumé des analyses effectuées :
   1. Statistiques globales du sentiment
   2. Sentiment moyen par source de presse
   3. Distribution des labels de sentiment
   4. Analyse des sentiments par ticker (AAPL, MSFT, GOOGL)
   5. Extraction des articles positifs et négatifs

📁 Tous les résultats sont exportés dans : {OUTPUT_DIR}/

📦 Formats disponibles :
   - JSON (pour réingestion)
   - CSV (pour Excel, Pandas)

🎯 Prochaines étapes :
   - Copier les résultats depuis le conteneur Docker
   - Inclure dans le rapport final
   - Créer les visualisations Kibana (Partie 4)
""")

# Arrêt propre de Spark
spark.stop()
print("🛑 Spark Session fermée\n")
