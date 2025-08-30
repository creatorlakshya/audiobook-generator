import streamlit as st
from gtts import gTTS
import PyPDF2
import tempfile
import base64
import textwrap

st.set_page_config(page_title="Audiobook Generator", page_icon="🎧", layout="centered")

# --- Title ---
st.title("🎧 Audiobook Generator")
st.write("Upload a `.txt` or `.pdf` file or type your own text. This app will convert it into audio, even if it's long!")

# --- Upload & Input ---
uploaded_file = st.file_uploader("📂 Upload file (.txt or .pdf)", type=["txt", "pdf"])
typed_text = st.text_area("✍️ Or type your custom text here:", height=200)

text_content = ""

# --- Read file if uploaded ---
if uploaded_file is not None:
    ext = uploaded_file.name.split('.')[-1].lower()
    if ext == "txt":
        try:
            text_content = uploaded_file.read().decode("utf-8")
        except:
            st.error("❌ Could not read text file.")
    elif ext == "pdf":
        try:
            reader = PyPDF2.PdfReader(uploaded_file)
            if reader.is_encrypted:
                try:
                    reader.decrypt("")  # Try blank password
                except:
                    st.error("❌ This PDF is encrypted and cannot be read.")
                    text_content = ""
            for page in reader.pages:
                text_content += page.extract_text()
        except Exception as e:
            st.error("❌ Error reading PDF file.")
            st.stop()

# --- Final text source ---
final_text = text_content.strip() if text_content.strip() else typed_text.strip()

st.markdown("---")
st.subheader("🗣️ Voice Settings")
lang = st.selectbox("🌐 Language", ["en", "hi", "fr", "es", "de", "it", "ja", "ru"], index=0)
slow = st.checkbox("🐢 Slow voice?", False)

# --- Split & Generate ---
if st.button("🎤 Convert to Audio (Auto Split)"):

    if not final_text:
        st.warning("Please upload a file or type some text.")
    else:
        # Split text into chunks of ~3000 characters
        max_chars = 3000
        chunks = textwrap.wrap(final_text, max_chars, break_long_words=False, break_on_hyphens=False)

        st.success(f"Total Chunks to Convert: {len(chunks)}")

        for i, chunk in enumerate(chunks):
            try:
                tts = gTTS(text=chunk, lang=lang, slow=slow)
                with tempfile.NamedTemporaryFile(delete=False, suffix=f"_part{i+1}.mp3") as fp:
                    tts.save(fp.name)
                    audio_path = fp.name

                with open(audio_path, "rb") as f:
                    audio_bytes = f.read()
                    b64 = base64.b64encode(audio_bytes).decode()

                    st.markdown(f"### 🔊 Audio Part {i+1}")
                    st.audio(audio_bytes, format="audio/mp3")
                    st.markdown(
                        f'<a href="data:audio/mp3;base64,{b64}" download="audiobook_part_{i+1}.mp3">📥 Download Part {i+1}</a>',
                        unsafe_allow_html=True
                    )

            except Exception as e:
                st.error(f"❌ Error converting part {i+1}: {e}")

# --- Footer ---
st.markdown("---")
st.markdown("<div style='text-align:center;'>Made with 💙 by <b>Lakshya Sharma</b></div>", unsafe_allow_html=True)
