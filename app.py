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

    pdf_files = [
        f for f in os.listdir(BOOK_FOLDER)
        if f.endswith(".pdf")
    ]

    if not pdf_files:
        return ""

    for pdf_file in pdf_files:

        pdf_path = os.path.join(BOOK_FOLDER, pdf_file)

        try:
            reader = PdfReader(pdf_path)

            full_text += f"\n\n========== কিতাবের নাম: {pdf_file} ==========\n\n"

            for page in reader.pages:

                text = page.extract_text()

                if text:
                    full_text += text + "\n"

        except Exception:
            full_text += f"\n[ত্রুটি: {pdf_file} পড়া যায়নি]\n"

    return full_text

# ================= RELEVANT SEARCH =================
def search_relevant_text(query, books_text, chunk_size=3000):

    query_words = query.lower().split()

    chunks = []

    for i in range(0, len(books_text), chunk_size):

        chunk = books_text[i:i + chunk_size]

        score = 0

        for word in query_words:

            if word in chunk.lower():
                score += 1

        if score > 0:
            chunks.append((score, chunk))

    chunks.sort(reverse=True, key=lambda x: x[0])

    if chunks:
        return "\n\n".join([c[1] for c in chunks[:3]])

    return books_text[:3000]

# ================= AVAILABLE BOOKS =================
available_books = [
    f for f in os.listdir(BOOK_FOLDER)
    if f.endswith(".pdf")
]

# ================= SESSION =================
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# ================= SIDEBAR =================
with st.sidebar:

    st.markdown(
        '<div class="sidebar-header">📖 বর্তমান কিতাবসমূহ</div>',
        unsafe_allow_html=True
    )

    if available_books:

        st.success(f"{len(available_books)} টি কিতাব পাওয়া গেছে")

        for book in available_books:
            st.markdown(f"🔹 **{book}**")

    else:
        st.error("⚠️ এখনো কোনো PDF upload করা হয়নি")

    st.markdown("---")

    st.markdown(
        '<div class="sidebar-header">📤 PDF Upload করুন</div>',
        unsafe_allow_html=True
    )

    uploaded_files = st.file_uploader(
        "এখানে PDF upload করুন",
        type=["pdf"],
        accept_multiple_files=True
    )

    if uploaded_files:

        for uploaded_file in uploaded_files:

            save_path = os.path.join(
                BOOK_FOLDER,
                uploaded_file.name
            )

            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

        st.success("✅ PDF সফলভাবে Upload হয়েছে")

        st.cache_data.clear()

        st.rerun()

    st.markdown("---")

    if st.button("🗑️ নতুন চ্যাট শুরু করুন", use_container_width=True):

        st.session_state["messages"] = []

        st.rerun()

# ================= OLD CHAT =================
for message in st.session_state["messages"]:

    with st.chat_message(message["role"]):

        st.write(message["content"], unsafe_allow_html=True)

# ================= CHAT INPUT =================
if prompt := st.chat_input("কিতাব সম্পর্কে প্রশ্ন লিখুন..."):

    st.session_state["messages"].append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):

        st.write(prompt)

    with st.chat_message("assistant"):

        with st.spinner("কিতাব থেকে উত্তর খোঁজা হচ্ছে..."):

            try:

                # ================= LOAD BOOKS =================
                books_content = extract_text_from_pdfs()

                if not books_content.strip():

                    st.warning("প্রথমে PDF Upload করুন")

                else:

                    # ================= SEARCH RELEVANT TEXT =================
                    relevant_text = search_relevant_text(
                        prompt,
                        books_content
                    )

                    # ================= CHAT HISTORY =================
                    chat_history = ""

                    for msg in st.session_state["messages"][-4:-1]:

                        role_name = (
                            "ইউজার"
                            if msg["role"] == "user"
                            else "সহকারী"
                        )

                        chat_history += (
                            f"{role_name}: {msg['content']}\n"
                        )

                    # ================= FINAL PROMPT =================
                    final_prompt = f"""
তুমি একজন প্রজ্ঞাবান ও নির্ভরযোগ্য ইসলামিক স্কলার।

শুধুমাত্র নিচে দেওয়া কিতাবের অংশ থেকে উত্তর দিবে।

মনগড়া কিছু বলা যাবে না।

তথ্য না পেলে বলবে:
"এই বিষয়ে কিতাবে স্পষ্ট তথ্য পাওয়া যায়নি"

পূর্ববর্তী চ্যাট:
{chat_history}

ব্যবহারকারীর প্রশ্ন:
{prompt}

কিতাবের relevant অংশ:
{relevant_text}

বিশেষ নির্দেশনা:

১. উত্তর বাংলা ভাষায় দিবে।

২. আরবি/উর্দু ইবারত দিলে এই format ব্যবহার করবে:

<div class='arabic-ur-ibarath'>
আরবি/উর্দু টেক্সট
</div>

<div class='bengali-translation'>
বাংলা অনুবাদ
</div>

৩. অপ্রয়োজনীয় বড় উত্তর দিবে না।
"""

                    # ================= API =================
                    url = "https://uai.sh/v1/chat/completions"

                    headers = {
                        "Authorization": "Bearer YOUR_API_KEY",
                        "Content-Type": "application/json"
                    }

                    payload = {
                        "model": "deepseek/deepseek-chat",
                        "messages": [
                            {
                                "role": "user",
                                "content": final_prompt
                            }
                        ],
                        "temperature": 0.3,
                        "max_tokens": 1200
                    }

                    # ================= REQUEST =================
                    response = requests.post(
                        url,
                        json=payload,
                        headers=headers,
                        timeout=60
                    )

                    # ================= RESPONSE =================
                    if response.status_code == 200:

                        response_data = response.json()

                        output_text = response_data[
                            "choices"
                        ][0]["message"]["content"]

                        st.write(
                            output_text,
                            unsafe_allow_html=True
                        )

                        st.session_state["messages"].append({
                            "role": "assistant",
                            "content": output_text
                        })

                    else:

                        st.error(
                            f"API Error: {response.status_code}"
                        )

                        st.write(response.text)

            except Exception as e:

                st.error(f"Error: {str(e)}")
