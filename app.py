import sqlite3
from datetime import datetime
from pathlib import Path

import streamlit as st


DB_PATH = Path(__file__).with_name("suggestions.db")


def initialize_database() -> None:
    """Create the suggestions table if it does not already exist."""
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS suggestions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )


def save_suggestion(content: str) -> None:
    """Save one suggestion. Names and other identifying fields are not collected."""
    submitted_at = datetime.now().astimezone().isoformat(timespec="seconds")
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute(
            "INSERT INTO suggestions (content, created_at) VALUES (?, ?)",
            (content, submitted_at),
        )


def get_suggestions() -> list[tuple[str, str]]:
    """Return suggestions in newest-first order."""
    with sqlite3.connect(DB_PATH) as connection:
        rows = connection.execute(
            "SELECT content, created_at FROM suggestions ORDER BY id DESC"
        ).fetchall()
    return rows


st.set_page_config(page_title="한 줄 건의함", page_icon="💬")
initialize_database()

st.title("💬 한 줄 건의함")
st.write("자유롭게 의견을 남겨 주세요. 이름은 입력하지 않습니다.")

with st.form("suggestion_form", clear_on_submit=True):
    suggestion = st.text_input(
        "건의 내용",
        placeholder="건의 내용을 한 줄로 입력해 주세요.",
    )
    submitted = st.form_submit_button("제출하기", use_container_width=True)

if submitted:
    cleaned_suggestion = suggestion.strip()
    if not cleaned_suggestion:
        st.error("건의 내용을 입력해 주세요. 빈 내용은 제출할 수 없습니다.")
    else:
        save_suggestion(cleaned_suggestion)
        st.success("건의가 제출되었습니다.")

st.divider()
st.subheader("접수된 건의")

suggestions = get_suggestions()
if not suggestions:
    st.info("아직 등록된 건의가 없습니다.")
else:
    for content, created_at in suggestions:
        try:
            formatted_time = datetime.fromisoformat(created_at).strftime(
                "%Y-%m-%d %H:%M"
            )
        except ValueError:
            formatted_time = created_at

        with st.container(border=True):
            st.write(content)
            st.caption(formatted_time)
