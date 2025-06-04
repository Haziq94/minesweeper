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

# Initialize state
if "board" not in st.session_state:
    st.session_state.board = None
if "revealed" not in st.session_state:
    st.session_state.revealed = None
if "flags" not in st.session_state:
    st.session_state.flags = None
if "game_over" not in st.session_state:
    st.session_state.game_over = False

# Generate board if needed
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

# Show game board with chording
def show_board():
    colors = [
        "", "blue", "green", "red", "purple",
        "maroon", "turquoise", "black", "gray"
    ]

    for r in range(rows):
        cols_layout = st.columns(cols, gap="small")
        for c in range(cols):
            key = f"{r}-{c}"
            val = st.session_state.board[r][c]
            revealed = st.session_state.revealed[r][c]
            flagged = st.session_state.flags[r][c]

            def auto_reveal_adjacent():
                count_flags = 0
                unrevealed_unflagged = []
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < rows and 0 <= nc < cols:
                            if st.session_state.flags[nr][nc]:
                                count_flags += 1
                            elif not st.session_state.revealed[nr][nc]:
                                unrevealed_unflagged.append((nr, nc))
                if count_flags == val:
                    for nr, nc in unrevealed_unflagged:
                        if st.session_state.board[nr][nc] == -1:
                            st.session_state.revealed[:, :] = True
                            st.session_state.game_over = True
                        else:
                            reveal(nr, nc)

            if revealed or (st.session_state.game_over and val == -1):
                if val == -1:
                    label = "💣"
                elif val == 0:
                    label = " "
                else:
                    color = colors[val]
                    label = f":{color}[{val}]"

                # Use button only if chording is possible
                if val > 0 and cols_layout[c].button(label, key=key):
                    auto_reveal_adjacent()
                    st.rerun()
                else:
                    cols_layout[c].markdown(
                        f"<div style='text-align:center;font-size:22px'></div>",
                        unsafe_allow_html=True
                    )

            else:
                label = "🚩" if flagged else "⬜"
                if cols_layout[c].button(label, key=key):
                    if flag_mode:
                        st.session_state.flags[r][c] = not flagged
                    else:
                        if val == -1:
                            st.session_state.game_over = True
                            st.session_state.revealed[:, :] = True
                        else:
                            reveal(r, c)
                    st.rerun()

# Win detection
total_cells = rows * cols
revealed_count = np.count_nonzero(st.session_state.revealed)
win_condition = (
    not st.session_state.game_over
    and revealed_count == total_cells - mines
)

# Game messages
if win_condition:
    st.success("🎉 Congratulations, you cleared the minefield!")
    st.session_state.revealed[:, :] = True
elif st.session_state.game_over:
    st.error("💥 Game Over! You hit a mine.")

# Render board
show_board()

# Reset button
if st.button("🔄 Reset Game"):
    st.session_state.clear()
    st.rerun()
