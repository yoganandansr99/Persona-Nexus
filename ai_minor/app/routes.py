from app import app
# app/routes.py - FINAL VERSION (ALL IMPROVEMENTS APPLIED)
import os
import json
import cv2
import numpy as np
import time
import traceback
import random
import logging
from flask import render_template, request, jsonify, Response, session, redirect, url_for, flash
from flask_mail import Message
from threading import Thread


import uuid
from threading import Thread

logger = logging.getLogger(__name__)

# --- GLOBAL STORE FOR BACKGROUND ANALYSIS (Non-blocking) ---
analysis_status = {}

# --- HEALTH CHECK ENDPOINT ---
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Docker and load balancers"""
    try:
        from app.db import db
        health_status = {
            "status": "healthy",
            "timestamp": time.time(),
            "version": "1.0.0",
            "services": {
                "app": "running",
                "database": "connected" if db else "disconnected",
                "models": {
                    "whisper": "loaded" if whisper_model else "not_loaded",
                    "sentiment": "loaded" if sentiment_analyzer else "not_loaded"
                }
            }
        }
        return jsonify(health_status), 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({"status": "unhealthy", "error": str(e)}), 503

# Import app and models
from app import app, mail, whisper_model, sentiment_analyzer, groq_client, get_groq_client, rotate_groq_key
from app import EYE_AR_THRESH, EYE_AR_CONSEC_FRAMES, LEFT_EYE_INDICES, RIGHT_EYE_INDICES
from app.utils import eye_aspect_ratio, create_pdf_bytes, analyze_audio_tone
from app.analysis import analyze_personality, calculate_behavioral_metrics, analyze_relevance_batch
from app.email import send_otp_email, send_report_email, send_malpractice_email, send_support_email

# --- Mediapipe Setup (Tasks API — compatible with mediapipe 0.10+) ---
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision

# Path to the face_landmarker.task model file (already in static folder)
_TASK_MODEL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'static', 'face_landmarker.task'
)

face_landmarker = None
try:
    _base_options = mp_python.BaseOptions(model_asset_path=_TASK_MODEL_PATH)
    _options = mp_vision.FaceLandmarkerOptions(
        base_options=_base_options,
        output_face_blendshapes=False,
        output_facial_transformation_matrixes=False,
        num_faces=1,
        min_face_detection_confidence=0.5,
        min_face_presence_confidence=0.5,
        min_tracking_confidence=0.5
    )
    face_landmarker = mp_vision.FaceLandmarker.create_from_options(_options)
    logger.info("MediaPipe FaceLandmarker loaded successfully.")
except Exception as _e:
    logger.error(f"MediaPipe FaceLandmarker failed to load: {_e}. Blink/focus detection disabled.")

from deepface import DeepFace

# --- Cleanup Function ---
def cleanup_uploads():
    folder = app.config['UPLOAD_FOLDER']
    if not os.path.exists(folder): return
    
    # Only delete files older than 1 hour to prevent race conditions with active users
    current_time = time.time()
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                creation_time = os.path.getmtime(file_path)
                if (current_time - creation_time) > 3600:
                    os.unlink(file_path)
        except Exception as e:
            logger.error(f"Failed to delete {file_path}: {e}")

@app.route('/')
def welcome():
    error_msg = request.args.get('error')
    success_msg = request.args.get('success')
    # Preserve recruiter/candidate interview session when entering from join/token links
    if request.args.get('portal_entry') != '1':
        session.clear()
    if error_msg:
        return render_template('welcome.html', error=error_msg)
    return render_template('welcome.html', success=success_msg)

# --- STATUS ENDPOINT (Support Task ID) ---
@app.route('/status')
def get_status():
    task_id = request.args.get('task_id')
    if not task_id or task_id not in analysis_status:
        # Fallback to session for old logic, but prefer task_id
        progress = session.get('analysis_progress', 0)
        message = session.get('analysis_message', 'Processing...')
        return jsonify({"progress": progress, "message": message})
    
    return jsonify(analysis_status[task_id])

# --- 1. VERIFICATION FLOW ---
@app.route('/initiate', methods=['POST'])
def initiate_verification():
    user_data = {
        "name": request.form.get('username'),
        "email": request.form.get('email'),
        "age": request.form.get('age'),
        "gender": request.form.get('gender')
    }

    if not user_data["name"] or not user_data["email"]:
        return "Name and Email are required.", 400

    otp_code = str(random.randint(100000, 999999))
    session['temp_user_data'] = user_data
    session['verification_otp'] = otp_code
    # Improvement #4: OTP expiry (10 minutes)
    session['otp_expiry'] = time.time() + 600
    session['otp_attempts'] = 0

    send_otp_email(user_data['email'], otp_code)
    return redirect(url_for('verify_otp_page'))

@app.route('/verify-otp', methods=['GET'])
def verify_otp_page():
    if 'verification_otp' not in session: return redirect(url_for('welcome'))
    return render_template('verify_otp.html')

@app.route('/check-otp', methods=['POST'])
def check_otp():
    # Improvement #4: Check OTP expiry
    if time.time() > session.get('otp_expiry', 0):
        session.pop('verification_otp', None)
        session.pop('otp_expiry', None)
        session.pop('otp_attempts', None)
        return render_template('verify_otp.html', error="OTP expired. Please go back and try again.")

    user_otp = request.form.get('otp_input')
    real_otp = session.get('verification_otp')

    if user_otp == real_otp:
        session['user_data'] = session['temp_user_data']
        session.pop('verification_otp', None)
        session.pop('otp_expiry', None)
        session.pop('temp_user_data', None)
        session.pop('otp_attempts', None)
        return redirect(url_for('start_interview_session'))
    else:
        attempts = session.get('otp_attempts', 0) + 1
        session['otp_attempts'] = attempts
        if attempts >= 3:
            session.pop('verification_otp', None)
            session.pop('otp_expiry', None)
            session.pop('temp_user_data', None)
            session.pop('otp_attempts', None)
            return render_template('verify_otp.html', fatal_error="Maximum attempts reached. Access Locked.")
        return render_template('verify_otp.html', error=f"Invalid Code. Attempt {attempts}/3.")

# --- 2. INTERVIEW PAGE ---
@app.route('/interview')
def start_interview_session():
    if 'user_data' not in session: return redirect(url_for('welcome'))
    user_data = session['user_data']

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    questions_path = os.path.join(base_dir, 'questions.json')
    
    is_dynamic = False
    
    if session.get('is_practice') or session.get('is_dynamic'):
        questions = ["Can you tell me a little about yourself and your background?"]
        is_dynamic = True
        num_questions = session.get('num_questions', 5)
    elif session.get('custom_questions'):
        questions = session['custom_questions']
        num_questions = len(questions)
    else:
        try:
            with open(questions_path, 'r', encoding='utf-8') as f:
                questions = json.load(f)
        except Exception:
            # Fallback if file missing
            questions = ["Tell me about yourself.", "What is your greatest strength?"]
        num_questions = session.get('num_questions') or len(questions)

    minutes_per_question = session.get('minutes_per_question')
    duration_minutes = session.get('duration_minutes')
    
    return render_template('interview.html', user_data=user_data, questions=questions, 
                          minutes_per_question=minutes_per_question, num_questions=num_questions, 
                          duration_minutes=duration_minutes, is_dynamic=is_dynamic)

@app.route('/api/next_question', methods=['POST'])
def next_question():
    data = request.get_json()
    if not data: return jsonify({"error": "No data"}), 400
    
    previous_answer = data.get('previous_answer', '')
    question_index = data.get('question_index', 1)
    
    active_client = get_groq_client()
    if not active_client:
        return jsonify({"question": "That's interesting. Can you tell me about a time you faced a difficult challenge?"})
        
    prompt = f"""
    You are an expert AI recruiter conducting a conversational behavioral and personality interview.
    The candidate just answered Question {question_index}.
    
    Candidate's previous answer: "{previous_answer}"
    
    TASK: Generate the NEXT interview question.
    - The question MUST be directly related to their previous answer to show you are listening.
    - Dig deeper into their personality, problem-solving skills, or true motivations to prevent generic, rehearsed answers.
    - Keep it strictly to ONE short, clear question.
    - Do NOT output any introductory text, quotes, or markdown. Just the question itself.
    """
    
    try:
        completion = active_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile"
        )
        q = completion.choices[0].message.content.strip()
        q = q.strip('"\'') # Clean any wrapped quotes
        return jsonify({"question": q})
    except Exception as e:
        logger.error(f"Failed to generate next question: {e}")
        return jsonify({"question": "Could you elaborate more on your previous experiences?"})

# --- 3. TRANSCRIPTION ---
@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    if 'audio_data' not in request.files: return jsonify({"error": "No audio"}), 400
    audio_file = request.files['audio_data']
    audio_path = os.path.join(app.config['UPLOAD_FOLDER'], f"temp_audio_{os.urandom(8).hex()}.webm")
    wav_path = audio_path.replace('.webm', '.wav')
    transcript = "Error"
    try:
        audio_file.save(audio_path)
        
        raw_transcript = ""
        # 1. Try Groq API for blazing fast & accurate transcription
        active_client = get_groq_client()
        if active_client:
            # Extract pure audio using ffmpeg to guarantee small file size and perfect format for Groq API
            import subprocess
            subprocess.run(['ffmpeg', '-i', audio_path, '-vn', '-acodec', 'pcm_s16le', '-ar', '16000', '-ac', '1', wav_path, '-y'], 
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            max_retries = 3 # Try up to 3 keys if you have them
            for attempt in range(max_retries):
                try:
                    with open(wav_path, "rb") as file:
                        transcription = active_client.audio.transcriptions.create(
                          file=(os.path.basename(wav_path), file.read()),
                          model="whisper-large-v3-turbo",
                          response_format="json",
                          language="en" # Enforce English to prevent mistaken translation
                        )
                    raw_transcript = transcription.text.strip()
                    break # Success!
                except Exception as groq_err:
                    err_str = str(groq_err).lower()
                    if 'rate_limit' in err_str or 'rate limit' in err_str or '429' in err_str:
                        logger.warning(f"Groq transcription rate limit hit. Rotating key...")
                        active_client = rotate_groq_key()
                    else:
                        logger.error(f"Groq transcription failed: {groq_err}, falling back to local.")
                        break
        
        # 2. Fallback to local model if Groq isn't available or fails
        if not raw_transcript:
            if whisper_model is None:
                raise Exception("Whisper model is not loaded and Groq client is not available.")
            # Set language="en" to stop it from translating to English if it gets confused by accents
            result = whisper_model.transcribe(audio_path, fp16=False, language="en")
            raw_transcript = result.get('text', '').strip()
            
        transcript = raw_transcript
    except Exception as e:
        logger.error(f"Transcription error: {e}")
    finally:
        # Clean up the temp audio files to prevent disk bloat
        for p in [audio_path, wav_path]:
            if os.path.exists(p):
                try: os.remove(p)
                except: pass
    return jsonify({"transcript": transcript})

# --- 3b. NLP CORRECTION (Run only when answer is fully complete) ---
@app.route('/correct_answer', methods=['POST'])
def correct_answer():
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({"error": "No text provided"}), 400
        
    raw_transcript = data.get('text', '').strip()
    if not raw_transcript:
        return jsonify({"transcript": ""})
        
    if groq_client:
        prompt = f"""
        You are an AI proofreader. The following text is a raw speech-to-text transcript from an interview. 
        It may contain phonetic mistakes, missing punctuation, or grammatical errors.
        Please correct the text to make it readable and accurate, while preserving the exact original meaning and tone.
        Return ONLY the corrected text, without any introductory phrases or quotes.
        
        Original Transcript: {raw_transcript}
        """
        transcript = raw_transcript
        
        try:
            chat_completion = groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile"
            )
            transcript = chat_completion.choices[0].message.content.strip()
            return jsonify({"transcript": transcript})
        except Exception as e:
            logger.error(f"Groq NLP correction failed: {e}")
                 
    return jsonify({"transcript": raw_transcript})

# --- 4. GENERATE REPORT ---
def perform_background_analysis(task_id, user_data, text_answers, actual_questions, video_paths, malpractice_flag, session_data):
    """Heavy lifting AI analysis running in a separate thread."""
    from app.auth.helpers import ROLE_PRACTICE_USER
    try:
        # We need to recreate the progress tracking for the task_id
        analysis_status[task_id] = {"progress": 5, "message": "Starting evaluation...", "status": "processing"}

        # ================= RELEVANCE =================
        qa_questions = actual_questions[:len(text_answers)]
        rel_data = analyze_relevance_batch(qa_questions, text_answers)
        relevance_scores = rel_data.get("scores", [])
        expected_points = rel_data.get("expected", [])
        # =============================================

        question_emotions = {}
        question_blinks = []
        question_sentiments = []
        audio_metrics_list = []
        head_pose_list = []
        video_durations = []

        num_questions = len(text_answers)

        for i in range(num_questions):
            analysis_status[task_id]["progress"] = 10 + int((i / num_questions) * 60)
            analysis_status[task_id]["message"] = f'Analyzing video {i+1} of {num_questions}...'

            try:
                sentiment = sentiment_analyzer.polarity_scores(text_answers[i])
                question_sentiments.append(sentiment['compound'])
            except:
                question_sentiments.append(0)

            video_path = video_paths[i] if i < len(video_paths) else None
            emotions_this_question = {}
            blink_count_this_question = 0
            video_duration_secs = 0
            focus_frames = 0
            total_frames_processed = 0

            if video_path and os.path.exists(video_path):
                audio_stats = analyze_audio_tone(video_path)
                audio_metrics_list.append(audio_stats)

                cap = None
                try:
                    cap = cv2.VideoCapture(video_path)
                    fps = cap.get(cv2.CAP_PROP_FPS) or 30
                    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                    video_duration_secs = frame_count / fps if fps > 0 else 0
                    video_durations.append(video_duration_secs)

                    frame_idx = 0
                    blink_counter = 0

                    while True:
                        ret, frame = cap.read()
                        if not ret: break

                        if frame is not None and frame.size > 0:
                            h, w = frame.shape[:2]
                            if w > 640:
                                scale = 640 / w
                                frame = cv2.resize(frame, (640, int(h * scale)))

                            if face_landmarker is not None:
                                try:
                                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                                    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
                                    detection = face_landmarker.detect(mp_image)

                                    if detection.face_landmarks:
                                        lm = detection.face_landmarks[0]
                                        h_f, w_f = frame.shape[:2]
                                        def lm_point(idx): return (lm[idx].x * w_f, lm[idx].y * h_f)

                                        l_pts = [lm_point(idx) for idx in LEFT_EYE_INDICES]
                                        r_pts = [lm_point(idx) for idx in RIGHT_EYE_INDICES]
                                        ear = (eye_aspect_ratio(l_pts) + eye_aspect_ratio(r_pts)) / 2.0

                                        if ear < EYE_AR_THRESH:
                                            blink_counter += 1
                                        else:
                                            if blink_counter >= EYE_AR_CONSEC_FRAMES:
                                                blink_count_this_question += 1
                                            blink_counter = 0

                                        if frame_idx % 10 == 0:
                                            nose_x = lm[1].x
                                            if 0.35 < nose_x < 0.65:
                                                focus_frames += 1
                                            total_frames_processed += 1
                                except Exception: pass

                            if frame_idx % 15 == 0:
                                try:
                                    res = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False, silent=True)
                                    if res:
                                        res_list = res if isinstance(res, list) else [res]
                                        for face_res in res_list:
                                            if 'emotion' in face_res:
                                                emo_dict = face_res['emotion']
                                                dom = face_res['dominant_emotion']
                                                happy_score = emo_dict.get('happy', 0)
                                                # Override neutral/sad/fear when happy signal is present
                                                if dom == 'neutral' and happy_score > 3:
                                                    dom = 'happy'
                                                elif dom in ('sad', 'fear') and happy_score > 15:
                                                    dom = 'happy'
                                                emotions_this_question[dom] = emotions_this_question.get(dom, 0) + 1
                                except: pass
                        frame_idx += 1
                except Exception as e:
                    logger.error(f"Video Error: {e}")
                finally:
                    if cap: cap.release()
                    try: os.remove(video_path)
                    except: pass
            else:
                video_durations.append(30)
                audio_metrics_list.append({"tone": "N/A", "pitch_std": 0, "energy": 0})

            focus_score = (focus_frames / total_frames_processed * 100) if total_frames_processed > 0 else 0
            head_pose_list.append({"focus_percent": round(focus_score, 1)})
            question_emotions[f"Q{i+1}"] = emotions_this_question
            blink_rate = (blink_count_this_question / video_duration_secs) if video_duration_secs > 0 else 0
            question_blinks.append(blink_rate)

        analysis_status[task_id]["progress"] = 75
        analysis_status[task_id]["message"] = 'Running personality analysis...'

        try:
            from concurrent.futures import ThreadPoolExecutor
            with ThreadPoolExecutor(max_workers=2) as executor:
                future_personality = executor.submit(
                    analyze_personality,
                    question_emotions, text_answers, question_sentiments, question_blinks,
                    video_durations, audio_metrics_list, head_pose_list
                )
                personality_profile = future_personality.result()

            behavioral_metrics = calculate_behavioral_metrics(
                question_emotions, question_sentiments, question_blinks,
                audio_metrics_list, head_pose_list,
                personality_profile.get('fluency_stats', [])
            )
        except Exception as e:
            logger.error(f"Analysis Crash: {e}")
            personality_profile = {"primary_color": "Neutral", "description": "Error", "suggestion": "", "scores": {}}
            behavioral_metrics = {"confidence": 0, "fluency": 0, "engagement": 0}

        avg_score = sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0

        analysis_status[task_id]["progress"] = 90
        analysis_status[task_id]["message"] = 'Generating final report...'

        report_data = {
            "user": user_data,
            "profile": personality_profile,
            "behavioral_metrics": behavioral_metrics,
            "question_details": [],
            "malpractice": malpractice_flag,
            "overall_emotion_percentages": {}
        }

        overall_emotions = {}
        for i in range(num_questions):
            q_emotions = question_emotions.get(f"Q{i+1}", {})
            total = sum(q_emotions.values())
            q_perc = {k: round(v / total * 100) for k, v in q_emotions.items()} if total else {}

            wpm = 0
            filler_breakdown = {}
            if 'fluency_stats' in personality_profile and i < len(personality_profile['fluency_stats']):
                wpm = personality_profile['fluency_stats'][i]['wpm']
                filler_breakdown = personality_profile['fluency_stats'][i].get('filler_breakdown', {})

            tone = audio_metrics_list[i]['tone'] if i < len(audio_metrics_list) else "N/A"
            focus = head_pose_list[i]['focus_percent'] if i < len(head_pose_list) else 0
            q_text = actual_questions[i] if i < len(actual_questions) else f"Question {i+1}"
            rel_score = relevance_scores[i] if i < len(relevance_scores) else 0
            exp_pt = expected_points[i] if i < len(expected_points) else "N/A"

            report_data["question_details"].append({
                "question": q_text,
                "answer": text_answers[i],
                "expected_point": exp_pt,
                "sentiment": round(question_sentiments[i], 2),
                "blink_rate": round(question_blinks[i], 2),
                "emotions": q_perc,
                "wpm": wpm,
                "audio_tone": tone,
                "focus_score": focus,
                "relevance": rel_score,
                "filler_breakdown": filler_breakdown
            })
            for k, v in q_emotions.items(): overall_emotions[k] = overall_emotions.get(k, 0) + v

        total_all = sum(overall_emotions.values())
        emotion_percentages = {k: round(v / total_all * 100) for k, v in overall_emotions.items()} if total_all else {}
        report_data["overall_emotion_percentages"] = emotion_percentages

        positive_emo = emotion_percentages.get("happy", 0) + emotion_percentages.get("neutral", 0) + emotion_percentages.get("surprise", 0)
        negative_emo = emotion_percentages.get("sad", 0) + emotion_percentages.get("fear", 0) + emotion_percentages.get("angry", 0) + emotion_percentages.get("disgust", 0)
        emotion_score = max(0, min(100, (positive_emo - (negative_emo * 1.5))))
        
        overall_performance = round((avg_score * 0.7) + (emotion_score * 0.3), 1)
        personality_profile['overall_performance'] = overall_performance
        personality_profile['avg_score'] = round(avg_score, 1)

        # Save to DB
        from app.db import db
        try:
            from app.repositories import reports_repo
            practice_uid = session_data.get("logged_in_user") if session_data.get("portal_role") == ROLE_PRACTICE_USER else None
            if session_data.get("is_candidate"): report_source = "recruiter_candidate"
            elif practice_uid: report_source = "practice"
            else: report_source = "anonymous"
            
            reports_repo.insert_normalized_report(
                db,
                candidate_email=user_data.get("email", ""),
                interview_id=session_data.get("current_interview_id"),
                interview_token=session_data.get("interview_token"),
                practice_user_id=practice_uid,
                source=report_source,
                primary_color=personality_profile.get("primary_color", ""),
                confidence=int(behavioral_metrics.get("confidence", 0)),
                fluency=int(behavioral_metrics.get("fluency", 0)),
                engagement=int(behavioral_metrics.get("engagement", 0)),
                empathy=int(behavioral_metrics.get("empathy", 0)),
                malpractice=malpractice_flag,
                report_data=report_data,
                overall_performance=overall_performance,
                avg_score=round(avg_score, 1)
            )
            if session_data.get("interview_token"):
                db.interviews.update_one({"token": session_data.get("interview_token")}, {"$set": {"is_completed": True}})
        except Exception as db_e:
            logger.error(f"Background DB save error: {db_e}")

        # --- SEND EMAILS ---
        if user_data.get("email"):
            if malpractice_flag:
                try:
                    from app.email import send_malpractice_email
                    send_malpractice_email(
                        user_name=user_data.get("name", "Candidate"),
                        user_email=user_data.get("email"),
                        is_candidate=session_data.get("is_candidate", False),
                        company_email=session_data.get("company_email")
                    )
                except Exception as mail_e:
                    logger.error(f"Background Malpractice Email Error: {mail_e}")
            else:
                try:
                    from app.utils import create_pdf_bytes
                    from app.email import send_report_email
                    pdf_bytes = create_pdf_bytes(
                        user_data, personality_profile, report_data["question_details"],
                        report_data["overall_emotion_percentages"], behavioral_metrics
                    )
                    send_report_email(
                        user_email=user_data.get("email"),
                        user_name=user_data.get("name", "User"),
                        primary_color=personality_profile.get("primary_color", "Neutral"),
                        pdf_bytes=pdf_bytes,
                        overall_performance=overall_performance,
                        avg_score=round(avg_score, 1),
                        is_candidate=session_data.get("is_candidate", False),
                        company_email=session_data.get("company_email")
                    )
                except Exception as mail_e:
                    logger.error(f"Background Email Error: {mail_e}")

        analysis_status[task_id].update({
            "progress": 100,
            "message": "Complete!",
            "status": "completed",
            "report_data": report_data
        })
    except Exception as e:
        logger.error(f"Background Task Failed: {e}")
        traceback.print_exc()
        analysis_status[task_id] = {"status": "failed", "error": str(e)}

@app.route('/report', methods=['POST'])
def generate_report():
    if 'user_data' not in session: return redirect(url_for('welcome'))
    
    try:
        text_answers = json.loads(request.form.get('text_answers'))
        user_data = session['user_data']
        malpractice_val = str(request.form.get('malpractice', '')).strip().lower()
        malpractice_flag = malpractice_val in ['true', '1', 'yes']
    except Exception as e: return f"Error: {e}", 400

    # Load questions (for thread)
    actual_questions = []
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    try:
        with open(os.path.join(base_path, 'questions.json'), 'r', encoding='utf-8') as f:
            actual_questions = json.load(f)
    except: actual_questions = ["Tell me about yourself."]

    # Save video files to disk and prepare paths
    video_paths = []
    for i in range(len(text_answers)):
        video_key = f'video_blob_{i}'
        if video_key in request.files:
            v_file = request.files[video_key]
            v_path = os.path.join(app.config['UPLOAD_FOLDER'], f"task_{uuid.uuid4().hex}_{i}.webm")
            v_file.save(v_path)
            video_paths.append(v_path)
        else: video_paths.append(None)

    task_id = str(uuid.uuid4())
    
    # Prepare session data snippet for thread (can't access 'session' in thread)
    from app.auth.helpers import get_portal_role, ROLE_PRACTICE_USER
    session_data = {
        "is_candidate":        session.get("is_candidate"),
        "interview_token":     session.get("interview_token"),
        "current_interview_id":session.get("current_interview_id"),
        "logged_in_user":      session.get("logged_in_user"),
        "company_email":       session.get("company_email"),   # FIX: was missing — recruiter never got report
        "portal_role":         get_portal_role(),              # FIX: renamed from "role" to match helper key
    }

    # Start thread
    thread = Thread(target=perform_background_analysis, args=(
        task_id, user_data, text_answers, actual_questions, video_paths, malpractice_flag, session_data
    ))
    thread.daemon = True
    thread.start()

    return render_template('processing.html', task_id=task_id)

@app.route('/report_final')
def report_final():
    task_id = request.args.get('task_id')
    if not task_id or task_id not in analysis_status:
        return redirect(url_for('welcome'))
    
    data = analysis_status[task_id]
    if data.get('status') != 'completed':
        return redirect(url_for('welcome')) # Or some error page
    
    report_data = data['report_data']
    # Set to session for download compatibility
    session['report_data'] = report_data
    
    return render_template('report.html', **report_data)

@app.route('/download_report')
def download_report():
    if 'report_data' not in session: return "Error", 404
    report_data = session['report_data']

    b_metrics = report_data.get('behavioral_metrics', {})

    pdf_bytes = create_pdf_bytes(
        report_data['user'],
        report_data['profile'],
        report_data['question_details'],
        report_data.get('overall_emotion_percentages', {}),
        b_metrics
    )
    return Response(pdf_bytes, mimetype='application/pdf', headers={'Content-Disposition': 'attachment; filename=Personality_Report.pdf'})

# --- NEW: DIRECT DISQUALIFICATION ROUTE ---
@app.route('/disqualify')
def disqualify_user():
    if 'user_data' not in session: return redirect(url_for('welcome'))
    user_data = session['user_data']
    
    # 1. Send the Malpractice Emails
    if user_data.get("email"):
        try:
            is_cand = session.get('is_candidate', False)
            comp_email = session.get('company_email', None)
            send_malpractice_email(user_data['name'], user_data['email'], is_candidate=is_cand, company_email=comp_email)
        except Exception as e:
            logger.error(f"Error sending malpractice email: {e}")
        cleanup_uploads()
        
    # 2. Save the failed attempt to MongoDB
    try:
        from app.db import db
        from datetime import datetime
        if db is not None:
            # Legacy Persona_chroma write removed. Unified logic follows.
            try:
                from app.repositories import reports_repo
                from app.auth.helpers import get_portal_role, ROLE_PRACTICE_USER

                practice_uid = (
                    session.get("logged_in_user")
                    if get_portal_role() == ROLE_PRACTICE_USER
                    else None
                )
                if session.get("is_candidate"):
                    report_source = "recruiter_candidate"
                elif practice_uid:
                    report_source = "practice"
                else:
                    report_source = "anonymous"
                reports_repo.insert_normalized_report(
                    db,
                    candidate_email=user_data.get("email", ""),
                    interview_id=session.get("current_interview_id"),
                    interview_token=session.get("interview_token"),
                    practice_user_id=practice_uid,
                    source=report_source,
                    primary_color="Disqualified",
                    confidence=0,
                    fluency=0,
                    engagement=0,
                    empathy=0,
                    malpractice=True,
                    report_data={},
                    overall_performance=0.0,
                    avg_score=0.0,
                )
                if session.get("interview_token"):
                    db.interviews.update_one({"token": session.get("interview_token")}, {"$set": {"is_completed": True}})
            except Exception as rep_e:
                logger.error(f"Normalized reports save (disqualify): {rep_e}")
    except Exception as e:
        logger.error(f"DB save error: {e}")

    session.pop('report_data', None)
    session.pop('user_data', None)
    session.pop('interview_token', None)
    session.pop('current_interview_id', None)
    session.pop('custom_questions', None)
    if session.get('is_candidate'):
        session.pop('is_candidate', None)
        session.pop('company_email', None)
    return render_template('disqualified.html', user_data=user_data)

# --- NEW: DIRECT DB TEST ROUTE ---


# --- NEW: ABOUT US PAGE ROUTE ---
@app.route('/about')
def about_page():
    return render_template('about.html')

# --- NEW: SUPPORT PAGE ROUTE ---
@app.route('/support', methods=['GET', 'POST'])
def support_page():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        query = request.form.get('query')
        if name and email and query:
            try:
                send_support_email(name, email, query)
                return redirect(url_for('support_page', success="Your support query was sent successfully! Our team will contact you soon."))
            except Exception as e:
                logger.error(f"Failed to send support email: {e}")
                return render_template('support.html', error="Failed to send query. Please try again.")
    
    success_msg = request.args.get('success')
    return render_template('support.html', success=success_msg)
