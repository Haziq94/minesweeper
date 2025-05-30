import streamlit as st
import numpy as np
import random

st.set_page_config(page_title="Minesweeper", layout="centered")
st.title("💣 Minesweeper")

# Controls
rows = st.slider("Rows", 5, 15, 8)
cols = st.slider("Columns", 5, 15, 8)
mines = st.slider("Mines", 1, rows * cols // 3, 10)
flag_mode = st.toggle("🚩 Flag Mode", value=False)

# Initialize session state
if "board" not in st.session_state:
    st.session_state.board = None
if "revealed" not in st.session_state:
    st.session_state.revealed = None
if "flags" not in st.session_state:
    st.session_state.flags = None
if "game_over" not in st.session_state:
    st.session_state.game_over = False

# Create or reset board
if (
    st.session_state.board is None
    or st.session_state.board.shape != (rows, cols)
):

    def generate_board():
        board = np.zeros((rows, cols), dtype=int)
        mine_coords = random.sample(range(rows * cols), mines)
        for idx in mine_coords:
            r, c = divmod(idx, cols)
            board[r][c] = -1
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < rows and 0 <= nc < cols and board[nr][nc] != -1:
                        board[nr][nc] += 1
        return board

    st.session_state.board = generate_board()
    st.session_state.revealed = np.full((rows, cols), False)
    st.session_state.flags = np.full((rows, cols), False)
    st.session_state.game_over = False

# Reveal logic
def reveal(r, c):
    if st.session_state.revealed[r][c] or st.session_state.flags[r][c]:
        return
    st.session_state.revealed[r][c] = True
    if st.session_state.board[r][c] == 0:
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols:
                    reveal(nr, nc)

# Show game board
def show_board():
    for r in range(rows):
        cols_layout = st.columns(cols)
        for c in range(cols):
            if st.session_state.revealed[r][c]:
                val = st.session_state.board[r][c]
                if val == -1:
                    cols_layout[c].markdown("### 💣")
                elif val == 0:
                    cols_layout[c].markdown("### &nbsp;")
                else:
                    cols_layout[c].markdown(f"### {val}")
            elif st.session_state.flags[r][c]:
                if cols_layout[c].button("🚩", key=f"flag-{r},{c}"):
                    if flag_mode:
                        st.session_state.flags[r][c] = False
                        st.rerun()
            else:
                if cols_layout[c].button(" ", key=f"cell-{r},{c}"):
                    if flag_mode:
                        st.session_state.flags[r][c] = True
                    else:
                        if st.session_state.board[r][c] == -1:
                            st.session_state.game_over = True
                            st.session_state.revealed[:, :] = True
                        else:
                            reveal(r, c)
                    st.rerun()

# Run the game
if not (st.session_state.game_over or win_condition):
    show_board()

# Check for win condition
total_cells = rows * cols
revealed_count = np.count_nonzero(st.session_state.revealed)
if not st.session_state.game_over and revealed_count == total_cells - mines:
    st.success("🎉 Congratulations, you cleared the minefield!")
    st.session_state.revealed[:, :] = True  # Show all

# Game Over message
if st.session_state.game_over:
    st.error("💥 Game Over! You hit a mine.")

# Reset
if st.button("🔄 Reset Game"):
    st.session_state.clear()
    st.rerun()
