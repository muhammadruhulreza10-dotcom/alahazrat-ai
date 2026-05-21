import streamlit as st
import google.genai as genai
from google.genai import types
import pdfplumber

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="আলা হযরত এআই কিতাবখানা",
    page_icon="📚",
    layout="centered"
)

# ---------------- CSS FOR ARABIC, URDU & INTERFACE ----------------
st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"], .stApp {
    background-color: #FFFFFF !important;
    background-image:
    linear-gradient(rgba(255,255,255,0.92), rgba(255,255,255,0.92)),
    url("https://images.vectorstock.com/preview-w850/22/21/ala-hazrat-tomb-ahmed-raza-khan-bareilly-vector-27702122.jpg") !important;
    background-size: auto 65% !important;
    background-position: center 70% !important;
    background-repeat: no-repeat !important;
    background-attachment: fixed !important;
}
.main-title { font-size: 2rem; color: #0F4C3A; text-align: center; font-weight: bold; margin-bottom: 5px; }
.sub-title { font-size: 1.05rem; color: #2D3748; text-align: center; margin-bottom: 15px; }
.urdu-sher-container { background-color: rgba(15, 76, 58, 0.06); border: 1px solid rgba(15, 76, 58, 0.2); border-left: 5px solid #0F4C3A; padding: 18px; border-radius: 8px; text-align: center; margin-bottom: 25px; }
.urdu-text { font-size: 1.5rem; color: #0F4C3A; line-height: 1.8; direction: rtl; }
.sidebar-header { font-size: 1.1rem; color: #0F4C3A; font-weight: bold; border-bottom: 2px solid #0F4C3A; padding-bottom: 5px; margin-bottom: 10px; }
.arabic-ur-ibarath {
    direction: rtl !important;
    text-align: right !important;
    unicode-bidi: bidi-override !important;
    font-family: 'Traditional Arabic', 'Amiri', 'Noto Naskh Arabic', sans-serif !important;
    font-size: 1.9rem !important;
    line-height: 2.5 !important;
    color: #0F4C3A !important;
    background-color: #F7FAFC !important;
    padding: 18px 25px;
    border-radius: 8px;
    border-right: 6px solid #0F4C3A;
    margin-top: 15px;
    margin-bottom: 15px;
}
.bengali-translation { font-size: 1.1rem; line-height: 1.7; color: #2D3748; margin-bottom: 15px; }
</style>
""", unsafe_allow_html=True)

# ---------------- TITLE & SHER ----------------
st.markdown('<div class="main-title">📚 ইমাম আহমদ رضا খাঁন আলা হযরত এআই কিতাবখানা</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Gemini API দ্বারা চালিত কাস্টম কিতাব সার্চ ইঞ্জিন</div>', unsafe_allow_html=True)

st.markdown("""
<div class="urdu-sher-container">
<div class="urdu-text">
ملکِ سخن کی شاہی تم کو رضاؔ مسلم <br>
جس سمت آ گئے ہو سکے بٹھা دیے ہیں
</div>
</div>
""", unsafe_allow_html=True)

# ---------------- GEMINI API KEYS FROM SECRETS ----------------
try:
    GEMINI_API_KEYS = [
        st.secrets["GEMINI_KEY_1"],
        st.secrets["GEMINI_KEY_2"]
    ]
except Exception as config_err:
    st.error("❌ Streamlit Secrets-এ API Key খুঁজে পাওয়া যায়নি! ড্যাশবোর্ডে GEMINI_KEY_1 এবং GEMINI_KEY_2 সেট করুন।")
    st.stop()

# ---------------- SESSION STATES ----------------
if "current_key_index" not in st.session_state:
    st.session_state["current_key_index"] = 0

if "messages" not in st.session_state:
    st.session_state["messages"] = []

if "uploaded_file_names" not in st.session_state:
    st.session_state["uploaded_file_names"] = []

if "extracted_books_content" not in st.session_state:
    st.session_state["extracted_books_content"] = ""

# ---------------- GEMINI CLIENT SETUP ----------------
idx = st.session_state["current_key_index"]
if idx >= len(GEMINI_API_KEYS):
    idx = 0
    st.session_state["current_key_index"] = 0

client = genai.Client(api_key=GEMINI_API_KEYS[idx])

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown('<div class="sidebar-header">📖 বর্তমান কিতাবসমূহ</div>', unsafe_allow_html=True)
    if st.session_state["uploaded_file_names"]:
        st.success(f"{len(st.session_state['uploaded_file_names'])} টি কিতাব যুক্ত আছে")
        for book_name in st.session_state["uploaded_file_names"]:
            st.markdown(f"🔹 **{book_name}**")
    else:
        st.error("⚠️ এখনো কোনো কিতাব (PDF) আপলোড করা হয়নি")

    st.markdown("---")
    st.markdown('<div class="sidebar-header">📤 কিতাব Upload করুন (PDF)</div>', unsafe_allow_html=True)
    uploaded_files = st.file_uploader("এখানে PDF ফাইল ড্রপ করুন", type=["pdf"], accept_multiple_files=True)

    if uploaded_files:
        new_content_added = False
        with st.spinner("কিতাবের পৃষ্ঠা ও ইনডেক্সিং অপ্টিমাইজ করা হচ্ছে..."):
            for uploaded_file in uploaded_files:
                if uploaded_file.name not in st.session_state["uploaded_file_names"]:
                    try:
                        with pdfplumber.open(uploaded_file) as pdf:
                            text_content = f"\n\n[কিতাব শুরু: {uploaded_file.name}]\n\n"
                            # প্রথম ৩০ পৃষ্ঠা সার্চ ফ্রেন্ডলি ফরম্যাটে রিড করা
                            pages_to_read = pdf.pages[:30]
                            for i, page in enumerate(pages_to_read):
                                text = page.extract_text()
                                if text:
                                    # প্রতি পৃষ্ঠার টেক্সটকে আলাদা ও চিহ্নিত রাখা হচ্ছে
                                    text_content += f"\n--- [পৃষ্ঠা নম্বর: {i+1}] ---\n"
                                    text_content += text + "\n"
                        
                        st.session_state["extracted_books_content"] += text_content
                        st.session_state["uploaded_file_names"].append(uploaded_file.name)
                        new_content_added = True
                    except Exception as parse_error:
                        st.error(f"ফাইল পড়তে সমস্যা হয়েছে: {str(parse_error)}")

            if new_content_added:
                st.success("✅ কিতাব সফলভাবে ইনডেক্স করা হয়েছে!")
                st.rerun()

    st.markdown("---")
    if st.button("🗑️ নতুন চ্যাট শুরু করুন", use_container_width=True):
        st.session_state["messages"] = []
        st.session_state["uploaded_file_names"] = []
        st.session_state["extracted_books_content"] = ""
        st.rerun()

# ---------------- DISPLAY OLD CHAT ----------------
for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"], unsafe_allow_html=True)

# ---------------- CHAT INPUT & EXECUTION ----------------
if prompt := st.chat_input("কিতাব সম্পর্কে যেকোনো প্রশ্ন বা মাসআলাহ জিজ্ঞেস করুন..."):
    st.session_state["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if not st.session_state["extracted_books_content"].strip():
            st.warning("অনুগ্রহ করে প্রথমে বামপাশের সাইডবার থেকে কিতাব (PDF) আপলোড করুন।")
        else:
            with st.spinner("কিতাবের নির্দিষ্ট পৃষ্ঠা স্ক্যান করা হচ্ছে..."):
                try:
                    chat_history = ""
                    for msg in st.session_state["messages"][-4:-1]:
                        role_name = "ইউজার" if msg["role"] == "user" else "সহকারী"
                        chat_history += f"{role_name}: {msg['content']}\n"

                    system_instruction = (
                        "তুমি একজন অত্যন্ত দ্রুত এবং প্রজ্ঞাবান ইসলামিক স্কলার এআই।\n"
                        "তোমার প্রধান কাজ হলো নিচে দেওয়া 'কিতাবের মূল কন্টেন্ট'-এর ভেতরের পৃষ্ঠা নম্বরগুলো দ্রুত স্ক্যান করে ব্যবহারকারীর সুনির্দিষ্ট উত্তরটি বের করা।\n\n"
                        f"[পূর্ববর্তী চ্যাট ইতিহাস]\n{chat_history}\n\n"
                        "কঠোর নিয়মাবলী:\n"
                        "১. নিচে সরবরাহ করা কিতাবের নির্দিষ্ট পৃষ্ঠার ডেটা বিশ্লেষণ করে শুধু সঠিক ও প্রাসঙ্গিক উত্তরটি সংক্ষেপে প্রদান করবে। অলীক বা বাইরের কোনো তথ্য বানিয়ে লিখবে না।\n"
                        "২. যদি প্রশ্নের সুনির্দিষ্ট উত্তর কিতাবের পৃষ্ঠাগুলোতে না থাকে, তবে অযথা সময় নষ্ট না করে সরাসরি বলবে: 'এই বিষয়ে কিতাবে স্পষ্ট তথ্য পাওয়া যায়নি।'\n"
                        "৩. কোনো আরবি বা উর্দু ইবারত দেওয়ার সময় বাধ্যতামূলকভাবে এই HTML ফরম্যাটে সাজাবে:\n"
                        "<div class='arabic-ur-ibarath'>আরবি/উর্দু টেক্সট</div>\n"
                        "৪. ইবারতের নিচে বাংলা অনুবাদ এই ফরম্যাটে দেবে:\n"
                        "<div class='bengali-translation'>বাংলা অনুবাদ</div>\n"
                        "৫. উত্তর সম্পূর্ণ সাবলীল ও স্পষ্ট বাংলা ভাষায় দেবে।"
                    )

                    # এআই যেন দ্রুত খুঁজতে পারে তাই ২৫,০০০ ক্যারেক্টার ইনডেক্সড ডেটা পাঠানো হচ্ছে
                    user_payload = (
                        "[কিতাবের মূল কন্টেন্ট (পৃষ্ঠা নম্বরসহ)]:\n"
                        f"{st.session_state['extracted_books_content'][:25000]}\n\n"
                        f"ব্যবহারকারীর বর্তমান প্রশ্ন: {prompt}"
                    )

                    config = types.GenerateContentConfig(
                        temperature=0.0,
                        system_instruction=system_instruction
                    )

                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=user_payload,
                        config=config
                    )

                    output_text = response.text if response.text else "দুঃখিত, কোনো উত্তর জেনারেট করা সম্ভব হয়নি।"

                    st.markdown(output_text, unsafe_allow_html=True)
                    st.session_state["messages"].append({"role": "assistant", "content": output_text})

                except Exception as e:
                    error_msg = str(e)
                    if any(x in error_msg.lower() for x in ["429", "resource_exhausted", "403", "permission_denied", "quota", "503", "unavailable"]):
                        next_index = st.session_state["current_key_index"] + 1
                        if next_index < len(GEMINI_API_KEYS):
                            st.session_state["current_key_index"] = next_index
                            st.warning("⚠️ সার্ভারে লোড বেশি থাকায় ব্যাকআপ এআই সার্ভারে সুইচ করা হয়েছে। অনুগ্রহ করে আর একবার প্রশ্নটি সাবমিট করুন।")
                        else:
                            st.session_state["current_key_index"] = 0
                            st.error("❌ সকল API Key-এর লিমিট এই মুহূর্তের জন্য শেষ। দয়া করে ৫ মিনিট পর চেষ্টা করুন।")
                    else:
                        st.error(f"❌ সমস্যা হয়েছে: {error_msg}")
