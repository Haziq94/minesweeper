# 💣 Minesweeper Game (Streamlit)

A simple, interactive Minesweeper game built using **Python** and **Streamlit**. Play directly in your browser with adjustable grid size and mine count.

---

## 🧩 Features

- Adjustable grid size (rows x columns)
- Adjustable number of mines
- Recursive reveal of empty cells
- Game over and win detection
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

## 🎮 How to Play

- Click a covered cell to reveal it.
- Turn on **🚩 Flag mode** to mark suspected mines instead of revealing them; turn it off to go back to revealing.
- Clear every cell that isn't a mine to win.
- **🔄 Restart Game** deals a fresh board at any time.
