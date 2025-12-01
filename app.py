import streamlit as st
import os
import base64
import json
import numpy as np
import cv2
from PIL import Image
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from groq import Groq
from twilio.rest import Client

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="AI Mask Detection & Alert System",
    page_icon="😷",
    layout="centered"
)

# --- LOAD SECRETS ---
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
    SENDER_EMAIL = st.secrets["SENDER_EMAIL"]
    EMAIL_PASSWORD = st.secrets["EMAIL_PASSWORD"]
    RECEIVER_EMAIL = st.secrets["RECEIVER_EMAIL"]
    TWILIO_ACCOUNT_SID = st.secrets["TWILIO_ACCOUNT_SID"]
    TWILIO_AUTH_TOKEN = st.secrets["TWILIO_AUTH_TOKEN"]
    TWILIO_WHATSAPP_NUMBER = st.secrets["TWILIO_WHATSAPP_NUMBER"]
    MY_WHATSAPP_NUMBER = st.secrets["MY_WHATSAPP_NUMBER"]
except FileNotFoundError:
    st.error("Secrets file not found. Please create a .streamlit/secrets.toml file.")
    st.stop()
except KeyError as e:
    st.error(f"Missing a secret key in your secrets.toml file: {e}")
    st.stop()

# --- BACKEND FUNCTIONS (from our notebook) ---

# 1. Groq LLM Analysis Function
def analyze_image_for_mask(image_bytes):
    try:
        client = Groq(api_key=GROQ_API_KEY)
        base64_image = base64.b64encode(image_bytes).decode('utf-8')
        prompt = """
        Analyze the person in the provided image. Respond with a JSON object that has two keys:
        1. "mask_detected": a boolean (true if a face mask is worn correctly, otherwise false).
        2. "reason": a brief string explaining your choice in 1-2 sentences.
        Provide only the raw JSON object in your response.
        """
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "user", "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}},
                ]},
            ],
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            response_format={"type": "json_object"},
        )
        response_content = chat_completion.choices[0].message.content
        return json.loads(response_content)
    except Exception as e:
        st.error(f"Groq API Error: {e}")
        return None

# 2. Face Detection Function
def detect_faces(image_np):
    try:
        face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        gray = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        
        # Draw rectangles on the original image
        image_with_boxes = image_np.copy()
        for (x, y, w, h) in faces:
            cv2.rectangle(image_with_boxes, (x, y), (x+w, y+h), (255, 0, 0), 2)
            
        return image_with_boxes, len(faces)
    except FileNotFoundError:
        st.error("haarcascade_frontalface_default.xml not found. Please download it.")
        return image_np, 0
    except Exception as e:
        st.error(f"Face detection error: {e}")
        return image_np, 0

# 3. Email Notification Function
def send_alert_email(subject, body, image_bytes):
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECEIVER_EMAIL
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        image = MIMEImage(image_bytes, name="violation_capture.jpg")
        msg.attach(image)

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        st.toast("✅ Email alert sent successfully!", icon="📧")
    except Exception as e:
        st.error(f"Failed to send email: {e}")

# 4. WhatsApp Notification Function
def send_whatsapp_alert(body):
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            from_=f'whatsapp:{TWILIO_WHATSAPP_NUMBER}',
            body=body,
            to=f'whatsapp:{MY_WHATSAPP_NUMBER}'
        )
        st.toast(f"✅ WhatsApp alert sent successfully!", icon="📱")
    except Exception as e:
        st.error(f"Failed to send WhatsApp message: {e}")


# --- STREAMLIT UI ---

st.title("😷 AI Mask Detection & Alert System")
st.write("Powered by Meta Llama 4, Groq, and OpenCV")

# --- SIDEBAR SETTINGS ---
with st.sidebar:
    st.header("⚙️ Settings")
    alerts_enabled = st.toggle("Enable Email/WhatsApp Alerts", value=True, help="Turn this off to disable notifications.")
    
    with st.expander("ℹ️ How to Use"):
        st.write("""
            1. **Upload an image** or **use your camera**.
            2. Click the **Analyze Image** button.
            3. The app will first detect faces using OpenCV.
            4. If a face is found, the image is sent to Meta's Llama 4 model via Groq for mask classification.
            5. If a violation is detected and alerts are enabled, an email and WhatsApp message will be sent.
        """)
    with st.expander("🔑 Required Secrets"):
        st.info("Make sure you have a `.streamlit/secrets.toml` file with all the necessary API keys and credentials.")


# --- IMAGE INPUT ---
st.subheader("1. Provide an Image")
source_img = None
img_file_buffer = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])
if img_file_buffer:
    source_img = img_file_buffer
else:
    st.info("Or, use the camera input below.")
    camera_img = st.camera_input("Take a picture")
    if camera_img:
        source_img = camera_img

# --- ANALYSIS AND DISPLAY ---
if source_img:
    st.subheader("2. Analyze and Get Results")
    
    # Convert uploaded file/camera input to a format OpenCV can use
    image_bytes = source_img.getvalue()
    pil_image = Image.open(source_img).convert('RGB')
    image_np = np.array(pil_image)
    # Convert RGB to BGR for OpenCV
    image_cv = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)

    if st.button("Analyze Image"):
        # Step 1: Face Detection
        with st.spinner('Step 1/2: Detecting faces...'):
            image_with_boxes, num_faces = detect_faces(image_cv)
        
        if num_faces == 0:
            st.warning("No faces were detected in the image. Cannot proceed with mask analysis.")
            st.image(image_with_boxes, caption="Face Detection Result", channels="BGR")
        else:
            st.image(image_with_boxes, caption=f"Face Detection Result: {num_faces} face(s) found!", channels="BGR")
            
            # Step 2: Mask Classification with LLM
            with st.spinner('Step 2/2: Analyzing for mask with Meta Llama 4...'):
                analysis_result = analyze_image_for_mask(image_bytes)
            
            if analysis_result:
                st.subheader("📈 Analysis Complete")
                col1, col2 = st.columns(2)
                
                mask_detected = analysis_result.get("mask_detected", False)
                reason = analysis_result.get("reason", "No reason provided.")

                if mask_detected:
                    col1.success(f"**Status:** Mask Detected")
                else:
                    col1.error(f"**Status:** No Mask Detected (Violation)")
                
                col2.info(f"**AI Reason:** {reason}")

                # Step 3: Send Alerts if needed
                if not mask_detected and alerts_enabled:
                    st.warning("Violation detected! Sending alerts...")
                    alert_subject = "ALERT: Face Mask Violation Detected!"
                    alert_body_whatsapp = f"🚨 *ALERT: Face Mask Violation!* 🚨\n\n*Reason:* {reason}"
                    send_alert_email(alert_subject, reason, image_bytes)
                    send_whatsapp_alert(alert_body_whatsapp)