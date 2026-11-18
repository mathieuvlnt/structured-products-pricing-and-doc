"""Independent brown/taupe UI; no bank affiliation or trademarks."""
import streamlit as st

def apply_theme():
    st.markdown("""<style>
    :root {--brown:#503B32;--taupe:#866C5C;--ivory:#F8F6F3;--ink:#30343A;--line:#DDD2C6;}
    .stApp {background:var(--ivory);color:var(--ink);}
    [data-testid="stSidebar"] {background:#F1ECE6;border-right:1px solid var(--line);}
    [data-testid="stSidebar"] h2,[data-testid="stSidebar"] label {color:var(--brown);}
    .block-container {max-width:1230px;padding-top:6rem !important;padding-bottom:3rem;}
    .desk-kicker {font-size:.72rem;letter-spacing:.16em;color:var(--taupe);font-weight:750;margin-bottom:.3rem;}
    .desk-title {color:var(--brown);font-weight:700;letter-spacing:-.025em;font-size:2.5rem;margin:0;}
    .desk-subtitle {color:#71675F;font-size:.9rem;margin-top:.35rem;}
    .desk-rule {height:4px;background:var(--brown);margin:1.2rem 0 1.8rem;border-radius:2px;}
    .desk-section {color:var(--brown);font-size:.87rem;font-weight:800;letter-spacing:.075em;border-bottom:1px solid var(--line);padding:.6rem 0;margin:1rem 0 1.1rem;}
    div[data-testid="stMetric"] {background:white;border:1px solid var(--line);border-radius:9px;padding:1.1rem;}
    div[data-testid="stMetricLabel"] {color:var(--taupe);}
    div[data-testid="stMetricValue"] {color:var(--brown);}
    .stButton>button[kind="primary"],.stDownloadButton>button {background:var(--brown)!important;color:white!important;border:1px solid var(--brown)!important;border-radius:6px;}
    .stButton>button[kind="primary"]:hover,.stDownloadButton>button:hover {background:#715549!important;color:white!important;}
    div[data-baseweb="select"]>div,div[data-testid="stNumberInput"] input,div[data-testid="stTextInput"] input {border-radius:5px;}
    </style>""",unsafe_allow_html=True)
