import pandas as pd
import os
import sys

INPUT_FILE = sys.argv[1]
OUTPUT_DIR = sys.argv[2]

courses_df = pd.read_csv(INPUT_FILE)

courses_df["keyword"] = (
    courses_df["Department"] + " " + courses_df["Course Number"]
)

courses_df = courses_df["keyword"].drop_duplicates()
courses_df.to_csv(
    os.path.join(OUTPUT_DIR, "keywords_courses.csv"), index=False
)
