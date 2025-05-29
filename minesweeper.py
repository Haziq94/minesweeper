# minesweeper_app.py
import streamlit as st
import numpy as np
import random

st.set_page_config(page_title="Minesweeper Game")

st.title("💣 Minesweeper Game")

rows = st.slider("Rows", 5, 15, 8)
cols = st.slider("Columns", 5, 15, 8)
mines = st.slider("Mines", 5, min(rows * cols - 1, 50), 10)

if "board" not in st.session_state:
    def generate_board():
        board = np.zeros((rows, cols), dtype=int)
        mine_coords = random.sample(range(rows * cols), mines)
        for idx in mine_coords:
            r, c = divmod(idx, cols)
            board[r][c] = -1  # -1 means mine
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if 0 <= r + dr < rows and 0 <= c + dc < cols and board[r + dr][c + dc] != -1:
                        board[r + dr][c + dc] += 1
        return board

    st.session_state.board = generate_board()
    st.session_state.revealed = np.full((rows, cols), False)

def show_board():
    for r in range(rows):
        cols_list = []
        for c in range(cols):
            if st.session_state.revealed[r][c]:
                val = st.session_state.board[r][c]
                if val == -1:
                    cols_list.append("💣")
                elif val == 0:
                    cols_list.append("⬜")
                else:
                    cols_list.append(str(val))
            else:
                if st.button(" ", key=f"{r}_{c}"):
                    st.session_state.revealed[r][c] = True
                    if st.session_state.board[r][c] == -1:
                        st.error("Game Over! You hit a mine.")
        st.write(" ".join(cols_list))

show_board()

if st.button("Reset Game"):
    st.session_state.clear()
    st.experimental_rerun()
