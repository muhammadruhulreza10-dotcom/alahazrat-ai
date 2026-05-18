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
    
    /* আরবি ও উর্দু ইবারত ডান দিক থেকে শুরু করার বিশেষ সিএসএস */
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

# Function to read ALL PDFs with advanced character normalization
@st.cache_resource
def load_all_kitabs_text():
    kitabs_dict = {}
    pdf_files = glob.glob("*.pdf") 
    loaded_books = []
    
    if not pdf_files:
        return {}, []
        
    for file_path in pdf_files:
        file_name = os.path.basename(file_path)
        book_text = ""
        try:
            reader = PdfReader(file_path)
            loaded_books.append(file_name)
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    book_text += text + "\n"
            
            cleaned_text = " ".join(book_text.split())
            kitabs_dict[file_name] = cleaned_text if cleaned_text.strip() else "[সংযুক্ত মোবারক কিতাব]"
        except Exception as e:
            continue
            
    return kitabs_dict, loaded_books

# Load books
kitab_data, available_books = load_all_kitabs_text()

# --- CHAT HISTORY & CONTEXT SYSTEM ---
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
    
    # 🕒 চ্যাট হিস্ট্রি রিস্টার্ট বা ডিলিট করার বাটন
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
                # চূড়ান্ত শক্তিশালী গাইডলাইন (ভাঙা ফন্ট অটো-কারেকশন সহ)
                system_instruction = (
                    "তুমি একজন অত্যন্ত প্রজ্ঞাবান, বিশ্বস্ত এবং কঠোরভাবে সত্যনিষ্ঠ ইসলামিক স্কলার। তোমার দায়িত্ব হলো নিচে দেওয়া কিতাবগুলোর তথ্যের আলোকে সর্বোচ্চ শক্তিশালী ও জ্ঞানগর্ভ উত্তর দেওয়া।\n\n"
                    "কঠোর কার্যপ্রণালী নিয়মাবলী:\n"
                    "১. প্রতিটি কিতাবের কন্টেন্ট আলাদাভাবে এবং গভীরভাবে স্ক্যান করবে যাতে কোনো তথ্য বাদ না পড়ে।\n"
                    "২. কোনো মনগড়া, আনুমানিক বা ভুল তথ্য (Hallucination) দেওয়া সম্পূর্ণ নিষিদ্ধ।\n"
                    "৩. ফন্ট ও আয়াত কারেকশন লজিক: পিডিএফ ফাইলের টেক্সটে যদি কোনো কুরআনের আয়াত বা হাদিসের টেক্সট ভেঙে গিয়ে অদ্ভুত চিহ্ন বা ভুল কোড (যেমন: a!$# â'θçP ইত্যাদি) আকারে থাকে, তবে তুমি তোমার নিজস্ব অভ্যন্তরীণ ইসলামিক জ্ঞান ভাণ্ডার ব্যবহার করে সেই আয়াত বা উদ্ধৃতির হুবহু আসল ও শুদ্ধ রূপটি (Original Correct Arabic/Urdu Text) পুনরুদ্ধার করে প্রদান করবে। কোনো অবস্থাতেই স্ক্রিনে ভাঙা বা অদ্ভুত কোড দেখানো যাবে না।\n"
                    "৪. ইবারত নিয়ন্ত্রণের নিয়ম: ব্যবহারকারী যদি তার প্রশ্নে স্পষ্টভাবে 'আরби ইবারত দিন', 'উর্দু ইবারত দিন', 'মূল আয়াত দিন' বা এই জাতীয় কোনো অনুরোধ করে, কেবল তখনই তুমি মূল কিতাবের টেক্সট প্রদান করবে। ব্যবহারকারী নিজে থেকে ইবারত না চাইলে স্বয়ংক্রিয়ভাবে ইবারত দেওয়ার প্রয়োজন নেই, শুধু বাংলায় মজবুত ও সঠিক উত্তর দিলেই হবে।\n"
                    "৫. যতটুকু ইবারত বা আয়াত চাওয়া হবে, ঠিক ততটুকুই নিখুঁতভাবে দিবে। ইবারতটি দেখানোর সময় বাধ্যতামূলকভাবে এই HTML ট্যাগের ভেতরে রাখবে: <div class='arabic-ur-ibarath'>শুদ্ধ ইবারত/আয়াত এখানে</div>। এতে লেখাটি ডান দিক থেকে শুরু হবে।\n"
                    "৬. মূল ইবারতের ঠিক নিচেই তার সাবলীল বাংলা অনুবাদ এই ট্যাগের ভেতর দিবে: <div class='bengali-translation'>বাংলা অনুবাদ এখানে</div>।\n"
                    "৭. যদি উত্তর কিতাবগুলোর কোনোটিতেই না থাকে, তবে বানোয়াট কিছু না বলে বলবে: 'দুঃখিত, এই তথ্যটি বর্তমান কিতাবসমূহে খুঁজে পাওয়া যায়নি।'\n"
                    "৮. আলা হযরত এবং ধর্মীয় বিষয়ের প্রতি সর্বোচ্চ আদব ও সম্মান বজায় রেখে কথা বলবে।"
                )
                
                # চ্যাট ইতিহাস সাজানো
                history_data = []
                for msg in st.session_state["messages"][:-1]:
                    role_type = "user" if msg["role"] == "user" else "model"
                    history_data.append(types.Content(role=role_type, parts=[types.Part.from_text(text=msg["content"])]))
                
                # সব কিতাবের কন্টেন্ট প্রম্পটে যুক্ত করা
                all_kitabs_context = ""
                for b_name, b_text in kitab_data.items():
                    all_kitabs_context += f"--- কিতাবের নাম: {b_name} ---\n{b_text}\n\n"
                
                current_prompt = f"কিতাবসমূহের মূল তথ্যভাণ্ডার:\n{all_kitabs_context}\n\nব্যবহারকারীর বর্তমান প্রশ্ন: {prompt}"
                
                # জেমিনি মডেল রান করা (সর্বোচ্চ নির্ভুলতার জন্য temperature=0.1 করা হয়েছে)
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=history_data + [types.Content(role="user", parts=[types.Part.from_text(text=current_prompt)])],
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=0.1
                    )
                )
                
                st.write(response.text, unsafe_allow_html=True)
                st.session_state["messages"].append({"role": "assistant", "content": response.text})
                
            except Exception as e:
                st.error("দুঃখিত, উত্তর তৈরিতে সমস্যা হয়েছে। দয়া করে আবার চেষ্টা করুন।")
