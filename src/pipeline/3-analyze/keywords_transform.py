import pandas as pd
import os
import sys

INPUT_DIR = sys.argv[1]
ANALYSIS_TYPE = sys.argv[2]

# store all dfs in
df = pd.read_csv(os.path.join(INPUT_DIR,f"{ANALYSIS_TYPE}.csv"))


n = len(df)
new_pvalue = 0.05/n
#only keep nonempty valid partions
df = df[df["splits_both_nonempty"] == True]

#with_count_sampled >= 10
df = df[df["with_count_sampled"] >= 10]

#bonferri correction
df["pvalue_significant_bonferri"] = df["pvalue"] < new_pvalue

#add new column: ration of avg_score
new_col_name = f"{ANALYSIS_TYPE}_ratio"
avg_col_name_with = f"avg_{ANALYSIS_TYPE}_with"
avg_col_name_without = f"avg_{ANALYSIS_TYPE}_without"



df[new_col_name] = df[avg_col_name_with]/df[avg_col_name_without]


#sort by lowest to highest pvalue
df = df.sort_values(["pvalue_significant_bonferri", new_col_name], ascending=False)

df.to_csv(
    os.path.join(INPUT_DIR,f"{ANALYSIS_TYPE}_transformed.csv"), index=False
)
