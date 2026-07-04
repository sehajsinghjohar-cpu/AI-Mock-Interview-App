import json
import os
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_groq import ChatGroq


load_dotenv()


DEFAULT_MODEL = "llama-3.3-70b-versatile"


INTERVIEWER_SYSTEM_PROMPT = """You are an expert AI mock interviewer.

Interview style:
- Ask exactly one question at a time.
- Adapt follow-up questions to the candidate's previous answer.
- Keep questions realistic for the selected role, level, and interview type.
- Do not answer your own questions.
- Be concise, professional, and encouraging.
- If the candidate gives a weak or vague answer, ask a useful probing follow-up.
- Track coverage across fundamentals, practical experience, tradeoffs, and communication.

Session configuration:
Role: {role}
Level: {level}
Interview type: {interview_type}
Focus areas: {focus_areas}
Number of questions: {question_count}

Begin by greeting the candidate in one sentence, then ask the first interview question.
"""


FEEDBACK_SYSTEM_PROMPT = """You are a senior interview coach.

Return practical, candid feedback for the mock interview. Use this structure:

## Overall verdict
One concise paragraph.

## Scorecard
- Technical accuracy: X/10
- Problem solving: X/10
- Communication: X/10
- Role readiness: X/10

## Strengths
3-5 bullets.

## Improvements
3-5 bullets with specific advice.

## Suggested answer patterns
Give 2-3 reusable answer frameworks the candidate can use next time.

## Hiring recommendation
Choose one: Strong hire, Hire, Lean hire, Lean no-hire, No-hire.
Explain briefly.
"""


def init_state() -> None:
    defaults = {
        "started": False,
        "finished": False,
        "messages": [],
        "question_count_seen": 0,
        "session_config": {},
        "feedback": "",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def get_api_key() -> str:
    return st.session_state.get("groq_api_key") or os.getenv("GROQ_API_KEY", "")


def make_llm(temperature: float = 0.55) -> ChatGroq:
    api_key = get_api_key()
    if not api_key:
        st.error("Add your Groq API key in the sidebar or set GROQ_API_KEY in your environment.")
        st.stop()

    return ChatGroq(
        model=st.session_state.get("model", DEFAULT_MODEL),
        groq_api_key=api_key,
        temperature=temperature,
        streaming=True,
    )


def reset_interview() -> None:
    st.session_state.started = False
    st.session_state.finished = False
    st.session_state.messages = []
    st.session_state.question_count_seen = 0
    st.session_state.session_config = {}
    st.session_state.feedback = ""


def build_system_message(config: dict) -> SystemMessage:
    return SystemMessage(
        content=INTERVIEWER_SYSTEM_PROMPT.format(
            role=config["role"],
            level=config["level"],
            interview_type=config["interview_type"],
            focus_areas=config["focus_areas"],
            question_count=config["question_count"],
        )
    )


def stream_interviewer_reply() -> str:
    llm = make_llm()
    messages = [build_system_message(st.session_state.session_config), *st.session_state.messages]
    response_placeholder = st.empty()
    full_response = ""

    for chunk in llm.stream(messages):
        full_response += chunk.content or ""
        response_placeholder.markdown(full_response)

    return full_response


def generate_feedback() -> str:
    llm = make_llm(temperature=0.25)
    transcript = "\n".join(
        f"{'Candidate' if isinstance(message, HumanMessage) else 'Interviewer'}: {message.content}"
        for message in st.session_state.messages
    )
    config = st.session_state.session_config
    messages = [
        SystemMessage(content=FEEDBACK_SYSTEM_PROMPT),
        HumanMessage(
            content=(
                "Evaluate this mock interview transcript.\n\n"
                f"Role: {config['role']}\n"
                f"Level: {config['level']}\n"
                f"Interview type: {config['interview_type']}\n"
                f"Focus areas: {config['focus_areas']}\n\n"
                f"Transcript:\n{transcript}"
            )
        ),
    ]

    response_placeholder = st.empty()
    full_response = ""
    for chunk in llm.stream(messages):
        full_response += chunk.content or ""
        response_placeholder.markdown(full_response)

    return full_response


def export_session() -> str:
    payload = {
        "created_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "config": st.session_state.session_config,
        "transcript": [
            {
                "role": "candidate" if isinstance(message, HumanMessage) else "interviewer",
                "content": message.content,
            }
            for message in st.session_state.messages
        ],
        "feedback": st.session_state.feedback,
    }
    return json.dumps(payload, indent=2)


def render_sidebar() -> None:
    with st.sidebar:
        st.header("Setup")
        st.text_input(
            "Groq API key",
            type="password",
            key="groq_api_key",
            placeholder="gsk_...",
            help="You can also set GROQ_API_KEY in a .env file.",
        )
        st.selectbox(
            "Model",
            [
                "llama-3.3-70b-versatile",
                "llama-3.1-8b-instant",
                "openai/gpt-oss-120b",
                "openai/gpt-oss-20b",
            ],
            key="model",
        )

        st.divider()
        role = st.text_input("Target role", value="Backend Engineer")
        level = st.selectbox("Level", ["Intern", "Junior", "Mid-level", "Senior", "Staff"])
        interview_type = st.selectbox(
            "Interview type",
            ["Technical deep dive", "Behavioral", "System design", "Coding concepts", "Mixed"],
        )
        focus_areas = st.text_area(
            "Focus areas",
            value="Python, APIs, databases, debugging, system design tradeoffs",
            height=90,
        )
        question_count = st.slider("Questions", min_value=3, max_value=12, value=6)

        start_disabled = st.session_state.started and not st.session_state.finished
        if st.button("Start interview", type="primary", disabled=start_disabled, use_container_width=True):
            st.session_state.session_config = {
                "role": role.strip() or "Software Engineer",
                "level": level,
                "interview_type": interview_type,
                "focus_areas": focus_areas.strip() or "General role readiness",
                "question_count": question_count,
            }
            st.session_state.messages = []
            st.session_state.feedback = ""
            st.session_state.finished = False
            st.session_state.started = True
            st.session_state.question_count_seen = 1

            with st.chat_message("assistant"):
                first_reply = stream_interviewer_reply()
            st.session_state.messages.append(AIMessage(content=first_reply))
            st.rerun()

        if st.button("Reset", use_container_width=True):
            reset_interview()
            st.rerun()


def render_chat() -> None:
    for message in st.session_state.messages:
        role = "user" if isinstance(message, HumanMessage) else "assistant"
        with st.chat_message(role):
            st.markdown(message.content)

    if st.session_state.finished:
        return

    if not st.session_state.started:
        st.info("Configure the session in the sidebar, then start the interview.")
        return

    answer = st.chat_input("Answer the interviewer...")
    if not answer:
        return

    st.session_state.messages.append(HumanMessage(content=answer))
    with st.chat_message("user"):
        st.markdown(answer)

    if st.session_state.question_count_seen >= st.session_state.session_config["question_count"]:
        st.session_state.finished = True
        with st.chat_message("assistant"):
            st.markdown("Thanks. I have enough signal now. Generating your interview feedback...")
        with st.spinner("Reviewing transcript..."):
            st.session_state.feedback = generate_feedback()
        st.rerun()

    st.session_state.question_count_seen += 1
    with st.chat_message("assistant"):
        reply = stream_interviewer_reply()
    st.session_state.messages.append(AIMessage(content=reply))
    st.rerun()


def render_feedback() -> None:
    if not st.session_state.feedback:
        return

    st.subheader("Interview feedback")
    st.markdown(st.session_state.feedback)
    st.download_button(
        "Download session JSON",
        data=export_session(),
        file_name="mock_interview_session.json",
        mime="application/json",
        use_container_width=True,
    )


def main() -> None:
    st.set_page_config(
        page_title="AI Mock Interview Simulator",
        page_icon=":material/record_voice_over:",
        layout="wide",
    )
    init_state()
    render_sidebar()

    st.title("AI Mock Interview Simulator")
    st.caption("Practice targeted interviews with Groq, LangChain, and Streamlit.")

    left, right = st.columns([0.68, 0.32], gap="large")
    with left:
        render_chat()
    with right:
        if st.session_state.started:
            st.subheader("Session")
            st.write(f"**Role:** {st.session_state.session_config.get('role', '-')}")
            st.write(f"**Level:** {st.session_state.session_config.get('level', '-')}")
            st.write(f"**Type:** {st.session_state.session_config.get('interview_type', '-')}")
            st.progress(
                min(
                    st.session_state.question_count_seen,
                    st.session_state.session_config.get("question_count", 1),
                )
                / st.session_state.session_config.get("question_count", 1)
            )
            st.caption(
                f"Question {min(st.session_state.question_count_seen, st.session_state.session_config.get('question_count', 1))}"
                f" of {st.session_state.session_config.get('question_count', 1)}"
            )
        render_feedback()


if __name__ == "__main__":
    main()
