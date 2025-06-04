import streamlit as st
import numpy as np
import random

# Configuration
rows, cols, num_mines = 10, 10, 10
colors = {
    1: "blue", 2: "green", 3: "red", 4: "darkblue",
    5: "brown", 6: "teal", 7: "black", 8: "gray"
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

# Check win condition
def check_win():
    for r in range(rows):
        for c in range(cols):
            if st.session_state.board[r][c] != -1 and not st.session_state.revealed[r][c]:
                return False
    return True

# UI toggle for flag mode
flag_mode = st.toggle("🚩 Flag mode", value=False)

# Display board
def show_board():
    for r in range(rows):
        cols_layout = st.columns(cols, gap="small")
        for c in range(cols):
            key = f"{r}-{c}"
            val = st.session_state.board[r][c]
            revealed = st.session_state.revealed[r][c]
            flagged = st.session_state.flags[r][c]
            cell_is_mine = val == -1
            show_bomb = st.session_state.game_over and cell_is_mine

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

            if revealed or show_bomb:
                if cell_is_mine:
                    label = "💣"
                    color_style = "color:red;" if revealed else ""
                elif val == 0:
                    label = "&nbsp;"
                    color_style = ""
                else:
                    color = colors[val]
                    label = f"<b style='color:{color}'>{val}</b>"
                    color_style = ""

                cols_layout[c].markdown(
                    f"<div style='text-align:center;font-size:22px;{color_style}'>{label}</div>",
                    unsafe_allow_html=True
                )
            else:
                label = "🚩" if flagged else "⬜"
                if cols_layout[c].button(label, key=key):
                    if flag_mode:
                        st.session_state.flags[r][c] = not flagged
                    else:
                        if cell_is_mine:
                            st.session_state.revealed[r][c] = True
                            st.session_state.game_over = True
                            st.session_state.revealed[:, :] = True
                        else:
                            reveal(r, c)
                    st.rerun()

# Main logic
if not st.session_state.game_over and not st.session_state.won:
    show_board()
    if check_win():
        st.success("🎉 Congratulations! You won!")
        st.session_state.won = True
elif st.session_state.game_over:
    show_board()
    st.error("💥 Boom! You hit a mine.")

# Restart game
if st.button("🔄 Restart"):
    for key in ["board", "revealed", "flags", "game_over", "won"]:
        st.session_state.pop(key, None)
    st.rerun()
