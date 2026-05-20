import streamlit as st
import google.genai as genai
from google.genai import types
from pypdf import PdfReader

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="আলা হযরত এআই কিতাবখানা",
    page_icon="📚",
    layout="centered"
)

# ---------------- CSS FOR ARABIC, URDU & INTERFACE ----------------
# পেজ ফ্রিজিং এড়াতে CSS ডাইনামিক স্ট্রিং ফরম্যাট সম্পূর্ণ ফিক্সড করা হয়েছে
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
جس سمت آ گئے ہو سکے بٹھا دیے ہیں
</div>
</div>
""", unsafe_allow_html=True)

# ---------------- GEMINI TWO-KEY CONFIG ----------------
GEMINI_API_KEYS = [
    "AIzaSyC6vsaAkvRiXBOLiic50Cu9CtURyutJmGQ",
    "AIzaSyCrki8Y2_WcdM5009kxj_iRlhp1JQ4cStA"
]

if "current_key_index" not in st.session_state:
    st.session_state["current_key_index"] = 0

current_index = st.session_state["current_key_index"]
if current_index >= len(GEMINI_API_KEYS):
    current_index = 0
    st.session_state["current_key_index"] = 0

client = genai.Client(api_key=GEMINI_API_KEYS[current_index])

# ---------------- SESSION STATES ----------------
if "messages" not in st.session_state:
    st.session_state["messages"] = []

if "uploaded_file_names" not in st.session_state:
    st.session_state["uploaded_file_names"] = []

if "extracted_books_content" not in st.session_state:
    st.session_state["extracted_books_content"] = ""

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown('<div class="sidebar-header">📖 বর্তমান কিতাবসমূহ</div>', unsafe_allow_html=True)
    if st.session_state["uploaded_file_names"]:
        st.success(f"{len(st.session_state['uploaded_file_names'])} টি কিতাব যুক্ত আছে")
        for book_name in st.session_state["uploaded_file_names"]:
            st.markdown(f"🔹 **{book_name}**")
    else:
        st.error("⚠️ এখনো কোনো কিতাব (PDF) আপলোড করা হয়নি")

    st.markdown("---")
    st.markdown('<div class="sidebar-header">📤 কিতাব Upload করুন (PDF)</div>', unsafe_allow_html=True)
    uploaded_files = st.file_uploader("এখানে PDF ফাইল ড্রপ করুন", type=["pdf"], accept_multiple_files=True)

    if uploaded_files:
        with st.spinner("কিতাব থেকে তথ্য প্রসেস করা হচ্ছে..."):
            for uploaded_file in uploaded_files:
                if uploaded_file.name not in st.session_state["uploaded_file_names"]:
                    try:
                        reader = PdfReader(uploaded_file)
                        text_content = f"\n\n========== কিতাবের নাম: {uploaded_file.name} ==========\n\n"
                        for page in reader.pages:
                            text = page.extract_text()
                            if text:
                                text_content += text + "\n"
                        
                        st.session_state["extracted_books_content"] += text_content
                        st.session_state["uploaded_file_names"].append(uploaded_file.name)
                    except Exception as parse_error:
                        st.error(f"ফাইল পড়তে সমস্যা হয়েছে: {str(parse_error)}")
            st.success("✅ কিতাব সফলভাবে যুক্ত করা হয়েছে!")
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
        st.write(message["content"], unsafe_allow_html=True)

# ---------------- CHAT INPUT & EXECUTION ----------------
if prompt := st.chat_input("কিতাব সম্পর্কে যেকোনো প্রশ্ন বা মাসআলাহ জিজ্ঞেস করুন..."):
    st.session_state["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("কিতাব সার্চ করা হচ্ছে..."):
            try:
                if not st.session_state["extracted_books_content"].strip():
                    st.warning("অনুগ্রহ করে প্রথমে বামপাশের সাইডবার থেকে কিতাব (PDF) আপলোড করুন।")
                else:
                    chat_history = ""
                    for msg in st.session_state["messages"][-4:-1]:
                        role_name = "ইউজার" if msg["role"] == "user" else "সহকারী"
                        chat_history += f"{role_name}: {msg['content']}\n"

                    system_instruction = f"""
                    তুমি একজন অত্যন্ত প্রজ্ঞাবান, নির্ভরযোগ্য এবং গভীর জ্ঞানসম্পন্ন ইসলামিক স্কলার।
                    তোমার মূল কাজ হলো নিচে দেওয়া কিতাবের কন্টেন্ট থেকে ব্যবহারকারীর প্রশ্নের নিখুঁত উত্তর প্রদান করা।
                    
                    চ্যাট ইতিহাস:
                    {chat_history}
                    
                    তোমার কাজ ও কঠোর নির্দেশনা:
                    ১. নিচে 'কিতাবের মূল কন্টেন্ট' সেকশনে যুক্ত করা ডেটা গভীরভাবে বিশ্লেষণ করে শুধু তার ভেতরের সঠিক তথ্যের ওপর ভিত্তি করে উত্তর দেবে। মনগড়া বা বাইরের কোনো তথ্য যোগ করবে না।
                    ২. যদি এই প্রশ্নের সুনির্দিষ্ট উত্তর কিতাবের ভেতর না থাকে, তবে অমূলক উত্তর না দিয়ে স্পষ্ট বলবে: "এই বিষয়ে কিতাবে স্পষ্ট তথ্য পাওয়া যায়নি।"
                    ৩. কোনো আরবি বা উর্দু ইবারত, কোরআনের আয়াত বা হাদিস সরাসরি দেওয়ার সময় বাধ্যতামূলকভাবে এই HTML ফরম্যাটে সাজাবে:
                    <div class='arabic-ur-ibarath'>এখানে শুধু আরবি বা উর্দু টেক্সট লিখবে</div>
                    ４. ইবারতের ঠিক নিচে তার বাংলা অনুবাদ এই ফরম্যাটে দেবে:
                    <div class='bengali-translation'>বাংলা অনুবাদ এখানে লিখবে।</div>
                    ৫. উত্তর সম্পূর্ণ সাবলীল ও স্পষ্ট বাংলা ভাষায় সংক্ষেপে প্রকাশ করবে।
                    """

                    user_payload = f"""
                    {system_instruction}
                    
                    [কিতাবের মূল কন্টেন্ট]:
                    {st.session_state["extracted_books_content"][:60000]}
                    
                    ব্যবহারকারীর বর্তমান প্রশ্ন: {prompt}
                    """
                    
                    config = types.GenerateContentConfig(
                        temperature=0.0
                    )
                    
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=user_payload,
                        config=config
                    )
                    
                    output_text = response.text
                    st.write(output_text, unsafe_allow_html=True)
                    
                    st.session_state["messages"].append({"role": "assistant", "content": output_text})

            except Exception as e:
                error_msg = str(e)
                if any(x in error_msg for x in ["429", "RESOURCE_EXHAUSTED", "403", "PERMISSION_DENIED"]):
                    next_index = st.session_state["current_key_index"] + 1
                    if next_index < len(GEMINI_API_KEYS):
                        st.session_state["current_key_index"] = next_index
                        st.warning("⚠️ বর্তমান ফ্রি এআই সার্ভারের কোটা শেষ হওয়ায় ব্যাকআপ সার্ভারে সুইচ করা হয়েছে। অনুগ্রহ করে আর একবার আপনার প্রশ্নটি সাবমিট করুন।")
                    else:
                        st.session_state["current_key_index"] = 0
                        st.error("❌ দুঃখিত, যুক্ত করা সবকটি এআই কী-এর লিমিট এই মুহূর্তের জন্য শেষ। দয়া করে কিছুক্ষণ পর চেষ্টা করুন।")
                else:
                    st.error(f"দুঃখিত, উত্তর তৈরিতে সাময়িক সমস্যা হয়েছে। এরর: {error_msg}")
