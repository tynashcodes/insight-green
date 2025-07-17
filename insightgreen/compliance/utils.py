import google.generativeai as genai
import json

genai.configure(api_key="AIzaSyA5hzMuaEzsJC_mE5L4IorTi_RWcu6PSpQ")

def send_to_gemini(prompt):
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    try:
        return json.loads(response.text)
    except json.JSONDecodeError:
        return {
            "score": 0.0,
            "feedback": "Gemini response was not in valid JSON format.",
            "matched_excerpt": ""
        }
