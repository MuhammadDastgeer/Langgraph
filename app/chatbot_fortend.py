import streamlit as st
from chatbot_backend import chatbot, retrieve_all_threads
from langchain_core.messages import HumanMessage
import uuid

# **************************************** Utility Functions *************************

def generate_thread_id():
    return uuid.uuid4()

def reset_chat():
    st.session_state['thread_id'] = generate_thread_id()
    st.session_state['message_history'] = []

def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)

def load_conversation(thread_id):
    """Load messages for a given thread_id safely."""
    state = chatbot.get_state(config={'configurable': {'thread_id': thread_id}})
    if state and 'messages' in state.values:
        return state.values['messages']
    return []

# **************************************** Session Setup ******************************

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = []  # start empty

# **************************************** Sidebar UI *********************************

st.sidebar.title('Chatbot')

if st.sidebar.button('New Chat'):
    reset_chat()

st.sidebar.header('My Conversations')

for thread_id in st.session_state['chat_threads'][::-1]:
    messages = load_conversation(thread_id)
    if messages:
        first_human_msg = next((msg.content for msg in messages if isinstance(msg, HumanMessage)), None)
        title = first_human_msg if first_human_msg else str(thread_id)
    else:
        title = str(thread_id)

    if st.sidebar.button(title):
        st.session_state['thread_id'] = thread_id
        temp_messages = []
        for msg in messages:
            role = 'user' if isinstance(msg, HumanMessage) else 'assistant'
            temp_messages.append({'role': role, 'content': msg.content})
        st.session_state['message_history'] = temp_messages

# **************************************** Main UI ************************************

# Load existing conversation
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

user_input = st.chat_input('Type here')

if user_input:
    # پہلی بار message آنے پر thread add کریں
    if st.session_state['thread_id'] not in st.session_state['chat_threads']:
        add_thread(st.session_state['thread_id'])

    # Add user message to history
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message('user'):
        st.text(user_input)

    CONFIG = {'configurable': {'thread_id': st.session_state['thread_id']}}

    # Get assistant response
    with st.chat_message('assistant'):
        ai_message = st.write_stream(
            message_chunk.content
            for message_chunk, metadata in chatbot.stream(
                {'messages': [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode='messages'
            )
        )

    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})
