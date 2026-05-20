import streamlit as st
from google import genai
from google.genai import types
import os
import time

st.set_page_config(page_title="আলা হযরত এআই কিতাবখানা", page_icon="📚", layout="centered")

TEMP_FOLDER = "temp_books"
if not os.path.exists(TEMP_FOLDER):
    os.makedirs(TEMP_FOLDER)

# ---------------- CSS FIXED FOR ARABIC & URDU ----------------
st.markdown("""
<style>
.main-title { font-size: 2rem; color: #0F4C3A; text-align: center; font-weight: bold; margin-bottom: 5px; }
.sub-title { font-size: 1.05rem; color: #2D3748; text-align: center; margin-bottom: 15px; }
.arabic-ur-ibarath {
    direction: rtl !important; text-align: right !important;
    font-family: 'Traditional Arabic', 'Amiri', sans-serif !important;
    font-size: 1.9rem !important; line-height: 2.5 !important; color: #0F4C3A !important;
    background-color: #F7FAFC !important; padding: 18px; border-radius: 8px; border-right: 6px solid #0F4C3A;
}
.bengali-translation { font-size: 1.1rem; line-height: 1.7; color: #2D3748; margin-bottom: 15px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">📚 ইমাম আহমদ রেজা খাঁন আলা হযরত এআই কিতাবখানা</div>', unsafe_allow_html=True)

if "GEMINI_API_KEYS" not in st.secrets:
    st.error("⚠️ Streamlit Secrets-এ 'GEMINI_API_KEYS' খুঁজে পাওয়া যায়নি!")
    st.stop()

api_keys = st.secrets["GEMINI_API_KEYS"]
if "current_key_index" not in st.session_state:
    st.session_state["current_key_index"] = 0

current_index = st.session_state["current_key_index"]
client = genai.Client(api_key=api_keys[current_index])

if "messages" not in st.session_state: st.session_state["messages"] = []
if "uploaded_file_uris" not in st.session_state: st.session_state["uploaded_file_uris"] = []
if "uploaded_file_names" not in st.session_state: st.session_state["uploaded_file_names"] = []

with st.sidebar:
    st.markdown("### 📖 বর্তমান কিতাবসমূহ")
    if st.session_state["uploaded_file_names"]:
        for book_name in st.session_state["uploaded_file_names"]: st.markdown(f"🔹 **{book_name}**")
    else: st.error("⚠️ কোনো কিতাব upload করা হয়নি")

    uploaded_files = st.file_uploader("এখানে PDF upload করুন", type=["pdf"], accept_multiple_files=True)
    if uploaded_files:
        with st.spinner("গুগল এআই সার্ভারে প্রসেস হচ্ছে..."):
            for uploaded_file in uploaded_files:
                if uploaded_file.name not in st.session_state["uploaded_file_names"]:
                    temp_path = os.path.join(TEMP_FOLDER, uploaded_file.name)
                    with open(temp_path, "wb") as f: f.write(uploaded_file.getbuffer())
                    try:
                        google_file = client.files.upload(file=temp_path)
                        while google_file.state.name == "PROCESSING":
                            time.sleep(2)
                            google_file = client.files.get(name=google_file.name)
                        st.session_state["uploaded_file_uris"].append(google_file.uri)
                        st.session_state["uploaded_file_names"].append(uploaded_file.name)
                    except Exception as e: st.error(f"আপলোড ট্রাবল: {str(e)}")
                    finally:
                        if os.path.exists(temp_path): os.remove(temp_path)
            st.rerun()

for message in st.session_state["messages"]:
    with st.chat_message(message["role"]): st.write(message["content"], unsafe_allow_html=True)

if prompt := st.chat_input("কিতাব থেকে প্রশ্ন করুন..."):
    st.session_state["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("জেমিনি কিতাব স্ক্যান করছে..."):
            try:
                if not st.session_state["uploaded_file_uris"]:
                    st.warning("প্রথমে সাইডবার থেকে কিতাব Upload করুন।")
                else:
                    contents_payload = []
                    for uri in st.session_state["uploaded_file_uris"]:
                        contents_payload.append(types.Part.from_uri(file_uri=uri, mime_type="application/pdf"))
                    
                    system_instruction = f"তুমি একজন ইসলামিক স্কলার। কিতাব থেকে উত্তর দাও। আরবি/উর্দু ইবারত থাকলে অবশ্যই <div class='arabic-ur-ibarath'>আরবি টেক্সট</div> এবং বাংলা অনুবাদের জন্য <div class='bengali-translation'>অনুবাদ</div> ফরম্যাট ব্যবহার করবে। ব্যবহারকারীর প্রশ্ন: {prompt}"
                    contents_payload.append(system_instruction)
                    
                    response = client.models.generate_content(model="models/gemini-2.5-pro", contents=contents_payload)
                    output_text = response.text
                    st.write(output_text, unsafe_allow_html=True)
                    st.session_state["messages"].append({"role": "assistant", "content": output_text})
            except Exception as e:
                st.error(f"সমস্যা হয়েছে। এরর: {str(e)}")
