import pandas as pd
import streamlit as st

# Set up the page configuration for a clean layout
st.set_page_config(
    page_title="Raidió na Gaeltachta Archive", layout="wide"
)


# Load the compressed CSV archive with caching enabled for fast performance
@st.cache_data
def load_data():
    return pd.read_csv("RnG-1.1.csv.gz", encoding="latin1")


# Load the dataframe into memory
df = load_data()

# App Header
st.title("Raidió na Gaeltachta Archive")
st.subheader("Filter Archive")

# --- Dropdown Filters Setup ---
# 1. Programme (Clár) filter dropdown
programmes = ["All"] + sorted(df["Clár"].dropna().astype(str).unique())
selected_prog = st.selectbox("Select Clár (Programme):", programmes)

# 2. Presenter (Láithreoir) filter dropdown
presenters = ["All"] + sorted(df["Láithreoir"].dropna().astype(str).unique())
selected_presenter = st.selectbox("Select Láithreoir (Presenter):", presenters)

# 3. Category (Rannóg) filter dropdown
rannoga = ["All"] + sorted(df["Rannóg"].dropna().astype(str).unique())
selected_rannog = st.selectbox("Select Rannóg (Category):", rannoga)


# --- Apply Filters Logic ---
filtered_df = df.copy()

# Filter by Programme if a specific one is chosen
if selected_prog != "All":
    filtered_df = filtered_df[filtered_df["Clár"].astype(str) == selected_prog]

# Filter by Presenter if a specific one is chosen
if selected_presenter != "All":
    filtered_df = filtered_df[
        filtered_df["Láithreoir"].astype(str) == selected_presenter
    ]

# Filter by Category if a specific one is chosen
if selected_rannog != "All":
    filtered_df = filtered_df[filtered_df["Rannóg"].astype(str) == selected_rannog]


# --- Display Results ---
# Show how many records match the current filter selection
st.write(f"Showing {len(filtered_df)} records")

# Display the interactive dataframe table
st.dataframe(filtered_df, use_container_width=True)
