import streamlit as st
from google import genai
from google.genai import types
import os
from pypdf import PdfReader
import glob

# Page configuration
st.set_page_config(page_title="আলা হযরত এআই কিতাবখানা", page_icon="📚", layout="centered")

# মাজার শরীফের ডিরেক্ট ইমেজ লিংক
image_url = "https://images.vectorstock.com/preview-w850/22/21/ala-hazrat-tomb-ahmed-raza-khan-bareilly-vector-27702122.jpg"

# --- CUSTOM CSS FOR FULL LIGHT MODE, BACKGROUND IMAGE & RTL TEXT ---
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
        direction: rtl !important;
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
    
    /* আরবি ও উর্দু ফন্ট এবং ডান দিক থেকে শুরু করার বিশেষ ব্যবস্থা */
    .arabic-ur-ibarath {{
        direction: rtl !important;
        text-align: right !important;
        font-family: 'Traditional Arabic', 'Amiri', 'Arial', sans-serif !important;
        font-size: 1.45rem !important;
        line-height: 2.0 !important;
        color: #0F4C3A !important;
        background-color: #F7FAFC !important;
        padding: 12px;
        border-radius: 6px;
        border-right: 4px solid #0F4C3A;
        margin-bottom: 10px;
    }}
    .bengali-translation {{
        direction: ltr !important;
        text-align: left !important;
        font-size: 1.05rem !important;
        line-height: 1.6 !important;
        color: #2D3748 !important;
        margin-top: 5px;
        margin-bottom: 15px;
    }}
    </style>
""", unsafe_allow_html=True)

# App Title & Description
st.markdown('<div class="main-title">📚 ইমাম আহমদ رضا খাঁন আলা হযরত এআই কিতাবখানা</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">আলা হযরতের মোবারক কিতাবসমূহ থেকে সরাসরি সঠিক ও নির্ভরযোগ্য উত্তর পাওয়ার মাধ্যম।</div>', unsafe_allow_html=True)

# --- URDU SHER SECTION ---
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

# --- CHAT HISTORY & MEMORY SYSTEM ---
if "messages" not in st.session_state:
    st.session_state["messages"] = []

if "chat_session" not in st.session_state:
    # এআই-কে এইচটিএমএল ফরম্যাটে ইবারত সাজানোর জন্য নির্দেশনা আপগ্রেড করা হয়েছে
    system_instruction = (
        "তুমি একজন অত্যন্ত প্রজ্ঞাবান, বিশ্বস্ত এবং কঠোরভাবে সত্যনিষ্ঠ ইসলামিক স্কলার। তোমার মূল দায়িত্ব হলো নিচে দেওয়া কিতাবসমূহের তথ্যের আলোকে একদম নির্ভুল উত্তর দেওয়া।\n\n"
        "নিচের শর্তগুলো কঠোরভাবে মেনে চলতে হবে:\n"
        "১. ব্যবহারকারীর প্রশ্নের পেছনের আসল উদ্দেশ্য (Intent) এবং মনের ভাব খুব গভীরভাবে অনুধাবন করার চেষ্টা করো।\n"
        "২. কোনো অবস্থাতেই কোনো মনগড়া, আনুমানিক, কাল্পনিক বা ভুল তথ্য (Misinformation/Hallucination) দেওয়া যাবে না।\n"
        "৩. ব্যবহারকারী কিতাব সংক্রান্ত কোনো মাসআলা বা উদ্ধৃতি জিজ্ঞেস করলেই, কিতাবে থাকা মূল আরবি অথবা উর্দু ইবারত (Original Text) অবশ্যই প্রদান করবে।\n"
        "৪. ইবারতটি সুন্দরভাবে দেখানোর জন্য সেটিকে বাধ্যতামূলকভাবে এই HTML ট্যাগের ভেতরে রাখবে: <div class='arabic-ur-ibarath'>মূল আরবি/উর্দু ইবারত এখানে লিখবে</div>। এতে লেখাটি স্বয়ংক্রিয়ভাবে ডান দিক থেকে শুরু হবে।\n"
        "৫. মূল ইবারতের ঠিক নিচেই সহজ-সরল বাংলায় অনুবাদ প্রদান করবে এবং অনুবাদটিকে এই HTML ট্যাগের ভেতরে রাখবে: <div class='bengali-translation'>বাংলা অনুবাদ এখানে লিখবে</div>।\n"
        "৬. যদি কোনো প্রশ্নের উত্তর নিচে দেওয়া কিতাবসমূহের তথ্যের মধ্যে না থাকে, তবে কোনো মনগড়া ব্যাখ্যা না দিয়ে অত্যন্ত বিনয়ের সাথে বলবে: 'দুঃখিত, এই তথ্যটি বর্তমান কিতাবসমূহে খুঁজে পাওয়া যায়নি।'\n"
        "৭. আলা হযরত এবং ধর্মীয় বিষয়ের প্রতি সর্বোচ্চ আদব ও সম্মান বজায় রেখে কথা বলবে।"
    )
    
    st.session_state["chat_session"] = client.chats.create(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction=system_instruction
        )
    )

# আগের কথাগুলো স্ক্রিনে রেন্ডার রাখা
for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.write(message["content"], unsafe_allow_html=True)

# নতুন প্রশ্ন ইনপুট নেওয়া
if prompt := st.chat_input("আলা হযরতের কিতাবসমূহ সম্পর্কে যেকোনো প্রশ্ন লিখুন..."):
    
    st.session_state["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt, unsafe_allow_html=True)

    with st.chat_message("assistant"):
        with st.spinner("কিতাবখানা থেকে উত্তর খোঁজা হচ্ছে..."):
            try:
                full_message = f"কিতাবসমূহের মূল তথ্যভাণ্ডার:\n{kitab_context}\n\nব্যবহারকারীর প্রশ্ন: {prompt}"
                
                response = st.session_state["chat_session"].send_message(full_message)
                
                # স্ক্রিনে উত্তর দেখানো (HTML এলাউ করে, যাতে ডানদিক থেকে ইবারত শুরু হয়)
                st.write(response.text, unsafe_allow_html=True)
                
                st.session_state["messages"].append({"role": "assistant", "content": response.text})
                
            except Exception as e:
                st.error("দুঃখিত, উত্তর তৈরিতে সমস্যা হয়েছে। দয়া করে আবার চেষ্টা করুন।")
