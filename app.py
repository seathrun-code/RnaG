import pandas as pd
import streamlit as st

# Set up the page configuration for a wide, clean layout
st.set_page_config(page_title="Cartlann Raidió na Gaeltachta", layout="wide")


# Load the compressed CSV archive with caching enabled for fast performance
@st.cache_data
def load_data():
    return pd.read_csv("RnG-1.1.csv.gz", encoding="latin1")


# Load the dataframe into memory
df = load_data()

# App Header
st.title("Cartlann Raidió na Gaeltachta")
st.subheader("Cuardaigh agus Scag sa gCartlann")


# --- Callback to Reset Filters ---
def reset_filters():
    st.session_state.search_box = ""
    st.session_state.prog_select = "All"
    st.session_state.pres_select = "All"
    st.session_state.rannog_select = "All"


# --- General Search Box ---
search_query = st.text_input(
    "Cuardach Ginearálta (Cuardaigh trasna láithreoirí, léiritheoirí, cláir, ábhar srl.):",
    key="search_box",
)

# --- Dropdown Filters Setup in Columns ---
col1, col2, col3 = st.columns(3)

with col1:
    programmes = ["All"] + sorted(df["Clár"].dropna().astype(str).unique())
    selected_prog = st.selectbox(
        "Roghnaigh Clár:", programmes, key="prog_select"
    )

with col2:
    presenters = ["All"] + sorted(df["Láithreoir"].dropna().astype(str).unique())
    selected_presenter = st.selectbox(
        "Roghnaigh Láithreoir:", presenters, key="pres_select"
    )

with col3:
    rannoga = ["All"] + sorted(df["Rannóg"].dropna().astype(str).unique())
    selected_rannog = st.selectbox(
        "Roghnaigh Rannóg:", rannoga, key="rannog_select"
    )

# --- Clear Filters Button ---
st.button("Clear Filters", on_click=reset_filters)


# --- Apply Filters Logic ---
filtered_df = df.copy()

# Apply General Search query if text is entered
if search_query:
    mask = (
        filtered_df.astype(str)
        .apply(lambda x: x.str.contains(search_query, case=False, na=False))
        .any(axis=1)
    )
    filtered_df = filtered_df[mask]

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
st.write(f"Showing {len(filtered_df)} records")

# Display the interactive dataframe table
st.dataframe(filtered_df, use_container_width=True)
