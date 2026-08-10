import pandas as pd
import streamlit as st

# Load your data (make sure this matches your actual filename)
df = pd.read_csv("your_archive_data.csv.gz")

st.title("Raidió na Gaeltachta Archive")

# --- Filters Section ---
st.subheader("Filter Archive")

# Separate search boxes
presenter_query = st.text_input("Search by Presenter:")
placename_query = st.text_input("Search by Placename:")

# --- Apply Filters ---
filtered_df = df.copy()

if presenter_query:
    filtered_df = filtered_df[
        filtered_df["Presenter"]
        .astype(str)
        .str.contains(presenter_query, case=False, na=False)
    ]

if placename_query:
    filtered_df = filtered_df[
        filtered_df["Placename"]
        .astype(str)
        .str.contains(placename_query, case=False, na=False)
    ]

# Display the filtered table
st.dataframe(filtered_df)
