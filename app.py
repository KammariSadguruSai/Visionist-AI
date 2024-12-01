import streamlit as st
from PIL import Image, ImageDraw
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_core.messages import HumanMessage
import pytesseract
from gtts import gTTS
import io
import base64

# Set Tesseract command for local testing (Windows)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Configure Google Gemini API Key
GOOGLE_API_KEY = ""  # Add your API key
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=GOOGLE_API_KEY)

# Function to convert an image to Base64 format
def image_to_base64(image):
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    return base64.b64encode(buffer.getvalue()).decode()

# Function to run OCR on an image
def run_ocr(image):
    return pytesseract.image_to_string(image).strip()

# Function to analyze the image using Gemini
def analyze_image(image, prompt):
    try:
        image_base64 = image_to_base64(image)
        message = HumanMessage(
            content=[
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": f"data:image/png;base64,{image_base64}"}
            ]
        )
        response = llm.invoke([message])
        return response.content.strip()
    except Exception as e:
        return f"Error: {str(e)}"

# Function to convert text to speech
def text_to_speech(text):
    tts = gTTS(text=text, lang='en', slow=False)
    audio_bytes = io.BytesIO()
    tts.write_to_fp(audio_bytes)
    audio_bytes.seek(0)
    return audio_bytes.getvalue()

# Function to detect and highlight objects in the image
def detect_and_highlight_objects(image):
    draw = ImageDraw.Draw(image)
    objects = [
        {"label": "Obstacle", "bbox": (50, 50, 200, 200)},
        {"label": "Object", "bbox": (300, 100, 500, 300)}
    ]

    for obj in objects:
        bbox = obj['bbox']
        draw.rectangle([bbox[0], bbox[1], bbox[2], bbox[3]], outline="red", width=5)
        draw.text((bbox[0], bbox[1] - 10), obj['label'], fill="red")

    return image, objects

# Main app function
def main():
    st.set_page_config(page_title="AI Assistive Tool", layout="wide", page_icon="🤖")

    # Custom CSS for sidebar, JetBrains Mono font, and bottom bar
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&display=swap');

        [data-testid="stSidebar"] {
            background: linear-gradient(to bottom, #1f4037, #99f2c8);
            color: white;
        }
        [data-testid="stSidebar"] a {
            color: red !important;
            text-decoration: none;
        }
        [data-testid="stSidebar"] a:hover {
            text-decoration: underline;
        }
        .jetbrains-font {
            font-family: 'JetBrains Mono', monospace !important;
            font-size: 16px !important;
        }
        .button-bar {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: #f1f1f1;
            padding: 10px;
            display: flex;
            justify-content: center;
            gap: 10px;
            border-top: 2px solid #ccc;
        }
        .button-bar button {
            background-color: dodgerblue;
            color: white;
            border: none;
            padding: 10px 20px;
            font-size: 16px;
            cursor: pointer;
            border-radius: 5px;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        .button-bar button:hover {
            background-color: darkorange;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title('Visionist AI 💻👁️')
    st.write("""Upload an image to explore and interact with your surroundings more easily!""")

    # Main page for uploading images
    st.header("📂 Upload Image")
    uploaded_file = st.file_uploader("Choose an image (jpg, jpeg, png)", type=['jpg', 'jpeg', 'png'])

    # Sidebar section
    with st.sidebar:
        st.sidebar.title("🔧 Features")
        st.sidebar.markdown("""
        - Scene Understanding  
        - Text-to-Speech  
        - Object & Obstacle Detection  
        """)
        if st.button("🔗 About Developer"):
            st.markdown("""
            **Name:** Kammari Sadguru Sai  
            **GitHub:** [github.com/KammariSadguruSai](https://github.com/KammariSadguruSai)  
            **LinkedIn:** [linkedin.com/in/kammarisadgurusai](https://www.linkedin.com/in/kammarisadgurusai)  
            **Email:** [20259cm025@gmail.com](mailto:20259cm025@gmail.com)
            """)
            st.markdown("---")

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_container_width=True)

        # Bottom button bar
        st.markdown('<div class="button-bar">', unsafe_allow_html=True)
        if st.button("Describe Scene"):
            with st.spinner("Generating scene description..."):
                scene_prompt = "Describe this image briefly."
                scene_description = analyze_image(image, scene_prompt)
                st.subheader("Scene Description")
                st.markdown(f"<div class='jetbrains-font'>{scene_description}</div>", unsafe_allow_html=True)
                st.audio(text_to_speech(scene_description), format='audio/mp3')

        if st.button("Extract Text"):
            with st.spinner("Extracting text..."):
                extracted_text = run_ocr(image)
                st.subheader("Extracted Text")
                if extracted_text:
                    st.markdown(f"<div class='jetbrains-font'>{extracted_text}</div>", unsafe_allow_html=True)
                    st.audio(text_to_speech(extracted_text), format='audio/mp3')
                else:
                    no_text_message = "No text detected in the image."
                    st.markdown(f"<div class='jetbrains-font'>{no_text_message}</div>", unsafe_allow_html=True)
                    st.audio(text_to_speech(no_text_message), format='audio/mp3')

        if st.button("Detect Objects & Obstacles"):
            with st.spinner("Identifying objects and obstacles..."):
                obstacle_prompt = "Identify objects or obstacles in this image and provide their positions for safe navigation."
                obstacle_description = analyze_image(image, obstacle_prompt)
                st.subheader("Objects & Obstacles Detected")
                st.markdown(f"<div class='jetbrains-font'>{obstacle_description}</div>", unsafe_allow_html=True)
                st.audio(text_to_speech(obstacle_description), format='audio/mp3')

                # Highlight detected objects
                highlighted_image, objects = detect_and_highlight_objects(image.copy())
                st.image(highlighted_image, caption="Highlighted Image with Detected Objects", use_container_width=True)

        if st.button("Personalized Assistance"):
            with st.spinner("Providing personalized guidance..."):
                task_prompt = "Provide task-specific guidance based on the content of this image in brief. Include item recognition, label reading, and any relevant context."
                assistance_description = analyze_image(image, task_prompt)
                st.subheader("Personalized Assistance")
                st.markdown(f"<div class='jetbrains-font'>{assistance_description}</div>", unsafe_allow_html=True)
                st.audio(text_to_speech(assistance_description), format='audio/mp3')
        st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
