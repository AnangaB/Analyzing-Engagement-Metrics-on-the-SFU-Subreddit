import sys
from pyspark.sql import SparkSession, functions, types
import textstat
import pandas as pd
from scipy.stats import linregress
import matplotlib.pyplot as plt
import seaborn
seaborn.set_theme()

spark = SparkSession.builder.appName("first Spark app").getOrCreate()
spark.sparkContext.setLogLevel("WARN")

assert sys.version_info >= (3, 8)  # make sure we have Python 3.8+
assert spark.version >= "3.2"  # make sure we have Spark 3.2+


def main(column_name):
    # Note that it is safe to use Pandas here because the amount of data was limited
    # by MAX_SAMPLE_SCORE in readability.py, which generated the file being read
    submissions = pd.read_csv('data/readability_score_'+column_name+'.csv')

    fit = linregress(submissions['readability_score'], y=submissions[column_name])
    plt.scatter(submissions['readability_score'], submissions[column_name], s=10)
    plt.plot(submissions['readability_score'], submissions['readability_score']*fit.slope + fit.intercept, 'r')
    plt.xlabel('Readability Score')
    plt.ylabel(column_name.title())
    plt.title('Best Fit Line')
    plt.savefig('data/pipeline/4-plot/readability_score_'+column_name+'.png')

    return


if __name__ == "__main__":
    main(sys.argv[1])