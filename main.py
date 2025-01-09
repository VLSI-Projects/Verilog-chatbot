import streamlit as st
import ollama
from typing import Dict, Generator

# Set the page configuration
st.set_page_config(page_title='Verilog Testbench Generator', page_icon='🛠️', layout='wide')

# Function to generate responses using the qwen2.5 model
def ollama_generator(messages: Dict) -> Generator:
    stream = ollama.chat(model="qwen2.5", messages=messages, stream=True)
    ollama.chat(url="https://verilogtestbench.streamlit.app", model="qwen2.5", messages=messages, stream=True)
    for chunk in stream:
        yield chunk['message']['content']

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []

if "prompt_history" not in st.session_state:
    st.session_state.prompt_history = []

# App title and introduction
st.title("🛠️ Verilog Testbench Generator")
st.markdown(
    """
    Welcome to the **Verilog Testbench Generator**! This tool allows you to generate Verilog code or testbenches based on your input. 
    Enter a detailed description of the code or testbench you need, and our AI model will generate it for you.
    """
)

# Create a two-column layout
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("⚡Input Instructions")
    with st.expander("🕹️See how to describe your request"):
        st.markdown("""
        - **Example Input 1**: *Generate a testbench for a 4-bit ripple carry adder.*
        - **Example Input 2**: *Write Verilog code for a 2-to-1 multiplexer and create a corresponding testbench.*
        
        The more details you provide, the better the output will be.
        """)

    # User prompt input
    prompt = st.text_area(
        "🎯Enter your Verilog code/testbench description here:", 
        key="user_input", 
        on_change=lambda: st.session_state.update({"submit_trigger": True})
    )

    # Add a message send button
    if st.button("📨 Send") or st.session_state.get("submit_trigger"):
        if prompt:
            st.session_state.prompt_history.append(prompt)

            # Add the user's input to the session state
            st.session_state.messages.append({"role": "user", "content": prompt})

            # Add a system message to guide the AI model
            st.session_state.messages.append({
                "role": "system",
                "content": "You are an assistant that only generates Verilog code or Verilog testbenches. Please do not generate any other type of content. Focus only on writing valid Verilog code or creating Verilog testbenches based on the user's requests."
            })

            # Display the user's input
            st.write("**Your Request:**")
            st.markdown(f"> {prompt}")

            # Placeholder for the model's response
            response_placeholder = st.empty()

            # Generate the model's response
            response = ""
            with st.spinner("✨Generating Verilog code..."):
                for chunk in ollama_generator(st.session_state.messages):
                    response += chunk
                    response_placeholder.markdown(f"```\n{response}\n```")

            # Append the response to the session history
            st.session_state.messages.append({"role": "assistant", "content": response})

            # Reset the submit trigger
            st.session_state["submit_trigger"] = False

with col2:
    st.subheader("📜Generated Output")
    if st.session_state.messages:
        for message in st.session_state.messages:
            if message["role"] == "assistant":
                st.code(message["content"], language="verilog")

# Additional functionality: Show prompt history
st.sidebar.title("🕹️Prompt History")
if st.session_state.prompt_history:
    for idx, history in enumerate(st.session_state.prompt_history):
        st.sidebar.write(f"{idx + 1}. {history}")
else:
    st.sidebar.write("No prompts submitted yet.")
