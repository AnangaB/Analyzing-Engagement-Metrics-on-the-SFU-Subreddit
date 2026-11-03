import sys
from pyspark.sql import SparkSession, types

spark = SparkSession.builder.appName(
    "Remove Unengaged And Deleted Submissions"
).getOrCreate()
spark.sparkContext.setLogLevel("WARN")

assert sys.version_info >= (3, 8)  # make sure we have Python 3.8+
assert spark.version >= "3.2"  # make sure we have Spark 3.2+

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


def main(input_dir, output_dir):
    submissions = spark.read.json(input_dir)

    # Don't consider posts that were deleted or removed while having no
    # engagement. These posts were likely removed right away by automod, or the
    # OP deleted the post right away before engagement could happen.

    # This could include posts that were deleted by OP much later after being
    # posted and getting no attention. However, that would be harder to detect
    # and a much rarer occurrence. r/simonfraser requires a certain amount of
    # user karma or time passed since accoutn creation before posting. Thus, a
    # lot of these deleted/removed posts are likely from automod removing posts
    # from new accounts created to post to r/simonfraser.

    submissions = submissions.filter(
        ~(
            (submissions["num_comments"] == 0)
            & (submissions["score"] == 1)
            & (
                (submissions["selftext"] == "[deleted]")
                | (submissions["selftext"] == "[removed]")
            )
        )
    )

    submissions.write.json(output_dir, mode="overwrite", compression="gzip")


if __name__ == "__main__":
    INPUT_DIR = sys.argv[1]
    OUTPUT_DIR = sys.argv[2]
    main(INPUT_DIR, OUTPUT_DIR)
