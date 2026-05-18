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

# Load your uploaded image 
image_file = "12375.png"
img_base64 = get_base64_image(image_file)

# --- CUSTOM CSS FOR DESIGN & BACKGROUND ---
if img_base64:
    st.markdown(f"""
        <style>
        .stApp {{
            background-image: linear-gradient(rgba(255, 255, 255, 0.94), rgba(255, 255, 255, 0.94)), 
                              url("data:image/png;base64,{img_base64}");
            background-size: auto 55%;
            background-position: center 65%;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        </style>
    """, unsafe_allow_html=True)

st.markdown("""
    <style>
    .main-title {
        font-size: 2.2rem;
        color: #0F4C3A;
        text-align: center;
        font-weight: bold;
        margin-bottom: 5px;
    }
    .sub-title {
        font-size: 1.1rem;
        color: #2D3748;
        text-align: center;
        margin-bottom: 15px;
    }
    .urdu-sher-container {
        background-color: rgba(15, 76, 58, 0.08);
        border-left: 4px solid #0F4C3A;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
        margin-bottom: 25px;
    }
    .urdu-text {
        font-family: 'Urdu Typesetting', 'Nastaliq', serif;
        font-size: 1.6rem;
        color: #0F4C3A;
        direction: rtl;
        margin-bottom: 5px;
        font-weight: bold;
        line-height: 1.6;
    }
    .bangla-translation {
        font-size: 0.95rem;
        color: #4A5568;
        font-style: italic;
    }
    .sidebar-header {
        font-size: 1.2rem;
        color: #0F4C3A;
        font-weight: bold;
        border-bottom: 2px solid #0F4C3A;
        padding-bottom: 5px;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# App Title & Description (সব জায়গায় unsafe_allow_html=True নিশ্চিত করা হয়েছে)
st.markdown('<div class="main-title">📚 ইমাম আহমদ رضا খাঁন আলা হযরত এআই কিতাবখানা</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">আলা হযরতের মোবারক কিতাবসমূহ থেকে সরাসরি বাংলায় সঠিক ও নির্ভরযোগ্য উত্তর পাওয়ার মাধ্যম।</div>', unsafe_allow_html=True)

# --- URDU SHER SECTION ---
st.markdown("""
    <div class="urdu-sher-container">
        <div class="urdu-text">مُلکِ سُخَن کی شاہی تم کو رضاؔ مُسلَّم<br>جس سَمْت آ گئے ہو سِکّے بٹھا دیے ہیں</div>
        <div class="bangla-translation">কাব্যের জগতের রাজত্ব আপনারই হে رضا (রেজা), তা সর্বজনস্বীকৃত<br>যেদিকেই আপনি গিয়েছেন, নিজের বিজয়পতাকা উড়িয়ে দিয়েছেন।</div>
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

# --- CHAT INTERFACE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if prompt := st.chat_input("আলা হযরতের কিতাবসমূহ সম্পর্কে যেকোনো প্রশ্ন লিখুন..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("কিতাবখানা থেকে উত্তর খোঁজা হচ্ছে..."):
            try:
                full_prompt = (
                    f"তুমি একজন বিশিষ্ট ইসলামিক স্কলার। নিচে দেওয়া কিতাবসমূহের তথ্যের আলোকে ব্যবহারকারীর প্রশ্নের উত্তর দাও।\n"
                    f"১. উত্তরটি অবশ্যই অত্যন্ত আদব ও সম্মানের সাথে প্রদান করবে।\n"
                    f"২. কিতাবের তথ্যের বাইরে থেকে নিজের মতো কোনো উত্তর বানিয়ে দেবে না।\n"
                    f"৩. উত্তরটি সহজ- সরল বাংলায় উপস্থাপন করো।\n\n"
                    f"কিতাবসমূহের তথ্য:\n{kitab_context}\n\n"
                    f"ব্যবহারকারীর প্রশ্ন: {prompt}"
                )
                
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=full_prompt,
                )
                st.write(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error("দুঃখিত, উত্তর তৈরিতে সমস্যা হয়েছে। দয়া করে আবার চেষ্টা করুন।")
