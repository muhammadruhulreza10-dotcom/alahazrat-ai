import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="আলা হযরত এআই কিতাবখানা",
    page_icon="📚",
    layout="centered"
)

# ---------------- CSS ----------------
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

# ---------------- GEMINI API KEYS ----------------
GEMINI_API_KEYS = [
    "AIzaSyC6vsaAkvRiXBOLiic50Cu9CtURyutJmGQ",
    "AIzaSyCrki8Y2_WcdM5009kxj_iRlhp1JQ4cStA"
]

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
def get_gemini_model():
    idx = st.session_state["current_key_index"]
    if idx >= len(GEMINI_API_KEYS):
        idx = 0
        st.session_state["current_key_index"] = 0
    genai.configure(api_key=GEMINI_API_KEYS[idx])
    return genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=genai.GenerationConfig(temperature=0.0)
    )

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
    uploaded_files = st.file_uploader(
        "এখানে PDF ফাইল ড্রপ করুন",
        type=["pdf"],
        accept_multiple_files=True
    )

    if uploaded_files:
        new_content_added = False
        with st.spinner("কিতাব থেকে তথ্য প্রসেস করা হচ্ছে..."):
            for uploaded_file in uploaded_files:
                if uploaded_file.name not in st.session_state["uploaded_file_names"]:
                    try:
                        reader = PdfReader(uploaded_file)
                        text_content = f"\n\n========== কিতাবের নাম: {uploaded_file.name} ==========\n\n"
                        pages_to_read = reader.pages[:30]
                        for page in pages_to_read:
                            text = page.extract_text()
                            if text:
                                cleaned_page_text = " ".join(text.split())
                                text_content += cleaned_page_text + "\n"
                        st.session_state["extracted_books_content"] += text_content
                        st.session_state["uploaded_file_names"].append(uploaded_file.name)
                        new_content_added = True
                    except Exception as parse_error:
                        st.error(f"ফাইল পড়তে সমস্যা হয়েছে: {str(parse_error)}")

            if new_content_added:
                st.success("✅ কিতাব সফলভাবে যুক্ত করা হয়েছে!")
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
            with st.spinner("কিতাব সার্চ করা হচ্ছে..."):
                try:
                    chat_history = ""
                    for msg in st.session_state["messages"][-4:-1]:
                        role_name = "ইউজার" if msg["role"] == "user" else "সহকারী"
                        chat_history += f"{role_name}: {msg['content']}\n"

                    system_instruction = (
                        "তুমি একজন অত্যন্ত প্রজ্ঞাবান, নির্ভরযোগ্য এবং গভীর জ্ঞানসম্পন্ন ইসলামিক স্কলার।\n"
                        "তোমার মূল কাজ হলো নিচে দেওয়া কিতাবের কন্টেন্ট থেকে ব্যবহারকারীর প্রশ্নের নিখুঁত উত্তর প্রদান করা।\n\n"
                        f"[পূর্ববর্তী চ্যাট ইতিহাস]\n{chat_history}\n\n"
                        "তোমার কাজ ও কঠোর নির্দেশনা:\n"
                        "১. নিচে 'কিতাবের মূল কন্টেন্ট' সেকশনে যুক্ত করা ডেটা গভীরভাবে বিশ্লেষণ করে শুধু তার ভেতরের সঠিক তথ্যের ওপর ভিত্তি করে উত্তর দিবে।\n"
                        "২. যদি এই প্রশ্নের সুনির্দিষ্ট উত্তর কিতাবের ভেতর না থাকে, তবে স্পষ্ট বলবে: 'এই বিষয়ে কিতাবে স্পষ্ট তথ্য পাওয়া যায়নি।'\n"
                        "৩. কোনো আরবি বা উর্দু ইবারত দেওয়ার সময় এই HTML ফরম্যাটে সাজাবে:\n"
                        "<div class='arabic-ur-ibarath'>আরবি/উর্দু টেক্সট</div>\n"
                        "৪. ইবারতের নিচে বাংলা অনুবাদ এই ফরম্যাটে দেবে:\n"
                        "<div class='bengali-translation'>বাংলা অনুবাদ</div>\n"
                        "৫. উত্তর সম্পূর্ণ সাবলীল ও স্পষ্ট বাংলা ভাষায় দেবে।"
                    )

                    full_prompt = (
                        f"{system_instruction}\n\n"
                        "[কিতাবের মূল কন্টেন্ট]:\n"
                        f"{st.session_state['extracted_books_content'][:50000]}\n\n"
                        f"ব্যবহারকারীর বর্তমান প্রশ্ন: {prompt}"
                    )

                    model = get_gemini_model()
                    response = model.generate_content(full_prompt)

                    output_text = response.text if response.text else "দুঃখিত, কোনো উত্তর জেনারেট করা সম্ভব হয়নি।"

                    st.markdown(output_text, unsafe_allow_html=True)
                    st.session_state["messages"].append({"role": "assistant", "content": output_text})

                except Exception as e:
                    error_msg = str(e)
                    if any(x in error_msg for x in ["429", "RESOURCE_EXHAUSTED", "403", "PERMISSION_DENIED", "quota"]):
                        next_index = st.session_state["current_key_index"] + 1
                        if next_index < len(GEMINI_API_KEYS):
                            st.session_state["current_key_index"] = next_index
                            st.warning("⚠️ API কোটা শেষ। ব্যাকআপ সার্ভারে সুইচ হয়েছে। আবার প্রশ্ন করুন।")
                        else:
                            st.error("❌ সকল API Key-এর কোটা শেষ। কিছুক্ষণ পর চেষ্টা করুন।")
                    else:
                        st.error(f"❌ সমস্যা হয়েছে: {error_msg}")
