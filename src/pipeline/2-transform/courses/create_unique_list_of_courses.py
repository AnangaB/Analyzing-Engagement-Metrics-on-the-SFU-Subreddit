import pandas as pd
import os
import sys

INPUT_DIR = sys.argv[1]
OUTPUT_DIR = sys.argv[2]

# store all dfs in
df = pd.DataFrame(columns=["Department", "Course Number", "Course Title"])

for file in os.listdir(INPUT_DIR):
    if file.endswith(".csv"):
        print("getting data from:", file)
        # reading content into data frame
        df_new = pd.read_csv(os.path.join(INPUT_DIR, file))
        df = pd.concat(
            [df_new[["Department", "Course Number", "Course Title"]], df]
        )

# drop grad courses
unique_courses_offerings_df = df[df["Course Number"] < "500"]

# drop duplicate rows
unique_courses_offerings_df = (
    unique_courses_offerings_df.drop_duplicates().dropna(how="all")
)


unique_courses_offerings_df.to_csv(
    os.path.join(OUTPUT_DIR, "unique_courses_offerings.csv"), index=False
)
