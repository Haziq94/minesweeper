# minesweeper_app.py

import streamlit as st
import numpy as np
import random

st.set_page_config(page_title="Minesweeper Game", layout="centered")
st.title("💣 Minesweeper Game")

# Set board size
rows = st.slider("Rows", 5, 15, 8)
cols = st.slider("Columns", 5, 15, 8)
max_mines = rows * cols - 1
mines = st.slider("Mines", 5, min(50, max_mines), 10)

# Initialize game state
if "board" not in st.session_state:
    def generate_board():
        board = np.zeros((rows, cols), dtype=int)
        mine_coords = random.sample(range(rows * cols), mines)
        for idx in mine_coords:
            r, c = divmod(idx, cols)
            board[r][c] = -1  # -1 means mine
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < rows and 0 <= nc < cols and board[nr][nc] != -1:
                        board[nr][nc] += 1
        return board

    st.session_state.board = generate_board()
    st.session_state.revealed = np.full((rows, cols), False)
    st.session_state.game_over = False

# Recursive function to reveal 0-valued neighbors
def reveal_cell(r, c):
    if not (0 <= r < rows and 0 <= c < cols):
        return
    if st.session_state.revealed[r][c]:
        return
    st.session_state.revealed[r][c] = True
    if st.session_state.board[r][c] == 0:
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr != 0 or dc != 0:
                    reveal_cell(r + dr, c + dc)

# Draw the board
def show_board():
    for r in range(rows):
        cols_list = st.columns(cols)
        for c in range(cols):
            if st.session_state.revealed[r][c]:
                val = st.session_state.board[r][c]
                if val == -1:
                    cols_list[c].button("💣", key=f"{r}_{c}", disabled=True)
                elif val == 0:
                    cols_list[c].button("⬜", key=f"{r}_{c}", disabled=True)
                else:
                    cols_list[c].button(str(val), key=f"{r}_{c}", disabled=True)
            else:
                if cols_list[c].button(" ", key=f"{r}_{c}"):
                    if st.session_state.board[r][c] == -1:
                        st.session_state.revealed[r][c] = True
                        st.session_state.game_over = True
                    else:
                        reveal_cell(r, c)

# Display game status
if st.session_state.game_over:
    st.error("💥 Game Over! You hit a mine.")
else:
    # Check win
    unrevealed_count = np.sum(~st.session_state.revealed)
    if unrevealed_count == mines:
        st.success("🎉 You win! All safe cells revealed.")

show_board()
import platform
st.write("Python version:", platform.python_version())

# Reset button
if st.button("🔄 Reset Game"):
    st.session_state.clear()
    st.rerun()
