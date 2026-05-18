import streamlit as st
from google import genai
from google.genai import types
import os
from pypdf import PdfReader
import glob

# Page configuration
st.set_page_config(page_title="আলা হযরত এআই কিতাবখানা", page_icon="📚", layout="centered")

# ভেক্টরস্টকের সেই মাজার শরীফের ডিরেক্ট ইমেজ লিংক
image_url = "https://images.vectorstock.com/preview-w850/22/21/ala-hazrat-tomb-ahmed-raza-khan-bareilly-vector-27702122.jpg"

# --- CUSTOM CSS FOR FULL LIGHT MODE & ONLINE BACKGROUND IMAGE ---
st.markdown(f"""
    <style>
    html, body, [data-testid="stAppViewContainer"], .stApp {{
        background-color: #FFFFFF !important;
        background-image: linear-gradient(rgba(255, 255, 255, 0.85), rgba(255, 255, 255, 0.85)), 
                          url("{image_url}") !important;
        background-size: auto 65% !important;
        background-position: center 70% !important;
        background-repeat: no-repeat !important;
        background-attachment: fixed !important;
        color: #1A202C !important;
    }}
    .stAppHeader, .stMainBlockContainer, .stBlock, [data-testid="stHeader"], [data-testid="stVerticalBlock"] {{
        background-color: transparent !important;
        background: transparent !important;
    }}
    .main-title {{
        font-size: 2.0rem;
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
        font-family: 'Arial', sans-serif !important;
        font-size: 1.5rem;
        color: #0F4C3A;
        text-align: center !important;
        white-space: normal !important;
        line-height: 1.8;
    }}
    .sidebar-header {{
        font-size: 1.1rem;
        color: #0F4C3A;
        font-weight: bold;
        border-bottom: 2px solid #0F4C3A;
        padding-bottom: 5px;
        margin-bottom: 10px;
    }}
    [data-testid="stChatMessage"] {{
        background-color: rgba(255, 255, 255, 0.9) !important;
        border: 1px solid rgba(15, 76, 58, 0.15) !important;
    }}
    </style>
""", unsafe_allow_html=True)

# App Title & Description
st.markdown('<div class="main-title">📚 ইমাম আহমদ رضا খাঁন আলা হযরত এআই কিতাবখানা</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">আলা হযরতের মোবারক কিতাবসমূহ থেকে সরাসরি বাংলায় সঠিক ও নির্ভরযোগ্য উত্তর পাওয়ার মাধ্যম।</div>', unsafe_allow_html=True)

# --- URDU SHER SECTION (বিশুদ্ধ উর্দু শের) ---
st.markdown("""
    <div class="urdu-sher-container">
        <div class="urdu-text">ملکِ سخن کی شاہی تم کو رضاؔ مسلم<br>جس سمت آ گئے ہو سکے بٹھا دیے ہیں</div>
    </div>
""", unsafe_allow_html=True)

# Fetch API Key from Streamlit Secrets
api_key = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=api_key)

# Function to read ALL PDFs
@st.cache_resource
def load_all_kitabs_text():
    combined_text = ""
    pdf_files = glob.glob("*.pdf") 
    loaded_books = []
    
    if not pdf_files:
        return "কোনো কিতাব ফাইল খুঁজে পাওয়া যায়নি।", []
        
    for file_path in pdf_files:
        try:
            reader = PdfReader(file_path)
            file_name = os.path.basename(file_path)
            loaded_books.append(file_name)
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    combined_text += text + "\n"
        except Exception as e:
            continue
            
    return combined_text, loaded_books

# Load books
kitab_context, available_books = load_all_kitabs_text()

# --- SIDEBAR DESIGN ---
with st.sidebar:
    st.markdown('<div class="sidebar-header">📖 কিতাবখানার বর্তমান কিতাবসমূহ</div>', unsafe_allow_html=True)
    if available_books:
        for book in available_books:
            st.markdown(f"🔹 **{book}**")
    else:
        st.write("❌ কোনো কিতাব পাওয়া যায়নি।")
        
    st.markdown("---")
    st.markdown('<div class="sidebar-header">💡 ব্যবহার বিধি</div>', unsafe_allow_html=True)
    st.info(
        "১. নিচে থাকা চ্যাট বক্সে আপনার প্রশ্নটি বাংলায় লিখুন।\n\n"
        "২. এই এআই শুধুমাত্র ওপরে তালিকাভুক্ত কিতাবসমূহ থেকে উত্তর প্রদান করবে।"
    )
    st.markdown("---")
    st.caption("Developed with ❤️ for Islamic Research")

# --- 🛠️ CHAT INTERFACE WITH ADVANCED MEMORY SYSTEM ---
# ১. চ্যাট হিস্ট্রি সেভ রাখার মেমোরি ব্লক
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# ২. পেজ রিফ্রেশ হলেও আগের মেসেজগুলো স্ক্রিনে ধরে রাখার ব্যবস্থা
for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ৩. নতুন প্রশ্ন ইনপুট নেওয়া
if prompt := st.chat_input("আলা হযরতের কিতাবসমূহ সম্পর্কে যেকোনো প্রশ্ন লিখুন..."):
    
    # প্রশ্নটি স্ক্রিনে দেখানো এবং মেমোরিতে রাখা
    st.session_state["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # এআই-এর কাছ থেকে শক্তিশালী উত্তর নেওয়া
    with st.chat_message("assistant"):
        with st.spinner("কিতাবখানা থেকে উত্তর খোঁজা হচ্ছে..."):
            try:
                # এআই-এর জন্য সর্বোচ্চ শক্তিশালী এবং মনস্তাত্ত্বিক গাইডলাইন
                system_instruction = (
                    "তুমি একজন অত্যন্ত প্রজ্ঞাবান, বিশ্বস্ত এবং কঠোরভাবে সত্যনিষ্ঠ ইসলামিক স্কলার। তোমার কাজ হলো নিচে দেওয়া কিতাবসমূহের তথ্যের ওপর ভিত্তি করে ব্যবহারকারীর প্রশ্নের উত্তর দেওয়া।\n\n"
                    "তোমার চিন্তাভাবনা ও উত্তর দেওয়ার ক্ষেত্রে নিচের শর্তগুলো কঠোরভাবে অনুসরণ করতে হবে:\n"
                    "১. ব্যবহারকারীর প্রশ্নের পেছনের আসল উদ্দেশ্য (Intent) এবং মনের ভাব খুব গভীরভাবে অনুধাবন করার চেষ্টা করো, ঠিক যেভাবে একজন অভিজ্ঞ শিক্ষক তার ছাত্রের মনের কথা বোঝেন।\n"
                    "২. কোনো অবস্থাতেই কোনো মনগড়া, আনুমানিক, কাল্পনিক বা ভুল তথ্য (Misinformation/Hallucination) দেওয়া যাবে না। তথ্যের সত্যতা ও গ্রহণযোগ্যতা বজায় রাখা তোমার প্রধান কর্তব্য।\n"
                    "৩. ব্যবহারকারী কিতাব সংক্রান্ত কোনো মাসআলা বা উদ্ধৃতি জিজ্ঞেস করলেই, কিতাবে থাকা মূল আরবি অথবা উর্দু ইবারত (Original Text) হুবহু তুলে ধরবে।\n"
                    "৪. মূল ইবারতটি দেওয়ার পাশাপাশি তার ঠিক নিচেই সহজ-সরল, স্পষ্ট এবং সাবলীল বাংলা অনুবাদ (Bengali Translation) প্রদান করবে।\n"
                    "৫. যদি কোনো প্রশ্নের উত্তর নিচে দেওয়া কিতাবের মূল তথ্যের মধ্যে না থাকে, তবে কোনো মনগড়া ব্যাখ্যা না দিয়ে অত্যন্ত বিনয়ের সাথে বলবে: 'দুঃখিত, এই তথ্যটি বর্তমান কিতাবসমূহে খুঁজে পাওয়া যায়নি।' বানিয়ে কিছু বলা সম্পূর্ণ নিষিদ্ধ।\n"
                    "
