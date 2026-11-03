import sys
from pyspark.sql import SparkSession, functions, types
import textstat
from scipy.stats import linregress

spark = SparkSession.builder.appName("Readability").getOrCreate()
spark.sparkContext.setLogLevel("WARN")

assert sys.version_info >= (3, 8)  # make sure we have Python 3.8+
assert spark.version >= "3.2"  # make sure we have Spark 3.2+

MAX_SAMPLE_SIZE=25000

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


def main(reddit_data, column_to_analyze):
    print(f'Analyzing readability score with reddit data column "{column_to_analyze}"')

    submissions = spark.read.json(reddit_data)

    # removing submissions that contain links, as they mess up the readability score
    expression = 'https?://'
    submissions = submissions.filter(~submissions['selftext'].rlike(expression))

    # removing submissions that were deleted, removed, or empty
    submissions = submissions.filter(~((submissions['selftext']=='[deleted]') | (submissions['selftext']=='[removed]') | (submissions['selftext']=='')))

    # metric is Flesch Reading Ease (a score from 121.22 to -inf, where higher score means easier to read)
    # based on the number of sentences, words, and syllables in the text
    flesch_reading_ease_udf = functions.udf(
        lambda x: textstat.flesch_reading_ease(x), returnType=types.FloatType()
    )
    submissions = submissions.withColumn(
        "readability_score", flesch_reading_ease_udf("selftext")
    )


    #submissions.select('selftext','readability_score').filter(submissions['readability_score']<-100).toPandas().to_csv('test.csv')

    submissions = submissions.select(column_to_analyze, 'readability_score')

    submissions_count = submissions.count()
    submissions_sample_fraction = min(submissions_count, MAX_SAMPLE_SIZE) / submissions_count
    submissions = submissions.sample(fraction=submissions_sample_fraction)
    # Note that it is safe to use toPandas() and bring all the data into memory
    # because the amount of data is bounded by the MAX_SAMPLE_SIZE
    submissions = submissions.toPandas()

    fit = linregress(submissions['readability_score'], y=submissions[column_to_analyze])
    print('The p-value is {}'.format(fit.pvalue))

    submissions.to_csv('data/readability_score_'+column_to_analyze+'.csv')
    return

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
