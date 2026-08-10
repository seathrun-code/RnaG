import pandas as pd
import streamlit as st

# Set up the page configuration for a wide, clean layout
st.set_page_config(page_title="Cartlann Raidió na Gaeltachta", layout="wide")


# Load the compressed CSV archive and clean up string whitespace
@st.cache_data
def load_data():
    data = pd.read_csv("RnG-1.1.csv.gz", encoding="latin1")
    # Clean whitespace from string columns to prevent mismatch issues
    for col in data.select_dtypes(include=["object"]).columns:
        data[col] = data[col].astype(str).str.strip()
    return data


# Load the dataframe into memory
df = load_data()

# App Header
st.title("Cartlann Raidió na Gaeltachta")
st.subheader("Cuardaigh agus Scag")


# --- Callback to Reset Filters ---
def reset_filters():
    st.session_state.search_box = ""
    st.session_state.prog_select = "Gach Clár"
    st.session_state.pres_select = "Gach Láithreoir"
    st.session_state.rannog_select = "Gach Rannóg"


# --- General Search Box ---
search_query = st.text_input(
    "Cuardach Ginearálta:",
    key="search_box",
)

# --- Dropdown Filters Setup in Columns ---
col1, col2, col3 = st.columns(3)

with col1:
    programmes = ["Gach Clár"] + sorted(
        [str(x) for x in df["Clár"].dropna().unique() if x != "nan"]
    )
    selected_prog = st.selectbox(
        "Roghnaigh Clár:", programmes, key="prog_select"
    )

with col2:
    presenters = ["Gach Láithreoir"] + sorted(
        [str(x) for x in df["Láithreoir"].dropna().unique() if x != "nan"]
    )
    selected_presenter = st.selectbox(
        "Roghnaigh Láithreoir:", presenters, key="pres_select"
    )

with col3:
    rannoga = ["Gach Rannóg"] + sorted(
        [str(x) for x in df["Rannóg"].dropna().unique() if x != "nan"]
    )
    selected_rannog = st.selectbox(
        "Roghnaigh Rannóg:", rannoga, key="rannog_select"
    )

# --- Clear Filters Button ---
st.button("Glan Scagairí", on_click=reset_filters)


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

# Filter by Programme
if selected_prog != "Gach Clár":
    filtered_df = filtered_df[filtered_df["Clár"] == selected_prog]

# Filter by Presenter
if selected_presenter != "Gach Láithreoir":
    filtered_df = filtered_df[filtered_df["Láithreoir"] == selected_presenter]

# Filter by Category
if selected_rannog != "Gach Rannóg":
    filtered_df = filtered_df[filtered_df["Rannóg"] == selected_rannog]


# --- Display Results ---
st.write(f"Ag taispeáint {len(filtered_df)} taifead")

# Display the interactive dataframe table
st.dataframe(filtered_df, use_container_width=True)
