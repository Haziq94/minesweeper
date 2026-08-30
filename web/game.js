"use strict";

const COLORS = {
  1: "#1d6fd6", 2: "#2e8b48", 3: "#d4443c", 4: "#7b4bc4",
  5: "#c2570b", 6: "#0f9aa8", 7: "#3f4756", 8: "#8a91a0"
};
const MIN_DIM = 5;
const MAX_DIM = 30;
const GAP = 3;
const MAX_CELL = 44;
const PANEL_PADDING = 22;   // panel padding plus its border
const LONG_PRESS_MS = 400;

const el = {
  board: document.getElementById("board"),
  counter: document.getElementById("counter"),
  message: document.getElementById("message"),
  flagBtn: document.getElementById("flag-mode"),
  newBtn: document.getElementById("new-game"),
  applyBtn: document.getElementById("apply"),
  cancelBtn: document.getElementById("cancel"),
  settingsBtn: document.getElementById("settings-btn"),
  settings: document.getElementById("settings"),
  app: document.getElementById("app"),
  confetti: document.getElementById("confetti"),
  rows: document.getElementById("rows"),
  cols: document.getElementById("cols"),
  mines: document.getElementById("mines")
};

let S = null;
let cells = [];
let flagMode = false;

const clamp = (v, lo, hi) => Math.max(lo, Math.min(hi, Math.floor(Number(v) || 0)));
const rc = i => [Math.floor(i / S.cols), i % S.cols];

function neighbours(i) {
  const [r, c] = rc(i);
  const out = [];
  for (let dr = -1; dr <= 1; dr++) {
    for (let dc = -1; dc <= 1; dc++) {
      if (!dr && !dc) continue;
      const nr = r + dr;
      const nc = c + dc;
      if (nr >= 0 && nr < S.rows && nc >= 0 && nc < S.cols) out.push(nr * S.cols + nc);
    }
  }
  return out;
}

/* Setup ------------------------------------------------------------------ */

function newGame() {
  const rows = clamp(el.rows.value, MIN_DIM, MAX_DIM);
  const cols = clamp(el.cols.value, MIN_DIM, MAX_DIM);
  const mines = clamp(el.mines.value, 1, rows * cols - 1);
  el.rows.value = rows;
  el.cols.value = cols;
  el.mines.value = mines;
  el.mines.max = rows * cols - 1;

  const n = rows * cols;
  S = {
    rows, cols, mines, n,
    board: new Int8Array(n),
    revealed: new Uint8Array(n),
    flags: new Uint8Array(n),
    placed: false,
    over: false,
    won: false
  };

  buildGrid();
  setMessage("");
  updateCounter();
}

function buildGrid() {
  el.board.style.setProperty("--cols", S.cols);
  el.board.textContent = "";
  cells = new Array(S.n);
  const frag = document.createDocumentFragment();
  for (let i = 0; i < S.n; i++) {
    const cell = document.createElement("div");
    cell.className = "cell covered";
    cell.dataset.i = i;
    cells[i] = cell;
    frag.appendChild(cell);
  }
  el.board.appendChild(frag);
  fitBoard();
}

// Tiles are sized to fill the available width, so a wide grid still fits on a
// phone and a small one is not left tiny on a desktop. Measured against the app
// column, not the panel: the panel shrinks to fit the board, so measuring it
// would feed the board's own width back in and never grow.
function fitBoard() {
  if (!S) return;
  const avail = el.app.clientWidth - PANEL_PADDING;
  const size = Math.floor((avail - (S.cols - 1) * GAP) / S.cols);
  el.board.style.setProperty("--cell", clamp(size, 16, MAX_CELL) + "px");
}

/* Mines ------------------------------------------------------------------ */

// Laid only once the first cell is dug, so that click can never be a mine.
function placeMines(safe) {
  const spared = new Set([safe, ...neighbours(safe)]);
  let pool = [];
  for (let i = 0; i < S.n; i++) if (!spared.has(i)) pool.push(i);
  if (pool.length < S.mines) {
    // Too crowded to spare the neighbours; spare the dug cell alone.
    pool = [];
    for (let i = 0; i < S.n; i++) if (i !== safe) pool.push(i);
  }
  for (let k = 0; k < S.mines; k++) {
    const j = k + Math.floor(Math.random() * (pool.length - k));
    [pool[k], pool[j]] = [pool[j], pool[k]];
    S.board[pool[k]] = -1;
  }
  for (let i = 0; i < S.n; i++) {
    if (S.board[i] === -1) continue;
    S.board[i] = neighbours(i).filter(j => S.board[j] === -1).length;
  }
  S.placed = true;
}

/* Moves ------------------------------------------------------------------ */

function reveal(start) {
  const opened = [];
  const stack = [start];
  while (stack.length) {
    const i = stack.pop();
    if (S.revealed[i] || S.flags[i]) continue;
    S.revealed[i] = 1;
    opened.push(i);
    if (S.board[i] === 0) for (const j of neighbours(i)) stack.push(j);
  }
  return opened;
}

function tap(i) {
  if (!S || S.over || S.won) return;
  if (flagMode) { toggleFlag(i); return; }
  if (S.revealed[i]) { chord(i); return; }
  if (S.flags[i]) return;                       // a flag protects its cell
  if (!S.placed) placeMines(i);
  if (S.board[i] === -1) { lose(i); return; }
  animate(reveal(i), i);
  checkWin();
}

function chord(i) {
  const value = S.board[i];
  if (value <= 0) return;
  const nb = neighbours(i);
  if (nb.filter(j => S.flags[j]).length !== value) return;
  const hit = nb.find(j => !S.flags[j] && !S.revealed[j] && S.board[j] === -1);
  if (hit !== undefined) { lose(hit); return; }  // a wrong flag is still fatal
  let opened = [];
  for (const j of nb) {
    if (S.flags[j] || S.revealed[j]) continue;
    opened = opened.concat(reveal(j));
  }
  animate(opened, i);
  checkWin();
}

function toggleFlag(i) {
  if (!S || S.over || S.won || S.revealed[i]) return;
  S.flags[i] = S.flags[i] ? 0 : 1;
  paint(i);
  bounce(i, 0);
  updateCounter();
}

function lose(hit) {
  S.over = true;
  const mines = [];
  for (let i = 0; i < S.n; i++) {
    if (S.board[i] === -1) { S.revealed[i] = 1; mines.push(i); }
  }
  animate(mines.filter(i => i !== hit), hit);
  paint(hit);
  cells[hit].classList.add("boom");
  setMessage("💥 Boom! You hit a mine.", "bad");
}

function checkWin() {
  let open = 0;
  for (let i = 0; i < S.n; i++) if (S.revealed[i]) open++;
  if (open !== S.n - S.mines) return;
  S.won = true;
  const mines = [];
  for (let i = 0; i < S.n; i++) {
    if (S.board[i] === -1 && !S.flags[i]) { S.flags[i] = 1; mines.push(i); }
  }
  mines.forEach((i, k) => { paint(i); bounce(i, k * 40); });
  updateCounter();
  setMessage("🎉 Cleared! Every safe cell uncovered.", "good");
  confetti();
}

/* Drawing ---------------------------------------------------------------- */

function paint(i) {
  const cell = cells[i];
  const value = S.board[i];
  cell.className = "cell";
  cell.style.color = "";
  if (S.revealed[i]) {
    cell.classList.add("open");
    if (value === -1) {
      cell.classList.add("mine");
      cell.textContent = S.flags[i] ? "🚩" : "💣";
    } else if (value > 0) {
      cell.textContent = value;
      cell.style.color = COLORS[value];
    } else {
      cell.textContent = "";
    }
  } else {
    cell.classList.add("covered");
    cell.textContent = S.flags[i] ? "🚩" : "";
  }
}

// Restarting an animation needs the class removed and a reflow forced.
function bounce(i, delay) {
  const cell = cells[i];
  cell.classList.remove("pop");
  void cell.offsetWidth;
  cell.style.animationDelay = delay + "ms";
  cell.classList.add("pop");
}

// Cells ripple outward from wherever the move started.
function animate(list, origin) {
  const [orow, ocol] = rc(origin);
  for (const i of list) {
    const [r, c] = rc(i);
    const ring = Math.min(Math.max(Math.abs(r - orow), Math.abs(c - ocol)), 16);
    paint(i);
    bounce(i, ring * 22);
  }
}

function updateCounter() {
  let flagged = 0;
  for (let i = 0; i < S.n; i++) if (S.flags[i]) flagged++;
  el.counter.textContent = "🚩 " + (S.mines - flagged);
}

function setMessage(text, kind) {
  el.message.textContent = text;
  el.message.className = "message" + (kind ? " " + kind : "");
}

function confetti() {
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  const shades = ["#4c6ef5", "#2e8b48", "#d4443c", "#c2570b", "#7b4bc4"];
  for (let k = 0; k < 24; k++) {
    const piece = document.createElement("i");
    piece.style.left = Math.random() * 100 + "vw";
    piece.style.background = shades[k % shades.length];
    piece.style.animationDelay = Math.random() * 0.5 + "s";
    el.confetti.appendChild(piece);
    setTimeout(() => piece.remove(), 2400);
  }
}

/* Input ------------------------------------------------------------------ */

let pressTimer = null;
let longPressed = false;

const cellFrom = target => {
  const cell = target.closest && target.closest(".cell");
  return cell ? Number(cell.dataset.i) : null;
};

el.board.addEventListener("click", e => {
  const i = cellFrom(e.target);
  if (i !== null) tap(i);
});

el.board.addEventListener("contextmenu", e => {
  const i = cellFrom(e.target);
  if (i === null) return;
  e.preventDefault();
  toggleFlag(i);
});

el.board.addEventListener("touchstart", e => {
  const i = cellFrom(e.target);
  if (i === null) return;
  longPressed = false;
  pressTimer = setTimeout(() => {
    longPressed = true;
    toggleFlag(i);
    // Blocked by the browser until the page has seen a real gesture.
    try { if (navigator.vibrate) navigator.vibrate(15); } catch (e) { /* ignore */ }
  }, LONG_PRESS_MS);
}, { passive: true });

el.board.addEventListener("touchmove", () => clearTimeout(pressTimer), { passive: true });

el.board.addEventListener("touchend", e => {
  clearTimeout(pressTimer);
  const i = cellFrom(e.target);
  if (i === null) return;
  e.preventDefault();                      // suppress the synthetic click
  if (!longPressed) tap(i);
}, { passive: false });

el.flagBtn.addEventListener("click", () => {
  flagMode = !flagMode;
  el.flagBtn.setAttribute("aria-pressed", String(flagMode));
});

el.newBtn.addEventListener("click", newGame);

// Remember the values on open, so Cancel really cancels.
let savedSettings = null;

el.settingsBtn.addEventListener("click", () => {
  savedSettings = [el.rows.value, el.cols.value, el.mines.value];
  el.settings.showModal();
});

el.cancelBtn.addEventListener("click", () => {
  if (savedSettings) [el.rows.value, el.cols.value, el.mines.value] = savedSettings;
  el.settings.close();
});

el.settings.addEventListener("cancel", () => {          // the Esc key
  if (savedSettings) [el.rows.value, el.cols.value, el.mines.value] = savedSettings;
});

el.applyBtn.addEventListener("click", () => {
  newGame();
  el.settings.close();
});

window.addEventListener("resize", fitBoard);

newGame();
