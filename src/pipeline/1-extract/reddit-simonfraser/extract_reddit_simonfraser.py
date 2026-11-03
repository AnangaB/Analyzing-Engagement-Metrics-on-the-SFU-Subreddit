# NOTE: THIS IS TO BE RUN ON `cluster.cs.sfu.ca` TO EXTRACT THE "r/simonfraser"
# REDDIT DATA.

# This code was copied and adapted from:
# "https://coursys.sfu.ca/2024su-cmpt-353-d1/pages/RedditData"

import sys
from pyspark.sql import SparkSession, functions, types, Row

spark = SparkSession.builder.appName("erb5 reddit extracter all").getOrCreate()

reddit_submissions_path = "/courses/datasets/reddit_submissions_repartitioned/"
reddit_comments_path = "/courses/datasets/reddit_comments_repartitioned/"
output = "reddit-subset-erb5-all"

comments_schema = types.StructType(
    [
        types.StructField("archived", types.BooleanType()),
        types.StructField("author", types.StringType()),
        types.StructField("author_flair_css_class", types.StringType()),
        types.StructField("author_flair_text", types.StringType()),
        types.StructField("body", types.StringType()),
        types.StructField("controversiality", types.LongType()),
        types.StructField("created_utc", types.StringType()),
        types.StructField("distinguished", types.StringType()),
        types.StructField("downs", types.LongType()),
        types.StructField("edited", types.StringType()),
        types.StructField("gilded", types.LongType()),
        types.StructField("id", types.StringType()),
        types.StructField("link_id", types.StringType()),
        types.StructField("name", types.StringType()),
        types.StructField("parent_id", types.StringType()),
        types.StructField("retrieved_on", types.LongType()),
        types.StructField("score", types.LongType()),
        types.StructField("score_hidden", types.BooleanType()),
        types.StructField("subreddit", types.StringType()),
        types.StructField("subreddit_id", types.StringType()),
        types.StructField("ups", types.LongType()),
        types.StructField("year", types.IntegerType()),
        types.StructField("month", types.IntegerType()),
    ]
)

submissions_schema = types.StructType(
    [
        types.StructField("archived", types.BooleanType()),
        types.StructField("author", types.StringType()),
        types.StructField("author_flair_css_class", types.StringType()),
        types.StructField("author_flair_text", types.StringType()),
        types.StructField("created", types.LongType()),
        types.StructField("created_utc", types.StringType()),
        types.StructField("distinguished", types.StringType()),
        types.StructField("domain", types.StringType()),
        types.StructField("downs", types.LongType()),
        types.StructField("edited", types.BooleanType()),
        types.StructField("from", types.StringType()),
        types.StructField("from_id", types.StringType()),
        types.StructField("from_kind", types.StringType()),
        types.StructField("gilded", types.LongType()),
        types.StructField("hide_score", types.BooleanType()),
        types.StructField("id", types.StringType()),
        types.StructField("is_self", types.BooleanType()),
        types.StructField("link_flair_css_class", types.StringType()),
        types.StructField("link_flair_text", types.StringType()),
        types.StructField("media", types.StringType()),
        types.StructField("name", types.StringType()),
        types.StructField("num_comments", types.LongType()),
        types.StructField("over_18", types.BooleanType()),
        types.StructField("permalink", types.StringType()),
        types.StructField("quarantine", types.BooleanType()),
        types.StructField("retrieved_on", types.LongType()),
        types.StructField("saved", types.BooleanType()),
        types.StructField("score", types.LongType()),
        types.StructField("secure_media", types.StringType()),
        types.StructField("selftext", types.StringType()),
        types.StructField("stickied", types.BooleanType()),
        types.StructField("subreddit", types.StringType()),
        types.StructField("subreddit_id", types.StringType()),
        types.StructField("thumbnail", types.StringType()),
        types.StructField("title", types.StringType()),
        types.StructField("ups", types.LongType()),
        types.StructField("url", types.StringType()),
        types.StructField("year", types.IntegerType()),
        types.StructField("month", types.IntegerType()),
    ]
)


def main():
    reddit_submissions = spark.read.json(
        reddit_submissions_path, schema=submissions_schema
    )
    reddit_comments = spark.read.json(
        reddit_comments_path, schema=comments_schema
    )

    subs = ["simonfraser"]
    subs = list(map(functions.lit, subs))

    reddit_submissions.where(
        reddit_submissions["subreddit"].isin(subs)
    ).write.json(output + "/submissions", mode="overwrite", compression="gzip")
    # .where(reddit_submissions['year'] == 2022) \
    reddit_comments.where(reddit_comments["subreddit"].isin(subs)).write.json(
        output + "/comments", mode="overwrite", compression="gzip"
    )
    # .where(reddit_comments['year'] == 2022) \


main()
