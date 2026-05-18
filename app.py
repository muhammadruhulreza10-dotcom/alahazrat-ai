import streamlit as st
from google import genai
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
    
    .arabic-ur-ibarath {{
        direction: rtl !important;
        text-align: right !important;
        font-family: 'Traditional Arabic', 'Amiri', 'Noto Naskh Arabic', sans-serif !important;
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
        line-height: 1.6 !important;
        color: #2D3748 !important;
        margin-top: 5px;
        margin-bottom: 15px;
    }}
    </style>
""", unsafe_allow_html=True)

# App Title
st.markdown('<div class="main-title">📚 ইমাম আহমদ رضا খাঁন আলা হযরত এআই কিতাবখানা</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">আলা হযরতের মোবারক কিতাবসমূহ থেকে সরাসরি বাংলায় সঠিক ও নির্ভরযোগ্য উত্তর পাওয়ার মাধ্যম।</div>', unsafe_allow_html=True)

# --- URDU SHER SECTION ---
st.markdown("""
    <div class="urdu-sher-container">
        <div class="urdu-text">ملکِ سخن کی شاہی تم کو رضاؔ مسلم<br>جس سمت آ گئے ہو سکے بٹھا دیے ہیں</div>
    </div>
""", unsafe_allow_html=True)

# Fetch API Key from Streamlit Secrets
api_key = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=api_key)

# কিতাবের ডাটা পৃষ্ঠা আকারে লোড করার স্মার্ট ফাংশন
@st.cache_resource
def load_all_kitabs_chunks():
    chunks_dict = {}
    pdf_files = glob.glob("*.pdf") 
    loaded_books = []
    
    if not pdf_files:
        return {}, []
        
    for file_path in pdf_files:
        file_name = os.path.basename(file_path)
        chunks_dict[file_name] = []
        try:
            reader = PdfReader(file_path)
            loaded_books.append(file_name)
            for page_num, page in enumerate(reader.pages):
                text = page.extract_text()
                if text and text.strip():
                    cleaned_page_text = " ".join(text.split())
                    chunks_dict[file_name].append({
                        "page": page_num + 1,
                        "text": cleaned_page_text
                    })
        except Exception as e:
            continue
            
    return chunks_dict, loaded_books

# Load books chunks
kitab_chunks, available_books = load_all_kitabs_chunks()

# কিওয়ার্ডের ওপর ভিত্তি করে প্রাসঙ্গিক পাতা খুঁজে বের করার সার্চ ইঞ্জিন
def retrieve_relevant_context(query, chunks_data, top_n=4):
    relevant_segments = ""
    query_words = [word.lower() for word in query.split() if len(word) > 2]
    
    if not query_words:
        for b_name, pages in chunks_data.items():
            for p in pages[:2]:
                relevant_segments += f"[{b_name} - পৃষ্ঠা {p['page']}]: {p['text']}\n\n"
        return relevant_segments

    matched_chunks = []
    for b_name, pages in chunks_data.items():
        for p in pages:
            score = sum(1 for word in query_words if word in p['text'].lower())
            if score > 0:
                matched_chunks.append((score, b_name, p['page'], p['text']))
                
    matched_chunks.sort(key=lambda x: x[0], reverse=True)
    
    for score, b_name, p_num, p_text in matched_chunks[:top_n]:
        relevant_segments += f"--- কিতাবের নাম: {b_name} (পৃষ্ঠা: {p_num}) ---\n{p_text}\n\n"
        
    return relevant_segments

# --- INITIALIZE CHAT HISTORY ---
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# --- SIDEBAR DESIGN ---
with st.sidebar:
    st.markdown('<div class="sidebar-header">📖 কিতাবখানার বর্তমান কিতাবসমূহ</div>', unsafe_allow_html=True)
    if available_books:
        for book in available_books:
            st.markdown(f"🔹 **{book}**")
    else:
        st.write("❌ কোনো কিতাব পাওয়া যায়নি।")
        
    st.markdown("---")
    
    st.markdown('<div class="sidebar-header">🕒 চ্যাট মেমোরি কন্ট্রোল</div>', unsafe_allow_html=True)
    if st.button("🗑️ নতুন করে চ্যাট শুরু করুন (Clear History)", use_container_width=True):
        st.session_state["messages"] = []
        st.rerun()
        
    st.markdown("---")
    st.markdown('<div class="sidebar-header">💡 ব্যবহার বিধি</div>', unsafe_allow_html=True)
    st.info(
        "১. নিচে থাকা চ্যাট বক্সে আপনার প্রশ্নটি বাংলায় লিখুন।\n\n"
        "২. ইবারত বা কুরআনের মূল আয়াত প্রয়োজন হলে প্রশ্নে উল্লেখ করুন (যেমন: আয়াত/ইবারতসহ বলুন)।"
    )
    st.markdown("---")
    st.caption("Developed with ❤️ for Islamic Research")

# আগের মেসেজ স্ক্রিনে রেন্ডার রাখা
for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.write(message["content"], unsafe_allow_html=True)

# নতুন প্রশ্ন ইনপুট
if prompt := st.chat_input("আলা হযরতের কিতাবসমূহ সম্পর্কে যেকোনো প্রশ্ন লিখুন..."):
    
    st.session_state["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt, unsafe_allow_html=True)

    with st.chat_message("assistant"):
        with st.spinner("কিতাবখানা থেকে উত্তর খোঁজা হচ্ছে..."):
            try:
                # কিতাব থেকে প্রাসঙ্গিক অংশটুকু ফিল্টার করে আনা হচ্ছে
                relevant_context = retrieve_relevant_context(prompt, kitab_chunks)
                
                # চ্যাট কন্টেক্সট ইতিহাস স্ট্রিং আকারে তৈরি করা (টাইপ ক্র্যাশ এড়াতে)
                chat_history_str = ""
                for msg in st.session_state["messages"][-4:-1]:
                    role_name = "ইউজার" if msg["role"] == "user" else "সহকারী"
                    chat_history_str += f"{role_name}: {msg['content']}\n"

                # চূড়ান্ত প্রম্পট ডিজাইন
                final_prompt = (
                    "তুমি একজন প্রজ্ঞাবান এবং কঠোরভাবে সত্যনিষ্ঠ ইসলামিক স্কলার। নিচের নির্দেশনাবলী মেনে চলো:\n\n"
                    f"পূর্ববর্তী চ্যাট ইতিহাস:\n{chat_history_str}\n"
                    f"কিতাবসমূহ থেকে ফিল্টার করা প্রাসঙ্গিক তথ্য:\n{relevant_context}\n"
                    f"ব্যবহারকারীর বর্তমান প্রশ্ন: {prompt}\n\n"
                    "নিয়মাবলী:\n"
                    "১. সরবরাহকৃত প্রাসঙ্গিক তথ্যের আলোকেই শুধু উত্তর দেবে। বানিয়ে কিছু বলবে না।\n"
                    "২. পিডিএফ-এর ভাঙা ফন্ট (যেমন: a!$# â'θçP ইত্যাদি) স্ক্রিনে দেখাবে না। তোমার জ্ঞান থেকে শুদ্ধ আরবি আয়াতটি পুনরুদ্ধার করে দেখাবে।\n"
                    "৩. ব্যবহারকারী নিজে থেকে 'আয়াত' বা 'ইবারত' না চাইলে অযথা বড় আরবি টেক্সট দেবে না, শুধু বাংলায় সাবলীল উত্তর দেবে।\n"
                    "৪. আয়াত বা ইবারত দিলে তা বাধ্যতামূলকভাবে <div class='arabic-ur-ibarath'>শুদ্ধ টেক্সট</div> এবং তার নিচে <div class='bengali-translation'>অনুবাদ</div> আকারে সাজিয়ে দেবে।"
                )
                
                # জেমিনি মডেল রান (সরাসরি টেক্সট কন্টেন্ট পাস করা হচ্ছে)
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=final_prompt
                )
                
                output_text = response.text
                st.write(output_text, unsafe_allow_html=True)
                st.session_state["messages"].append({"role": "assistant", "content": output_text})
                
            except Exception as e:
                st.error("দুঃখিত, সিস্টেম লোড নিতে পারছে না। অনুগ্রহ করে সাইডবার থেকে 'Clear History' বাটনে ক্লিক করে আবার চেষ্টা করুন।")
