from pyspark.sql import SparkSession
from pyspark.sql import functions as F

spark = (
    SparkSession.builder
    .appName("market news stats")
    .config("spark.sql.session.timeZone", "UTC")
    .getOrCreate()
)

es_nodes = "elasticsearch"
es_port = "9200"

source_index = "market-news-*"
target_index_daily = "market-news-stats-daily"
target_index_source = "market-news-stats-by-source"
target_index_sentiment = "market-news-stats-by-sentiment"

df = (
    spark.read.format("org.elasticsearch.spark.sql")
    .option("es.nodes", es_nodes)
    .option("es.port", es_port)
    .option("es.nodes.wan.only", "true")
    .load(source_index)
)

# Nettoyage minimal
df = df.filter(F.col("published_at").isNotNull())

# 1) Serie temporelle par jour
# FIX: Convertir en string au format YYYY-MM-DD
daily = (
    df.withColumn("day", F.date_format(F.to_date(F.col("published_at")), "yyyy-MM-dd"))
      .groupBy("day")
      .agg(
          F.count("*").alias("doc_count"),
          F.avg(F.col("sentiment_score")).alias("avg_sentiment_score"),
      )
      .orderBy("day")
)

# 2) Stats par source
by_source = (
    df.groupBy("source")
      .agg(
          F.count("*").alias("doc_count"),
          F.avg(F.col("sentiment_score")).alias("avg_sentiment_score"),
      )
      .orderBy(F.desc("doc_count"))
)

# 3) Stats par label de sentiment
by_sentiment = (
    df.groupBy("sentiment_label")
      .agg(
          F.count("*").alias("doc_count"),
          F.avg(F.col("sentiment_score")).alias("avg_sentiment_score"),
      )
      .orderBy(F.desc("doc_count"))
)

def write_to_es(frame, index_name):
    (
        frame.write.format("org.elasticsearch.spark.sql")
        .option("es.nodes", es_nodes)
        .option("es.port", es_port)
        .option("es.nodes.wan.only", "true")
        .option("es.resource", index_name)
        .mode("overwrite")
        .save()
    )

write_to_es(daily, target_index_daily)
write_to_es(by_source, target_index_source)
write_to_es(by_sentiment, target_index_sentiment)

daily.show(20, truncate=False)
by_source.show(20, truncate=False)
by_sentiment.show(20, truncate=False)

spark.stop()