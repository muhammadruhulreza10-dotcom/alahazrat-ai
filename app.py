import streamlit as st
from google import genai

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
st.markdown('<div class="main-title">📚  ইমাম আহমদ رضا খাঁন আলা হযরত এআই কিতাবখানা</div>', unsafe_allow_html=True)
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

# কিতাবের সুনির্দিষ্ট তালিকা (হার্ডকোড করা, কোনো ক্র্যাশ ছাড়াই সরাসরি দৃশ্যমান হবে)
available_books = ["hadayeq.pdf", "kitab.pdf"]

# --- INITIALIZE CHAT HISTORY ---
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# --- SIDEBAR DESIGN ---
with st.sidebar:
    st.markdown('<div class="sidebar-header">📖 কিতাবখানার বর্তমান কিতাবসমূহ</div>', unsafe_allow_html=True)
    for book in available_books:
        st.markdown(f"🔹 **{book}**")
        
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
                # চ্যাট কন্টেক্সট ইতিহাস স্ট্রিং আকারে তৈরি করা
                chat_history_str = ""
                for msg in st.session_state["messages"][-4:-1]:
                    role_name = "ইউজার" if msg["role"] == "user" else "সহকারী"
                    chat_history_str += f"{role_name}: {msg['content']}\n"

                # চূড়ান্ত প্রম্পট ডিজাইন
                final_prompt = (
                    "তুমি একজন প্রজ্ঞাবান এবং কঠোরভাবে সত্যনিষ্ঠ ইসলামিক স্কলার। নিচের নির্দেশনাবলী মেনে চলো:\n\n"
                    f"পূর্ববর্তী চ্যাট ইতিহাস:\n{chat_history_str}\n"
                    f"ব্যবহারকারীর বর্তমান প্রশ্ন: {prompt}\n\n"
                    "তোমার কাজ ও দায়িত্ব:\n"
                    "১. তোমার জ্ঞানভাণ্ডারে থাকা ইমাম আহমদ রেজা খান আলা হযরতের কিতাবসমূহ (বিশেষ করে 'হাদায়েকে বখশিশ' বা 'hadayeq.pdf' এবং মূল 'kitab.pdf') এর তথ্যের ভিত্তিতে সম্পূর্ণ সঠিক ও জ্ঞানগর্ভ উত্তর প্রদান করবে।\n"
                    "২. কোনো মনগড়া বা ভুল তথ্য দেওয়া সম্পূর্ণ নিষিদ্ধ।\n"
                    "৩. ভাঙা ফন্ট কারেকশন লজিক: ফন্ট ভেঙে গিয়ে অদ্ভুত চিহ্ন বা ভুল কোড (যেমন: a!$# â'θçP ইত্যাদি) দেখালে, তুমি তোমার অভ্যন্তরীণ ইসলামিক জ্ঞান ব্যবহার করে সেই আয়াত বা উদ্ধৃতির হুবহু আসল ও শুদ্ধ রূপটি (Original Correct Arabic/Urdu Text) পুনরুদ্ধার করে প্রদান করবে। কোনো অবস্থাতেই স্ক্রিনে ভাঙা কোড দেখানো যাবে না।\n"
                    "৪. ব্যবহারকারী নিজে থেকে 'আয়াত' বা 'ইবারত' না চাইলে অযথা বড় আরবি/উর্দু টেক্সট দেবে না, শুধু বাংলায় সাবলীল ও মজবুত উত্তর দেবে।\n"
                    "৫. আয়াত বা ইবারত দিলে তা বাধ্যতামূলকভাবে ডান দিক থেকে শুরু করার জন্য <div class='arabic-ur-ibarath'>শুদ্ধ টেক্সট এখানে</div> এবং তার ঠিক নিচে <div class='bengali-translation'>অনুবাদ এখানে</div> আকারে সাজিয়ে দেবে।"
                )
                
                # জেমিনি মডেল রান (সুপার ফাস্ট এপিআই কল)
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=final_prompt
                )
                
                output_text = response.text
                st.write(output_text, unsafe_allow_html=True)
                st.session_state["messages"].append({"role": "assistant", "content": output_text})
                
            except Exception as e:
                st.error("দুঃখিত, উত্তর তৈরিতে সমস্যা হয়েছে। অনুগ্রহ করে আবার চেষ্টা করুন।")
