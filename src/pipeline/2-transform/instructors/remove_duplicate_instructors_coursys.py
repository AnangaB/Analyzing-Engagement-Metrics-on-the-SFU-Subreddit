import sys
import os
import pandas as pd

INPUT_DIR = sys.argv[1]
OUTPUT_DIR = sys.argv[2]

df_3_letter_search_ouput = pd.read_json(
    os.path.join(INPUT_DIR, "instructors_autocomplete_3_letters.json")
)
df_2_letter_search_ouput = pd.read_json(
    os.path.join(INPUT_DIR, "instructors_autocomplete_2_letters.json")
)

df = pd.concat([df_2_letter_search_ouput, df_3_letter_search_ouput])

df = df.drop_duplicates(["value"])
df.columns = ["id", "name"]

df.to_csv(os.path.join(OUTPUT_DIR, "instructors_coursys.csv"), index=False)
