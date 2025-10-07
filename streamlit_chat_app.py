# Import the necessary libraries
import streamlit as st
from google import genai

# --- 1. Page Configuration and Title ---

st.title("🏕️ AURA-Alpine Universal Route Assistant | Ready to assist your Mountain Expedition")
st.caption("Ask anything about mountain expeditions — from preparation to survival tips.")
st.caption("Supported by: Google's Gemini Flash model")

# --- 2. Sidebar for Settings and Expedition Context ---

with st.sidebar:
    st.subheader("⚙️ Settings")

    # Input API Key
    google_api_key = st.text_input("Google AI API Key", type="password")
    reset_button = st.button("🔄 Reset Conversation", help="Clear all messages and start fresh")

    st.divider()
    st.subheader("🏔️ Expedition Preferences")

    # 1️ Focus area
    focus_topic = st.selectbox(
        "Focus area of your expedition question:",
        [
            "General Preparation",
            "Clothing & Equipment",
            "Weather & Climate",
            "Safety & Emergency Tips",
            "Nutrition & Hydration",
            "Navigation & Route Planning",
            "Mental Readiness & Teamwork"
        ],
        index=0
    )

    # 2️ Level pengalaman
    experience_level = st.radio(
        "Your experience level:",
        ["Beginner", "Intermediate", "Advanced"]
    )

    # 3️ Target gunung (opsional)
    mountain_name = st.text_input(
        "Target mountain (optional):",
        placeholder="e.g., Mount Rinjani, Mount Fuji, Everest Base Camp"
    )

    # 4️ Musim pendakian
    season = st.selectbox(
        "Season of expedition:",
        ["Dry season", "Rainy season", "Winter (High altitude)", "All year"]
    )

    # 5️ Checklist perlengkapan
    st.write("🎒 Equipment Checklist")
    gear_items = {
        "Tent": st.checkbox("Tent", value=True),
        "Sleeping bag": st.checkbox("Sleeping bag"),
        "Hiking boots": st.checkbox("Hiking boots", value=True),
        "Cooking gear": st.checkbox("Cooking gear"),
        "First aid kit": st.checkbox("First aid kit", value=True),
        "Navigation tools (map/compass/GPS)": st.checkbox("Navigation tools (map/compass/GPS)")
    }

    # 6️ Gaya respon
    response_style = st.selectbox(
        "Response style:",
        ["Short & Practical", "Detailed & Educational", "Casual & Friendly"]
    )

    # 7️ Bahasa respon
    response_language = st.radio(
        "Response language:",
        ["English", "Bahasa Indonesia"]
    )

    st.caption("Customize your assistant's advice for your specific expedition.")

# --- 3. API Key and Client Initialization ---

if not google_api_key:
    st.info("Please add your Google AI API key in the sidebar to start chatting.", icon="🗝️")
    st.stop()

if ("genai_client" not in st.session_state) or (getattr(st.session_state, "_last_key", None) != google_api_key):
    try:
        st.session_state.genai_client = genai.Client(api_key=google_api_key)
        st.session_state._last_key = google_api_key
        st.session_state.pop("chat", None)
        st.session_state.pop("messages", None)
    except Exception as e:
        st.error(f"Invalid API Key: {e}")
        st.stop()

# --- 4. Chat History Management ---

if "chat" not in st.session_state:
    st.session_state.chat = st.session_state.genai_client.chats.create(model="gemini-2.5-flash")

if "messages" not in st.session_state:
    st.session_state.messages = []

if reset_button:
    st.session_state.pop("chat", None)
    st.session_state.pop("messages", None)
    st.rerun()

# --- 5. Display Past Messages ---

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 6. Handle User Input and API Communication ---

prompt = st.chat_input("Type your message here...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 🔗 Combine context info from sidebar into the system prompt
    selected_gear = [item for item, checked in gear_items.items() if checked]
    gear_text = ", ".join(selected_gear) if selected_gear else "No gear specified"

    context_prompt = (
        f"You are an experienced mountain expedition assistant. "
        f"Answer based on the following context:\n\n"
        f"- Focus: {focus_topic}\n"
        f"- Experience Level: {experience_level}\n"
        f"- Target Mountain: {mountain_name if mountain_name else 'Not specified'}\n"
        f"- Season: {season}\n"
        f"- Carried Equipment: {gear_text}\n"
        f"- Response Style: {response_style}\n"
        f"- Language: {response_language}\n\n"
        f"User message: {prompt}"
    )

    try:
        response = st.session_state.chat.send_message(context_prompt)
        answer = response.text if hasattr(response, "text") else str(response)
    except Exception as e:
        answer = f"An error occurred: {e}"

    with st.chat_message("assistant"):
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
