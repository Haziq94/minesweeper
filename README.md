# 💣 Minesweeper Game (Streamlit)

A simple, interactive Minesweeper game built using **Python** and **Streamlit**. Play directly in your browser with adjustable grid size and mine count.

---

## 🧩 Features

- Adjustable grid size (rows x columns)
- Adjustable number of mines
- First click is always safe - mines are laid after it
- Flood-fill reveal of empty cells
- Chording: open a satisfied number's remaining neighbours in one click
- Game over and win detection
- Animated reveals, a blast on the mine you hit, and balloons for a win
- Emoji-based UI for better UX
- Fully playable in browser

---

## 🚀 Demo

Play it live on **Streamlit Cloud**:  
👉 [Your Deployed App Link Here]

---

## 🛠️ Installation (Local)

1. Clone the repo:

```bash
git clone https://github.com/Haziq94/minesweeper.git
cd minesweeper
```

2. Install the dependencies:

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
streamlit run minesweeper.py
```

The app opens at <http://localhost:8501>.

---

## 📱 Web version (`web/`)

A self-contained HTML/CSS/JS build of the same game - no Python, no server, no
network. Same rules as the Streamlit app: safe first click, chording, protected
flags, animated reveals. Built to run well on a phone, and to be the base for
packaging as an installable app.

Open `web/index.html` directly, or serve it:

```bash
python -m http.server 8600 --directory web
```

Then visit <http://localhost:8600>. On a phone: tap to dig, long-press to flag,
tap a number to open its neighbours.

---

## 🎮 How to Play

- Set the grid size and mine count in the **⚙️ Settings** sidebar; changing any of them deals a new board.
- Click a covered cell to reveal it.
- Turn on **🚩 Flag mode** to mark suspected mines instead of revealing them; turn it off to go back to revealing.
- A flagged cell cannot be revealed until you unflag it.
- Click a revealed number once it carries as many flags as its value to open its remaining neighbours at once. If one of those flags is wrong, this hits a mine.
- Clear every cell that isn't a mine to win.
- **🔄 Restart Game** deals a fresh board at any time.
