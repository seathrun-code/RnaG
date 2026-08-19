import re
import unicodedata
import pandas as pd
import streamlit as st
from rapidfuzz import process, fuzz

# Set up the page configuration for a wide, clean layout
st.set_page_config(page_title="Cartlann Raidió na Gaeltachta", layout="wide")

# Hide the top-right header menu, including GitHub repo link and Fork button
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
    for col in data.select_dtypes(include=["object"]).columns:
        data[col] = data[col].astype(str).str.strip()
    data = data.rename(columns={"Uimhir Aitheantais": "UID"})
    return data


df = load_data()

# App Header
st.title("Cartlann Raidió na Gaeltachta")
st.subheader("Cuardaigh agus Scag")


def reset_filters():
    st.session_state.search_box = ""
    st.session_state.prog_select = "Gach Clár"
    st.session_state.pres_select = "Gach Láithreoir"
    st.session_state.rannog_select = "Gach Rannóg"


search_query = st.text_input(
    "Cuardach Ginearálta (suaimhneas: \"abairt\", -eisia, +cruinn):",
    key="search_box",
)

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

st.button("Glan Scagairí", on_click=reset_filters)


# --- Advanced Search Logic ---
def strip_accents(text):
    return "".join(
        c
        for c in unicodedata.normalize("NFD", str(text))
        if unicodedata.category(c) != "Mn"
    )


filtered_df = df.copy()

if search_query:
    # 1. Parse advanced syntax tokens
    quoted_phrases = re.findall(r'"([^"]*)"', search_query)
    unquoted_query = re.sub(r'"[^"]*"', "", search_query)

    tokens = unquoted_query.split()
    exclusions = [t[1:] for t in tokens if t.startswith("-")]
    inclusions = [t[1:] for t in tokens if t.startswith("+")]
    normal_tokens = [
        t for t in tokens if not t.startswith("-") and not t.startswith("+")
    ]

    row_texts = filtered_df.astype(str).apply(lambda row: " ".join(row.values), axis=1).tolist()
    choices_clean = [strip_accents(text).lower() for text in row_texts]

    valid_indices = set(range(len(filtered_df)))

    # Apply Exclusions (-)
    for exc in exclusions:
        exc_clean = strip_accents(exc).lower()
        valid_indices = {
            i for i in valid_indices if exc_clean not in choices_clean[i]
        }

    # Apply Quoted Phrases ("...")
    for phrase in quoted_phrases:
        phrase_clean = strip_accents(phrase).lower()
        valid_indices = {
            i for i in valid_indices if phrase_clean in choices_clean[i]
        }

    # Apply Strict Inclusions (+)
    for inc in inclusions:
        inc_clean = strip_accents(inc).lower()
        valid_indices = {
            i for i in valid_indices if inc_clean in choices_clean[i]
        }

    # Apply Normal Tokens (Fuzzy search on remaining subset)
    if normal_tokens:
        normal_query_clean = strip_accents(" ".join(normal_tokens)).lower()
        subset_choices = [choices_clean[i] for i in valid_indices]
        subset_indices = list(valid_indices)

        if subset_choices:
            results = process.extract(
                normal_query_clean,
                subset_choices,
                scorer=fuzz.WRatio,
                limit=None,
                score_cutoff=65,
            )
            valid_indices = {subset_indices[idx] for _, _, idx in results}
        else:
            valid_indices = set()

    filtered_df = filtered_df.iloc[list(valid_indices)]

# Filter by Dropdowns
if selected_prog != "Gach Clár":
    filtered_df = filtered_df[filtered_df["Clár"] == selected_prog]

if selected_presenter != "Gach Láithreoir":
    filtered_df = filtered_df[filtered_df["Láithreoir"] == selected_presenter]

if selected_rannog != "Gach Rannóg":
    filtered_df = filtered_df[filtered_df["Rannóg"] == selected_rannog]

filtered_df = filtered_df.reset_index(drop=True)

# --- Display Results ---
st.write(f"Ag taispeáint {len(filtered_df)} taifead")

event = st.dataframe(
    filtered_df,
    use_container_width=True,
    hide_index=True,
    on_select="rerun",
    selection_mode="single-row",
)

if len(event.selection["rows"]) > 0:
    selected_index = event.selection["rows"][0]
    selected_row = filtered_df.iloc[selected_index]

    with st.expander("Féach ar an Ábhar iomlán:", expanded=True):
        st.write(f"**Clár:** {selected_row['Clár']}")
        st.write(f"**Ábhar:**")
        st.info(selected_row["Ábhar"])
else:
    st.caption("Cliceáil ar líne sa tábla chun an t-ábhar iomlán a fheiceáil.")
