import pandas as pd
import streamlit as st


@st.cache_data
def load_data():
  return pd.read_csv("table.csv.gz", encoding="latin1")


df = load_data()

st.title("Raidió na Gaeltachta Archive")
st.subheader("Filter Archive")

# --- Dropdown Filters ---
# Get unique presenter names, clean them up, and add an "All" option
presenters = ["All"] + sorted(df["Láithreoir"].dropna().astype(str).unique())
selected_presenter = st.selectbox("Select Láithreoir (Presenter):", presenters)

# Get unique subject names and add an "All" option
abhair = ["All"] + sorted(df["Ábhar"].dropna().astype(str).unique())
selected_abhar = st.selectbox("Select Ábhar (Subject):", abhair)

# --- Apply Filters ---
filtered_df = df.copy()

if selected_presenter != "All":
  filtered_df = filtered_df[
      filtered_df["Láithreoir"].astype(str) == selected_presenter
  ]

if selected_abhar != "All":
  filtered_df = filtered_df[filtered_df["Ábhar"].astype(str) == selected_abhar]

# Display the filtered table
st.dataframe(filtered_df)
