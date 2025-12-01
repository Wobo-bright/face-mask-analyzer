# AI Mask Detection & Alert System

Powered by **Meta Llama 4**, **Groq**, and **OpenCV**, this system detects face masks in images and sends alerts for violations via WhatsApp.

---

## File Structure

```
nose_mask/
├─ app.py
├─ requirements.txt
├─ haarcascade_frontalface_default.xml
├─ .gitignore
└─ .streamlit/
   └─ secrets.toml
```

- `app.py` → Main application file  
- `haarcascade_frontalface_default.xml` → OpenCV face detection model  
- `.streamlit/secrets.toml` → Contains API keys (Groq, Twilio) — **do not commit to GitHub**  
- `requirements.txt` → Python dependencies  
- `.gitignore` → Excludes secrets and unnecessary files from Git  

---

## Settings

Before running, configure `.streamlit/secrets.toml` with your **Groq API key** and **Twilio credentials**.

---

## How to Use

1. **Provide an Image**  
   - Upload an image (PNG, JPG, JPEG, max 200MB)  
   - Or use the camera input to take a snapshot

2. **Analyze and Get Results**  
   - The AI detects faces in the image  
   - Displays the number of faces detected  
   - Shows mask detection status and AI reasoning  
   - Sends alerts for any detected violations  

---

## Required Secrets

- `GROQ_API_KEY`  
- `TWILIO_ACCOUNT_SID`  
- `TWILIO_AUTH_TOKEN`  

> Make sure `.streamlit/secrets.toml` is **ignored by Git**.  

---

## Features

- Real-time face mask detection  
- Alerts for violations via WhatsApp  
- Easy-to-use interface with image upload or camera input  
- Lightweight and powered by OpenCV + AI  

---

## Example Output

```
Face Detection Result: 1 face(s) found!
Status: No Mask Detected (Violation)
AI Reason: The person in the image is not wearing a face mask.
Violation detected! Sending alerts...
```

---

## Quick Start

1. **Clone the repository**
```bash
git clone https://github.com/Wobo-bright/face-mask-analyzer.git
cd nose_mask
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up secrets**

Create `.streamlit/secrets.toml` with your API keys:
```toml
GROQ_API_KEY="your_groq_api_key_here"
TWILIO_ACCOUNT_SID="your_twilio_sid_here"
TWILIO_AUTH_TOKEN="your_twilio_auth_token_here"
```

4. **Run the app**
```bash
streamlit run app.py
```

5. Open your browser at `http://localhost:8501` and start using the system.
