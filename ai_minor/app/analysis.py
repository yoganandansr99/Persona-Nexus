# app/analysis.py
import numpy as np
import re
import logging
from app import get_groq_client, rotate_groq_key

logger = logging.getLogger(__name__)

# --- Helper: Fluency Analysis ---
def analyze_fluency(text, duration_seconds):
    """Analyzes speech pacing and filler words."""
    if not text or duration_seconds <= 0:
        return {"wpm": 0, "fillers": 0, "pacing_label": "N/A"}

    word_count = len(text.split())
    wpm = (word_count / duration_seconds) * 60 # Words Per Minute

    if wpm < 110: pacing_label = "Slow & Deliberate"
    elif wpm > 160: pacing_label = "Fast / Nervous"
    else: pacing_label = "Perfect Pacing"

    # Use regex word boundaries (\b) to prevent false positives (e.g., counting "likely" as "like")
    fillers = [r"\bum\b", r"\buh\b", r"\blike\b", r"\byou know\b", r"\bsort of\b", r"\bmean\b", r"\bactually\b"]
    filler_breakdown = {}
    filler_count = 0
    for f in fillers:
        matches = len(re.findall(f, text.lower()))
        if matches > 0:
            clean_word = f.replace(r"\b", "")
            filler_breakdown[clean_word] = matches
            filler_count += matches

    return {"wpm": round(wpm), "fillers": filler_count, "filler_breakdown": filler_breakdown, "pacing_label": pacing_label}

# --- Main Analysis Function ---
def analyze_personality(emotion_data, text_answers, sentiment_scores, blink_rates, video_durations, audio_metrics, head_pose_stats):
    """Calculates personality profile using Multimodal Analysis."""
    scores = {"🟡 Yellow": 0, "🔵 Blue": 0, "🟢 Green": 0, "🔴 Red": 0}
    ai_analysis_text = "AI analysis not available."
    ai_provider = "Unknown"

    full_transcript = "\n".join([f"Q{i+1}: {ans}" for i, ans in enumerate(text_answers)])
    
    # Summarize new metrics for Gemini
    avg_focus = np.mean([h['focus_percent'] for h in head_pose_stats]) if head_pose_stats else 0
    avg_tone = audio_metrics[0]['tone'] if audio_metrics else "Unknown"
    avg_blink = np.mean(blink_rates) if blink_rates else 0.0

    # --- Call AI API (Groq Primary, Gemini Fallback) ---
    active_client = get_groq_client()
    if active_client and full_transcript.strip():
        prompt = f"""
        Analyze this interview based on Text, Audio, and Visual cues.
        
        TRANSCRIPT:
        {full_transcript}
        
        BEHAVIORAL DATA:
        - Average Focus (Looking at Camera): {avg_focus:.1f}%
        - Voice Tone: {avg_tone} (Monotone=Bored/Calm, Dynamic=Excited/Nervous)
        - Blink Rate: {avg_blink:.2f} blinks/sec

        TASK: Determine the primary personality color (Yellow, Blue, Green, Red) (True Colors Model), and provide a rich feedback description along with a specific growth tip.
        
        GUIDE:
        - High Focus + Balanced Tone -> Green/Red (Confidence)
        - Dynamic Tone + High Sentiment -> Yellow (Enthusiasm)
        - Low Focus + Monotone -> Blue/Green (Introspection or shyness)

        Output Format MUST be EXACTLY:
        Primary Color: [Yellow/Blue/Green/Red]
        Description: [A rich, professional 3-4 sentence paragraph analyzing their tone, focus, and verbal answers. Detail what they did well.]
        Grow Tip: [A highly specific, constructive 1-2 sentence tip on how they can improve their communication or interview skills.]
        """
        
        import time
        max_retries = 3
        for attempt in range(max_retries):
            try:
                chat_completion = active_client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile"
                )
                ai_analysis_text = chat_completion.choices[0].message.content
                ai_provider = "Groq"

                import re
                match = re.search(r"Primary Color:\s*(Yellow|Blue|Green|Red)", ai_analysis_text, re.IGNORECASE)
                if match:
                    color = match.group(1).capitalize()
                    if color == "Yellow": scores["🟡 Yellow"] += 20
                    elif color == "Blue": scores["🔵 Blue"] += 20
                    elif color == "Green": scores["🟢 Green"] += 20
                    elif color == "Red": scores["🔴 Red"] += 20
                break
            except Exception as e:
                err_str = str(e).lower()
                if 'rate_limit' in err_str or 'rate limit' in err_str or '429' in err_str:
                    logger.warning(f"Groq API rate limit in analyze_personality. Rotating key...")
                    active_client = rotate_groq_key()
                else:
                    logger.error(f"Groq API call for personality analysis failed: {e}")
                    if attempt == max_retries - 1:
                        ai_analysis_text = f"Error during AI analysis: {e}"
                    else:
                        time.sleep(1)
    else:
         ai_analysis_text = "AI analysis skipped (no Groq client or transcript)."

    # --- Local Analysis ---
    total_frames = sum(count for emotions in emotion_data.values() for count in emotions.values())
    if total_frames > 0:
        overall_emotions = {}
        for q_emotions in emotion_data.values():
            for emotion, count in q_emotions.items():
                overall_emotions[emotion] = overall_emotions.get(emotion, 0) + count

        if total_frames > 5: # Threshold to ensure we don't skew data based on very few frames
            scores["🟡 Yellow"] += (overall_emotions.get("happy", 0) + overall_emotions.get("surprise", 0)) / total_frames * 8
            scores["🔵 Blue"] += (overall_emotions.get("sad", 0) + overall_emotions.get("fear", 0)) / total_frames * 6
            scores["🟢 Green"] += overall_emotions.get("neutral", 0) / total_frames * 3
            scores["🔴 Red"] += (overall_emotions.get("angry", 0) + overall_emotions.get("disgust",0) ) / total_frames * 6

    full_text_lower = full_transcript.lower()
    if any(word in full_text_lower for word in ["fun", "friend", "party", "social", "excited", "happy", "enjoy", "together"]): scores["🟡 Yellow"] += 3
    if any(word in full_text_lower for word in ["feel", "care", "help", "connect", "understand", "sad", "listen", "support"]): scores["🔵 Blue"] += 3
    if any(word in full_text_lower for word in ["think", "analyze", "learn", "data", "logic", "because", "system", "know", "reason"]): scores["🟢 Green"] += 4
    if any(word in full_text_lower for word in ["lead", "goal", "achieve", "direct", "decide", "action", "result", "control", "power"]): scores["🔴 Red"] += 3

    avg_sentiment = np.mean(sentiment_scores) if sentiment_scores else 0
    if avg_sentiment > 0.15: scores["🟡 Yellow"] += 2; scores["🔵 Blue"] += 1
    elif avg_sentiment < -0.1: scores["🔵 Blue"] += 2; scores["🔴 Red"] += 1
    else: scores["🟢 Green"] += 1

    valid_blink_rates = [rate for rate in blink_rates if rate < 5]
    avg_blink_rate = np.mean(valid_blink_rates) if valid_blink_rates else 0.4
    if avg_blink_rate > 0.7: scores["🔴 Red"] += 1; scores["🔵 Blue"] += 1
    elif avg_blink_rate < 0.2 and avg_blink_rate > 0.01 : scores["🟢 Green"] += 1; scores["🔴 Red"] += 1

    # NEW: Score based on Head Pose (Focus)
    if avg_focus > 85: scores["🔴 Red"] += 3; scores["🟢 Green"] += 3
    elif avg_focus < 60: scores["🔵 Blue"] += 2; scores["🟡 Yellow"] += 1

    # NEW: Score based on Audio Tone
    if "Dynamic" in avg_tone: scores["🟡 Yellow"] += 4; scores["🔴 Red"] += 2
    elif "Monotone" in avg_tone: scores["🟢 Green"] += 3; scores["🔵 Blue"] += 2

    # --- Fluency ---
    fluency_stats = []
    total_fillers = 0
    total_wpm = 0
    count_wpm = 0
    
    for i, text in enumerate(text_answers):
        duration = video_durations[i] if i < len(video_durations) else 30
        stats = analyze_fluency(text, duration)
        fluency_stats.append(stats)
        total_fillers += stats['fillers']
        if stats['wpm'] > 0:
            total_wpm += stats['wpm']
            count_wpm += 1
            
    avg_wpm = int(total_wpm / count_wpm) if count_wpm > 0 else 0

    #q --- Determine Final Profile ---
    if not any(v > 0 for v in scores.values()):
         primary_color = "⚪️ Neutral"
         description = "Not enough data for a clear analysis."
         suggestion = "Try the interview again."
    else:
        primary_color = max(scores, key=scores.get)
        
        # Parse Description and Grow Tip from AI Output
        description_match = re.search(r"Description:\s*(.*?)(?:\nGrow Tip:|$)", ai_analysis_text, re.IGNORECASE | re.DOTALL)
        tip_match = re.search(r"Grow Tip:\s*(.*)", ai_analysis_text, re.IGNORECASE | re.DOTALL)
        
        if description_match:
            description = description_match.group(1).strip()
        else:
            description = "Overall, your interview showed a balance of distinct personality traits."

        speech_tip = ""
        if avg_wpm > 160: speech_tip = " Tip: You speak quite fast. Try slowing down to improve clarity."
        elif avg_wpm < 110 and avg_wpm > 0: speech_tip = " Tip: You speak slowly. Try picking up the pace to maintain engagement."
        if total_fillers > 2: speech_tip += f" Watch out for filler words (detected {total_fillers} total)."

        if tip_match:
            suggestion = tip_match.group(1).strip() + speech_tip
        else:
            suggestion = "Practice active listening and balance your enthusiasm with steady focus." + speech_tip

    return {
        "primary_color": primary_color,
        "description": description,
        "suggestion": suggestion,
        "scores": {k: round(v, 1) for k, v in scores.items()},
        "ai_raw_output": ai_analysis_text,
        "fluency_stats": fluency_stats,
        "avg_wpm": avg_wpm
    }

# ======================================================
# NEW FEATURE 1: BEHAVIORAL METRICS CALCULATION
# ======================================================
def calculate_behavioral_metrics(emotion_data, sentiment_scores, blink_rates, audio_metrics, head_pose_stats, fluency_stats):
    """
    Calculates 0-100 scores for Confidence, Stress, and Engagement.
    """
    total_frames = sum(count for emotions in emotion_data.values() for count in emotions.values())
    overall_emotions = {}
    if total_frames > 0:
        for q_emotions in emotion_data.values():
            for emotion, count in q_emotions.items():
                overall_emotions[emotion] = overall_emotions.get(emotion, 0) + count
    
    happy_pct = overall_emotions.get("happy", 0) / total_frames if total_frames else 0
    fear_pct = overall_emotions.get("fear", 0) / total_frames if total_frames else 0
    sad_pct = overall_emotions.get("sad", 0) / total_frames if total_frames else 0
    neutral_pct = overall_emotions.get("neutral", 0) / total_frames if total_frames else 0

    avg_blink = np.mean(blink_rates) if blink_rates else 0.4
    avg_focus = np.mean([h['focus_percent'] for h in head_pose_stats]) if head_pose_stats else 0
    avg_sentiment = np.mean(sentiment_scores) if sentiment_scores else 0
    avg_wpm = np.mean([f['wpm'] for f in fluency_stats]) if fluency_stats else 0
    total_fillers = sum(f['fillers'] for f in fluency_stats) if fluency_stats else 0
    is_dynamic = any(a['tone'] == 'Dynamic' for a in audio_metrics)

    # 1. Confidence
    confidence = 50 + (avg_focus / 100 * 20) + ((happy_pct + neutral_pct) * 20) - (total_fillers * 2) - (fear_pct * 20)
    if is_dynamic: confidence += 10
    if 110 < avg_wpm < 160: confidence += 10 
    
    # 2. Stress
    # 2. Fluency Score
    fluency_score = 100
    # Penalize for pacing outside the ideal 110-160 WPM range
    if avg_wpm > 0:
        if avg_wpm < 110:
            fluency_score -= (110 - avg_wpm) * 0.5 # Gradual penalty for being too slow
        elif avg_wpm > 160:
            fluency_score -= (avg_wpm - 160) * 0.5 # Gradual penalty for being too fast
    # Penalize for each filler word
    fluency_score -= total_fillers * 4
    
    # 3. Engagement
    engagement = 30 + (avg_focus / 100 * 30) + (happy_pct * 20) + (10 if is_dynamic else 0)
    if avg_sentiment > 0.2: engagement += 10

    # 4. Empathy / Warmth
    empathy = 50 + (happy_pct * 30) + (avg_sentiment * 20)
    if any(a['tone'] == 'Balanced' for a in audio_metrics): empathy += 10
    if overall_emotions.get("angry", 0) > 0: empathy -= 15

    return {
        "confidence": max(0, min(100, int(confidence))),
        "fluency": max(0, min(100, int(fluency_score))),
        "engagement": max(0, min(100, int(engagement))),
        "empathy": max(0, min(100, int(empathy)))
    }

# ======================================================
# NEW FEATURE 2: ANSWER RELEVANCE (Uses Gemini)
# ======================================================
def analyze_relevance_batch(questions, answers):
    """
    Checks if answers are relevant and generates a 1-line key point of what was expected.
    Returns a dict with 'scores' (list of ints) and 'expected' (list of strings).
    """
    active_client = get_groq_client()
    default_res = {"scores": [50] * len(answers), "expected": ["Provide a detailed and professional response."] * len(answers)}
    
    if not questions or not answers or not active_client:
        return default_res

    # Prepare prompt
    prompt = "You are an interview AI judge. Rate the RELEVANCE/DEPTH of the candidate answers and provide a 1-line KEY EXPECTED POINT for each question.\n"
    prompt += "RELEVANCE SCORE: 0-100 (100 = Perfect, 0 = Irrelevant).\n"
    prompt += "EXPECTED POINT: A single sentence (max 15 words) describing the core takeaway or fact a candidate should have mentioned for that specific question.\n\n"
    prompt += "You MUST output ONLY a valid JSON object with keys 'scores' (array of integers) and 'expected' (array of strings).\n"
    prompt += "Example Output: {\"scores\": [95, 20], \"expected\": [\"Should mention relevant technical experience and team collaboration.\", \"Expected an introduction including name, education, and career goals.\"]}\n\n"
    
    limit = min(len(questions), len(answers))
    for i in range(limit):
        prompt += f"Question {i+1}: {questions[i]}\nAnswer {i+1}: {answers[i]}\n\n"

    import time
    text = ""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            chat_completion = active_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}], 
                model="llama-3.3-70b-versatile",
                response_format={"type": "json_object"}
            )
            text = chat_completion.choices[0].message.content
            break
        except Exception as e:
            err_str = str(e).lower()
            if 'rate_limit' in err_str or 'rate limit' in err_str or '429' in err_str:
                logger.warning(f"Groq API rate limit in analyze_relevance_batch. Rotating key...")
                active_client = rotate_groq_key()
            else:
                logger.error(f"Groq API call for relevance analysis failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(1)
            
    if not text:
        return default_res

    import json
    try:
        parsed = json.loads(text.strip())
        scores = [int(s) for s in parsed.get("scores", []) if str(s).isdigit()]
        expected = [str(e) for e in parsed.get("expected", [])]

        # Pad or trim to match answers length
        if len(scores) < len(answers): scores.extend([50] * (len(answers) - len(scores)))
        if len(expected) < len(answers): expected.extend(["Provide a detailed professional response."] * (len(answers) - len(expected)))
        
        return {
            "scores": scores[:len(answers)],
            "expected": expected[:len(answers)]
        }
    except Exception as e:
        logger.error(f"Failed to parse relevance JSON: {e} - Raw text: {text}")
        return default_res