import streamlit as st
import requests
from pypdf import PdfReader
import os

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="আলা হযরত এআই কিতাবখানা",
    page_icon="📚",
    layout="centered"
)

# ================= AUTO CREATE BOOKS FOLDER =================
BOOK_FOLDER = "books"

if not os.path.exists(BOOK_FOLDER):
    os.makedirs(BOOK_FOLDER)

# ================= BACKGROUND IMAGE =================
image_url = "https://images.vectorstock.com/preview-w850/22/21/ala-hazrat-tomb-ahmed-raza-khan-bareilly-vector-27702122.jpg"

# ================= CSS =================
st.markdown(f"""
<style>

html, body, [data-testid="stAppViewContainer"], .stApp {{
    background-color: #FFFFFF !important;

    background-image:
    linear-gradient(rgba(255,255,255,0.92), rgba(255,255,255,0.92)),
    url("{image_url}") !important;

    background-size: auto 65% !important;
    background-position: center 70% !important;
    background-repeat: no-repeat !important;
    background-attachment: fixed !important;
}}

.main-title {{
    font-size: 2rem;
    color: #0F4C3A;
    text-align: center;
    font-weight: bold;
    margin-bottom: 5px;
}}

.sub-title {{
    font-size: 1.05rem;
    color: #2D3748;
    text-align: center;
    margin-bottom: 15px;
}}

.urdu-sher-container {{
    background-color: rgba(15, 76, 58, 0.06);
    border: 1px solid rgba(15, 76, 58, 0.2);
    border-left: 5px solid #0F4C3A;
    padding: 18px;
    border-radius: 8px;
    text-align: center;
    margin-bottom: 25px;
}}

.urdu-text {{
    font-size: 1.5rem;
    color: #0F4C3A;
    line-height: 1.8;
    direction: rtl;
}}

.sidebar-header {{
    font-size: 1.1rem;
    color: #0F4C3A;
    font-weight: bold;
    border-bottom: 2px solid #0F4C3A;
    padding-bottom: 5px;
    margin-bottom: 10px;
}}

.arabic-ur-ibarath {{
    direction: rtl !important;
    text-align: right !important;

    font-family:
    'Traditional Arabic',
    'Amiri',
    'Noto Naskh Arabic',
    sans-serif !important;

    font-size: 1.7rem !important;
    line-height: 2.2 !important;

    color: #0F4C3A !important;

    background-color: #F7FAFC !important;

    padding: 15px;
    border-radius: 8px;

    border-right: 5px solid #0F4C3A;

    margin-top: 10px;
    margin-bottom: 10px;
}}

.bengali-translation {{
    font-size: 1.1rem;
    line-height: 1.7;
    color: #2D3748;
    margin-bottom: 15px;
}}

</style>
""", unsafe_allow_html=True)

# ================= TITLE =================
st.markdown(
    '<div class="main-title">📚 ইমাম আহমদ رضا খাঁন আলা হযরত এআই কিতাবখানা</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">কিতাবসমূহ থেকে নির্ভরযোগ্য উত্তর অনুসন্ধান</div>',
    unsafe_allow_html=True
)

# ================= SHER =================
st.markdown("""
<div class="urdu-sher-container">
<div class="urdu-text">
ملکِ سخن کی شاہی تم کو رضاؔ مسلم<br>
جس سمت آ گئے ہو سکے بٹھا دیے ہیں
</div>
</div>
""", unsafe_allow_html=True)

# ================= PDF TEXT EXTRACTION =================
@st.cache_data
def extract_text_from_pdfs():

    full_text = ""

    pdf_
