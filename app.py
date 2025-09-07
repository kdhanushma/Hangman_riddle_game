import streamlit as st
import requests
import random
import base64

# -------- Audio files --------
WIN_SOUND = "win.mp3"   # make sure these files exist in your repo
LOSE_SOUND = "lose.mp3"

# -------- Play sounds using HTML autoplay --------
def play_sound(file_path):
    try:
        with open(file_path, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            md = f"""
                <audio autoplay>
                    <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                </audio>
            """
            st.markdown(md, unsafe_allow_html=True)
    except Exception as e:
        st.warning(f"Audio error: {e}")

# -------- Hangman visuals --------
FACES = ["", "🙂", "🙂", "😯", "😟", "😟", "😵"]
COLORS = ["#e0e0e0", "#8bc34a", "#cddc39", "#ffeb3b",
          "#ff9800", "#ff5722", "#f44336"]

# -------- API config --------
API_URL = "https://api.api-ninjas.com/v1/riddles"
API_KEY = "xDq89VT+ktKUGGhC0o7Mjg==ad8fhAnhP5M6ray4"

# -------- Session state --------
for key, default in {
    "word": "", "display": [], "lives": 6, "question": "",
    "guessed": [], "score": 0, "hints": 0
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# -------- Fetch riddle --------
def fetch_riddle():
    try:
        headers = {"X-Api-Key": API_KEY}
        res = requests.get(API_URL, headers=headers)
        if res.status_code == 200:
            data = res.json()
            if data and isinstance(data, list):
                riddle = data[0]
                return riddle.get("question", ""), riddle.get("answer", "").lower().strip()
        return None, None
    except:
        return None, None

# -------- New Game --------
def new_game():
    q, ans = fetch_riddle()
    if q and ans:
        st.session_state.word = ans
        st.session_state.display = ["-" if c.isalpha() else c for c in ans]
        st.session_state.lives = 6
        st.session_state.question = q
        st.session_state.guessed = []
        st.session_state.hints = 0
    else:
        st.error("⚠️ Could not fetch riddle!")

# -------- Check guess --------
def check_guess(letter):
    if not letter or letter in st.session_state.guessed:
        return
    st.session_state.guessed.append(letter)

    if letter in st.session_state.word:
        for i, ch in enumerate(st.session_state.word):
            if ch == letter:
                st.session_state.display[i] = ch
        st.session_state.score += 2
    else:
        st.session_state.lives -= 1
        st.session_state.score -= 1

# -------- Use hint --------
def use_hint():
    if st.session_state.hints >= 2:
        st.warning("⚠️ Only 2 hints allowed!")
        return
    hidden = [i for i, c in enumerate(st.session_state.display) if c == "-"]
    if hidden:
        idx = random.choice(hidden)
        st.session_state.display[idx] = st.session_state.word[idx]
        st.session_state.hints += 1
        st.session_state.score -= 2

# -------- Build ASCII scene --------
def build_scene(lives):
    mistakes = 6 - lives
    head = mistakes >= 1; body = mistakes >= 2
    l_arm = mistakes >= 3; r_arm = mistakes >= 4
    l_leg = mistakes >= 5; r_leg = mistakes >= 6

    line1 = "  +---+"; line2 = "  |   |"; line3 = "  |   " + ("O" if head else "")
    if body:
        if l_arm and r_arm: line4 = "  |  /|\\"
        elif l_arm: line4 = "  |  /| "
        elif r_arm: line4 = "  |   |\\"
        else: line4 = "  |   | "
    else: line4 = "  |     "
    if l_leg and r_leg: line5 = "  |  / \\"
    elif l_leg: line5 = "  |  /  "
    elif r_leg: line5 = "  |    \\"
    else: line5 = "  |     "
    line6 = "  |"; line7 = "========="
    return "\n".join([line1,line2,line3,line4,line5,line6,line7])

# -------- Streamlit UI --------
st.set_page_config(page_title="Hangman Riddle Game", page_icon="🎮", layout="centered")
st.markdown("<h1 style='text-align: center; color: #ffcc80;'>🎮 Hangman Riddle Game</h1>", unsafe_allow_html=True)
st.markdown(f"<h3 style='text-align: center; color: #ffffff;'>Score: {st.session_state.score}</h3>", unsafe_allow_html=True)

# Buttons
col1, col2 = st.columns([1,1])
with col1:
    if st.button("🔄 New Game"):
        new_game()
with col2:
    if st.button("💡 Hint"):
        use_hint()

# Game display
if st.session_state.question:
    st.markdown(f"**💡 Riddle:** {st.session_state.question}")
    st.code(build_scene(st.session_state.lives))
    st.markdown(f"**Word:** {' '.join(st.session_state.display)}")
    st.markdown(f"**Lives:** {st.session_state.lives} | **Hints used:** {st.session_state.hints}/2")

    # Input with callback
    def submit_guess():
        letter = st.session_state.guess_input
        check_guess(letter)
        st.session_state.guess_input = ""  # reset

    st.text_input("Enter a letter", max_chars=1, key="guess_input", on_change=submit_guess)

    # Win/Lose conditions
    if "-" not in st.session_state.display:
        st.success(f"🎉 You Win! Word: {st.session_state.word}")
        play_sound(WIN_SOUND)
        st.session_state.score += 10
    elif st.session_state.lives <= 0:
        st.error(f"💀 You Lose! Word was: {st.session_state.word}")
        play_sound(LOSE_SOUND)
