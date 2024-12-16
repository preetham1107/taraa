import streamlit as st
import json
import random
from datetime import datetime
import pandas as pd
from collections import Counter
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from io import BytesIO
import hashlib
import matplotlib.colors as mcolors

# Constants
MOODS = ["Happy 😊", "Sad 😢", "Anxious 😰", "Calm 😌", "Excited 🎉"]
AFFIRMATIONS = [
    "You are capable of amazing things. ✨",
    "Every day is a fresh start. 🌅",
    "You are worthy of love and respect. 💖",
    "Your potential is limitless. 🚀",
    "You have the power to create change. 💪",
]
PROMPTS = [
    "What made you smile today? 😊",
    "What's a challenge you overcame recently? 💪",
    "What's something you're looking forward to? �期待",
    "Describe a moment of kindness you experienced or witnessed. 🤗",
    "What's a small victory you had today? 🏆",
]
COMPLIMENTS = [
    "You're doing great! Keep up the good work! 🌟",
    "Your dedication to self-improvement is inspiring! 💪",
    "You should be proud of yourself for prioritizing your well-being! 🥇",
    "Your journey is unique and valuable. Keep going! 🚀",
    "You're making progress every day, even if you don't see it! 🌱",
]

# Dark mode CSS
DARK_MODE_CSS = """
<style>
    .stApp {
        background-color: #1E1E1E;
        color: #FFFFFF;
    }
    .stTextInput > div > div > input {
        background-color: #2E2E2E;
        color: #FFFFFF;
    }
    .stTextArea > div > div > textarea {
        background-color: #2E2E2E;
        color: #FFFFFF;
    }
    .stSelectbox > div > div > select {
        background-color: #2E2E2E;
        color: #FFFFFF;
    }
    .stDateInput > div > div > input {
        background-color: #2E2E2E;
        color: #FFFFFF;
    }
    .stButton > button {
        background-color: #4CAF50;
        color: #FFFFFF;
    }
</style>
"""

# User authentication functions
def load_users():
    try:
        with open("users.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_users(users):
    with open("users.json", "w") as f:
        json.dump(users, f)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password):
    users = load_users()
    if username in users:
        return False
    users[username] = hash_password(password)
    save_users(users)
    return True

def authenticate_user(username, password):
    users = load_users()
    return username in users and users[username] == hash_password(password)

# Data management functions
def load_user_data(username):
    try:
        with open(f"{username}_data.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"moods": [], "journal": [], "gratitude": []}

def save_user_data(username, data):
    with open(f"{username}_data.json", "w") as f:
        json.dump(data, f)

# App sections
def home():
    st.header("✨ Tara, your new best friend ✨")
    st.subheader("Today's Affirmation 💖")
    st.info(random.choice(AFFIRMATIONS))
    if st.button("Get a new affirmation 🔄"):
        st.rerun()

def mood_tracker(username):
    st.header("Mood Tracker 📊")
    date = st.date_input("Date 📅")
    mood = st.select_slider("How are you feeling today? 😊😢😰😌🎉", options=MOODS)
    intensity = st.slider("Intensity 🔥", 1, 10, 5)
    
    color = st.color_picker("Choose a color to represent your mood 🎨", "#1E90FF")
    
    if st.button("Save Mood 💾"):
        data = load_user_data(username)
        data["moods"].append({"date": str(date), "mood": mood, "intensity": intensity, "color": color})
        save_user_data(username, data)
        st.success("Mood saved successfully! 🎉")
        st.balloons()

def daily_journal(username):
    st.header("Daily Journal 📓")
    date = st.date_input("Date 📅")
    prompt = st.checkbox("Use a prompt? 💡")
    if prompt:
        selected_prompt = st.selectbox("Choose a prompt", PROMPTS)
        st.write(selected_prompt)
    entry = st.text_area("Your journal entry ✍️")
    
    word_count = len(entry.split())
    st.write(f"Word count: {word_count} 📊")
    
    if st.button("Save Journal Entry 💾"):
        if entry.strip():
            data = load_user_data(username)
            data["journal"].append({"date": str(date), "entry": entry, "word_count": word_count})
            save_user_data(username, data)
            st.success("Journal entry saved successfully! 🎉")
            if word_count >= 100:
                st.balloons()
                st.success("Great job! You wrote over 100 words! 🏆")
        else:
            st.warning("Please write something before saving. ✍️")

def gratitude_log(username):
    st.header("Gratitude Log 🙏")
    date = st.date_input("Date 📅")
    gratitude = st.text_area("What are you grateful for today? 💖")
    
    if st.button("Save Gratitude 💾"):
        if gratitude.strip():
            data = load_user_data(username)
            data["gratitude"].append({"date": str(date), "gratitude": gratitude})
            save_user_data(username, data)
            st.success("Gratitude entry saved successfully! 🎉")
            st.balloons()
        else:
            st.warning("Please write something before saving. ✍️")

def insights_and_trends(username):
    st.header("Insights & Trends 📊")
    st.write("This section provides an overview of your mood patterns, gratitude entries, and journal reflections. 🧐")
    data = load_user_data(username)
    
    if data["moods"]:
        with st.expander("Mood Trends 📈", expanded=True):
            df_moods = pd.DataFrame(data["moods"])
            df_moods["date"] = pd.to_datetime(df_moods["date"])
            df_moods = df_moods.sort_values("date")
            
            fig = plotly.graph_objs.Figure(data=[
                plotly.graph_objs.Bar(x=df_moods["date"], y=df_moods["intensity"], marker_color=df_moods["color"])
            ])
            fig.update_layout(title="Mood Intensity Over Time", xaxis_title="Date", yaxis_title="Intensity")
            st.plotly_chart(fig)
            
            mood_counts = Counter(df_moods["mood"])
            st.subheader("Mood Frequency 📊")
            for mood, count in mood_counts.items():
                st.write(f"{mood}: {count} times")
            
            most_common_mood = mood_counts.most_common(1)[0][0]
            st.write(f"Your most common mood: {most_common_mood} 🔍")
    else:
        st.info("No mood data available yet. Start tracking your mood to see trends! 📊")
    
    if data["gratitude"]:
        with st.expander("Gratitude Summary 🙏", expanded=True):
            st.subheader("Recent Gratitude Entries 📝")
            for entry in data["gratitude"][-5:]:
                st.write(f"{entry['date']}: {entry['gratitude']}")
            
            all_gratitude = " ".join([entry["gratitude"] for entry in data["gratitude"]])
            words = all_gratitude.lower().split()
            word_counts = Counter(words)
            st.subheader("Most Common Words in Gratitude Entries 🔤")
            st.write(", ".join(word for word, _ in word_counts.most_common(5)))
    else:
        st.info("No gratitude entries yet. Start logging what you're grateful for! 🙏")
    
    if data["journal"]:
        with st.expander("Journal Reflections 📓", expanded=True):
            st.subheader("Journal Entry Summary 📊")
            total_entries = len(data['journal'])
            total_words = sum(entry['word_count'] for entry in data['journal'])
            st.write(f"Total journal entries: {total_entries} 📚")
            st.write(f"Total words written: {total_words} ✍️")
            st.progress(min(total_words / 10000, 1.0), text=f"Writing goal: {total_words}/10000 words 🎯")
            st.write("Most recent entry:")
            st.write(data["journal"][-1]["date"])
            st.write(data["journal"][-1]["entry"][:100] + "..." if len(data["journal"][-1]["entry"]) > 100 else data["journal"][-1]["entry"])
    else:
        st.info("No journal entries yet. Start writing in your journal to see reflections! 📝")

def export_data(username):
    st.header("Export Your Data 📤")
    data = load_user_data(username)
    
    if not any(data.values()):
        st.warning("No data available for export. Start using the app to generate data! 📊")
        return

    with st.expander("Data Preview 👀", expanded=True):
        df_moods = pd.DataFrame(data["moods"])
        df_journal = pd.DataFrame(data["journal"])
        df_gratitude = pd.DataFrame(data["gratitude"])
        
        st.subheader("Mood Tracker Data 😊😢😰😌🎉")
        st.dataframe(df_moods)
        
        st.subheader("Daily Journal Data 📓")
        st.dataframe(df_journal)
        
        st.subheader("Gratitude Log Data 🙏")
        st.dataframe(df_gratitude)

    st.subheader("Export Options 🔽")
    selected_types = st.multiselect(
        "Select data types to export",
        ["Mood Tracker", "Daily Journal", "Gratitude Log"],
        default=["Mood Tracker", "Daily Journal", "Gratitude Log"]
    )

    if selected_types:
        export_data = {}
        if "Mood Tracker" in selected_types:
            export_data["moods"] = data["moods"]
        if "Daily Journal" in selected_types:
            export_data["journal"] = data["journal"]
        if "Gratitude Log" in selected_types:
            export_data["gratitude"] = data["gratitude"]
        
        df_export = pd.DataFrame([item for sublist in export_data.values() for item in sublist])
        
        col1, col2 = st.columns(2)
        
        with col1:
            csv = df_export.to_csv(index=False)
            st.download_button(
                label="Download as CSV 📄",
                data=csv,
                file_name="mental_health_journal_data.csv",
                mime="text/csv",
            )
        
        with col2:
            pdf_buffer = generate_pdf(export_data)
            st.download_button(
                label="Download as PDF 📑",
                data=pdf_buffer,
                file_name="mental_health_journal_data.pdf",
                mime="application/pdf",
            )
        
        if st.button("Export Complete 🎉"):
            st.success("Data exported successfully! 🚀")
            st.write(random.choice(COMPLIMENTS))
    else:
        st.warning("Please select at least one data type to export. 🔍")

def login_signup():
    st.title("Mental Health Journal: Login/Signup 🔐")
    
    tab1, tab2 = st.tabs(["Login 🔑", "Sign Up 📝"])
    
    with tab1:
        st.header("Login 🔑")
        login_username = st.text_input("Username 👤", key="login_username")
        login_password = st.text_input("Password 🔒", type="password", key="login_password")
        if st.button("Login 🚀"):
            if authenticate_user(login_username, login_password):
                st.session_state.logged_in = True
                st.session_state.username = login_username
                st.success("Logged in successfully! 🎉")
                st.rerun()
            else:
                st.error("Invalid username or password ❌")
    
    with tab2:
        st.header("Sign Up 📝")
        signup_username = st.text_input("Choose a username 👤", key="signup_username")
        signup_password = st.text_input("Choose a password 🔒", type="password", key="signup_password")
        confirm_password = st.text_input("Confirm password 🔒", type="password")
        if st.button("Sign Up 🚀"):
            if signup_password != confirm_password:
                st.error("Passwords do not match ❌")
            elif len(signup_password) < 6:
                st.error("Password must be at least 6 characters long ❌")
            elif register_user(signup_username, signup_password):
                st.success("Account created successfully! Please log in. 🎉")
            else:
                st.error("Username already exists ❌")

def toggle_dark_mode():
    if 'dark_mode' not in st.session_state:
        st.session_state.dark_mode = False
    if st.sidebar.button("Toggle Dark Mode 🌓"):
        st.session_state.dark_mode = not st.session_state.dark_mode
    
    if st.session_state.dark_mode:
        st.markdown(DARK_MODE_CSS, unsafe_allow_html=True)

def main():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    toggle_dark_mode()

    if not st.session_state.logged_in:
        login_signup()
    else:
        st.sidebar.title(f"Welcome, {st.session_state.username}! 👋")
        
        menu = ["Home 🏠", "Mood Tracker 😊", "Daily Journal 📓", "Gratitude Log 🙏", "Insights & Trends 📊", "Export Data 📤", "Logout 🚪"]
        choice = st.sidebar.selectbox("Navigation 🧭", menu)
        
        if choice == "Home 🏠":
            home()
        elif choice == "Mood Tracker 😊":
            mood_tracker(st.session_state.username)
        elif choice == "Daily Journal 📓":
            daily_journal(st.session_state.username)
        elif choice == "Gratitude Log 🙏":
            gratitude_log(st.session_state.username)
        elif choice == "Insights & Trends 📊":
            insights_and_trends(st.session_state.username)
        elif choice == "Export Data 📤":
            export_data(st.session_state.username)
        elif choice == "Logout 🚪":
            st.session_state.logged_in = False
            st.session_state.username = None
            st.rerun()

if __name__ == "__main__":
    main()
        
    
