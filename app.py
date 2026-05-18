import streamlit as st
import google.genai as genai
import os

# ১. পেজ সেটআপ ও সুন্দর ডিজাইন
st.set_page_config(page_title="আলা হযরত এআই কিতাবখানা", page_icon="📚", layout="centered")

st.title("📚 ইমাম আহমদ রেজা খাঁন আলা হযরত এআই কিতাবখানা")
st.write("আলা হযরতের কিতাব থেকে সরাসরি বাংলায় সঠিক ও নির্ভরযোগ্য উত্তর পাওয়ার নির্ভরযোগ্য মাধ্যম।")
st.markdown("---")

# ২. এপিআই কি সেটআপ (আপনার কি-টি এখানে ফিক্স করে দেওয়া হলো)
os.environ["GEMINI_API_KEY"] = "AIzaSyBLsmQfrQVaSn79WvIlqcbtBvMw1hbI4ew"
client = genai.Client()

# ৩. কিতাব প্রসেস করার ফাংশন
@st.cache_resource
def load_kitab():
    # এই ফাইলটি গিটহাবে থাকতে হবে
    file_path = "kitab.pdf" 
    if os.path.exists(file_path):
        gemini_file = client.files.upload(file=file_path)
        return gemini_file
    return None

gemini_file = load_kitab()

if gemini_file is None:
    st.error("⚠️ 'kitab.pdf' ফাইলটি সার্ভারে খুঁজে পাওয়া যায়নি! গিটহাবে কিতাবটি আপলোড করুন।")
else:
    st.success("✅ আলা হযরতের কিতাব সফলভাবে এআই-এর স্মৃতিতে লোড হয়েছে!")

    # ৪. চ্যাট হিস্ট্রি বা মেসেজ মেমোরি সেটআপ
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # আগের কথাগুলো স্ক্রিনে দেখানো
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # ৫. ইউজারের কাছ থেকে প্রশ্ন নেওয়া
    if user_question := st.chat_input("আপনার প্রশ্নটি এখানে বাংলায় লিখুন..."):
        # স্ক্রিনে ইউজারের প্রশ্ন দেখানো
        with st.chat_message("user"):
            st.markdown(user_question)
        st.session_state.messages.append({"role": "user", "content": user_question})

        # এআই-এর উত্তর খোঁজার লজিক
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("🔍 কিতাব ঘেঁটে উত্তর খোঁজা হচ্ছে...")
            
            system_instruction = (
                "তুমি একজন নির্ভরযোগ্য সুন্নি ইসলামিক এআই অ্যাসিস্ট্যান্ট। তোমার একমাত্র কাজ হলো "
                "ইউজারের আপলোড করা ইমাম আহমদ রেজা খাঁন আলা হযরতের কিতাবের তথ্যের ওপর ভিত্তি করে উত্তর দেওয়া। "
                "যদি প্রশ্নের উত্তর এই নির্দিষ্ট কিতাবে না থাকে, তবে বিনীতভাবে বলবে 'এই বিষয়টি আমার এই কিতাবের ডাটাবেজে নেই।' "
                "কোনো অবস্থাতেই কিতাবের বাইরে থেকে নিজের মতো করে কোনো ফতোয়া বা মনগড়া উত্তর তৈরি করবে না। "
                "ইউজার বাংলায় প্রশ্ন করলে তুমি উর্দু কিতাব থেকে তথ্য নিয়ে তাকে সহজ বাংলায় উত্তর দেবে।"
            )
            
            try:
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=[gemini_file, user_question],
                    config=genai.types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=0.2
                    )
                )
                answer = response.text
            except Exception as e:
                answer = f"একটি সমস্যা হয়েছে: {str(e)}"
                
            message_placeholder.markdown(answer)
            
        st.session_state.messages.append({"role": "assistant", "content": answer})
