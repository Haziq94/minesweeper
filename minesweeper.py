import streamlit as st
import numpy as np
import random

# Configuration
rows, cols, num_mines = 10, 10, 10
colors = {
    1: "blue", 2: "green", 3: "red", 4: "navy",
    5: "brown", 6: "turquoise", 7: "black", 8: "gray"
}

# Initialize game state
def initialize_game():
    board = np.zeros((rows, cols), dtype=int)
    mines = random.sample(range(rows * cols), num_mines)
    for mine in mines:
        r, c = divmod(mine, cols)
        board[r][c] = -1
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and board[nr][nc] != -1:
                    board[nr][nc] += 1
    st.session_state.board = board
    st.session_state.revealed = np.full((rows, cols), False)
    st.session_state.flags = np.full((rows, cols), False)
    st.session_state.game_over = False
    st.session_state.won = False

if "board" not in st.session_state:
    initialize_game()

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

# Win check
def check_win():
    for r in range(rows):
        for c in range(cols):
            if st.session_state.board[r][c] != -1 and not st.session_state.revealed[r][c]:
                return False
    return True

# CSS for tight layout
st.markdown("""
    <style>
    div[data-testid="column"] {
        padding: 0px !important;
        margin: 0px !important;
    }
    button[kind="secondary"] {
        height: 40px !important;
        width: 40px !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    </style>
""", unsafe_allow_html=True)

flag_mode = st.toggle("🚩 Flag mode", value=False)

def show_board():
    for r in range(rows):
        cols_layout = st.columns(cols)  # removed gap="0"
        for c in range(cols):
            key = f"{r}-{c}"
            val = st.session_state.board[r][c]
            revealed = st.session_state.revealed[r][c]
            flagged = st.session_state.flags[r][c]
            is_mine = val == -1
            show_mine = st.session_state.game_over and is_mine

            if revealed or show_mine:
                if is_mine:
                    display = "💣"
                elif val == 0:
                    display = ""
                else:
                    color = colors[val]
                    display = f"<span style='color:{color};'><b>{val}</b></span>"
                cols_layout[c].markdown(
                    f"<div style='text-align:center; font-size:22px; height:40px;'>{display}</div>",
                    unsafe_allow_html=True
                )
            else:
                label = "🚩" if flagged else " "
                if cols_layout[c].button(label, key=key):
                    if flag_mode:
                        st.session_state.flags[r][c] = not flagged
                    else:
                        if is_mine:
                            st.session_state.revealed[r][c] = True
                            st.session_state.game_over = True
                            st.session_state.revealed[:, :] = True
                        else:
                            reveal(r, c)
                    st.rerun()

# Game logic
if not st.session_state.game_over and not st.session_state.won:
    show_board()
    if check_win():
        st.success("🎉 You cleared the board! Well done!")
        st.session_state.won = True
elif st.session_state.game_over:
    show_board()
    st.error("💥 Boom! You hit a mine.")

# Restart button
st.markdown("---")
st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
if st.button("🔄 Restart Game", key="restart"):
    for key in ["board", "revealed", "flags", "game_over", "won"]:
        st.session_state.pop(key, None)
    st.rerun()
st.markdown("</div>", unsafe_allow_html=True)
