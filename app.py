import streamlit as st
from google import genai
from pypdf import PdfReader
import os

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="আলা হযরত এআই কিতাবখানা",
    page_icon="📚",
    layout="centered"
)

# ---------------- AUTO CREATE BOOKS FOLDER ----------------
BOOK_FOLDER = "books"

if not os.path.exists(BOOK_FOLDER):
    os.makedirs(BOOK_FOLDER)

# ---------------- BACKGROUND IMAGE ----------------
image_url = "https://images.vectorstock.com/preview-w850/22/21/ala-hazrat-tomb-ahmed-raza-khan-bareilly-vector-27702122.jpg"

# ---------------- CSS ----------------
st.markdown(f"""
<style>

html, body, [data-testid="stAppViewContainer"], .stApp {{
    background-color: #FFFFFF !important;

    background-image:
    linear-gradient(rgba(255,255,255,0.90), rgba(255,255,255,0.90)),
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

# ---------------- TITLE ----------------
st.markdown(
    '<div class="main-title">📚 ইমাম আহমদ رضا খাঁন আলা হযরত এআই কিতাবখানা</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">কিতাবসমূহ থেকে নির্ভরযোগ্য উত্তর অনুসন্ধান</div>',
    unsafe_allow_html=True
)

# ---------------- URDU SHER ----------------
st.markdown("""
<div class="urdu-sher-container">
<div class="urdu-text">
ملکِ سخن کی شاہی تم کو رضاؔ مسلم<br>
جس سمت آ گئے ہو سکے بٹھا دیے ہیں
</div>
</div>
""", unsafe_allow_html=True)

# ---------------- PDF TEXT EXTRACTION ----------------
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

            full_text += f"\n\n========== {pdf_file} ==========\n\n"

            for page in reader.pages:

                text = page.extract_text()

                if text:
                    full_text += text + "\n"

        except Exception as e:
            full_text += f"\n{pdf_file} পড়তে সমস্যা হয়েছে\n"

    return full_text

# ---------------- AVAILABLE BOOKS ----------------
available_books = [
    f for f in os.listdir(BOOK_FOLDER)
    if f.endswith(".pdf")
]

# ---------------- GEMINI API ----------------
api_key = st.secrets["GEMINI_API_KEY"]

client = genai.Client(api_key=api_key)

# ---------------- SESSION ----------------
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# ---------------- SIDEBAR ----------------
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

# ---------------- OLD CHAT ----------------
for message in st.session_state["messages"]:

    with st.chat_message(message["role"]):

        st.write(message["content"], unsafe_allow_html=True)

# ---------------- CHAT INPUT ----------------
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

                # ---------------- LOAD BOOK TEXT ----------------
                books_content = extract_text_from_pdfs()

                if not books_content:

                    st.warning("প্রথমে PDF Upload করুন")

                else:

                    # ---------------- CHAT HISTORY ----------------
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

                    # ---------------- FINAL PROMPT ----------------
                    # এখানে ডাটার দৈর্ঘ্য ১৫০০০০ থেকে কমিয়ে ৩০০০১ করা হয়েছে যেন ফ্রি API ক্র্যাশ না করে
                    final_prompt = f"""
তুমি একজন প্রজ্ঞাবান ও নির্ভরযোগ্য ইসলামিক স্কলার।

পূর্ববর্তী চ্যাট:
{chat_history}

ব্যবহারকারীর প্রশ্ন:
{prompt}

নিচে কিতাবসমূহের টেক্সট দেওয়া হলো:

{books_content[:30000]}

নির্দেশনা:

১. শুধুমাত্র কিতাবের তথ্য থেকে উত্তর দিবে।

২. মনগড়া কিছু বলা যাবে না।

৩. তথ্য না পেলে বলবে:
"এই বিষয়ে কিতাবে স্পষ্ট তথ্য পাওয়া যায়নি"

৪. আয়াত বা ইবারত দিলে এই format ব্যবহার করবে:

<div class='arabic-ur-ibarath'>
আরবি/উর্দু টেক্সট
</div>

<div class='bengali-translation'>
বাংলা অনুবাদ
</div>

৫. উত্তর বাংলা ভাষায় দিবে।

৬. অপ্রয়োজনীয় বড় উত্তর দিবে না।
"""

                    # ---------------- GEMINI ----------------
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=final_prompt
                    )

                    output_text = response.text

                    st.write(output_text, unsafe_allow_html=True)

                    st.session_state["messages"].append({
                        "role": "assistant",
                        "content": output_text
                    })

            except Exception as e:
                # গুগলের ওভারলোড এরর কোড ফিল্টার করে নিরাপদ ও সুন্দর বার্তা প্রদর্শন
                error_msg = str(e)
                if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                    st.warning("⚠️ গুগলের ফ্রি সার্ভারে এখন অনেক চাপ। অনুগ্রহ করে ৩০ সেকেন্ড পর আপনার প্রশ্নটি আবার সাবমিট করুন।")
                elif "403" in error_msg or "PERMISSION_DENIED" in error_msg:
                    st.error("🔒 আপনার API Key-টি ব্লক হয়েছে। অনুগ্রহ করে AI Studio থেকে নতুন Key নিয়ে Secrets-এ আপডেট করুন।")
                else:
                    st.error("দুঃখিত, কিতাবখানা থেকে উত্তর তৈরিতে সাময়িক সমস্যা হয়েছে। অনুগ্রহ করে আবার চেষ্টা করুন।")
