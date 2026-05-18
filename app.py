import streamlit as st
from google import genai
from google.genai import types
import os
from pypdf import PdfReader
import glob
import base64

# Page configuration
st.set_page_config(page_title="আলা হযরত এআই কিতাবখানা", page_icon="📚", layout="centered")

# --- FUNCTION TO CONVERT LOCAL IMAGE TO BASE64 ---
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None

# আপনার আপলোড করা ছবির নাম (নিশ্চিত করুন গিটহাবে ফাইলটির নাম "12375.png" আছে)
image_file = "12375.png" 
img_base64 = get_base64_image(image_file)

# --- CUSTOM CSS FOR FULL LIGHT MODE & VISIBLE BACKGROUND ---
st.markdown("""
    <style>
    /* ১. পুরো অ্যাপের ব্যাকগ্রাউন্ড কালার জোরপূর্বক সাদা করা */
    html, body, [data-testid="stAppViewContainer"], .stApp {
        background-color: #FFFFFF !important;
        background: #FFFFFF !important;
        color: #1A202C !important;
    }
    
    /* ২. স্ট্রিমলিটের অন্যান্য কালো বা ধূসর ব্লকগুলো সম্পূর্ণ সাদা/স্বচ্ছ করা */
    .stAppHeader, .stMainBlockContainer, .stBlock, [data-testid="stHeader"], [data-testid="stVerticalBlock"] {
        background-color: transparent !important;
        background: transparent !important;
    }
    </style>
""", unsafe_allow_html=True)

if img_base64:
    st.markdown(f"""
        <style>
        /* ৩. ব্যাকগ্রাউন্ডে মাজার শরীফের ছবি দৃশ্যমান জলছাপ (Watermark) হিসেবে সেট করা */
        .stApp {{
            background-image: linear-gradient(rgba(255, 255, 255, 0.82), rgba(255, 255, 255, 0.82)), 
                              url("data:image/png;base64,{img_base64}") !important;
            background-size: auto 60% !important;
            background-position: center 65% !important;
            background-repeat: no-repeat !important;
            background-attachment: fixed !important;
        }}
        </style>
    """, unsafe_allow_html=True)

st.markdown("""
    <style>
    /* ৪. টাইপোগ্রাফি ও টেক্সট স্টাইল (মোবাইলে উর্দু ভাঙা রোধ করার জন্য স্ট্যান্ডার্ড ফন্ট) */
    .main-title {
        font-size: 2.0rem;
        color: #0F4C3A;
        text-align: center;
        font-weight: bold;
        margin-bottom: 5px;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #2D3748;
        text-align: center;
        margin-bottom: 15px;
    }
    .urdu-sher-container {
        background-color: rgba(15, 76, 58,
