import pandas as pd
import os
import sys

INPUT_FILE = sys.argv[1]
OUTPUT_DIR = sys.argv[2]

instructors_df = pd.read_csv(INPUT_FILE)

instructor_names = instructors_df["Instructor Name"].drop_duplicates()
instructor_names.to_csv(
    os.path.join(OUTPUT_DIR, "keywords_instructor_fullname.csv"),
    header=["keyword"],
    index=False,
)
