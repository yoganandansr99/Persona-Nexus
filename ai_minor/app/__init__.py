# app/__init__.py
import os
import logging
from dotenv import load_dotenv
load_dotenv()

try:
    import whisper
except ImportError as e:
    logging.warning(f"Whisper module not available: {e}. Speech recognition will be disabled.")
    whisper = None

from flask import Flask
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from groq import Groq
from flask_mail import Mail

# --- Flask App Initialization ---
# Find the correct path to the 'templates' folder relative to this file
# os.path.dirname(__file__) is the current directory 'app/'
# os.path.dirname(os.path.dirname(__file__)) goes up one level to the project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
template_dir = os.path.join(BASE_DIR, 'templates')
static_dir = os.path.join(BASE_DIR, 'static')  # Also set static folder path

# Create the Flask app instance and tell it where templates/static files are
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

# --- Secrets from .env ---
app.secret_key = os.environ.get('SECRET_KEY')
if not app.secret_key:
    logger.warning("No SECRET_KEY set in environment. Using a static fallback key. Please set it in .env for production.")
    app.secret_key = "dev-fallback-secret-key"
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USERNAME')

app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'uploads')  # Correct path relative to project root

# --- Create Upload Folder ---
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
logger.info(f"Upload folder set to: {app.config['UPLOAD_FOLDER']}")

logger.info("Configuring APIs and loading models...")

# --- CONFIGURE GROQ API (MULTI-KEY ROTATION) ---
groq_clients = []
current_groq_idx = 0

# Load all keys starting with GROQ_API_KEY (e.g., GROQ_API_KEY, GROQ_API_KEY_2)
for key, value in os.environ.items():
    if key.startswith('GROQ_API_KEY') and value.strip():
        try:
            client = Groq(api_key=value.strip())
            groq_clients.append(client)
        except Exception as e:
            logger.error(f"Error configuring Groq API for {key}: {e}")

if groq_clients:
    logger.info(f"Loaded {len(groq_clients)} Groq API keys for automatic rotation.")
else:
    logger.warning("No valid GROQ_API_KEY found. AI analysis will be disabled.")

# Helper function to get the currently active client
def get_groq_client():
    if not groq_clients:
        return None
    return groq_clients[current_groq_idx]

# Helper function to rotate to the next API key when rate limited
def rotate_groq_key():
    global current_groq_idx
    if groq_clients:
        current_groq_idx = (current_groq_idx + 1) % len(groq_clients)
        logger.warning(f"Rate limit hit! Rotated to Groq API Key #{current_groq_idx + 1}")
        return groq_clients[current_groq_idx]
    return None

# For backward compatibility with modules that import `groq_client` directly (we will update routes to use get_groq_client instead)
groq_client = get_groq_client()

# --- Load other models ---
try:
    if whisper is not None:
        whisper_model = whisper.load_model("base")
        logger.info("Whisper model loaded.")
    else:
        whisper_model = None
        logger.warning("Whisper module not available. Speech recognition disabled.")
except Exception as e:
    logger.error(f"!!! ERROR loading Whisper model: {e}")
    whisper_model = None

sentiment_analyzer = SentimentIntensityAnalyzer()
logger.info("Sentiment Analyzer loaded.")

# --- Blink Detection Setup (MediaPipe-based, no dlib required) ---
# MediaPipe Face Mesh landmark indices for eyes
# Left eye: outer=33, inner=133, top=159, bottom=145, top2=158, bottom2=153
# Right eye: outer=362, inner=263, top=386, bottom=374, top2=385, bottom2=380
LEFT_EYE_INDICES  = [33, 160, 158, 133, 153, 144]   # P1..P6 for EAR
RIGHT_EYE_INDICES = [362, 385, 387, 263, 373, 380]  # P1..P6 for EAR
EYE_AR_THRESH = 0.25        # EAR threshold for blink
EYE_AR_CONSEC_FRAMES = 2    # Consecutive frames below threshold = blink

logger.info("Blink detection configured using MediaPipe (dlib not required).")

logger.info("Model loading complete.")

# --- SMTP / EMAIL CONFIGURATION ---
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True

mail = Mail(app)  # Initialize Mail

# --- Import Routes (at the bottom) ---
# This import is placed here to avoid circular dependencies (routes needs 'app')
from app import routes

# --- Import New Role-Based Blueprints ---
try:
    from app.routes_user import user_bp
    from app.routes_company import company_bp
    from app.routes_candidate import candidate_bp
    from app.candidate_portal.routes import interview_portal_bp
    from app.practice.routes import practice_bp
    from app.recruiter.routes import recruiter_bp

    app.register_blueprint(user_bp)
    app.register_blueprint(company_bp)
    app.register_blueprint(candidate_bp)
    app.register_blueprint(interview_portal_bp)
    app.register_blueprint(practice_bp)
    app.register_blueprint(recruiter_bp)
except ImportError as e:
    logger.warning(f"New modular blueprints not loaded yet: {e}")
