import pandas as pd
import os
import sys

INPUT_DIR = sys.argv[1]
OUTPUT_DIR = sys.argv[2]
  
#relevant_columns = ["Course ID",'Instructor Name', 'Instructor First Name','Instructor Last Name', 'Instructor Common Name', 'Instructor Email']
  
relevant_columns = ["Course ID",'Instructor Name']

raw_instructors = pd.DataFrame(columns=relevant_columns)

for file in os.listdir(INPUT_DIR):
    if file.endswith(".csv"):
        print(file)
        # reading content into data frame
        df_new = pd.read_csv(os.path.join(INPUT_DIR, file))
        raw_instructors = pd.concat(
            [df_new[relevant_columns], raw_instructors]
        )


# clean up some of the instructor names

# remove brackets and words inside brackets
raw_instructors["Instructor Name"] = raw_instructors[
    "Instructor Name"
].str.replace(r"\(.*\)", "", regex=True)

raw_instructors["Instructor Name"] = raw_instructors[
    "Instructor Name"
].str.replace(", Ph.D.", "", regex=False)

# clean up invalid instructor names
invalid_instructor_names = [
    "Faculty",
    ", Dr. TBD",
    ", TBA",
    "- TBA",
    "- Travers",
    "- Travers ",
    ". Faculty",
    ". TBA",
    "Senior Supervisor Faculty",
    ".",
]
for name in invalid_instructor_names:
    raw_instructors["Instructor Name"] = raw_instructors[
        "Instructor Name"
    ].str.replace(name, "", regex=False)

raw_instructors["Instructor Name"] = raw_instructors["Instructor Name"].map(
    lambda s: s.strip()
)
# remove empty names
raw_instructors = raw_instructors[
    (raw_instructors["Instructor Name"] != "")
    | (raw_instructors["Instructor Name"].isna())
]

instructors_df = (
    raw_instructors.groupby(["Instructor Name"])
    .agg({"Course ID": "count"})
    .reset_index()
)

instructors_df.rename(columns={"Course ID": "counts"}, inplace=True)


instructors_df.to_csv(
    os.path.join(OUTPUT_DIR, "unique_instructors_full_name_sfuapi.csv"), index=False
)
