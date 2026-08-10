import streamlit as st
import sqlite3
import pandas as pd
import os

st.set_page_config(page_title="RnaG Archive Search", layout="wide")

@st.cache_resource
def init_db():
    conn = sqlite3.connect(':memory:', check_same_thread=False) # In-memory DB is super fast!
    if not os.path.exists('archive.db_built'):
        # Pandas reads .gz files automatically
        df = pd.read_csv('table.csv.gz', compression='gzip', quotechar='"', doublequote=True, low_memory=False, encoding='latin1')
        text_cols = ['Aíonna', 'Ábhar', 'Fo_abhar', 'Chlár', 'Léiritheoir', 'Láithreoir']
        for col in text_cols:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace('\n', ' ', regex=False).str.strip()
        df.to_sql('broadcasts', conn, if_exists='replace', index=False)
    return conn

conn = init_db()

def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        
    if not st.session_state.authenticated:
        st.title("Raidió na Gaeltachta Archive")
        pwd = st.text_input("Enter password to access archive:", type="password")
        if pwd == "giúsach phortaigh":
            st.session_state.authenticated = True
            st.rerun()
        elif pwd:
            st.error("Incorrect password")
        return False
    return True

if check_password():
    st.title("Raidió na Gaeltachta Archive")
    
    search_query = st.text_input("Search keywords (Subject, Guest, Presenter):")
    
    if search_query:
        query = "SELECT * FROM broadcasts WHERE Ábhar LIKE ? OR Aíonna LIKE ? OR Láithreoir LIKE ?"
        params = [f"%{search_query}%", f"%{search_query}%", f"%{search_query}%"]
        df_results = pd.read_sql(query, conn, params=params)
    else:
        df_results = pd.read_sql("SELECT * FROM broadcasts LIMIT 100", conn)
        
    st.write(f"Showing {len(df_results)} results:")
    st.dataframe(df_results, use_container_width=True)
