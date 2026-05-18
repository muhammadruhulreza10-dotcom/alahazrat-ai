import streamlit as st
from google import genai
from google.genai import types
import os
from pypdf import PdfReader

st.set_page_config(page_title="আলা হযরত এআই কিতাবখানা", page_icon="📚")
st.title("📚 ইমাম আহমদ রেজা খাঁন আলা হযরত এআই কিতাবখানা")
st.write("আলা হযরতের কিতাব থেকে সরাসরি বাংলায় সঠিক ও নির্ভরযোগ্য উত্তর পাওয়ার নির্ভরযোগ্য মাধ্যম।")

# Fetch API Key from Streamlit Secrets
api_key = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=api_key)

# Function to read PDF text directly using PyPDF
@st.cache_resource
def load_kitab_text():
    file_path = "kitab.pdf" # গিটহাবে আপনার পিডিএফ বইটির নাম যেন ঠিক এইরকম থাকে
    if os.path.exists(file_path):
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    return "কিতাব ফাইলটি খুঁজে পাওয়া যায়নি।"

# Load the text content of the book
kitab_context = load_kitab_text()

# Chat interface
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# এখানে ভুলটি শুধরে st.chat_input করা হয়েছে
if prompt := st.chat_input("আলা হযরতের কিতাব সম্পর্কে যেকোনো প্রশ্ন লিখুন..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("কিতাবখানা থেকে উত্তর খোঁজা হচ্ছে..."):
            try:
                # Combine the book context with the user's prompt
                full_prompt = f"তুমি একজন ইসলামিক স্কলার। নিচে দেওয়া কিতাবের তথ্যের আলোকে ব্যবহারকারীর প্রশ্নের উত্তর দাও। কিতাবের বাইরে থেকে কোনো উত্তর দেবে না।\n\nকিতাবের তথ্য:\n{kitab_context}\n\nপ্রশ্ন: {prompt}"
                
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=full_prompt,
                )
                st.write(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"দুঃখিত, উত্তর তৈরিতে সমস্যা হয়েছে। আবার চেষ্টা করুন।")
