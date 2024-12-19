
        
import streamlit as st
import json
import random
from datetime import datetime, time, timedelta
import pandas as pd
from collections import Counter
import hashlib
import base64
import plotly.graph_objects as go
import plotly.express as px
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from PIL import Image

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
        return {"moods": [], "journal": [], "gratitude": [], "sleep": [], "memories": [], "goals": [], "memory_vault_password": None}

def save_user_data(username, data):
    with open(f"{username}_data.json", "w") as f:
        json.dump(data, f)

# App sections
def dashboard(username):
    st.header("Dashboard")
    data = load_user_data(username)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        streak = calculate_streak(data)
        st.metric("Current Streak", f"{streak} days")
    
    with col2:
        avg_mood = calculate_average_mood(data)
        st.metric("Average Mood", f"{avg_mood:.2f}/10")
    
    with col3:
        total_entries = len(data["journal"])
        st.metric("Total Journal Entries", total_entries)
    
    st.subheader("Mood Over Time")
    fig = plot_mood_over_time(data)
    st.plotly_chart(fig)
    
    st.subheader("Sleep Patterns")
    fig = plot_sleep_patterns(data)
    st.plotly_chart(fig)

def home():
    st.header("Tara ✨, your new best friend")
    st.subheader("Today's Affirmation")
    st.info(random.choice(AFFIRMATIONS))
    if st.button("Get a new affirmation"):
        st.rerun()

def mood_tracker(username):
    st.header("Mood Tracker")
    data = load_user_data(username)
    
    col1, col2 = st.columns(2)
    
    with col1:
        mood = st.selectbox("How are you feeling today?", MOODS)
        intensity = st.slider("Intensity", 1, 10, 5)
    
    with col2:
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
    
    st.subheader("Your Mood History")
    fig = plot_mood_history(data)
    st.plotly_chart(fig)

def daily_journal(username):
    st.header("Daily Journal")
    data = load_user_data(username)
    
    prompt = st.selectbox("Choose a prompt (optional):", [""] + JOURNAL_PROMPTS)
    entry = st.text_area("Write your journal entry here", value=prompt, height=300)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Save Journal Entry"):
            data["journal"].append({
                "date": datetime.now().isoformat(),
                "entry": entry,
                "word_count": len(entry.split())
            })
            save_user_data(username, data)
            st.success("Journal entry saved successfully!")
    
    with col2:
        st.metric("Word Count", len(entry.split()))
    
    st.subheader("Your Journaling Stats")
    fig = plot_journal_stats(data)
    st.plotly_chart(fig)

def gratitude_log(username):
    st.header("Gratitude Log")
    data = load_user_data(username)
    
    gratitude = st.text_area("What are you grateful for today?")
    
    if st.button("Save Gratitude"):
        data["gratitude"].append({
            "date": datetime.now().isoformat(),
            "gratitude": gratitude
        })
        save_user_data(username, data)
        st.success("Gratitude logged successfully!")
    
    st.subheader("Your Gratitude Cloud")
    fig = plot_gratitude_cloud(data)
    st.plotly_chart(fig)

def sleep_tracker(username):
    st.header("Sleep Tracker")
    data = load_user_data(username)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        date = st.date_input("Date")
    
    with col2:
        duration = st.number_input("Sleep Duration (hours)", min_value=0.0, max_value=24.0, step=0.5)
    
    with col3:
        quality = st.slider("Sleep Quality", 1, 10, 5)
    
    if st.button("Save Sleep Data"):
        data["sleep"].append({
            "date": date.isoformat(),
            "duration": duration,
            "quality": quality
        })
        save_user_data(username, data)
        st.success("Sleep data saved successfully!")
    
    st.subheader("Your Sleep Patterns")
    fig = plot_sleep_patterns(data)
    st.plotly_chart(fig)

def memory_vault(username):
    st.header("Memory Vault")
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
            
            tab1, tab2 = st.tabs(["Add Memory", "View Memories"])
            
            with tab1:
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
            
            with tab2:
                if "memories" in data and data["memories"]:
                    for memory in data["memories"]:
                        with st.expander(f"{memory['title']} - {memory['date'][:10]}"):
                            st.write(memory["memory"])
                            if "image" in memory:
                                image = Image.open(io.BytesIO(base64.b64decode(memory["image"])))
                                st.image(image, use_column_width=True)
                else:
                    st.info("No memories saved yet. Start capturing your special moments!")
            
            if st.button("Lock Memory Vault"):
                st.session_state.memory_vault_unlocked = False
                st.rerun()

def goal_setting(username):
    st.header("Goal Setting")
    data = load_user_data(username)
    
    tab1, tab2 = st.tabs(["Set New Goal", "View Goals"])
    
    with tab1:
        goal = st.text_input("Set a new goal")
        goal_type = st.radio("Goal Type", ["Short-term", "Long-term"])
        deadline = st.date_input("Deadline")
        
        if st.button("Save Goal"):
            data["goals"].append({
                "date_set": datetime.now().isoformat(),
                "goal": goal,
                "type": goal_type,
                "deadline": deadline.isoformat(),
                "completed": False
            })
            save_user_data(username, data)
            st.success("Goal saved successfully!")
    
    with tab2:
        if "goals" in data and data["goals"]:
            for i, goal in enumerate(data["goals"]):
                with st.expander(f"{goal['goal']} - {goal['type']}"):
                    st.write(f"Set on: {goal['date_set'][:10]}")
                    st.write(f"Deadline: {goal['deadline']}")
                    completed = st.checkbox("Completed", value=goal["completed"], key=f"goal_{i}")
                    if completed != goal["completed"]:
                        data["goals"][i]["completed"] = completed
                        save_user_data(username, data)
                        st.success("Goal status updated!")
        else:
            st.info("No goals set yet. Start setting some goals!")

def export_data(username):
    st.header("Export Your Data")
    data = load_user_data(username)
    
    if not any(data.values()):
        st.warning("No data available for export. Start using the app to generate data!")
        return

    st.subheader("Data Preview")
    st.json(data)

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Export Mood Chart (PNG)"):
            img_buffer = generate_mood_chart(data)
            b64 = base64.b64encode(img_buffer.getvalue()).decode()
            href = f'<a href="data:image/png;base64,{b64}" download="{username}_mood_chart.png">Download Mood Chart (PNG)</a>'
            st.markdown(href, unsafe_allow_html=True)
            st.success("Mood chart exported successfully!")

    with col2:
        if st.button("Export Sleep Chart (PNG)"):
            img_buffer = generate_sleep_chart(data)
            b64 = base64.b64encode(img_buffer.getvalue()).decode()
            href = f'<a href="data:image/png;base64,{b64}" download="{username}_sleep_chart.png">Download Sleep Chart (PNG)</a>'
            st.markdown(href, unsafe_allow_html=True)
            st.success("Sleep chart exported successfully!")

    with col3:
        if st.button("Export Full Report (PDF)"):
            pdf_buffer = generate_pdf_report(data, username)
            b64 = base64.b64encode(pdf_buffer.getvalue()).decode()
            href = f'<a href="data:application/pdf;base64,{b64}" download="{username}_mental_health_report.pdf">Download Full Report (PDF)</a>'
            st.markdown(href, unsafe_allow_html=True)
            st.success("PDF report exported successfully!")

# Helper functions
def calculate_streak(data):
    if not data["moods"]:
        return 0
    
    dates = [datetime.fromisoformat(mood["date"]).date() for mood in data["moods"]]
    dates.sort(reverse=True)
    
    streak = 1
    for i in range(1, len(dates)):
        if dates[i] == dates[i-1] - timedelta(days=1):
            streak += 1
        else:
            break
    
    return streak

def calculate_average_mood(data):
    if not data["moods"]:
        return 0
    
    intensities = [mood["intensity"] for mood in data["moods"]]
    return sum(intensities) / len(intensities)

def plot_mood_over_time(data):
    df = pd.DataFrame(data["moods"])
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")
    
    fig = px.line(df, x="date", y="intensity", title="Mood Intensity Over Time")
    fig.update_layout(xaxis_title="Date", yaxis_title="Mood Intensity")
    return fig

def plot_sleep_patterns(data):
    df = pd.DataFrame(data["sleep"])
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["date"], y=df["duration"], name="Duration", mode="lines+markers"))
    fig.add_trace(go.Scatter(x=df["date"], y=df["quality"], name="Quality", mode="lines+markers"))
    fig.update_layout(title="Sleep Patterns Over Time", xaxis_title="Date", yaxis_title="Hours / Quality")
    return fig

def plot_mood_history(data):
    df = pd.DataFrame(data["moods"])
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")
    
    fig = px.scatter(df, x="date", y="intensity", color="mood", hover_data=["notes"],
                     title="Mood History")
    fig.update_layout(xaxis_title="Date", yaxis_title="Mood Intensity")
    return fig

def plot_journal_stats(data):
    df = pd.DataFrame(data["journal"])
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")
    
    fig = px.bar(df, x="date", y="word_count", title="Journal Entry Word Counts")
    fig.update_layout(xaxis_title="Date", yaxis_title="Word Count")
    return fig

def plot_gratitude_cloud(data):
    if not data["gratitude"]:
        return go.Figure()
    
    text = " ".join([entry["gratitude"] for entry in data["gratitude"]])
    words = text.split()
    word_counts = Counter(words)
    
    fig = go.Figure(data=[go.Bar(x=list(word_counts.keys()), y=list(word_counts.values()))])
    fig.update_layout(title="Gratitude Word Frequency", xaxis_title="Words", yaxis_title="Frequency")
    return fig

def generate_mood_chart(data):
    fig = plot_mood_over_time(data)
    img_bytes = fig.to_image(format="png")
    return io.BytesIO(img_bytes)

def generate_sleep_chart(data):
    fig = plot_sleep_patterns(data)
    img_bytes = fig.to_image(format="png")
    return io.BytesIO(img_bytes)

def generate_pdf_report(data, username):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

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

    # Journal summary
    if data["journal"]:
        c.drawString(50, y, "Journal Summary:")
        y -= 20
        total_entries = len(data["journal"])
        total_words = sum(entry["word_count"] for entry in data["journal"])
        c.drawString(70, y, f"Total entries: {total_entries}")
        y -= 15
        c.drawString(70, y, f"Total words written: {total_words}")
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

    # Goal summary
    if data["goals"]:
        c.drawString(50, y, "Goal Summary:")
        y -= 20
        total_goals = len(data["goals"])
        completed_goals = sum(1 for goal in data["goals"] if goal["completed"])
        c.drawString(70, y, f"Total goals: {total_goals}")
        y -= 15
        c.drawString(70, y, f"Completed goals: {completed_goals}")
        y -= 20

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

def login_signup():
    st.header("Welcome to Tara ✨")
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
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        login_signup()
    else:
        st.sidebar.title(f"Welcome, {st.session_state.username}!")
        
        menu = ["Dashboard", "Mood Tracker", "Daily Journal", "Gratitude Log", "Sleep Tracker", "Memory Vault", "Goal Setting", "Export Data", "Logout"]
        choice = st.sidebar.selectbox("Navigation", menu)
        
        if choice == "Dashboard":
            dashboard(st.session_state.username)
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

if __name__ == "__main__":
    main()
        
    
