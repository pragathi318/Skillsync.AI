from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import uuid
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Email configuration
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")


# -------------------------------
# 1. Webhook Endpoint
# -------------------------------
@app.route("/webhook", methods=["GET", "POST"])
def webhook_handler():
    if request.method == "GET":
        data = request.args.to_dict()
    else:
        data = request.json

    name = data.get("name")
    email = data.get("email")
    job = data.get("job")
    resume_link = data.get("resume_link")

    print(f"Received request from {name} for {job}")

    # Step 1: Fetch and summarize resume
    resume_text = fetch_resume(resume_link)
    summary = summarize_resume(resume_text)

    # Step 2: Create Interview Agent via Beyond Presence API
    agent_result = create_agent(name, job, summary)

    if agent_result["success"] and agent_result["interview_link"]:
        interview_link = agent_result["interview_link"]

        # Step 3: Send Email from YOUR Gmail
        send_email(email, interview_link, name, job)

        return jsonify({
            "success": True,
            "url": interview_link
        })
    else:
        return jsonify({
            "success": False,
            "error": "Failed to create interview agent"
        }), 500


# -------------------------------
# 2. Fetch Resume
# -------------------------------
def fetch_resume(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
    except Exception as e:
        print(f"Error fetching resume: {e}")
    return ""


# -------------------------------
# 3. AI Resume Summarization
# -------------------------------
def summarize_resume(text):
    prompt = f"""
    Summarize this resume for HR in short paragraph. Include key skills, experience, and education:
    {text}
    """

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:3000",
                "X-Title": "Mock Interview Chatbot"
            },
            json={
                "model": "openai/gpt-4o-mini",
                "messages": [{"role": "user", "content": prompt}]
            }
        )

        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Error summarizing resume: {e}")
        return "Resume summary not available"


# -------------------------------
# 4. Create Interview Agent (Beyond Presence API)
# -------------------------------
def create_agent(name, job, summary):
    system_prompt = f"""You are a professional HR interviewer named David conducting an interview for the {job} position.

Resume Summary: {summary}

Interview Guidelines:
- Start with a warm welcome and brief introduction
- Ask about their interest in the role and company
- Explore their relevant experience with specific examples
- Assess technical skills and cultural fit
- Allow time for their questions
- Close professionally with next steps

Be conversational, ask follow-up questions, and show genuine interest in their responses."""

    try:
        response = requests.post(
            "https://api.bey.dev/v1/agents",
            headers={
                "x-api-key": os.getenv('BEYOND_PRESENCE_API_KEY'),
                "Content-Type": "application/json"
            },
            json={
                "name": f"David - Interview for {name}",
                "avatar_id": "2ed7477f-3961-4ce1-b331-5e4530c55a57",
                "system_prompt": system_prompt,
                "greeting": f"Hello {name}! Welcome to your interview for the {job} position. I'm David, and I'll be conducting your interview today. I'm excited to learn more about you. Let's start - can you tell me a bit about yourself?"
            },
            timeout=30
        )

        print(f"Beyond Presence API Status: {response.status_code}")
        print(f"Beyond Presence API Response: {response.text}")

        if response.status_code == 201 or response.status_code == 200:
            data = response.json()
            agent_id = data.get("id", "")
            interview_link = f"https://bey.chat/{agent_id}"

            return {
                "success": True,
                "agent_id": agent_id,
                "interview_link": interview_link
            }
        else:
            print(f"Beyond Presence API error: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"Error creating agent: {e}")

    return {
        "success": False,
        "agent_id": "",
        "interview_link": ""
    }


# -------------------------------
# 5. Send Email
# -------------------------------
def send_email(to_email, link, name, job):
    if not EMAIL_USER or not EMAIL_PASS:
        print("Email credentials not configured")
        return False

    try:
        msg = MIMEMultipart()
        msg["From"] = EMAIL_USER
        msg["To"] = to_email
        msg["Subject"] = f"{name} Interview Invitation for {job} role"

        body = f"""
Hi {name},

Thank you for applying for the {job} position. Your interview is now ready.

You can start the interview by clicking the link below:
{link}

Please make sure you are in a quiet environment and have a stable internet connection before starting.

If you face any issues or have questions, feel free to reply to this email.

Best of luck!

Regards,
HR Team
        """

        msg.attach(MIMEText(body, "plain"))

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.sendmail(EMAIL_USER, to_email, msg.as_string())
        server.quit()

        print(f"Email sent successfully to {to_email}")
        return True

    except Exception as e:
        print(f"Error sending email: {e}")
        return False


# -------------------------------
# Run Server
# -------------------------------
if __name__ == "__main__":
    print("Starting Python backend server on http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
