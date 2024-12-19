
        
import streamlit as st
import json
import random
from datetime import datetime, time
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

# Constants (unchanged)
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

# User authentication and data management functions (unchanged)
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
        return {"moods": [], "journal": [], "gratitude": [], "sleep": [], "memories": [], "goals": [], "memory_vault_password": None}

def save_user_data(username, data):
    with open(f"{username}_data.json", "w") as f:
        json.dump(data, f)

# App sections (unchanged except for goal_setting and sleep_tracker)
def home():
    st.header("Tara ✨, your new best friend 🏠")
    st.subheader("Today's Affirmation")
    st.info(random.choice(AFFIRMATIONS))
    if st.button("Get a new affirmation"):
        st.rerun()

def mood_tracker(username):
    st.header("Mood Tracker 😊")
    data = load_user_data(username)
    
    mood = st.selectbox("How are you feeling today?", MOODS)
    intensity = st.slider("Intensity", 1, 10, 5)
    notes = st.text_area("Notes (optional)")
    
    if st.button("Save Mood"):
        data["moods"].append({
            "date": datetime.now().isoformat(),
            "mood": mood,
            "intensity": intensity,
            "notes": notes
        })
        save_user_data(username, data)
        st.success("Mood saved successfully!")

def daily_journal(username):
    st.header("Daily Journal 📔")
    data = load_user_data(username)
    
    prompt = st.selectbox("Choose a prompt (optional):", [""] + JOURNAL_PROMPTS)
    entry = st.text_area("Write your journal entry here", value=prompt)
    
    if st.button("Save Journal Entry"):
        data["journal"].append({
            "date": datetime.now().isoformat(),
            "entry": entry,
            "word_count": len(entry.split())
        })
        save_user_data(username, data)
        st.success("Journal entry saved successfully!")

def gratitude_log(username):
    st.header("Gratitude Log 🙏")
    data = load_user_data(username)
    
    gratitude = st.text_area("What are you grateful for today?")
    
    if st.button("Save Gratitude"):
        data["gratitude"].append({
            "date": datetime.now().isoformat(),
            "gratitude": gratitude
        })
        save_user_data(username, data)
        st.success("Gratitude logged successfully!")

def sleep_tracker(username):
    st.header("Sleep Tracker 😴")
    data = load_user_data(username)
    
    date = st.date_input("Date")
    duration = st.number_input("Sleep Duration (hours)", min_value=0.0, max_value=24.0, step=0.5)
    quality = st.slider("Sleep Quality", 1, 10, 5)
    
    if st.button("Save Sleep Data"):
        data["sleep"].append({
            "date": date.isoformat(),
            "duration": duration,
            "quality": quality
        })
        save_user_data(username, data)
        st.success("Sleep data saved successfully!")
        
        if duration < 5 and quality < 5:
            st.warning("It looks like you didn't have a great night's sleep. Here are some tips to improve your sleep:")
            st.write("1. Stick to a consistent sleep schedule")
            st.write("2. Create a relaxing bedtime routine")
            st.write("3. Limit screen time before bed")
            st.write("4. Ensure your bedroom is dark, quiet, and cool")
            st.write("5. Avoid caffeine and heavy meals close to bedtime")
            st.write("Remember, good sleep is crucial for your mental and physical health. You've got this!")

def memory_vault(username):
    st.header("Memory Vault 🔒")
    data = load_user_data(username)
    
    if "memory_vault_password" not in data or data["memory_vault_password"] is None:
        st.subheader("Set Your Memory Vault Password")
        new_password = st.text_input("Enter a 4-digit password for your Memory Vault", type="password")
        if st.button("Set Password"):
            if len(new_password) == 4 and new_password.isdigit():
                data["memory_vault_password"] = hash_password(new_password)
                save_user_data(username, data)
                st.success("Password set successfully!")
                st.rerun()
            else:
                st.error("Please enter a valid 4-digit password.")
    else:
        if "memory_vault_unlocked" not in st.session_state:
            st.session_state.memory_vault_unlocked = False

        if not st.session_state.memory_vault_unlocked:
            passcode = st.text_input("Enter your 4-digit Memory Vault password", type="password")
            if st.button("Unlock Vault"):
                if hash_password(passcode) == data["memory_vault_password"]:
                    st.session_state.memory_vault_unlocked = True
                    st.rerun()
                else:
                    st.error("Incorrect password. Please try again.")
        else:
            st.success("Memory Vault Unlocked")
            title = st.text_input("Memory Title")
            memory = st.text_area("Capture a special memory")
            image = st.file_uploader("Upload an image (optional)", type=["jpg", "png", "jpeg"])
            
            if st.button("Save Memory"):
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
                st.success("Memory saved successfully!")
            
            if st.button("Lock Memory Vault"):
                st.session_state.memory_vault_unlocked = False
                st.rerun()

def goal_setting(username):
    st.header("Goal Setting 🎯")
    data = load_user_data(username)
    
    with st.expander("View Your Goals"):
        if "goals" in data and data["goals"]:
            for i, goal in enumerate(data["goals"], 1):
                st.write(f"{i}. {goal['goal']} ({goal['type']}) - Due: {goal['deadline']}")
                if goal['completed']:
                    st.write("   ✅ Completed")
                else:
                    if st.button(f"Mark as Completed", key=f"complete_goal_{i}"):
                        goal['completed'] = True
                        save_user_data(username, data)
                        st.rerun()
        else:
            st.write("You haven't set any goals yet. Start setting some goals below!")
    
    goal = st.text_input("Set a new goal")
    goal_type = st.radio("Goal Type", ["Short-term", "Long-term"])
    deadline = st.date_input("Deadline")
    
    if st.button("Save Goal"):
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
        st.success("Goal saved successfully!")
        st.rerun()

def generate_pdf_report(data, username):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    styles = getSampleStyleSheet()

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, f"Mental Health Report for {username}")

    c.setFont("Helvetica", 12)
    y = height - 80

    # Mood summary
    if data["moods"]:
        c.drawString(50, y, "Mood Summary:")
        y -= 20
        mood_counts = Counter(mood["mood"] for mood in data["moods"])
        for mood, count in mood_counts.most_common(3):
            c.drawString(70, y, f"{mood}: {count} times")
            y -= 15
        y -= 20

    # Journal entries
    if data["journal"]:
        c.drawString(50, y, "Journal Entries:")
        y -= 20
        for entry in data["journal"][-5:]:  # Show last 5 entries
            p = Paragraph(f"Date: {entry['date'][:10]}<br/>Entry: {entry['entry'][:200]}...", styles['Normal'])
            p.wrapOn(c, width - 100, height)
            p.drawOn(c, 70, y - p.height)
            y -= p.height + 10
        y -= 20

    # Gratitude logs
    if data["gratitude"]:
        c.drawString(50, y, "Gratitude Logs:")
        y -= 20
        for gratitude in data["gratitude"][-5:]:  # Show last 5 entries
            p = Paragraph(f"Date: {gratitude['date'][:10]}<br/>Gratitude: {gratitude['gratitude'][:200]}...", styles['Normal'])
            p.wrapOn(c, width - 100, height)
            p.drawOn(c, 70, y - p.height)
            y -= p.height + 10
        y -= 20

    # Sleep summary
    if data["sleep"]:
        c.drawString(50, y, "Sleep Summary:")
        y -= 20
        avg_duration = sum(float(sleep["duration"]) for sleep in data["sleep"]) / len(data["sleep"])
        avg_quality = sum(sleep["quality"] for sleep in data["sleep"]) / len(data["sleep"])
        c.drawString(70, y, f"Average sleep duration: {avg_duration:.2f} hours")
        y -= 15
        c.drawString(70, y, f"Average sleep quality: {avg_quality:.2f}/10")
        y -= 20

    # Goals
    if data["goals"]:
        c.drawString(50, y, "Goals:")
        y -= 20
        for goal in data["goals"]:
            status = "Completed" if goal["completed"] else "In Progress"
            p = Paragraph(f"Goal: {goal['goal']}<br/>Type: {goal['type']}<br/>Deadline: {goal['deadline']}<br/>Status: {status}", styles['Normal'])
            p.wrapOn(c, width - 100, height)
            p.drawOn(c, 70, y - p.height)
            y -= p.height + 10
        y -= 20

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

def export_data(username):
    st.header("Export Your Data 📊")
    data = load_user_data(username)
    
    if not any(data.values()):
        st.warning("No data available for export. Start using the app to generate data!")
        return

    st.subheader("Data Preview")
    st.json(data)

    if st.button("Export Full Report (PDF)"):
        pdf_buffer = generate_pdf_report(data, username)
        b64 = base64.b64encode(pdf_buffer.getvalue()).decode()
        href = f'<a href="data:application/pdf;base64,{b64}" download="{username}_mental_health_report.pdf">Download Full Report (PDF)</a>'
        st.markdown(href, unsafe_allow_html=True)
        st.success("PDF report exported successfully!")

def login_signup():
    st.header("Meet Tara! ✨")
    choice = st.radio("Choose an option", ["Login", "Sign Up"])
    
    users = load_users()
    
    if choice == "Login":
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            if username in users and users[username] == hash_password(password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success("Logged in successfully!")
                st.rerun()
            else:
                st.error("Invalid username or password")
    
    else:
        new_username = st.text_input("Choose a username")
        new_password = st.text_input("Choose a password", type="password")
        
        if st.button("Sign Up"):
            if new_username in users:
                st.error("Username already exists")
            else:
                users[new_username] = hash_password(new_password)
                save_users(users)
                st.success("Account created successfully! Please log in.")

def main():
    try:
        if 'logged_in' not in st.session_state:
            st.session_state.logged_in = False

        if not st.session_state.logged_in:
            login_signup()
        else:
            st.sidebar.title(f"Welcome, {st.session_state.username}!")
            
            menu = ["Home", "Mood Tracker", "Daily Journal", "Gratitude Log", "Sleep Tracker", "Memory Vault", "Goal Setting", "Export Data", "Logout"]
            choice = st.sidebar.selectbox("Navigation", menu)
            
            if choice == "Home":
                home()
            elif choice == "Mood Tracker":
                mood_tracker(st.session_state.username)
            elif choice == "Daily Journal":
                daily_journal(st.session_state.username)
            elif choice == "Gratitude Log":
                gratitude_log(st.session_state.username)
            elif choice == "Sleep Tracker":
                sleep_tracker(st.session_state.username)
            elif choice == "Memory Vault":
                memory_vault(st.session_state.username)
            elif choice == "Goal Setting":
                goal_setting(st.session_state.username)
            elif choice == "Export Data":
                export_data(st.session_state.username)
            elif choice == "Logout":
                st.session_state.logged_in = False
                st.session_state.username = None
                st.rerun()
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
        
    
