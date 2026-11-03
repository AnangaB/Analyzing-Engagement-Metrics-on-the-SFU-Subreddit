import pandas as pd

relevant_columns = [
    "Department",
    "Course Number",
    "Instructor Name",
    "Instructor First Name",
    "Instructor Last Name",
    "Instructor Common Name",
    "Instructor Email",
    "Course Section",
]

raw_courses = pd.DataFrame(columns=relevant_columns)

for file in os.listdir(INPUT_DIR):
    if file.endswith(".csv"):
        print(file)
        # reading content into data frame
        df_new = pd.read_csv(os.path.join(INPUT_DIR, file))
        raw_courses = pd.concat([df_new[relevant_columns], raw_courses])


# df contains instructors and a count of each courses they have taught
instructors_and_courses_taught_df = (
    raw_courses.drop_duplicates()
    .dropna()
    .groupby(
        [
            "Department",
            "Course Number",
            "Instructor Name",
            "Instructor First Name",
            "Instructor Last Name",
            "Instructor Common Name",
            "Instructor Email",
        ]
    )
    .count()
    .reset_index()
)

instructors_and_courses_taught_df.to_csv(
    os.path.join(OUTPUT_DIR, "instructors_and_courses_taught.csv"), index=False
)
