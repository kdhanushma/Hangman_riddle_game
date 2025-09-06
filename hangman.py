import warnings
warnings.filterwarnings("ignore", category=UserWarning)

import requests
import tkinter as tk
import random
import pygame  # for audio
import threading  # play audio without freezing Tkinter
import warnings

# ----------------- suppress pygame warnings -----------------
warnings.filterwarnings("ignore", category=UserWarning)

# --------- API config ---------
API_URL = "https://api.api-ninjas.com/v1/riddles"
API_KEY = "xDq89VT+ktKUGGhC0o7Mjg==ad8fhAnhP5M6ray4"

# ------- Hangman visuals & colors --------
FACES = ["", "🙂", "🙂", "😯", "😟", "😟", "😵"]
COLORS = ["#e0e0e0", "#8bc34a", "#cddc39", "#ffeb3b",
          "#ff9800", "#ff5722", "#f44336"]

score = 0
hints_used = 0

# --------- Initialize pygame safely ---------
if not pygame.mixer.get_init():
    pygame.mixer.init()

# --------- Audio files (raw strings for Windows) ---------
WIN_SOUND = "win.mp3.wav"
LOSE_SOUND = "lose.mp3.wav"

# --------- Play sound in separate thread safely ---------
def play_sound(sound_file, loop=False):
    def _play():
        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.load(sound_file)
            pygame.mixer.music.play(-1 if loop else 0)
        except Exception as e:
            print("Audio Error:", e)
    threading.Thread(target=_play, daemon=True).start()

# ---------------- Theme Changer ----------------
def set_theme(mode):
    if mode == "start":
        bg = "#1c1c1c"; fg = "#ffcc80"
    elif mode == "win":
        bg = "#4caf50"; fg = "#a5d6a7"
    elif mode == "lose":
        bg = "#f44336"; fg = "#ef9a9a"
    else:
        bg = "#1c1c1c"; fg = "#ffffff"

    root.config(bg=bg)
    title_label.config(bg=bg, fg=fg)
    hint_label.config(bg=bg, fg=fg)
    word_label.config(bg=bg, fg=fg)
    result_label.config(bg=bg, fg=fg)
    score_label.config(bg=bg, fg=fg)
    footer.config(bg=bg, fg=fg)
    art_frame.config(bg=bg)
    btns.config(bg=bg)
    entry.config(bg="#2c2c2c", fg="white", insertbackground="white")
    art_text.config(bg="#3a2b24", fg=fg)

# ---------------- Hangman ASCII Scene ----------------
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
    return [line1,line2,line3,line4,line5,line6,line7]

# ---------------- Fetch a random riddle ----------------
def fetch_riddle():
    try:
        headers = {"X-Api-Key": API_KEY}
        res = requests.get(API_URL, headers=headers)
        if res.status_code == 200:
            data = res.json()
            if data and isinstance(data, list):
                riddle = data[0]
                return riddle.get("question",""), riddle.get("answer","").lower().strip()
        return None,None
    except Exception as e:
        print("Error fetching riddle:", e)
        return None,None

# ---------------- Game control ----------------
def start_game():
    global chosen_word, lives, display, hints_used
    pygame.mixer.music.stop()
    question, answer = fetch_riddle()
    if question and answer:
        chosen_word = answer
        lives = 6; hints_used = 0
        display = ["-" if ch.isalpha() else ch for ch in chosen_word]
        hint_label.config(text=f"💡 Riddle: {question}")
        word_label.config(text="".join(display))
        result_label.config(text="")
        entry.config(state="normal")
        draw_scene()
        set_theme("start")
    else:
        hint_label.config(text="⚠️ Could not fetch riddle.")
        word_label.config(text="")
        result_label.config(text="")
        entry.config(state="disabled")

def draw_scene():
    lines = build_scene(lives)
    face_idx = 6 - lives
    face = FACES[face_idx]
    color = COLORS[face_idx]

    art_text.config(state="normal")
    art_text.delete("1.0", "end")
    for line in lines: art_text.insert("end", line+"\n")

    if face:
        start_index = art_text.search("O","1.0",tk.END)
        if start_index:
            end_index = f"{start_index}+1c"
            art_text.delete(start_index,end_index)
            art_text.insert(start_index, face)
            art_text.tag_add("face", start_index,f"{start_index}+1c")
            art_text.tag_config("face", foreground=color)
    art_text.config(state="disabled")

def check_letter():
    global lives, score
    guess = entry.get().lower().strip(); entry.delete(0,tk.END)

    if not (len(guess)==1 and guess.isalpha()):
        result_label.config(text="⚠️ Enter a single letter!", fg="#ff9800"); return

    if guess in chosen_word:
        for i,ch in enumerate(chosen_word):
            if ch==guess: display[i]=ch
        word_label.config(text="".join(display))
        result_label.config(text="✅ Correct!", fg="#4caf50")
        score += 2
    else:
        lives -=1
        draw_scene()
        result_label.config(text=f"❌ Wrong! {lives} lives left.", fg="#f44336")
        score -=1

    if "-" not in display:
        result_label.config(text="🎉 You win!", fg="#ffffff")
        entry.config(state="disabled")
        score +=10
        set_theme("win")
        score_label.config(text=f"🏆 Score: {score}")
        play_sound(WIN_SOUND, loop=True)
    elif lives==0:
        result_label.config(text=f"💀 You lose! Word was '{chosen_word}'.", fg="#ffffff")
        entry.config(state="disabled")
        set_theme("lose")
        play_sound(LOSE_SOUND)

    score_label.config(text=f"🏆 Score: {score}")

def use_hint():
    global score, hints_used
    if entry["state"]=="disabled" or "-" not in display: return

    if hints_used>=2:
        result_label.config(text="⚠️ Only 2 hints allowed per word!", fg="#ff9800")
        return

    hidden_indices = [i for i,ch in enumerate(display) if ch=="-"]
    if hidden_indices:
        idx = random.choice(hidden_indices)
        display[idx] = chosen_word[idx]
        word_label.config(text="".join(display))
        result_label.config(text=f"💡 Hint used! Revealed '{chosen_word[idx]}'.", fg="#00bcd4")
        score -=2; hints_used+=1
        score_label.config(text=f"🏆 Score: {score}")

        if "-" not in display:
            result_label.config(text="🎉 You win!", fg="#ffffff")
            entry.config(state="disabled")
            score+=10
            set_theme("win")
            score_label.config(text=f"🏆 Score: {score}")
            play_sound(WIN_SOUND, loop=True)

# ---------------- GUI Setup ----------------
root = tk.Tk()
root.title("🎮 Hangman Game - Riddle Edition")
root.geometry("700x700")
root.config(bg="#1c1c1c")

title_label = tk.Label(root, text=" 🎮 Hangman Challenge 🎮 ",
                       font=("Arial",24,"bold"), bg="#1c1c1c", fg="#ffcc80")
title_label.pack(pady=15)

hint_label = tk.Label(root, text="", font=("Arial",13), wraplength=600,
                      bg="#1c1c1c", fg="#eeeeee")
hint_label.pack(pady=8)

word_label = tk.Label(root, text="", font=("Consolas",28,"bold"),
                      bg="#1c1c1c", fg="#ffffff")
word_label.pack(pady=12)

art_frame = tk.Frame(root, bg="#1c1c1c"); art_frame.pack(pady=8)
art_text = tk.Text(art_frame, width=20,height=9,font=("Consolas",18),
                   bg="#3a2b24", fg="#eeeeee", bd=0,padx=8,pady=6)
art_text.configure(state="disabled"); art_text.pack()

result_label = tk.Label(root, text="", font=("Arial",15,"bold"),
                        bg="#1c1c1c", fg="white")
result_label.pack(pady=8)

entry = tk.Entry(root, font=("Arial",18), justify="center", width=5,
                 bg="#2c2c2c", fg="white", insertbackground="white")
entry.pack(pady=6)

btns = tk.Frame(root, bg="#1c1c1c"); btns.pack(pady=12)

tk.Button(btns, text="Guess", command=check_letter,
          font=("Arial",13,"bold"), bg="#6d4c41", fg="white",
          activebackground="#4e342e", width=12).grid(row=0,column=0,padx=10)

tk.Button(btns, text="🔄 New Game", command=start_game,
          font=("Arial",13,"bold"), bg="#455a64", fg="white",
          activebackground="#263238", width=12).grid(row=0,column=1,padx=10)

tk.Button(btns, text="💡 Hint", command=use_hint,
          font=("Arial",13,"bold"), bg="#00796b", fg="white",
          activebackground="#004d40", width=12).grid(row=0,column=2,padx=10)

score_label = tk.Label(root, text=f"🏆 Score: {score}", font=("Arial",14,"bold"),
                       bg="#1c1c1c", fg="#ffeb3b")
score_label.pack(pady=8)

footer = tk.Label(root, text="Made with ❤️ in Tkinter", font=("Arial",10,"italic"),
                  bg="#1c1c1c", fg="#aaaaaa")
footer.pack(side="bottom", pady=8)

start_game()
root.mainloop()
