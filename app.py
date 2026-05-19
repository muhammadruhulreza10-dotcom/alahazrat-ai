import streamlit as st
from google import genai
from google.genai import types
import os
import time

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="আলা হযরত এআই কিতাবখানা",
    page_icon="📚",
    layout="centered"
)

# ---------------- AUTO CREATE TEMP FOLDER ----------------
# নতুন পদ্ধতিতে ফাইলগুলো সরাসরি গুগলে আপলোড করার আগে সাময়িকভাবে এখানে জমা হবে
TEMP_FOLDER = "temp_books"
if not os.path.exists(TEMP_FOLDER):
    os.makedirs(TEMP_FOLDER)

# ---------------- BACKGROUND IMAGE ----------------
image_url = "https://images.vectorstock.com/preview-w850/22/21/ala-hazrat-tomb-ahmed-raza-khan-bareilly-vector-27702122.jpg"

# ---------------- CSS FIXED FOR ARABIC & URDU ----------------
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

/* আরবি ও উর্দু ফন্ট এবং ব্র্যাকেট যাতে একদম সোজা থাকে তার জন্য শক্তিশালী CSS */
.arabic-ur-ibarath {{
    direction: rtl !important;
    text-align: right !important;
    unicode-bidi: bidi-override !important;

    font-family:
    'Scheherazade New',
    'Traditional Arabic',
    'Amiri',
    'Noto Naskh Arabic',
    'Jameel Noori Nastaleeq',
    sans-serif !important;

    font-size: 1.9rem !important;
    line-height: 2.5 !important;
    color: #0F4C3A !important;
    background-color: #F7FAFC !important;
    padding: 18px 25px;
    border-radius: 8px;
    border-right: 6px solid #0F4C3A;
    margin-top: 15px;
    margin-bottom: 15px;
}}

.bengali-translation {{
    font-size: 1.1rem;
    line-height: 1.7;
    color: #2D3748;
    margin-bottom: 15px;
}}

</style>
""", unsafe_allow_html=True)

# ---------------- TITLE & SHER ----------------
st.markdown('<div class="main-title">📚 ইমাম আহমদ رضا খাঁন আলা হযরত এআই কিতাবখানা</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">কিতাবসমূহ থেকে নির্ভরযোগ্য উত্তর অনুসন্ধান (Pro Version)</div>', unsafe_allow_html=True)

st.markdown("""
<div class="urdu-sher-container">
<div class="urdu-text">
ملکِ سخن کی شاہی تم کو رضاؔ مسلم<br>
جس سمت آ گئے ہو سکے بٹھا دیے ہیں
</div>
</div>
""", unsafe_allow_html=True)

# ---------------- GEMINI MULTI-KEY CONFIG ----------------
api_keys = st.secrets["GEMINI_API_KEYS"]

if "current_key_index" not in st.session_state:
    st.session_state["current_key_index"] = 0

current_index = st.session_state["current_key_index"]
if current_index >= len(api_keys):
    current_index = 0
    st.session_state["current_key_index"] = 0

# সচল ক্লায়েন্ট তৈরি
client = genai.Client(api_key=api_keys[current_index])

# ---------------- SESSION STATES ----------------
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "uploaded_file_uris" not in st.session_state:
    st.session_state["uploaded_file_uris"] = []
if "uploaded_file_names" not in st.session_state:
    st.session_state["uploaded_file_names"] = []

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown('<div class="sidebar-header">📖 বর্তমান কিতাবসমূহ</div>', unsafe_allow_html=True)
    
    if st.session_state["uploaded_file_names"]:
        st.success(f"{len(st.session_state['uploaded_file_names'])} টি কিতাব সচল আছে")
        for book_name in st.session_state["uploaded_file_names"]:
            st.markdown(f"🔹 **{book_name}**")
    else:
        st.error("⚠️ এখনো কোনো কিতাব upload করা হয়নি")

    st.markdown("---")
    st.markdown('<div class="sidebar-header">📤 কিতাব Upload করুন (PDF)</div>', unsafe_allow_html=True)
    
    uploaded_files = st.file_uploader(
        "এখানে PDF upload করুন (সরাসরি গুগল এআই রিড করবে)",
        type=["pdf"],
        accept_multiple_files=True
    )

    if uploaded_files:
        with st.spinner("গুগল এআই সার্ভারে কিতাব আপলোড এবং প্রসেসিং হচ্ছে..."):
            for uploaded_file in uploaded_files:
                if uploaded_file.name not in st.session_state["uploaded_file_names"]:
                    
                    # ১. সাময়িকভাবে ফাইল সেভ
                    temp_path = os.path.join(TEMP_FOLDER, uploaded_file.name)
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # ২. গুগলের অ্যাডভান্সড File API-তে ফাইল আপলোড
                    google_file = client.files.upload(file=temp_path)
                    
                    # গুগলের প্রসেসিং শেষ হওয়া পর্যন্ত অপেক্ষা
                    while google_file.state.name == "PROCESSING":
                        time.sleep(2)
                        google_file = client.files.get(name=google_file.name)
                    
                    if google_file.state.name == "FAILED":
                        st.error(f"{uploaded_file.name} প্রসেস করতে সমস্যা হয়েছে।")
                        continue
                        
                    # সেশন স্টেটে গুগলের ফাইল লিংক (URI) জমা রাখা
                    st.session_state["uploaded_file_uris"].append(google_file.uri)
                    st.session_state["uploaded_file_names"].append(uploaded_file.name)
                    
                    # সাময়িক লোকাল ফাইল মুছে ফেলা
                    try:
                        os.remove(temp_path)
                    except:
                        pass
            
            st.success("✅ কitাব সফলভাবে গুগল এআই-তে যুক্ত হয়েছে!")
            st.rerun()

    st.markdown("---")
    if st.button("🗑️ নতুন চ্যাট শুরু করুন", use_container_width=True):
        st.session_state["messages"] = []
        # চ্যাট ক্লিয়ার করলেও ফাইল লিংক থেকে যাবে, যাতে বারবার আপলোড করতে না হয়
        st.rerun()

# ---------------- OLD CHAT ----------------
for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.write(message["content"], unsafe_allow_html=True)

# ---------------- CHAT INPUT ----------------
if prompt := st.chat_input("কিতাব থেকে যেকোনো প্রশ্ন বা রেফারেঞ্চ জানতে লিখুন..."):

    st.session_state["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("জেমিনি প্রো কিতাব স্ক্যান করছে..."):
            try:
                if not st.session_state["uploaded_file_uris"]:
                    st.warning("অনুগ্রহ করে প্রথমে সাইডবার থেকে কিতাব (PDF) Upload করুন।")
                else:
                    # ১. কন্টেন্ট বা ফাইল লিস্ট তৈরি
                    contents_payload = []
                    for uri in st.session_state["uploaded_file_uris"]:
                        contents_payload.append(types.Part.from_uri(file_uri=uri, mime_type="application/pdf"))
                    
                    # ২. পূর্ববর্তী চ্যাট হিস্ট্রি যুক্ত করা
                    chat_history = ""
                    for msg in st.session_state["messages"][-4:-1]:
                        role_name = "ইউজার" if msg["role"] == "user" else "সহকারী"
                        chat_history += f"{role_name}: {msg['content']}\n"

                    # ৩. কড়া সিস্টেম এবং ফন্ট নির্দেশনা (প্রম্পট)
                    system_instruction = f"""
তুমি একজন অত্যন্ত প্রজ্ঞাবান, নির্ভরযোগ্য এবং গভীর জ্ঞানসম্পন্ন ইসলামিক স্কলার।

পূর্ববর্তী চ্যাট হিস্ট্রি:
{chat_history}

ব্যবহারকারীর প্রশ্ন:
{prompt}

নির্দেশনা:
১. তোমাকে দেওয়া কিতাব বা ফাইলটি খুব নিখুঁতভাবে পড়ে শুধু তার সঠিক তথ্যের আলোকে উত্তর দিবে। মনগড়া বা নিজের থেকে কোনো ব্যাখ্যা দিবে না।
২. কিতাবে তথ্য স্পষ্ট না থাকলে বা খুঁজে না পেলে অত্যন্ত বিনয়ের সাথে বলবে: "এই বিষয়ে কিতাবে স্পষ্ট তথ্য পাওয়া যায়নি।"
৩. সবচেয়ে গুরুত্বপূর্ণ (আরবি/উর্দু ফন্ট বিন্যাস): যেকোনো আরবি ইবারত, কোরআনের আয়াত বা হাদিসের মূল টেক্সট বা উর্দু শের দেওয়ার সময় অবশ্যই এবং বাধ্যতামূলকভাবে নিচের HTML ফরম্যাটে দিবে। আরবি/উর্দু লেখার ভেতরে কোনো বাংলা ব্র্যাকেট, বাংলা সংখ্যা, বা বাংলা শব্দ মিক্স করবে না। সম্পূর্ণ আরবি অংশটুকুকে এই সুনির্দিষ্ট বক্সের ভেতরে রাখবে:

<div class='arabic-ur-ibarath'>
এখানে শুধুমাত্র মূল আরবি বা উর্দু ইবারতটি লিখবে (কোনো বাংলা চিহ্ন বা ব্র্যাকেট ছাড়া)
</div>

৪. আরবি/উর্দু ইবারতের ঠিক নিচে তার বাংলা অনুবাদ এই ফরম্যাটে দিবে:

<div class='bengali-translation'>
বাংলা অনুবাদ বা ব্যাখ্যা এখানে লিখবে।
</div>

৫. উত্তর সম্পূর্ণ শুদ্ধ বাংলা ভাষায় দিবে এবং অপ্রয়োজনীয় বড় উত্তর দেওয়া থেকে বিরত থাকবে।
"""
                    contents_payload.append(system_instruction)

                    # ৪. GEMINI 2.5 PRO মডেল দিয়ে জেনারেট করা (যা এখন গুগলে থাকা ফাইল সরাসরি রিড করবে)
                    response = client.models.generate_content(
                        model="models/gemini-2.5-pro",
                        contents=contents_payload
                    )

                    output_text = response.text
                    st.write(output_text, unsafe_allow_html=True)

                    st.session_state["messages"].append({"role": "assistant", "content": output_text})

            except Exception as e:
                error_msg = str(e)
                # অটো-রোটেশন ও ব্যাকআপ কী লজিক
                if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg or "403" in error_msg or "PERMISSION_DENIED" in error_msg:
                    next_index = st.session_state["current_key_index"] + 1
                    if next_index < len(st.secrets["GEMINI_API_KEYS"]):
                        st.session_state["current_key_index"] = next_index
                        st.warning("🔄 বর্তমান ফ্রি সার্ভারের কোটা শেষ হওয়ায় আপনার ২য় ব্যাকআপ সার্ভারে শিফট করা হয়েছে। অনুগ্রহ করে আর একবার প্রশ্নটি সাবমিট করুন।")
                    else:
                        st.session_state["current_key_index"] = 0  
                        st.error("⚠️ দুঃখিত, যুক্ত করা সবকটি ফ্রি কী-এর লিমিট এই মুহূর্তের জন্য শেষ। দয়া করে কিছুক্ষণ পর চেষ্টা করুন।")
                else:
                    st.error("দুঃখিত, কিতাবখানা থেকে উত্তর তৈরিতে সাময়িক সমস্যা হয়েছে। অনুগ্রহ করে আবার চেষ্টা করুন।")
