import streamlit as st
import openai
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

TOOLS = {
    "Paraphrase": {
        "description": "Rephrases your text while preserving the original meaning.",
        "system_prompt": "You are a helpful assistant that paraphrases text while preserving its meaning."
    },
    "Fix Grammar": {
        "description": "Corrects grammatical mistakes in your text.",
        "system_prompt": "You are a helpful assistant that fixes grammatical errors in a given text."
    },
    "Abstract Writing": {
        "description": "Generates a concise abstract for your longer text.",
        "system_prompt": "You are a helpful assistant that writes a concise academic-style abstract from a longer passage."
    }
}

# --- Sidebar ---
st.sidebar.title("🧠 AI Tools")
tool = st.sidebar.radio("Select a tool", list(TOOLS.keys()))

# --- Initialize State ---
if "tool_chats" not in st.session_state:
    st.session_state.tool_chats = {t: {} for t in TOOLS}
if "active_chat_id" not in st.session_state:
    st.session_state.active_chat_id = {t: None for t in TOOLS}
if "chat_titles" not in st.session_state:
    st.session_state.chat_titles = {t: {} for t in TOOLS}

tool_chats = st.session_state.tool_chats[tool]
chat_titles = st.session_state.chat_titles[tool]
active_id = st.session_state.active_chat_id[tool]

def new_chat_id():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

# --- Sidebar Chat Management ---
st.sidebar.markdown("### 💬 Chats")

if st.sidebar.button("➕ New Chat"):
    cid = new_chat_id()
    title = f"Chat {len(chat_titles) + 1}"
    tool_chats[cid] = []
    chat_titles[cid] = title
    st.session_state.active_chat_id[tool] = cid
    st.rerun()  # <-- Force a rerun to refresh state/UI



for cid in list(tool_chats.keys()):
    if f"show_menu_{cid}" not in st.session_state:
        st.session_state[f"show_menu_{cid}"] = False
    if f"edit_title_{cid}" not in st.session_state:
        st.session_state[f"edit_title_{cid}"] = False

    col1, col2 = st.sidebar.columns([8, 1])
    with col1:
        if st.sidebar.button(chat_titles[cid], key=f"select_{cid}"):
            st.session_state.active_chat_id[tool] = cid
            st.session_state[f"show_menu_{cid}"] = False
            st.rerun()
    with col2:
        if st.sidebar.button("⋮", key=f"menu_btn_{cid}"):
            st.session_state[f"show_menu_{cid}"] = not st.session_state[f"show_menu_{cid}"]

    if st.session_state[f"show_menu_{cid}"]:
        with st.sidebar:
            if st.button("✏️ Rename", key=f"rename_option_{cid}"):
                st.session_state[f"edit_title_{cid}"] = True
            if st.button("🗑️ Delete", key=f"delete_option_{cid}"):
                del tool_chats[cid]
                del chat_titles[cid]
                if st.session_state.active_chat_id[tool] == cid:
                    st.session_state.active_chat_id[tool] = None
                st.rerun()

        if st.session_state[f"edit_title_{cid}"]:
            new_title = st.text_input("New Title", chat_titles[cid], key=f"title_input_{cid}")
            if st.button("✅ Save", key=f"save_title_{cid}"):
                chat_titles[cid] = new_title.strip() or chat_titles[cid]
                st.session_state[f"edit_title_{cid}"] = False
                st.session_state[f"show_menu_{cid}"] = False
                st.rerun()


# --- Main Area ---
st.title(f"🛠 {tool}")
st.caption(TOOLS[tool]["description"])

if not active_id or active_id not in tool_chats:
    st.info("Start a new chat from the sidebar.")
    st.stop()

chat_history = tool_chats[active_id]

for msg in chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Enter your message..."):
    chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    messages = [{"role": "system", "content": TOOLS[tool]["system_prompt"]}] + chat_history

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7
        )
        reply = response.choices[0].message["content"].strip()
    except Exception as e:
        reply = f"❌ Error: {str(e)}"

    chat_history.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.markdown(reply)
