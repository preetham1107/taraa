
        
import streamlit as st
import json
import random
from datetime import datetime, time, timedelta
import pandas as pd
from collections import Counter
import hashlib
import base64
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph
from PIL import Image
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from googletrans import Translator
import uuid

# Constants
MOODS = ["Happy", "Sad", "Anxious", "Calm", "Excited", "Angry", "Frustrated", "Confident", "Confused", "Grateful"]
AFFIRMATIONS = [
    "You are capable of amazing things.",
    "Every day is a fresh start.",
    "You are worthy of love and respect.",
    "Your potential is limitless.",
    "You have the power to create change.",
    "You are stronger than you know.",
    "Your efforts are paying off.",
    "You make a difference in the world.",
    "You are deserving of happiness and success.",
    "Your voice matters and deserves to be heard.",
]
JOURNAL_PROMPTS = [
    "What made you smile today?",
    "What's a challenge you're facing, and how can you overcome it?",
    "Describe a moment of kindness you witnessed or experienced.",
    "What are you looking forward to in the near future?",
    "Reflect on a mistake you made and what you learned from it.",
    "What's something new you learned today?",
    "Describe a person who inspires you and why.",
    "What's a goal you're working towards? What steps can you take to achieve it?",
    "Write about a place that makes you feel peaceful.",
    "What's a fear you'd like to overcome? How can you start facing it?",
    "Describe your ideal day. What would you do?",
    "What's a habit you'd like to develop or break?",
    "Write a letter to your future self.",
    "What are three things you're grateful for today?",
    "Describe a recent accomplishment and how it made you feel.",
]

LANGUAGES = {
    "English": "en",
    "Telugu": "te",
    "Hindi": "hi"
}

# User authentication and data management functions
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    try:
        with open("users.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_users(users):
    with open("users.json", "w") as f:
        json.dump(users, f)

def load_user_data(username):
    try:
        with open(f"{username}_data.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "moods": [],
            "journal": [],
            "gratitude": [],
            "sleep": [],
            "memories": [],
            "goals": [],
            "memory_vault_password": None,
            "streak": 0,
            "last_login": None
        }

def save_user_data(username, data):
    with open(f"{username}_data.json", "w") as f:
        json.dump(data, f)

def send_reset_email(email, reset_token):
    sender_email = "your_email@gmail.com"  # Replace with your Gmail
    sender_password = "your_password"  # Replace with your Gmail password

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = email
    message["Subject"] = "Password Reset for Mental Health Journal App"

    body = f"Use this token to reset your password: {reset_token}"
    message.attach(MIMEText(body, "plain"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, email, message.as_string())

def generate_reset_token():
    return str(uuid.uuid4())

def translate_text(text, target_language):
    translator = Translator()
    try:
        translation = translator.translate(text, dest=target_language)
        return translation.text
    except Exception as e:
        st.error(f"Translation error: {str(e)}")
        return text

def update_streak(username):
    data = load_user_data(username)
    today = datetime.now().date()
    last_login = datetime.fromisoformat(data["last_login"]).date() if data["last_login"] else None

    if last_login is None or (today - last_login).days == 1:
        data["streak"] += 1
    elif (today - last_login).days > 1:
        data["streak"] = 1
    
    data["last_login"] = today.isoformat()
    save_user_data(username, data)

def display_streak(username):
    data = load_user_data(username)
    streak = data["streak"]
    st.sidebar.write(f"🔥 Current streak: {streak} days")
    if streak > 0:
        st.sidebar.write("Keep it up! You're doing great!")

# App sections
def home(lang):
    st.header(translate_text("Tara ✨, your new best friend 🏠", lang))
    st.subheader(translate_text("Today's Affirmation", lang))
    st.info(translate_text(random.choice(AFFIRMATIONS), lang))
    if st.button(translate_text("Get a new affirmation", lang)):
        st.rerun()

def mood_tracker(username, lang):
    st.header(translate_text("Mood Tracker 😊", lang))
    data = load_user_data(username)
    
    mood = st.selectbox(translate_text("How are you feeling today?", lang), [translate_text(mood, lang) for mood in MOODS])
    intensity = st.slider(translate_text("Intensity", lang), 1, 10, 5)
    notes = st.text_area(translate_text("Notes (optional)", lang))
    
    if st.button(translate_text("Save Mood", lang)):
        data["moods"].append({
            "date": datetime.now().isoformat(),
            "mood": mood,
            "intensity": intensity,
            "notes": notes
        })
        save_user_data(username, data)
        st.success(translate_text("Mood saved successfully!", lang))

def daily_journal(username, lang):
    st.header(translate_text("Daily Journal 📔", lang))
    data = load_user_data(username)
    
    prompt = st.selectbox(translate_text("Choose a prompt (optional):", lang), [""] + [translate_text(prompt, lang) for prompt in JOURNAL_PROMPTS])
    entry = st.text_area(translate_text("Write your journal entry here", lang), value=prompt)
    
    if st.button(translate_text("Save Journal Entry", lang)):
        data["journal"].append({
            "date": datetime.now().isoformat(),
            "entry": entry,
            "word_count": len(entry.split())
        })
        save_user_data(username, data)
        st.success(translate_text("Journal entry saved successfully!", lang))

def gratitude_log(username, lang):
    st.header(translate_text("Gratitude Log 🙏", lang))
    data = load_user_data(username)
    
    gratitude = st.text_area(translate_text("What are you grateful for today?", lang))
    
    if st.button(translate_text("Save Gratitude", lang)):
        data["gratitude"].append({
            "date": datetime.now().isoformat(),
            "gratitude": gratitude
        })
        save_user_data(username, data)
        st.success(translate_text("Gratitude logged successfully!", lang))

def sleep_tracker(username, lang):
    st.header(translate_text("Sleep Tracker 😴", lang))
    data = load_user_data(username)
    
    date = st.date_input(translate_text("Date", lang))
    duration = st.number_input(translate_text("Sleep Duration (hours)", lang), min_value=0.0, max_value=24.0, step=0.5)
    quality = st.slider(translate_text("Sleep Quality", lang), 1, 10, 5)
    
    if st.button(translate_text("Save Sleep Data", lang)):
        data["sleep"].append({
            "date": date.isoformat(),
            "duration": duration,
            "quality": quality
        })
        save_user_data(username, data)
        st.success(translate_text("Sleep data saved successfully!", lang))
        
        if duration < 5 and quality < 5:
            st.warning(translate_text("It looks like you didn't have a great night's sleep. Here are some tips to improve your sleep:", lang))
            tips = [
                "Stick to a consistent sleep schedule",
                "Create a relaxing bedtime routine",
                "Limit screen time before bed",
                "Ensure your bedroom is dark, quiet, and cool",
                "Avoid caffeine and heavy meals close to bedtime"
            ]
            for tip in tips:
                st.write(translate_text(tip, lang))
            st.write(translate_text("Remember, good sleep is crucial for your mental and physical health. You've got this!", lang))

def memory_vault(username, lang):
    st.header(translate_text("Memory Vault 🔒", lang))
    data = load_user_data(username)
    
    if "memory_vault_password" not in data or data["memory_vault_password"] is None:
        st.subheader(translate_text("Set Your Memory Vault Password", lang))
        new_password = st.text_input(translate_text("Enter a 4-digit password for your Memory Vault", lang), type="password")
        if st.button(translate_text("Set Password", lang)):
            if len(new_password) == 4 and new_password.isdigit():
                data["memory_vault_password"] = hash_password(new_password)
                save_user_data(username, data)
                st.success(translate_text("Password set successfully!", lang))
                st.rerun()
            else:
                st.error(translate_text("Please enter a valid 4-digit password.", lang))
    else:
        if "memory_vault_unlocked" not in st.session_state:
            st.session_state.memory_vault_unlocked = False

        if not st.session_state.memory_vault_unlocked:
            passcode = st.text_input(translate_text("Enter your 4-digit Memory Vault password", lang), type="password")
            if st.button(translate_text("Unlock Vault", lang)):
                if hash_password(passcode) == data["memory_vault_password"]:
                    st.session_state.memory_vault_unlocked = True
                    st.rerun()
                else:
                    st.error(translate_text("Incorrect password. Please try again.", lang))
        else:
            st.success(translate_text("Memory Vault Unlocked", lang))
            title = st.text_input(translate_text("Memory Title", lang))
            memory = st.text_area(translate_text("Capture a special memory", lang))
            image = st.file_uploader(translate_text("Upload an image (optional)", lang), type=["jpg", "png", "jpeg"])
            
            if st.button(translate_text("Save Memory", lang)):
                memory_data = {
                    "date": datetime.now().isoformat(),
                    "title": title,
                    "memory": memory,
                }
                if image:
                    img = Image.open(image)
                    img_byte_arr = io.BytesIO()
                    img.save(img_byte_arr, format='PNG')
                    img_byte_arr = img_byte_arr.getvalue()
                    memory_data["image"] = base64.b64encode(img_byte_arr).decode()
                
                if "memories" not in data:
                    data["memories"] = []
                data["memories"].append(memory_data)
                save_user_data(username, data)
                st.success(translate_text("Memory saved successfully!", lang))
            
            if st.button(translate_text("Lock Memory Vault", lang)):
                st.session_state.memory_vault_unlocked = False
                st.rerun()

def goal_setting(username, lang):
    st.header(translate_text("Goal Setting 🎯", lang))
    data = load_user_data(username)
    
    with st.expander(translate_text("View Your Goals", lang)):
        if "goals" in data and data["goals"]:
            for i, goal in enumerate(data["goals"], 1):
                st.write(f"{i}. {translate_text(goal['goal'], lang)} ({translate_text(goal['type'], lang)}) - {translate_text('Due', lang)}: {goal['deadline']}")
                if goal['completed']:
                    st.write(f"   ✅ {translate_text('Completed', lang)}")
                else:
                    if st.button(translate_text("Mark as Completed", lang), key=f"complete_goal_{i}"):
                        goal['completed'] = True
                        save_user_data(username, data)
                        st.rerun()
        else:
            st.write(translate_text("You haven't set any goals yet. Start setting some goals below!", lang))
    
    goal = st.text_input(translate_text("Set a new goal", lang))
    goal_type = st.radio(translate_text("Goal Type", lang), [translate_text("Short-term", lang), translate_text("Long-term", lang)])
    deadline = st.date_input(translate_text("Deadline", lang))
    
    if st.button(translate_text("Save Goal", lang)):
        if "goals" not in data:
            data["goals"] = []
        data["goals"].append({
            "date_set": datetime.now().isoformat(),
            "goal": goal,
            "type": goal_type,
            "deadline": deadline.isoformat(),
            "completed": False
        })
        save_user_data(username, data)
        st.success(translate_text("Goal saved successfully!", lang))
        st.rerun()

def generate_pdf_report(data, username, lang):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    styles = getSampleStyleSheet()

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, translate_text(f"Mental Health Report for {username}", lang))

    c.setFont("Helvetica", 12)
    y = height - 80

    # Mood summary
    if data["moods"]:
        c.drawString(50, y, translate_text("Mood Summary:", lang))
        y -= 20
        mood_counts = Counter(mood["mood"] for mood in data["moods"])
        for mood, count in mood_counts.most_common(3):
            c.drawString(70, y, f"{translate_text(mood, lang)}: {count} {translate_text('times', lang)}")
            y -= 15
        y -= 20

    # Journal entries
    if data["journal"]:
        c.drawString(50, y, translate_text("Journal Entries:", lang))
        y -= 20
        for entry in data["journal"][-5:]:  # Show last 5 entries
            p = Paragraph(f"{translate_text('Date', lang)}: {entry['date'][:10]}<br/>{translate_text('Entry', lang)}: {translate_text(entry['entry'][:200], lang)}...", styles['Normal'])
            p.wrapOn(c, width - 100, height)
            p.drawOn(c, 70, y - p.height)
            y -= p.height + 10
        y -= 20

    # Gratitude logs
    if data["gratitude"]:
        c.drawString(50, y, translate_text("Gratitude Logs:", lang))
        y -= 20
        for gratitude in data["gratitude"][-5:]:  # Show last 5 entries
            p = Paragraph(f"{translate_text('Date', lang)}: {gratitude['date'][:10]}<br/>{translate_text('Gratitude', lang)}: {translate_text(gratitude['gratitude'][:200], lang)}...", styles['Normal'])
            p.wrapOn(c, width - 100, height)
            p.drawOn(c, 70, y - p.height)
            y -= p.height + 10
        y -= 20

    # Sleep summary
    if data["sleep"]:
        c.drawString(50, y, translate_text("Sleep Summary:", lang))
        y -= 20
        avg_duration = sum(float(sleep["duration"]) for sleep in data["sleep"]) / len(data["sleep"])
        avg_quality = sum(sleep["quality"] for sleep in data["sleep"]) / len(data["sleep"])
        c.drawString(70, y, f"{translate_text('Average sleep duration', lang)}: {avg_duration:.2f} {translate_text('hours', lang)}")
        y -= 15
        c.drawString(70, y, f"{translate_text('Average sleep quality', lang)}: {avg_quality:.2f}/10")
        y -= 20

    # Goals
    if data["goals"]:
        c.drawString(50, y, translate_text("Goals:", lang))
        y -= 20
        for goal in data["goals"]:
            status = translate_text("Completed", lang) if goal["completed"] else translate_text("In Progress", lang)
            p = Paragraph(f"{translate_text('Goal', lang)}: {translate_text(goal['goal'], lang)}<br/>{translate_text('Type', lang)}: {translate_text(goal['type'], lang)}<br/>{translate_text('Deadline', lang)}: {goal['deadline']}<br/>{translate_text('Status', lang)}: {status}", styles['Normal'])
            p.wrapOn(c, width - 100, height)
            p.drawOn(c, 70, y - p.height)
            y -= p.height + 10
        y -= 20

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

def export_data(username, lang):
    st.header(translate_text("Export Your Data 📊", lang))
    data = load_user_data(username)
    
    if not any(data.values()):
        st.warning(translate_text("No data available for export. Start using the app to generate data!", lang))
        return

    st.subheader(translate_text("Data Preview", lang))
    st.json(data)

    if st.button(translate_text("Export Full Report (PDF)", lang)):
        pdf_buffer = generate_pdf_report(data, username, lang)
        b64 = base64.b64encode(pdf_buffer.getvalue()).decode()
        href = f'<a href="data:application/pdf;base64,{b64}" download="{username}_mental_health_report.pdf">{translate_text("Download Full Report (PDF)", lang)}</a>'
        st.markdown(href, unsafe_allow_html=True)
        st.success(translate_text("PDF report exported successfully!", lang))

def login_signup():
    st.header("Meet Tara! ✨")
    choice = st.radio("Choose an option", ["Login", "Sign Up", "Reset Password"])
    
    users = load_users()
    
    if choice == "Login":
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            if username in users and users[username]["password"] == hash_password(password):
                st.session_state.logged_in = True
                st.session_state.username = username
                update_streak(username)
                st.success("Logged in successfully!")
                st.rerun()
            else:
                st.error("Invalid username or password")
    
    elif choice == "Sign Up":
        new_username = st.text_input("Choose a username")
        new_password = st.text_input("Choose a password", type="password")
        email = st.text_input("Enter your email")
        
        if st.button("Sign Up"):
            if new_username in users:
                st.error("Username already exists")
            else:
                users[new_username] = {
                    "password": hash_password(new_password),
                    "email": email
                }
                save_users(users)
                st.success("Account created successfully! Please log in.")
    
    else:  # Reset Password
        email = st.text_input("Enter your email")
        if st.button("Reset Password"):
            user_found = False
            for username, user_data in users.items():
                if user_data["email"] == email:
                    reset_token = generate_reset_token()
                    user_data["reset_token"] = reset_token
                    save_users(users)
                    send_reset_email(email, reset_token)
                    st.success("Password reset email sent. Please check your inbox.")
                    user_found = True
                    break
            if not user_found:
                st.error("Email not found. Please check the email address or sign up.")

        reset_token = st.text_input("Enter reset token")
        new_password = st.text_input("Enter new password", type="password")
        if st.button("Set New Password"):
            for username, user_data in users.items():
                if user_data.get("reset_token") == reset_token:
                    user_data["password"] = hash_password(new_password)
                    del user_data["reset_token"]
                    save_users(users)
                    st.success("Password reset successfully. Please log in with your new password.")
                    return
            st.error("Invalid or expired reset token. Please try again.")

def main():
    try:
        if 'logged_in' not in st.session_state:
            st.session_state.logged_in = False

        if 'language' not in st.session_state:
            st.session_state.language = "en"

        if not st.session_state.logged_in:
            login_signup()
        else:
            st.sidebar.title(f"Welcome, {st.session_state.username}!")
            
            # Language selection
            lang_choice = st.sidebar.selectbox("Select Language", list(LANGUAGES.keys()))
            st.session_state.language = LANGUAGES[lang_choice]

            display_streak(st.session_state.username)
            
            menu = ["Home", "Mood Tracker", "Daily Journal", "Gratitude Log", "Sleep Tracker", "Memory Vault", "Goal Setting", "Export Data", "Logout"]
            choice = st.sidebar.selectbox("Navigation", [translate_text(item, st.session_state.language) for item in menu])
            
            if choice == translate_text("Home", st.session_state.language):
                home(st.session_state.language)
            elif choice == translate_text("Mood Tracker", st.session_state.language):
                mood_tracker(st.session_state.username, st.session_state.language)
            elif choice == translate_text("Daily Journal", st.session_state.language):
                daily_journal(st.session_state.username, st.session_state.language)
            elif choice == translate_text("Gratitude Log", st.session_state.language):
                gratitude_log(st.session_state.username, st.session_state.language)
            elif choice == translate_text("Sleep Tracker", st.session_state.language):
                sleep_tracker(st.session_state.username, st.session_state.language)
            elif choice == translate_text("Memory Vault", st.session_state.language):
                memory_vault(st.session_state.username, st.session_state.language)
            elif choice == translate_text("Goal Setting", st.session_state.language):
                goal_setting(st.session_state.username, st.session_state.language)
            elif choice == translate_text("Export Data", st.session_state.language):
                export_data(st.session_state.username, st.session_state.language)
            elif choice == translate_text("Logout", st.session_state.language):
                st.session_state.logged_in = False
                st.session_state.username = None
                st.rerun()
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
        
    
