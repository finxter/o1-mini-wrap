import streamlit as st
from openai import OpenAI

# Define the prompt
copy_prompt = (
    "A monkey only becomes happy when it eats 3 different fruits. "
    "How many monkeys can I make happy if I have 20 pears, 30 bananas, "
    "40 peaches, and 50 apples?"
)

# Show title and description.
st.title("🍓 Trying OpenAI's o1-mini")

# Optional: Add a brief description or instructions
st.markdown("""
Welcome to the OpenAI Chat Interface! Below you can find a predefined prompt that you can use. 
Feel free to copy it using the button provided.
""")

# Display the prompt in a text area
st.text_area(
    "📋 Prompt for Copying:",
    value=copy_prompt,
    height=150,
    max_chars=None,
    key="prompt_text_area"
)

# Add a copy button if available
if hasattr(st, "copy_button"):
    st.copy_button(
        label="📋 Copy Prompt",
        data=copy_prompt,
        mime=None,
        key="copy_button"
    )
else:
    st.warning(
        "Streamlit version does not support `st.copy_button`. "
        "Please update Streamlit or use the manual copy option.",
        icon="⚠️"
    )

st.markdown("---")  # Add a horizontal separator for better layout

# Ask user for their OpenAI API key via `st.text_input`.
# Alternatively, you can store the API key in `./.streamlit/secrets.toml` and access it
# via `st.secrets`, see https://docs.streamlit.io/develop/concepts/connections/secrets-management
openai_api_key = st.secrets.get("OPENAI_KEY", "")

if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
else:
    try:
        # Create an OpenAI client.
        client = OpenAI(api_key=openai_api_key)

        # Create a session state variable to store the chat messages. This ensures that the
        # messages persist across reruns.
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Display the existing chat messages via `st.chat_message`.
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Create a chat input field to allow the user to enter a message. This will display
        # automatically at the bottom of the page.
        prompt = st.chat_input("What is up?")

        if prompt:
            # Store and display the current prompt.
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Generate a response using the OpenAI API.
            stream = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
            )

            # Stream the response to the chat using `st.write_stream`, then store it in 
            # session state.
            with st.chat_message("assistant"):
                response = st.write_stream(stream)
            st.session_state.messages.append({"role": "assistant", "content": response})

    except Exception as e:
        st.error(f"An error occurred: {e}")
