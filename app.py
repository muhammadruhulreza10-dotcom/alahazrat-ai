import streamlit as st
import google.genai as genai
from google.genai import types
from pypdf import PdfReader
import os

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

.main-title {
    font-size: 2rem;
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
    background-color: rgba(15, 76, 58, 0.06);
    border: 1px solid rgba(15, 76, 58, 0.2);
    border-left: 5px solid #0F4C3A;
    padding: 18px;
    border-radius: 8px;
    text-align: center;
    margin-bottom: 25px;
}

.urdu-text {
    font-size: 1.5rem;
    color: #0F4C3A;
    line-height: 1.8;
    direction: rtl;
}

.sidebar-header {
    font-size: 1.1rem;
    color: #0F4C3A;
    font-weight: bold;
    border-bottom: 2px solid #0F4C3A;
    padding-bottom: 5px;
    margin-bottom: 10px;
}

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

.bengali-translation {
    font-size: 1.1rem;
    line-height: 1.7;
    color: #2D3748;
    margin-bottom: 15px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- TITLE ----------------
st.markdown(
    '<div class="main-title">📚 ইমাম আহমদ رضا খাঁন আলা হযরত এআই কিতাবখানা</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">Gemini API দ্বারা চালিত কাস্টম কিতাব সার্চ ইঞ্জিন</div>',
    unsafe_allow_html=True
)

# ---------------- SHER ----------------
st.markdown("""
<div class="urdu-sher-container">
<div class="urdu-text">
ملکِ سخن کی شاہی تم کو رضاؔ مسلم <br>
جس سمت آ گئے ہو سکے بٹھا دیے ہیں
</div>
</div>
""", unsafe_allow_html=True)

# ---------------- API KEYS ----------------
# নিজের API Key দিন
GEMINI_API_KEYS = [
    "YOUR_API_KEY_1",
    "YOUR_API_KEY_2"
]

# ---------------- SESSION ----------------
if "current_key_index" not in st.session_state:
    st.session_state["current_key_index"] = 0

if "messages" not in st.session_state:
    st.session_state["messages"] = []

if "uploaded_file_names" not in st.session_state:
    st.session_state["uploaded_file_names"] = []

if "book_chunks" not in st.session_state:
    st.session_state["book_chunks"] = []

# ---------------- API CLIENT ----------------
current_index = st.session_state["current_key_index"]

if current_index >= len(GEMINI_API_KEYS):
    current_index = 0
    st.session_state["current_key_index"] = 0

client = genai.Client(
    api_key=GEMINI_API_KEYS[current_index]
)

# ---------------- PDF TEXT CLEANER ----------------
def clean_text(text):
    if not text:
        return ""

    text = text.replace("\n", " ")
    text = text.replace("\t", " ")

    while "  " in text:
        text = text.replace("  ", " ")

    return text.strip()

# ---------------- TEXT CHUNKER ----------------
def chunk_text(text, chunk_size=4000):
    chunks = []

    for i in range(0, len(text), chunk_size):
        chunks.append(text[i:i + chunk_size])

    return chunks

# ---------------- SIDEBAR ----------------
with st.sidebar:

    st.markdown(
        '<div class="sidebar-header">📖 বর্তমান কিতাবসমূহ</div>',
        unsafe_allow_html=True
    )

    if st.session_state["uploaded_file_names"]:
        st.success(
            f"{len(st.session_state['uploaded_file_names'])} টি কিতাব যুক্ত আছে"
        )

        for book_name in st.session_state["uploaded_file_names"]:
            st.markdown(f"🔹 {book_name}")

    else:
        st.warning("এখনো কোনো PDF আপলোড হয়নি")

    st.markdown("---")

    st.markdown(
        '<div class="sidebar-header">📤 PDF Upload করুন</div>',
        unsafe_allow_html=True
    )

    uploaded_files = st.file_uploader(
        "এখানে PDF দিন",
        type=["pdf"],
        accept_multiple_files=True
    )

    # ---------------- PROCESS PDF ----------------
    if uploaded_files:

        with st.spinner("কিতাব প্রসেস করা হচ্ছে..."):

            for uploaded_file in uploaded_files:

                if uploaded_file.name not in st.session_state["uploaded_file_names"]:

                    try:
                        reader = PdfReader(uploaded_file)

                        full_text = ""

                        # শুধু প্রথম ৩০ পৃষ্ঠা
                        pages = reader.pages[:30]

                        for page in pages:

                            text = page.extract_text()

                            if text:
                                full_text += clean_text(text) + "\n"

                        chunks = chunk_text(full_text)

                        st.session_state["book_chunks"].extend(chunks)

                        st.session_state["uploaded_file_names"].append(
                            uploaded_file.name
                        )

                    except Exception as e:
                        st.error(f"PDF Error: {str(e)}")

            st.success("✅ কিতাব সফলভাবে যুক্ত হয়েছে")
            st.rerun()

    st.markdown("---")

    # ---------------- CLEAR CHAT ----------------
    if st.button("🗑️ নতুন চ্যাট", use_container_width=True):

        st.session_state["messages"] = []
        st.session_state["uploaded_file_names"] = []
        st.session_state["book_chunks"] = []

        st.rerun()

# ---------------- SHOW OLD CHAT ----------------
for message in st.session_state["messages"]:

    with st.chat_message(message["role"]):
        st.write(message["content"], unsafe_allow_html=True)

# ---------------- CHAT ----------------
prompt = st.chat_input(
    "কিতাব সম্পর্কে প্রশ্ন করুন..."
)

if prompt:

    st.session_state["messages"].append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):

        with st.spinner("কিতাব সার্চ করা হচ্ছে..."):

            try:

                if not st.session_state["book_chunks"]:

                    st.warning(
                        "অনুগ্রহ করে প্রথমে PDF আপলোড করুন"
                    )

                else:

                    # ---------------- SEARCH RELEVANT CHUNKS ----------------
                    relevant_text = ""

                    keyword_matches = []

                    for chunk in st.session_state["book_chunks"]:

                        if any(word in chunk for word in prompt.split()):
                            keyword_matches.append(chunk)

                    # যদি কিছু না মিলে
                    if not keyword_matches:
                        keyword_matches = st.session_state["book_chunks"][:3]

                    # Limit
                    relevant_text = "\n\n".join(keyword_matches[:3])

                    # ---------------- CHAT HISTORY ----------------
                    chat_history = ""

                    for msg in st.session_state["messages"][-4:-1]:

                        role_name = (
                            "ইউজার"
                            if msg["role"] == "user"
                            else "সহকারী"
                        )

                        chat_history += f"{role_name}: {msg['content']}\n"

                    # ---------------- SYSTEM PROMPT ----------------
                    system_instruction = f"""
তুমি একজন অত্যন্ত প্রজ্ঞাবান ইসলামিক স্কলার।

কঠোর নির্দেশনা:

১। শুধুমাত্র নিচে দেওয়া কিতাবের তথ্য থেকে উত্তর দিবে।

২। মনগড়া উত্তর দিবে না।

৩। উত্তর না পেলে বলবে:
"এই বিষয়ে কিতাবে স্পষ্ট তথ্য পাওয়া যায়নি।"

৪। আরবি/উর্দু ইবারত এই HTML এ দিবে:

<div class='arabic-ur-ibarath'>
আরবি টেক্সট
</div>

৫। বাংলা অনুবাদ এই HTML এ দিবে:

<div class='bengali-translation'>
বাংলা অনুবাদ
</div>

৬। সংক্ষিপ্ত, স্পষ্ট ও সুন্দর বাংলা ব্যবহার করবে।

চ্যাট ইতিহাস:
{chat_history}
"""

                    # ---------------- FINAL PAYLOAD ----------------
                    user_payload = f"""
{system_instruction}

[কিতাবের তথ্য]

{relevant_text}

[প্রশ্ন]

{prompt}
"""

                    # ---------------- CONFIG ----------------
                    config = types.GenerateContentConfig(
                        temperature=0.1,
                        max_output_tokens=2048
                    )

                    # ---------------- API CALL ----------------
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=user_payload,
                        config=config
                    )

                    # ---------------- SAFE RESPONSE ----------------
                    output_text = ""

                    if hasattr(response, "text") and response.text:
                        output_text = response.text
                    else:
                        output_text = "কোনো উত্তর পাওয়া যায়নি।"

                    # ---------------- SHOW ----------------
                    st.write(
                        output_text,
                        unsafe_allow_html=True
                    )

                    # ---------------- SAVE CHAT ----------------
                    st.session_state["messages"].append({
                        "role": "assistant",
                        "content": output_text
                    })

            # ---------------- ERROR HANDLER ----------------
            except Exception as e:

                error_msg = str(e)

                # API LIMIT
                if any(x in error_msg for x in [
                    "429",
                    "RESOURCE_EXHAUSTED",
                    "quota",
                    "Quota"
                ]):

                    next_index = (
                        st.session_state["current_key_index"] + 1
                    )

                    if next_index < len(GEMINI_API_KEYS):

                        st.session_state["current_key_index"] = next_index

                        st.warning(
                            "বর্তমান API limit শেষ। আবার প্রশ্ন করুন।"
                        )

                    else:

                        st.session_state["current_key_index"] = 0

                        st.error(
                            "সব API key limit শেষ। পরে চেষ্টা করুন।"
                        )

                else:

                    st.error(f"Error: {error_msg}")
