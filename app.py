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

# ---------------- BACKGROUND IMAGE ----------------
image_url = "https://images.vectorstock.com/preview-w850/22/21/ala-hazrat-tomb-ahmed-raza-khan-bareilly-vector-27702122.jpg"

# ---------------- CUSTOM CSS ----------------
st.markdown(f"""
<style>

html, body, [data-testid="stAppViewContainer"], .stApp {{
    background-color: #FFFFFF !important;

    background-image:
    linear-gradient(rgba(255,255,255,0.88), rgba(255,255,255,0.88)),
    url("{image_url}") !important;

    background-size: auto 65% !important;
    background-position: center 70% !important;
    background-repeat: no-repeat !important;
    background-attachment: fixed !important;

    color: #1A202C !important;
}}

.stAppHeader,
.stMainBlockContainer,
.stBlock,
[data-testid="stHeader"],
[data-testid="stVerticalBlock"] {{
    background: transparent !important;
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
    font-family: 'Arial', sans-serif !important;
    font-size: 1.5rem;
    color: #0F4C3A;
    text-align: center !important;
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
    background-color: rgba(255,255,255,0.92) !important;
    border: 1px solid rgba(15, 76, 58, 0.15) !important;
    border-radius: 10px;
}}

.arabic-ur-ibarath {{
    direction: rtl !important;
    text-align: right !important;

    font-family:
    'Traditional Arabic',
    'Amiri',
    'Noto Naskh Arabic',
    sans-serif !important;

    font-size: 1.65rem !important;
    line-height: 2.3 !important;

    color: #0F4C3A !important;

    background-color: #F7FAFC !important;

    padding: 15px;
    border-radius: 6px;

    border-right: 5px solid #0F4C3A;

    margin-top: 10px;
    margin-bottom: 10px;
}}

.bengali-translation {{
    direction: ltr !important;
    text-align: left !important;

    font-size: 1.1rem !important;
    line-height: 1.7 !important;

    color: #2D3748 !important;

    margin-top: 5px;
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
    '<div class="sub-title">আলা হযরতের কিতাবসমূহ থেকে নির্ভরযোগ্য উত্তর পাওয়ার মাধ্যম</div>',
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

# ---------------- BOOK FOLDER ----------------
BOOK_FOLDER = "books"

# ---------------- PDF TEXT EXTRACTION ----------------
@st.cache_data
def extract_text_from_pdfs():

    full_text = ""

    if not os.path.exists(BOOK_FOLDER):
        os.makedirs(BOOK_FOLDER)

    pdf_files = [
        f for f in os.listdir(BOOK_FOLDER)
        if f.endswith(".pdf")
    ]

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
if not os.path.exists(BOOK_FOLDER):
    os.makedirs(BOOK_FOLDER)

available_books = [
    f for f in os.listdir(BOOK_FOLDER)
    if f.endswith(".pdf")
]

# ---------------- GEMINI API ----------------
api_key = st.secrets["GEMINI_API_KEY"]

client = genai.Client(api_key=api_key)

# ---------------- SESSION STATE ----------------
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# ---------------- SIDEBAR ----------------
with st.sidebar:

    st.markdown(
        '<div class="sidebar-header">📖 বর্তমান কিতাবসমূহ</div>',
        unsafe_allow_html=True
    )

    if available_books:
        for book in available_books:
            st.markdown(f"🔹 **{book}**")
    else:
        st.warning("books ফোল্ডারে কোনো PDF পাওয়া যায়নি")

    st.markdown("---")

    st.markdown(
        '<div class="sidebar-header">🕒 চ্যাট কন্ট্রোল</div>',
        unsafe_allow_html=True
    )

    if st.button("🗑️ নতুন চ্যাট শুরু করুন", use_container_width=True):
        st.session_state["messages"] = []
        st.rerun()

    st.markdown("---")

    st.markdown(
        '<div class="sidebar-header">💡 ব্যবহার বিধি</div>',
        unsafe_allow_html=True
    )

    st.info(
        "১. books ফোল্ডারে PDF আপলোড করুন\n\n"
        "২. নিচে প্রশ্ন লিখুন\n\n"
        "৩. AI কিতাব থেকে উত্তর খুঁজে দিবে"
    )

    st.markdown("---")

    st.caption("Developed with ❤️ for Islamic Research")

# ---------------- OLD CHAT RENDER ----------------
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

                # ---------------- LOAD PDF CONTENT ----------------
                books_content = extract_text_from_pdfs()

                # ---------------- CHAT HISTORY ----------------
                chat_history_str = ""

                for msg in st.session_state["messages"][-4:-1]:

                    role_name = (
                        "ইউজার"
                        if msg["role"] == "user"
                        else "সহকারী"
                    )

                    chat_history_str += (
                        f"{role_name}: {msg['content']}\n"
                    )

                # ---------------- FINAL PROMPT ----------------
                final_prompt = f"""
তুমি একজন প্রজ্ঞাবান ও সত্যনিষ্ঠ ইসলামিক স্কলার।

পূর্ববর্তী চ্যাট:
{chat_history_str}

ব্যবহারকারীর প্রশ্ন:
{prompt}

নিচে কিতাবসমূহের টেক্সট দেওয়া হলো:

{books_content[:150000]}

নির্দেশনা:

১. শুধুমাত্র কিতাবের তথ্য থেকে উত্তর দিবে।

২. মনগড়া কিছু বলা যাবে না।

৩. যদি তথ্য না পাও তাহলে বলবে:
"এই বিষয়ে কিতাবে স্পষ্ট তথ্য পাওয়া যায়নি"

৪. আয়াত বা ইবারত দিলে এই format ব্যবহার করবে:

<div class='arabic-ur-ibarath'>
আরবি/উর্দু টেক্সট
</div>

<div class='bengali-translation'>
বাংলা অনুবাদ
</div>

৫. অপ্রয়োজনীয় বড় উত্তর দিবে না।

৬. বাংলা ভাষায় সুন্দর ও নির্ভুল উত্তর দিবে।
"""

                # ---------------- GEMINI RESPONSE ----------------
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

                st.error(f"Error: {str(e)}")
