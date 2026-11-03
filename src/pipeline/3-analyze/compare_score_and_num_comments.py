import pandas as pd
import os
import sys

INPUT_DIR = sys.argv[1]

# store all dfs in
score_df = pd.read_csv(os.path.join(INPUT_DIR,"score_transformed.csv"))
num_comments_df = pd.read_csv(os.path.join(INPUT_DIR,"num_comments_transformed.csv"))

#join the two dfs to commbine
df =  pd.merge(score_df, num_comments_df, on='keyword',  suffixes=('_score', '_comment'))

#score_df.join(num_comments_df, on='keyword', how="left" ,lsuffix='_score', rsuffix='_num_comments')

print("\nKeywords that are significant in both: ")

print((  list(df[((df["pvalue_significant_bonferri_score"] == True) & (df["pvalue_significant_bonferri_comment"] == True) )]["keyword"]))) 


print("\nKeywords that are significant only in one: ")

print((  list(df[((df["pvalue_significant_bonferri_score"] == True) & (df["pvalue_significant_bonferri_comment"] == False) ) | ((df["pvalue_significant_bonferri_score"] == False) & (df["pvalue_significant_bonferri_comment"] == True) )]["keyword"]))) 

print("\nKeywords that are significant only in score: ")

print((  list(df[((df["pvalue_significant_bonferri_score"] == True) & (df["pvalue_significant_bonferri_comment"] == False) )]["keyword"]))) 

print("\nKeywords that are significant only in num_comments: ")

print(list(  df[((df["pvalue_significant_bonferri_score"] == False) & (df["pvalue_significant_bonferri_comment"] == True) )]["keyword"]))

print("\nKeywords that have the lowest pvalues for score: ")

print(list(  score_df.sort_values("pvalue").head(5)["keyword"]))

print("\nKeywords that have the lowest pvalues for num_comments ")

print(list(  num_comments_df.sort_values("pvalue").head(5)["keyword"]))
