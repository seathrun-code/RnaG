import pandas as pd
import streamlit as st

# Load your data
df = pd.read_csv("your_archive_data.csv.gz")

st.title("Raidió na Gaeltachta Archive")

# --- Filters Section ---
st.subheader("Filter Archive")

# 1. Text search box for presenters
presenter_query = st.text_input("Search by Presenter:")

# 2. Text search box or selectbox for placenames
placename_query = st.text_input("Search by Placename:")

# --- Apply Filters ---
filtered_df = df.copy()

if presenter_query:
  filtered_df = filtered_df[
      filtered_df["Presenter"].str.contains(
          presenter_query, case=False, na=False
      )
  ]

if placename_query:
  filtered_df = filtered_df[
      filtered_df["Placename"].str.contains(
          placename_query, case=False, na=False
      )
  ]

# Display the filtered table
st.dataframe(filtered_df)
