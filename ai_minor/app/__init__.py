# app/__init__.py
import os
import google.generativeai as genai
import whisper
from flask import Flask
import dlib
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from flask_mail import Mail

# --- Flask App Initialization ---
# Find the correct path to the 'templates' folder relative to this file
# os.path.dirname(__file__) is the current directory 'app/'
# os.path.dirname(os.path.dirname(__file__)) goes up one level to the project root
template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static') # Also set static folder path

# Create the Flask app instance and tell it where templates/static files are
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

app.secret_key = 'your_very_secret_key_here' # IMPORTANT: Change this for production
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads') # Correct path relative to project root

# --- Create Upload Folder ---
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
print(f"Upload folder set to: {app.config['UPLOAD_FOLDER']}") # Debug print

# --- CONFIGURE GEMINI API ---
print("Configuring APIs and loading models...")
try:
    # IMPORTANT: Replace with your key or use environment variables
    GOOGLE_API_KEY = "AIzaSyAEBaFdmbfTMt1gDa_c5JKCmnXBTPwz_Ec" # <<< PASTE YOUR KEY HERE
    genai.configure(api_key=GOOGLE_API_KEY)
    gemini_model = genai.GenerativeModel('gemini-2.5-pro')
    print("Gemini API configured.")
except Exception as e:
    print(f"!!! ERROR configuring Gemini API: {e}. Analysis will proceed without Gemini.")
    gemini_model = None

# --- Load other models ---
try:
    whisper_model = whisper.load_model("base")
    print("Whisper model loaded.")
except Exception as e:
    print(f"!!! ERROR loading Whisper model: {e}")
    whisper_model = None

sentiment_analyzer = SentimentIntensityAnalyzer()
print("Sentiment Analyzer loaded.")

# --- dlib setup ---
dlib_detector = None
dlib_predictor = None
lStart, lEnd = (42, 48) # Indices for left eye landmarks based on dlib's 68 points
rStart, rEnd = (36, 42) # Indices for right eye landmarks based on dlib's 68 points
EYE_AR_THRESH = 0.25 # Threshold for blink detection
EYE_AR_CONSEC_FRAMES = 2 # Number of consecutive frames below threshold to count as blink
try:
    # Assume predictor file is in the root project directory (one level up from 'app')
    predictor_path_relative = "shape_predictor_68_face_landmarks.dat"
    # Get absolute path relative to this __init__.py file's location
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # Project root
    predictor_path_absolute = os.path.join(base_dir, predictor_path_relative)

    if not os.path.exists(predictor_path_absolute):
         # Try looking inside the 'app' directory as a fallback (less ideal)
         alt_predictor_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), predictor_path_relative)
         if os.path.exists(alt_predictor_path):
             predictor_path_absolute = alt_predictor_path
             print(f"Note: Found predictor file inside 'app' folder: {predictor_path_absolute}")
         else:
             raise RuntimeError(f"Predictor file not found at expected path: {predictor_path_absolute} or {alt_predictor_path}")

    dlib_detector = dlib.get_frontal_face_detector()
    dlib_predictor = dlib.shape_predictor(predictor_path_absolute)
    print(f"Dlib blink detector initialized using predictor: {predictor_path_absolute}")
except RuntimeError as e:
    print(f"\n!!! WARNING: Dlib initialization failed: {e}. Blink detection disabled. !!!\n")
except Exception as e:
    print(f"\n!!! UNEXPECTED ERROR initializing Dlib: {e}. Blink detection disabled. !!!\n")


print("Model loading complete.")

# --- Import Routes (at the bottom) ---
# This import is placed here to avoid circular dependencies (routes needs 'app')

# In app/__init__.py

# ... (previous code) ...

# --- SMTP / EMAIL CONFIGURATION ---
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True

# REPLACE THESE WITH YOUR REAL DETAILS
app.config['MAIL_USERNAME'] = 'promotionp270@gmail.com' 
app.config['MAIL_PASSWORD'] = 'lcza opcj apfp kaoi' # Paste the 16-char App Password here
app.config['MAIL_DEFAULT_SENDER'] = app.config['MAIL_USERNAME']

mail = Mail(app) # Initialize Mail

# ... (rest of the code) ...

from app import routes