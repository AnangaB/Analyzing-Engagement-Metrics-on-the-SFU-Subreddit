import pandas as pd
import os
import sys

INPUT_DIR = sys.argv[1]
OUTPUT_DIR = sys.argv[2]

relevant_columns = ["Course ID",'Instructor Last Name']

raw_instructors = pd.DataFrame(columns=relevant_columns)

for file in os.listdir(INPUT_DIR):
    if file.endswith(".csv"):
        print(file)
        # reading content into data frame
        df_new = pd.read_csv(os.path.join(INPUT_DIR, file))
        raw_instructors = pd.concat(
            [df_new[relevant_columns], raw_instructors]
        )


instructors_df = raw_instructors[["Instructor Last Name"]].dropna().drop_duplicates()

# remove brackets and words inside brackets
instructors_df["Instructor Last Name"] = instructors_df[
    "Instructor Last Name"
].str.replace(r"\(.*\)", "", regex=True)

#more clean up
instructors_df["Instructor Last Name"] = instructors_df[
    "Instructor Last Name"
].str.replace(".", "", regex=False)

instructors_df["Instructor Last Name"] = instructors_df[
    "Instructor Last Name"
].str.replace(", Lab Instructor", "", regex=False)

instructors_df["Instructor Last Name"] = instructors_df[
    "Instructor Last Name"
].str.replace("TBA", "", regex=False)

instructors_df["Instructor Last Name"] = instructors_df[
    "Instructor Last Name"
].str.replace("- Teaching Lab/Collection Technician", "", regex=False)

instructors_df["Instructor Last Name"] = instructors_df[
    "Instructor Last Name"
].str.replace(", PhD", "", regex=False)
instructors_df["Instructor Last Name"] = instructors_df[
    "Instructor Last Name"
].str.replace("Sessional Instructor", "", regex=False)

# remove empty names
instructors_df = instructors_df[
    (instructors_df["Instructor Last Name"] != "")
    | (instructors_df["Instructor Last Name"].isna())
]



instructors_df.to_csv(
    os.path.join(OUTPUT_DIR, "unique_instructors_last_name_sfuapi.csv"), index=False
)
