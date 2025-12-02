# app/routes.py - FINAL VERSION (WITH QUESTIONS BACKUP)
import os
import json
import cv2
import numpy as np
import time
import traceback
import random
from flask import render_template, request, jsonify, Response, session, redirect, url_for, flash
from flask_mail import Message
from threading import Thread

# Import app and models
from app import app, mail, whisper_model, sentiment_analyzer, dlib_detector, dlib_predictor
from app import lStart, lEnd, rStart, rEnd, EYE_AR_THRESH, EYE_AR_CONSEC_FRAMES
from app.utils import eye_aspect_ratio, create_pdf_bytes, analyze_audio_tone
from app.analysis import analyze_personality_with_gemini
from app.email import send_otp_email, send_report_email

# --- Mediapipe Setup ---
import mediapipe as mp
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5)

from deepface import DeepFace

# --- Cleanup Function ---
def cleanup_uploads():
    folder = app.config['UPLOAD_FOLDER']
    if not os.path.exists(folder): return
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path): os.unlink(file_path)
        except Exception as e: print(f"Failed to delete {file_path}: {e}")

@app.route('/')
def welcome():
    session.clear()
    return render_template('welcome.html')

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
    
    send_otp_email(user_data['email'], otp_code)
    return redirect(url_for('verify_otp_page'))

@app.route('/verify-otp', methods=['GET'])
def verify_otp_page():
    if 'verification_otp' not in session: return redirect(url_for('welcome'))
    return render_template('verify_otp.html')

@app.route('/check-otp', methods=['POST'])
def check_otp():
    user_otp = request.form.get('otp_input')
    real_otp = session.get('verification_otp')
    
    if user_otp == real_otp:
        session['user_data'] = session['temp_user_data']
        session.pop('verification_otp', None)
        session.pop('temp_user_data', None)
        return redirect(url_for('start_interview_session'))
    else:
        return render_template('verify_otp.html', error="Invalid Code.")

# --- 2. INTERVIEW PAGE ---
@app.route('/interview')
def start_interview_session():
    if 'user_data' not in session: return redirect(url_for('welcome'))
    user_data = session['user_data']
    
    questions_path = os.path.join(app.root_path, '..', 'questions.json')
    try:
        with open(questions_path, 'r', encoding='utf-8') as f: questions = json.load(f)
    except Exception: 
        # Fallback if file missing
        questions = ["Tell me about yourself.", "What is your greatest strength?"]

    return render_template('interview.html', user_data=user_data, questions=questions)

# --- 3. TRANSCRIPTION ---
@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    if 'audio_data' not in request.files: return jsonify({"error": "No audio"}), 400
    audio_file = request.files['audio_data']
    audio_path = os.path.join(app.config['UPLOAD_FOLDER'], f"temp_audio_{os.urandom(8).hex()}.webm")
    transcript = "Error"
    try:
        audio_file.save(audio_path)
        result = whisper_model.transcribe(audio_path, fp16=False)
        transcript = result.get('text', '')
    except Exception as e: print(e)
    return jsonify({"transcript": transcript})

# --- 4. GENERATE REPORT ---
@app.route('/report', methods=['POST'])
def generate_report():
    if 'user_data' not in session: return redirect(url_for('welcome'))

    try:
        text_answers = json.loads(request.form.get('text_answers'))
        user_data = session['user_data']
    except Exception as e: return f"Error: {e}", 400
    
    # --- LOAD QUESTIONS TEXT (SAFE & ROBUST) ---
    actual_questions = []
    questions_path = os.path.join(app.root_path, '..', 'questions.json')
    
    # Try loading from file
    try:
        with open(questions_path, 'r', encoding='utf-8') as f: 
            actual_questions = json.load(f)
    except Exception: 
        print("Warning: Could not load questions.json")

    # Fallback List (This prevents 'Q1: Q1')
    if not actual_questions:
        actual_questions = [
            "Tell me about yourself.",
            "What are your strengths and weaknesses?",
            "Where do you see yourself in 5 years?",
            "Why should we hire you?"
        ]

    question_emotions = {}
    question_blinks = []
    question_sentiments = []
    audio_metrics_list = []
    head_pose_list = []
    video_durations = []
    
    num_questions = len(text_answers)

    for i in range(num_questions):
        try:
            sentiment = sentiment_analyzer.polarity_scores(text_answers[i])
            question_sentiments.append(sentiment['compound'])
        except: question_sentiments.append(0)

        video_key = f'video_blob_{i}'
        emotions_this_question = {}
        blink_count_this_question = 0
        video_duration_secs = 0
        focus_frames = 0
        total_frames_processed = 0
        
        if video_key in request.files:
            video_file = request.files[video_key]
            video_path = os.path.join(app.config['UPLOAD_FOLDER'], f"resp_{i}_{os.urandom(8).hex()}.webm")
            video_file.save(video_path)
            
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
                        if frame_idx % 10 == 0:
                            try:
                                res = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False, silent=True)
                                if res: 
                                    dom = res[0]['dominant_emotion']
                                    emotions_this_question[dom] = emotions_this_question.get(dom, 0) + 1
                            except: pass
                        
                        if frame_idx % 5 == 0:
                            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                            results = face_mesh.process(rgb_frame)
                            if results.multi_face_landmarks:
                                nose_x = results.multi_face_landmarks[0].landmark[1].x
                                if 0.35 < nose_x < 0.65: focus_frames += 1
                            total_frames_processed += 1

                            if dlib_predictor and dlib_detector:
                                try:
                                    rects = dlib_detector(gray, 0)
                                    for rect in rects:
                                        shape = dlib_predictor(gray, rect)
                                        shape_np = np.array([(shape.part(j).x, shape.part(j).y) for j in range(68)])
                                        ear = eye_aspect_ratio(shape_np[lStart:lEnd]) + eye_aspect_ratio(shape_np[rStart:rEnd]) / 2.0
                                        if ear < EYE_AR_THRESH: blink_counter += 1
                                        else:
                                            if blink_counter >= EYE_AR_CONSEC_FRAMES: blink_count_this_question += 1
                                            blink_counter = 0
                                        break
                                except: pass
                    frame_idx += 1
            except Exception as e: print(f"Video Error: {e}")
            finally:
                if cap: cap.release()
        else:
            video_durations.append(30)
            audio_metrics_list.append({"tone": "N/A", "pitch_std": 0, "energy": 0})
        
        focus_score = (focus_frames / total_frames_processed * 100) if total_frames_processed > 0 else 0
        head_pose_list.append({"focus_percent": round(focus_score, 1)})

        question_emotions[f"Q{i+1}"] = emotions_this_question
        blink_rate = (blink_count_this_question / video_duration_secs) if video_duration_secs > 0 else 0
        question_blinks.append(blink_rate)

    try:
        personality_profile = analyze_personality_with_gemini(
            question_emotions, text_answers, question_sentiments, question_blinks, 
            video_durations, audio_metrics_list, head_pose_list
        )
    except Exception as e:
        print(f"Analysis Crash: {e}")
        traceback.print_exc()
        personality_profile = {"primary_color": "Neutral", "description": "Error", "suggestion": "", "scores": {}}

    report_data = { "user": user_data, "profile": personality_profile, "question_details": [] }
    overall_emotions = {}
    
    for i in range(num_questions):
        q_emotions = question_emotions.get(f"Q{i+1}", {})
        total = sum(q_emotions.values())
        q_perc = {k: round(v/total*100) for k,v in q_emotions.items()} if total else {}
        
        wpm = 0
        if 'fluency_stats' in personality_profile and i < len(personality_profile['fluency_stats']):
             wpm = personality_profile['fluency_stats'][i]['wpm']

        tone = audio_metrics_list[i]['tone'] if i < len(audio_metrics_list) else "N/A"
        focus = head_pose_list[i]['focus_percent'] if i < len(head_pose_list) else 0

        # --- KEY FIX: MAP INDEX TO ACTUAL TEXT ---
        # If we have text for this index, use it. Otherwise, use "Question X"
        if i < len(actual_questions):
            q_text = actual_questions[i]
        else:
            q_text = f"Question {i+1}"

        report_data["question_details"].append({
            "question": q_text, # Sends "Tell me about yourself"
            "answer": text_answers[i],
            "sentiment": round(question_sentiments[i], 2),
            "blink_rate": round(question_blinks[i], 2),
            "emotions": q_perc,
            "wpm": wpm,
            "audio_tone": tone,
            "focus_score": focus
        })
        for k,v in q_emotions.items(): overall_emotions[k] = overall_emotions.get(k,0) + v

    total_all = sum(overall_emotions.values())
    report_data["overall_emotion_percentages"] = {k: round(v/total_all*100) for k,v in overall_emotions.items()} if total_all else {}
    
    session['report_data'] = report_data

    if user_data.get("email"):
        try:
            pdf_bytes = create_pdf_bytes(
                user_data, 
                personality_profile, 
                report_data['question_details'], 
                report_data.get('overall_emotion_percentages', {})
            )
            send_report_email(user_data['email'], user_data['name'], personality_profile['primary_color'], pdf_bytes)
        except Exception as e:
            print(f"Error sending report email: {e}")

    return render_template('report.html', **report_data)

@app.route('/download_report')
def download_report():
    if 'report_data' not in session: return "Error", 404
    report_data = session['report_data']
    pdf_bytes = create_pdf_bytes(
        report_data['user'], 
        report_data['profile'], 
        report_data['question_details'], 
        report_data.get('overall_emotion_percentages', {})
    )
    return Response(pdf_bytes, mimetype='application/pdf', headers={'Content-Disposition': 'attachment; filename=Personality_Report.pdf'})