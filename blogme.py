# -*- coding: utf-8 -*-

"""
Created on Sat Nov 11 06:50:57 2023

@author: Malcomb C. Brown

BlogMe Keyword and Sentiment Analysis
"""

# Import Libraries
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


# Reading excel files
raw_df = pd.read_excel("Data/articles.xlsx")

# Inspect the dataset
# raw_df.info()

# Get summary statistics
raw_df.describe()
raw_df.describe(include="O")

# Save a copy of the raw data
data = raw_df.copy()
# data.info()

# How many articles have been written per publisher('source_id')?
data.groupby(by="source_name")["article_id"].count().sort_values(ascending=False)

# How many reactions has each publisher received?
data.groupby(by="source_name")["engagement_reaction_count"].sum()\
    .sort_values(ascending=False)

# Dropping unnecessary column
data.drop(columns=["engagement_comment_plugin_count"], inplace=True)
# data.info()

# keyword = "crash"
# flag_list = []

# for idx, row in data.iterrows():
#     if keyword in str(row.title):
#         flag = 1
#     else:
#         flag = 0
#     flag_list.append(flag)


# Create a function to flag select keywords from column values
def keyword_flag(dataframe: pd.DataFrame, keyword: str, col_name: str) -> pd.DataFrame:
    """
        Takes in a Dataframe, keyword and column name.  The function iterates over the desired
    column of the DataFrame and checks whether or not the keyword is present in each row of the
    column.  If the keyword is present a 1 will be appended to the flags list, otherwise a 0 will
    be appended.
    Returns a list that can be added to the exiting data frame.
    """
    flag_list = []
    df = dataframe.copy()
    for idx, row in df.iterrows():
        try:
            if keyword in row[col_name]:
                flag = 1
            else:
                flag = 0
        except TypeError:
            flag = 0
        finally:
            flag_list.append(flag)
    df[f"{keyword}_{col_name}_flagged"] = flag_list
    return df


data = keyword_flag(dataframe=data, keyword="murder", col_name="title")
# data = keyword_flag(dataframe=data, keyword="murder", col_name="content")
# data.info()


# SentimentIntensityAnalyzer
def sentiment_analyzer(dataframe: pd.DataFrame, col_name: str) -> pd.DataFrame:
    """Takes in a Dataframe and column name and iterates over the desired column of the
    DataFrame and checks whether or not the keyword is present in each row of the column.
    If the keyword is present a 1 will be appended to the flags list, otherwise a 0 will
    be appended.  Returns a list that can be added to the exiting data frame.
    """
    analyzer = SentimentIntensityAnalyzer()
    neg_sent = []
    pos_sent = []
    neu_sent = []
    comp_sent = []
    sent_df = dataframe.copy()
    for idx, row in sent_df.iterrows():
        text = str(row[col_name])
        sent_dict = analyzer.polarity_scores(text)
        neg_sent.append(sent_dict["neg"])
        pos_sent.append(sent_dict["pos"])
        neu_sent.append(sent_dict["neu"])
        comp_sent.append(sent_dict["compound"])

    scores_dict = {"neg": neg_sent, "pos": pos_sent, "neu": neu_sent, "compound": comp_sent}
    score_results = add_scores(scores_dict, sent_df, col_name)
    return score_results


def add_scores(sent_scores: dict, dataframe: pd.DataFrame, column: str) -> pd.DataFrame:
    """Merge sentiment scores into the datafrmae."""
    scores_df = dataframe.copy()
    for key in sent_scores.keys():
        scores_df[f"{column}_{key}_score"] = sent_scores[key]
    return scores_df


# Create sentiment score columns for 'title', 'description', and 'content'
# Add score columns to the dataframe and save the file.
col_list = ["title", "description", "content"]
for col in col_list:
    data = sentiment_analyzer(data, col)

data.info()

# Save the prepared dataset to an Excel workbook.
data.to_excel("Data/Blogme_prepped.xlsx", sheet_name="Prepped Data", index=False)
