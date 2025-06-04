def show_board():
    for r in range(rows):
        cols_layout = st.columns(cols)  # Removed gap
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

            cell_style = (
                "display:flex; align-items:center; justify-content:center; "
                "font-size:22px; height:40px; width:100%; border:1px solid #ccc; padding:0; margin:0;"
            )

            if revealed or show_bomb:
                if cell_is_mine:
                    label = "💣"
                    color_style = "color:red;"
                elif val == 0:
                    label = "&nbsp;"
                    color_style = ""
                else:
                    color = colors[val]
                    label = f"<b style='color:{color}'>{val}</b>"
                    color_style = ""

                cols_layout[c].markdown(
                    f"<div style='{cell_style}{color_style}'>{label}</div>",
                    unsafe_allow_html=True
                )
            else:
                label = "🚩" if flagged else ""
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
