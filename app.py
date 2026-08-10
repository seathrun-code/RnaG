import pandas as pd
import streamlit as st

# Load with encoding specified to handle Irish fadas safely
@st.cache_data
def load_data():
    return pd.read_csv("table.csv.gz", encoding="latin1")

df = load_data()

st.title("Raidió na Gaeltachta Archive")

# --- Filters Section ---
st.subheader("Filter Archive")

laithreoir_query = st.text_input("Search by Láithreoir (Presenter):")
abhar_query = st.text_input("Search by Ábhar (Subject):")

# --- Apply Filters ---
filtered_df = df.copy()

if laithreoir_query:
    filtered_df = filtered_df[
        filtered_df["Láithreoir"]
        .astype(str)
        .str.contains(laithreoir_query, case=False, na=False)
    ]

if abhar_query:
    filtered_df = filtered_df[
        filtered_df["Ábhar"]
        .astype(str)
        .str.contains(abhar_query, case=False, na=False)
    ]

# Display the filtered table
st.dataframe(filtered_df)
