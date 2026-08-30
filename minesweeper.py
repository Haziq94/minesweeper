import streamlit as st
import numpy as np
import random

st.set_page_config(page_title="Minesweeper", page_icon="💣", layout="wide")

# Configuration
def clamp(value, low, high):
    return max(low, min(int(value), high))

st.sidebar.header("⚙️ Settings")
# Bounds are held here rather than left to the widgets, so a typed value is
# capped whatever the browser sends.
st.session_state.setdefault("rows", 10)
st.session_state.setdefault("cols", 10)
st.session_state.rows = clamp(st.session_state.rows, 5, 20)
st.session_state.cols = clamp(st.session_state.cols, 5, 20)
rows = st.sidebar.number_input("Rows", min_value=5, max_value=20, step=1, key="rows")
cols = st.sidebar.number_input("Columns", min_value=5, max_value=20, step=1, key="cols")

# The mine field's ceiling follows the grid, so clamp a carried-over value
# before the widget is drawn with a smaller maximum.
max_mines = rows * cols - 1
st.session_state.setdefault("num_mines", 10)
st.session_state.num_mines = clamp(st.session_state.num_mines, 1, max_mines)
num_mines = st.sidebar.number_input(
    "Mines", min_value=1, max_value=max_mines, step=1, key="num_mines"
)
st.sidebar.caption("Changing a setting starts a new game.")

# Cells shrink on wider grids so the board still fits the page.
if cols <= 10:
    cell_size, font_size = 40, 22
elif cols <= 15:
    cell_size, font_size = 32, 18
else:
    cell_size, font_size = 26, 15
# Tile widths + 3px gaps + the panel's 10px padding on each side.
board_width = cols * cell_size + (cols - 1) * 3 + 22
colors = {
    1: "#1d6fd6", 2: "#2e8b48", 3: "#d4443c", 4: "#7b4bc4",
    5: "#c2570b", 6: "#0f9aa8", 7: "#3f4756", 8: "#8a91a0"
}

# Initialize game state
def initialize_game():
    # The board starts empty. Mines are laid on the first click so that it
    # can never land on one.
    st.session_state.board = np.zeros((rows, cols), dtype=int)
    st.session_state.mines_placed = False
    st.session_state.revealed = np.full((rows, cols), False)
    st.session_state.flags = np.full((rows, cols), False)
    st.session_state.game_over = False
    st.session_state.won = False
    st.session_state.fresh = np.full((rows, cols), False)
    st.session_state.origin = None
    st.session_state.celebrated = False
    st.session_state.settings = (rows, cols, num_mines)

if "board" not in st.session_state or st.session_state.settings != (rows, cols, num_mines):
    initialize_game()

# Mine placement, deferred until the first click
def place_mines(safe_r, safe_c):
    board = st.session_state.board
    # Keep the clicked cell and its neighbours clear, so the first click
    # opens a region rather than a lone number.
    zone = {
        (safe_r + dr) * cols + (safe_c + dc)
        for dr in [-1, 0, 1]
        for dc in [-1, 0, 1]
        if 0 <= safe_r + dr < rows and 0 <= safe_c + dc < cols
    }
    choices = [i for i in range(rows * cols) if i not in zone]
    if len(choices) < num_mines:
        # Too crowded to spare the neighbours; spare the clicked cell alone.
        choices = [i for i in range(rows * cols) if i != safe_r * cols + safe_c]
    for mine in random.sample(choices, num_mines):
        r, c = divmod(mine, cols)
        board[r][c] = -1
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and board[nr][nc] != -1:
                    board[nr][nc] += 1
    st.session_state.mines_placed = True

# Reveal logic
def reveal(r, c):
    stack = [(r, c)]
    while stack:
        r, c = stack.pop()
        if st.session_state.revealed[r][c] or st.session_state.flags[r][c]:
            continue
        st.session_state.revealed[r][c] = True
        if st.session_state.board[r][c] == 0:
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < rows and 0 <= nc < cols:
                        stack.append((nr, nc))

# A rerun redraws the whole board, so record which cells actually changed in
# the last action - only those are allowed to animate.
def mark_fresh(before, origin):
    st.session_state.fresh = st.session_state.revealed & ~before
    st.session_state.origin = origin

def is_fresh(r, c):
    return bool(st.session_state.fresh[r][c]) or st.session_state.origin == (int(r), int(c))

def anim_delay(r, c):
    # Stagger by distance from the click, so a cascade ripples outward.
    origin = st.session_state.origin
    if origin is None:
        return 0
    return min(max(abs(int(r) - origin[0]), abs(int(c) - origin[1])), 16) * 22

# Chording: a revealed number opens its unflagged neighbours once it carries
# as many flags as its own value.
def chord(r, c):
    value = st.session_state.board[r][c]
    neighbours = [
        (r + dr, c + dc)
        for dr in [-1, 0, 1]
        for dc in [-1, 0, 1]
        if (dr or dc) and 0 <= r + dr < rows and 0 <= c + dc < cols
    ]
    if sum(st.session_state.flags[nr][nc] for nr, nc in neighbours) != value:
        return
    for nr, nc in neighbours:
        if st.session_state.flags[nr][nc] or st.session_state.revealed[nr][nc]:
            continue
        if st.session_state.board[nr][nc] == -1:
            # A misplaced flag makes chording as fatal as digging by hand.
            st.session_state.game_over = True
            st.session_state.revealed[:, :] = True
            return
        reveal(nr, nc)

# Win check
def check_win():
    for r in range(rows):
        for c in range(cols):
            if st.session_state.board[r][c] != -1 and not st.session_state.revealed[r][c]:
                return False
    return True

# Styling. The board rules are scoped to the container keyed "board", so the
# tight grid spacing leaves the rest of the page alone.
st.markdown(f"""
    <style>
    .title {{
        text-align: center;
        font-size: 2.1rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        margin: 0.2rem 0 1.2rem;
    }}
    .chip {{
        display: inline-flex;
        align-items: center;
        padding: 0.35rem 0.9rem;
        border-radius: 999px;
        background: #ffffff;
        border: 1px solid #e2e6f0;
        font-size: 0.95rem;
        font-variant-numeric: tabular-nums;
    }}
    .st-key-board,
    .st-key-board div[data-testid="stVerticalBlock"],
    .st-key-board div[data-testid="stHorizontalBlock"] {{
        gap: 3px !important;
    }}
    /* The board sits on its own panel rather than bleeding into the page. */
    .st-key-board {{
        width: fit-content;
        margin: 0 auto;
        padding: 10px;
        border-radius: 14px;
        background: #ffffff;
        border: 1px solid #e6eaf2;
    }}
    /* Element containers size themselves to text, which squashes a cell. */
    .st-key-board div[data-testid="stElementContainer"],
    .st-key-board div[data-testid="stMarkdown"] {{
        height: {cell_size}px !important;
        min-height: {cell_size}px !important;
    }}
    .st-key-board div[data-testid="stHorizontalBlock"] {{
        justify-content: center !important;
        flex-wrap: nowrap !important;
    }}
    .st-key-board div[data-testid="stColumn"] {{
        flex: 0 0 {cell_size}px !important;
        min-width: {cell_size}px !important;
        width: {cell_size}px !important;
    }}
    .st-key-board button[kind="secondary"] {{
        width: {cell_size}px !important;
        height: {cell_size}px !important;
        min-height: {cell_size}px !important;
        padding: 0 !important;
        border: none !important;
        border-radius: 6px !important;
        background: #c3cbdc !important;
        box-shadow: inset 0 -2px 0 rgba(0, 0, 0, 0.07) !important;
        font-size: {font_size}px !important;
        line-height: 1 !important;
        transition: background 0.12s ease, transform 0.12s ease !important;
    }}
    .st-key-board button[kind="secondary"]:hover {{
        background: #aeb8cd !important;
        transform: translateY(-1px) !important;
    }}
    .st-key-board button[kind="tertiary"] {{
        width: {cell_size}px !important;
        height: {cell_size}px !important;
        min-height: {cell_size}px !important;
        padding: 0 !important;
        border: none !important;
        border-radius: 6px !important;
        background: #e6eaf3 !important;
        font-size: {font_size}px !important;
        font-weight: 700 !important;
        line-height: 1 !important;
    }}
    .st-key-board button[kind="tertiary"]:hover {{
        background: #dbe2f0 !important;
    }}
    .cell {{
        width: {cell_size}px;
        height: {cell_size}px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 6px;
        background: #e6eaf3;
        font-size: {font_size}px;
        font-weight: 700;
    }}
    .cell.mine {{
        background: #f6c9c4;
    }}
    @keyframes pop {{
        from {{ opacity: 0; transform: scale(0.55); }}
        to {{ opacity: 1; transform: scale(1); }}
    }}
    @keyframes boom {{
        0% {{ transform: scale(0.4); }}
        55% {{ transform: scale(1.35); }}
        100% {{ transform: scale(1); }}
    }}
    .cell.pop {{
        animation: pop 0.24s ease-out both;
    }}
    .cell.boom {{
        animation: boom 0.45s ease-out both;
        background: #ef6a5c;
    }}
    /* Keep the chrome the same width as the board panel. */
    .st-key-status div[data-testid="stColumn"]:last-child {{
        align-items: flex-end;
    }}
    .st-key-status,
    .st-key-newgame,
    div[data-testid="stAlert"] {{
        max-width: {board_width}px;
        margin-left: auto !important;
        margin-right: auto !important;
    }}
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='title'>💣 Minesweeper</div>", unsafe_allow_html=True)

# Status bar
mines_left = num_mines - int(st.session_state.flags.sum())
with st.container(key="status"):
    counter, switch = st.columns([1, 1], vertical_alignment="center")
    counter.markdown(
        f"<div class='chip'>🚩 {mines_left} left</div>", unsafe_allow_html=True
    )
    flag_mode = switch.toggle("🚩 Flag mode", value=False)

# Game logic
if not st.session_state.game_over and not st.session_state.won and check_win():
    st.session_state.won = True
    st.session_state.flags[st.session_state.board == -1] = True
    st.session_state.fresh = st.session_state.fresh | (st.session_state.board == -1)

if st.session_state.game_over:
    st.error("💥 Boom! You hit a mine.")
elif st.session_state.won:
    st.success("🎉 You cleared the board! Well done!")
    if not st.session_state.celebrated:
        # Once only, or every later rerun would set them off again.
        st.balloons()
        st.session_state.celebrated = True

def cell_styles():
    board, revealed = st.session_state.board, st.session_state.revealed
    rules = []
    for value, color in colors.items():
        cells = np.argwhere((board == value) & revealed)
        if len(cells):
            selector = ", ".join(f".st-key-{r}-{c} button" for r, c in cells)
            rules.append(f"{selector} {{ color: {color} !important; }}")
    # Numbers are buttons, so their animation has to come through CSS too.
    animated = [(r, c) for r, c in np.argwhere(revealed & (board > 0)) if is_fresh(r, c)]
    origin = st.session_state.origin
    if origin is not None and not revealed[origin[0]][origin[1]]:
        # A freshly placed flag sits on a covered tile.
        animated.append(origin)
    for r, c in animated:
        rules.append(
            f".st-key-{r}-{c} button {{ animation: pop 0.24s ease-out both; "
            f"animation-delay: {anim_delay(r, c)}ms; }}"
        )
    return " ".join(rules)

def show_board():
    finished = st.session_state.game_over or st.session_state.won
    for r in range(rows):
        cols_layout = st.columns(cols)
        for c in range(cols):
            key = f"{r}-{c}"
            val = st.session_state.board[r][c]
            revealed = st.session_state.revealed[r][c]
            flagged = st.session_state.flags[r][c]
            is_mine = val == -1

            if revealed and val > 0 and not finished:
                # A revealed number stays clickable so it can be chorded.
                if cols_layout[c].button(str(val), key=key, type="tertiary"):
                    # A revealed number cannot be flagged, so it chords
                    # in either mode.
                    before = st.session_state.revealed.copy()
                    chord(r, c)
                    mark_fresh(before, (r, c))
                    st.rerun()
            elif revealed or (finished and is_mine):
                style = "cell"
                if is_mine:
                    # A flagged mine reads as a catch, not as the one you hit.
                    display = "🚩" if flagged else "💣"
                    style = "cell" if flagged else "cell mine"
                elif val == 0:
                    display = ""
                else:
                    display = f"<span style='color:{colors[val]};'>{val}</span>"
                if is_fresh(r, c):
                    hit = st.session_state.game_over and is_mine and not flagged
                    style += " boom" if hit and st.session_state.origin == (r, c) else " pop"
                cols_layout[c].markdown(
                    f"<div class='{style}' style='animation-delay:{anim_delay(r, c)}ms'>"
                    f"{display}</div>",
                    unsafe_allow_html=True,
                )
            else:
                label = "🚩" if flagged else " "
                if cols_layout[c].button(label, key=key):
                    before = st.session_state.revealed.copy()
                    if flag_mode:
                        st.session_state.flags[r][c] = not flagged
                    elif flagged:
                        # A flag protects its cell; unflag it to dig there.
                        pass
                    elif not st.session_state.mines_placed:
                        place_mines(r, c)
                        reveal(r, c)
                    elif is_mine:
                        st.session_state.game_over = True
                        st.session_state.revealed[:, :] = True
                    else:
                        reveal(r, c)
                    mark_fresh(before, (r, c))
                    st.rerun()

st.markdown(f"<style>{cell_styles()}</style>", unsafe_allow_html=True)
with st.container(key="board"):
    show_board()

# Restart button
st.write("")
new_game = st.container(key="newgame")
if new_game.button("🔄 New Game", key="restart", type="primary", use_container_width=True):
    for key in ["board", "revealed", "flags", "game_over", "won", "settings",
                "mines_placed", "fresh", "origin", "celebrated"]:
        st.session_state.pop(key, None)
    st.rerun()
