# app/analysis.py
import numpy as np
from app import gemini_model

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

    fillers = ["um", "uh", "like", "you know", "sort of", "mean", "actually"]
    filler_count = sum(text.lower().count(f) for f in fillers)

    return {"wpm": round(wpm), "fillers": filler_count, "pacing_label": pacing_label}

# --- Main Analysis Function ---
def analyze_personality_with_gemini(emotion_data, text_answers, sentiment_scores, blink_rates, video_durations, audio_metrics, head_pose_stats):
    """Calculates personality profile using Multimodal Analysis."""
    scores = {"🟡 Yellow": 0, "🔵 Blue": 0, "🟢 Green": 0, "🔴 Red": 0}
    gemini_analysis_text = "Gemini analysis not available."

    full_transcript = "\n".join([f"Q{i+1}: {ans}" for i, ans in enumerate(text_answers)])
    
    # Summarize new metrics for Gemini
    avg_focus = np.mean([h['focus_percent'] for h in head_pose_stats]) if head_pose_stats else 0
    avg_tone = audio_metrics[0]['tone'] if audio_metrics else "Unknown"
    avg_blink = np.mean(blink_rates) if blink_rates else 0.0

    # --- Call Gemini API ---
    if gemini_model and full_transcript.strip():
        try:
            prompt = f"""
            Analyze this interview based on Text, Audio, and Visual cues.
            
            TRANSCRIPT:
            {full_transcript}
            
            BEHAVIORAL DATA:
            - Average Focus (Looking at Camera): {avg_focus:.1f}%
            - Voice Tone: {avg_tone} (Monotone=Bored/Calm, Dynamic=Excited/Nervous)
            - Blink Rate: {avg_blink:.2f} blinks/sec

            TASK: Determine the primary personality color (Yellow, Blue, Green, Red) (True Colors Model).
            
            GUIDE:
            - High Focus + Balanced Tone -> Green/Red (Confidence)
            - Dynamic Tone + High Sentiment -> Yellow (Enthusiasm)
            - Low Focus + Monotone -> Blue/Green (Introspection or shyness)

            Output Format:
            Primary Color: [Yellow/Blue/Green/Red]
            Justification: [2-3 sentences explaining how the tone, focus, and text align]
            """
            response = gemini_model.generate_content(prompt)
            
            if not response.parts:
                 gemini_analysis_text = "Gemini response blocked due to safety settings."
            else:
                gemini_analysis_text = response.text
                if "Yellow" in response.text: scores["🟡 Yellow"] += 15
                if "Blue" in response.text: scores["🔵 Blue"] += 15
                if "Green" in response.text: scores["🟢 Green"] += 15
                if "Red" in response.text: scores["🔴 Red"] += 15

        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            gemini_analysis_text = f"Error during Gemini analysis: {e}"
    else:
         gemini_analysis_text = "Gemini analysis skipped."

    # --- Local Analysis ---
    total_frames = sum(count for emotions in emotion_data.values() for count in emotions.values())
    if total_frames > 0:
        overall_emotions = {}
        for q_emotions in emotion_data.values():
            for emotion, count in q_emotions.items():
                overall_emotions[emotion] = overall_emotions.get(emotion, 0) + count

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
        justification = "Analysis based on keywords, emotions, sentiment, and blink rate."
        if "Justification:" in gemini_analysis_text and "Error" not in gemini_analysis_text:
             try:
                 justification_text = gemini_analysis_text.split("Justification:", 1)[1].strip()
                 if "Primary Color:" in gemini_analysis_text:
                     gemini_predicted_color_text = gemini_analysis_text.split("Primary Color:", 1)[1].split("\n",1)[0].strip()
                     justification = f"Gemini Analysis ({gemini_predicted_color_text}): {justification_text}"
                 else:
                     justification = f"Gemini Analysis: {justification_text}"
             except IndexError:
                 justification = f"Gemini Analysis: {gemini_analysis_text}"

        base_descriptions = {
            "🟡 Yellow": "Overall, you seem enthusiastic, social, and optimistic.",
            "🔵 Blue": "Overall, you seem empathetic, emotional, and relationship-oriented.",
            "🟢 Green": "Overall, you seem analytical, logical, and independent.",
            "🔴 Red": "Overall, you seem assertive, direct, and goal-oriented."
        }
        description = f"{justification}\n{base_descriptions.get(primary_color, '')}"

        speech_tip = ""
        if avg_wpm > 160: speech_tip = "\nTip: You speak quite fast. Try slowing down."
        elif avg_wpm < 110 and avg_wpm > 0: speech_tip = "\nTip: You speak slowly. Try picking up the pace."
        if total_fillers > 2: speech_tip += f"\nWatch out for filler words (detected {total_fillers})."

        suggestions_map = {
            "🟡 Yellow": "To grow, practice active listening and balance enthusiasm with focus.",
            "🔵 Blue": "To grow, be mindful of letting emotions cloud objective decisions.",
            "🟢 Green": "To grow, try connecting with the emotional side of decisions.",
            "🔴 Red": "To grow, practice patience and consider the feelings of your team."
        }
        suggestion = suggestions_map.get(primary_color, "") + speech_tip

    return {
        "primary_color": primary_color,
        "description": description,
        "suggestion": suggestion,
        "scores": {k: round(v, 1) for k, v in scores.items()},
        "gemini_raw_output": gemini_analysis_text,
        "fluency_stats": fluency_stats,
        "avg_wpm": avg_wpm
    }