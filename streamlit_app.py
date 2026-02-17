import os
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components

from super_agent.brain.openai_brain import OpenAIBrain
from super_agent.voice.elevenlabs_tts import ElevenLabsTTS


# ==================================================
# Page Config
# ==================================================

st.set_page_config(page_title="Super Agent (V1)", layout="wide")

st.title("Super Agent (V1)")
st.caption("Conversation-aware AI with optional voice + avatar")


# ==================================================
# Layout (Chat Left / Avatar Right)
# ==================================================

chat_col, avatar_col = st.columns([2, 1])


# ==================================================
# Sidebar Settings
# ==================================================

with st.sidebar:
    st.header("Agent Settings")

    system_prompt = st.text_area(
        "System Prompt",
        value="You are a helpful AI assistant.",
        height=150
    )

    st.divider()

    enable_voice = st.checkbox("Enable ElevenLabs Voice", value=False)

    voice_id = st.text_input(
        "ElevenLabs Voice ID",
        value="4YYIPFl9wE5c4L2eu2Gb"
    )

    st.divider()

    show_avatar = st.checkbox("Show D-ID Avatar", value=False)

    did_share_url = st.text_input(
        "D-ID Share URL",
        value=""
    )


# ==================================================
# Session State
# ==================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "audio_counter" not in st.session_state:
    st.session_state.audio_counter = 0


# ==================================================
# Brain Initialization
# ==================================================

brain = OpenAIBrain(system_prompt=system_prompt)


# ==================================================
# Optional Voice Init
# ==================================================

tts = None
if enable_voice and voice_id.strip():
    try:
        tts = ElevenLabsTTS(voice_id=voice_id.strip())
    except Exception as e:
        st.sidebar.warning("Voice failed to initialize.")
        tts = None


# ==================================================
# Avatar Panel
# ==================================================

with avatar_col:
    if show_avatar and did_share_url.strip():
        components.iframe(
            did_share_url.strip(),
            height=720,
            scrolling=True
        )
    else:
        st.info("Enable 'Show D-ID Avatar' and paste a share URL.")


# ==================================================
# Chat History
# ==================================================

with chat_col:

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

            if msg["role"] == "assistant" and msg.get("audio_path"):
                st.audio(msg["audio_path"])


    # ==================================================
    # Chat Input
    # ==================================================

    user_text = st.chat_input("Type a message...")

    if user_text:

        # Store user message
        st.session_state.messages.append({
            "role": "user",
            "content": user_text
        })

        with st.chat_message("user"):
            st.markdown(user_text)

        # Get AI reply
        try:
            reply = brain.reply(st.session_state.messages)
        except Exception as e:
            st.error(f"Brain error: {e}")
            st.stop()

        assistant_message = {
            "role": "assistant",
            "content": reply
        }

        # ==================================================
        # Optional Voice Generation
        # ==================================================

        if tts:
            try:
                Path("temp").mkdir(exist_ok=True)

                st.session_state.audio_counter += 1
                audio_file = f"temp/reply_{st.session_state.audio_counter}.mp3"

                audio_path = tts.synthesize_to_file(
                    reply,
                    audio_file
                )

                assistant_message["audio_path"] = audio_path

            except Exception as e:
                st.warning("Voice generation failed. Showing text only.")

        # Save assistant message
        st.session_state.messages.append(assistant_message)

        # Render assistant reply
        with st.chat_message("assistant"):
            st.markdown(reply)

            if assistant_message.get("audio_path"):
                st.audio(assistant_message["audio_path"])
