import sys
import os

import pandas as pd
from pyspark.sql import SparkSession, types
import pyspark.sql.functions as F
import matplotlib.pyplot as plt
from scipy import stats
import seaborn

seaborn.set()

spark = SparkSession.builder.appName("Word").getOrCreate()
spark.sparkContext.setLogLevel("WARN")

assert sys.version_info >= (3, 8)  # make sure we have Python 3.8+
assert spark.version >= "3.2"  # make sure we have Spark 3.2+


MAX_SAMPLE_AMOUNT = 25000
KEYWORDS_TO_PLOT = ("ubc",)


def get_sample_fraction(n_rows):
    sample_amount = min(n_rows, MAX_SAMPLE_AMOUNT)
    return sample_amount / n_rows


def plot_histogram(df, column, n_bins):
    # Make a histogram.
    # transformed = without_word.filter(without_word['score'] != 0).select(F.log10(without_word['score']).alias(column_to_analyze))
    histogram = df.rdd.map(lambda row: row[column]).histogram(n_bins)
    # Get histogram x-axis numbers.
    histogram_labels = histogram[0]
    # Don't include last label which is ending label for last bar.
    histogram_start_labels = histogram_labels[:-1]
    # Get histogram y-axis count for each bin.
    histogram_counts = histogram[1]
    # Plot the histogram.
    plt.figure()
    plt.hist(histogram_start_labels, bins=n_bins, weights=histogram_counts)


def save_plot(directory, filename):
    if not os.path.exists(directory):
        os.makedirs(directory)
    plt.savefig(os.path.join(directory, filename))


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


def main(input_keywords, output_keywords, reddit_data, column_to_analyze):
    keywords = pd.read_csv(os.path.join(input_keywords))

    print(f'Analyzing keywords with reddit data column "{column_to_analyze}"')

    submissions = spark.read.json(reddit_data)
    submissions = submissions.select(
        column_to_analyze,
        F.lower("title").alias("title"),
        F.lower("selftext").alias("selftext"),
    )
    submissions.cache()

    def analyze_keyword(row):
        keyword = row["keyword"]
        keyword = keyword.lower()

        print(f'Analyzing keyword "{keyword}"...')

        with_word = submissions.filter(
            submissions["title"].contains(keyword)
            | submissions["selftext"].contains(keyword)
        )
        without_word = submissions.filter(
            ~(
                submissions["title"].contains(keyword)
                | submissions["selftext"].contains(keyword)
            )
        )

        with_word_count = with_word.count()
        without_word_count = without_word.count()

        avg_score_with = -1
        avg_score_without = -1
        pvalue = -1
        pvalue_significant = False
        splits_both_nonempty = False
        with_count_sampled = -1
        without_count_sampled = -1

        if with_word_count != 0 and without_word_count != 0:
            splits_both_nonempty = True

            with_word_sample_fraction = get_sample_fraction(with_word_count)
            without_word_sample_fraction = get_sample_fraction(
                without_word_count
            )

            with_word_sample = with_word.sample(
                fraction=with_word_sample_fraction
            )
            without_word_sample = without_word.sample(
                fraction=without_word_sample_fraction
            )

            with_count_sampled = with_word_sample.count()
            without_count_sampled = without_word_sample.count()

            # .toPandas is safe cause sampled from entire dataset a maximum
            # of MAX_SAMPLE_AMOUNT posts from the with and without partitions,
            # and chose MAX_SAMPLE_AMOUNT to make sure don't run out of
            # memory.
            result = stats.mannwhitneyu(
                with_word_sample.toPandas()[column_to_analyze].values,
                without_word_sample.toPandas()[column_to_analyze].values,
            )

            # Calculate the average score.
            avg_score_with = with_word.summary("mean").collect()[0][
                column_to_analyze
            ]
            avg_score_without = without_word.summary("mean").collect()[0][
                column_to_analyze
            ]

            pvalue = result.pvalue
            pvalue_significant = pvalue < 0.05

            # Make plots. Only do this for certain keywords.
            if keyword in KEYWORDS_TO_PLOT:
                for keyword_split in (
                    (with_word, "With Keyword"),
                    (without_word, "Without Keyword"),
                ):
                    df = keyword_split[0]
                    description = keyword_split[1]
                    filename_description = description.lower().replace(
                        " ", "_"
                    )

                    # Plot data without any transformations.
                    plot_histogram(df, column_to_analyze, 100)
                    plt.title(f'Original {description}: "{keyword}"')
                    plt.xlabel(f"Reddit Post {column_to_analyze.title()}")
                    plt.ylabel(
                        f"Amount Of Reddit Posts With Given {column_to_analyze.title()}"
                    )
                    # Save plot.
                    directory = os.path.join(
                        output_keywords, "plots", column_to_analyze, keyword
                    )
                    filename = f"{filename_description}_original_{keyword}.png"
                    save_plot(directory, filename)

                    # Try transformation to make normal.
                    transformation_funcs = (
                        (F.sqrt, ()),
                        (F.cbrt, ()),
                        (F.log, ()),
                        (F.log10, ()),
                        (F.pow, (-1,)),
                    )
                    for func_data in transformation_funcs:
                        func = func_data[0]
                        args = func_data[1]

                        offset = 0
                        # For pow with exponent -1, need offset = 1 so don't do
                        # 0^-1
                        if func == F.pow:
                            offset = 1

                        plot_histogram(
                            df.select(
                                func(
                                    df[column_to_analyze] + offset, *args
                                ).alias(column_to_analyze)
                            ),
                            column_to_analyze,
                            100,
                        )
                        plt.title(
                            f'{func.__name__} {description}: "{keyword}"'
                        )
                        plt.xlabel(
                            f"Reddit Post {func.__name__}({column_to_analyze.title()}{', -1' if args else ''})"
                        )
                        plt.ylabel(
                            f"Amount Of Reddit Posts With Given {func.__name__}({column_to_analyze.title()})"
                        )
                        # Save plot.
                        directory = os.path.join(
                            output_keywords,
                            "plots",
                            column_to_analyze,
                            keyword,
                        )
                        filename = f"{filename_description}_{func.__name__}_{keyword}.png"
                        save_plot(directory, filename)

        return pd.Series(
            [
                row["keyword"],
                avg_score_with,
                avg_score_without,
                pvalue,
                pvalue_significant,
                splits_both_nonempty,
                with_word_count,
                without_word_count,
                with_count_sampled,
                without_count_sampled,
            ],
            index=[
                "keyword",
                f"avg_{column_to_analyze}_with",
                f"avg_{column_to_analyze}_without",
                "pvalue",
                "pvalue_significant",
                "splits_both_nonempty",
                "with_count",
                "without_count",
                "with_count_sampled",
                "without_count_sampled",
            ],
        )

    keywords = keywords.apply(analyze_keyword, axis=1)

    if not os.path.exists(output_keywords):
        os.makedirs(output_keywords)
    keywords.set_index("keyword").to_csv(
        os.path.join(output_keywords, f"{column_to_analyze}.csv")
    )

    # print(keywords)

    # with_word.show()
    # without_word.show()
    # print("with len:", len(list(with_word.collect())))
    # print("without len:", len(list(without_word.collect())))

    # # Make a histogram.
    # n_bins = 100
    # # transformed = without_word.filter(without_word['score'] != 0).select(F.log10(without_word['score']).alias(column_to_analyze))
    # histogram = with_word.rdd.map(lambda row: row['score']).histogram(n_bins)
    # # Get histogram x-axis numbers.
    # histogram_labels = histogram[0]
    # # Don't include last label which is ending label for last bar.
    # histogram_start_labels = histogram_labels[:-1]
    # # Get histogram y-axis count for each bin.
    # histogram_counts = histogram[1]
    # # Plot the histogram.
    # plt.hist(histogram_start_labels, bins=n_bins, weights=histogram_counts)
    # plt.show()

    # def get_results_with():
    #     a = with_word.select(column_to_analyze).rdd.map(lambda row: row['score']).toLocalIterator()
    #     yield from a
    #
    # def get_results_without():
    #     a = without_word.select(column_to_analyze).rdd.map(lambda row: row['score']).toLocalIterator()
    #     yield from a

    # for a in get_results_with():
    #     print(a)

    # result = stats.mannwhitneyu(
    #     get_results_with(),
    #     get_results_without()
    # )
    # print(with_word.toPandas()['score'].values)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
