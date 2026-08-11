import pandas as pd
import streamlit as st

# Set up the page configuration for a wide, clean layout
st.set_page_config(page_title="Cartlann Raidió na Gaeltachta", layout="wide")

# Hide the top-right header menu and footer elements
hide_github_style = """
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stAppViewContainer footer {visibility: hidden;}
    div[data-testid="stStatusWidget"] {visibility: hidden;}
    .viewerBadge_container__1QSob {visibility: hidden;}
    </style>
"""
st.markdown(hide_github_style, unsafe_allow_html=True)


# Load the compressed CSV archive and clean up string whitespace
@st.cache_data
def load_data():
    data = pd.read_csv("RnG-1.1.csv.gz", encoding="latin1")
    # Clean whitespace from string columns to prevent mismatch issues
    for col in data.select_dtypes(include=["object"]).columns:
        data[col] = data[col].astype(str).str.strip()
    
    # Rename 'Uimhir Aitheantais' to 'UID' and handle potential truncation/variations safely
    rename_dict = {}
    for col in data.columns:
        if "Uimhir Aitheant" in col or col == "Uimhir Aitheantais":
            rename_dict[col] = "UID"
    data = data.rename(columns=rename_dict)
    
    return data


# Load the dataframe into memory
df = load_data()

# App Header
st.title("Cartlann Raidió na Gaeltachta")
st.subheader("Cuardaigh agus Scag")


# --- Callback to Reset Filters ---
def reset_filters():
    st.session_state.content_search = ""
    st.session_state.prog_search = ""
    st.session_state.prog_select = "Gach Clár"
    st.session_state.pres_select = "Gach Láithreoir"
    st.session_state.rannog_select = "Gach Rannóg"


# --- Targeted Search Inputs in Columns ---
col_search1, col_search2 = st.columns(2)

with col_search1:
    content_query = st.text_input("Cuardaigh san Ábhar:", key="content_search")

with col_search2:
    prog_query = st.text_input("Cuardaigh sa gClár: (m.sh. "Adhmhaidin")", key="prog_search")

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

# Apply Targeted Content Filter
if content_query:
    filtered_df = filtered_df[filtered_df["Ábhar"].str.contains(content_query, case=False, na=False)]

# Apply Targeted Programme Filter
if prog_query:
    filtered_df = filtered_df[filtered_df["Clár"].str.contains(prog_query, case=False, na=False)]

# Filter by Programme
if selected_prog != "Gach Clár":
    filtered_df = filtered_df[filtered_df["Clár"] == selected_prog]

# Filter by Presenter
if selected_presenter != "Gach Láithreoir":
    filtered_df = filtered_df[filtered_df["Láithreoir"] == selected_presenter]

# Filter by Category
if selected_rannog != "Gach Rannóg":
    filtered_df = filtered_df[filtered_df["Rannóg"] == selected_rannog]

# Clean up index mapping for matching selection views
filtered_df = filtered_df.reset_index(drop=True)


# --- Display Results ---
st.write(f"Ag taispeáint {len(filtered_df)} taifead")

# Display the interactive dataframe table with row selection and hidden index
event = st.dataframe(
    filtered_df, 
    use_container_width=True,
    hide_index=True,
    on_select="rerun",
    selection_mode="single-row"
)

# --- Expanded Full Content View ---
if len(event.selection["rows"]) > 0:
    selected_index = event.selection["rows"][0]
    selected_row = filtered_df.iloc[selected_index]
    
    with st.expander("Féach ar an Ábhar iomlán:", expanded=True):
        st.write(f"**Clár:** {selected_row['Clár']}")
        st.write(f"**Ábhar:**")
        st.info(selected_row["Ábhar"])
else:
    st.caption("Cliceáil ar líne sa tábla chun an t-ábhar iomlán a fheiceáil.")
