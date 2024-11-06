"""chatbot.py"""
import streamlit as st
from datetime import datetime
from typing import List, Dict
import boto3

bedrock_runtime = boto3.client('bedrock-runtime')

def callLLM(messages):
    claudeMessages = []
    for message in messages:
        claudeMessages.append({'role': message['role'], 'content':[{'text': message['content']}]})
    
    response = bedrock_runtime.converse_stream(
        modelId='anthropic.claude-3-sonnet-20240229-v1:0',
        messages=claudeMessages
    )
    for chunk in response["stream"]:
        if "contentBlockDelta" in chunk:
            text = chunk["contentBlockDelta"]["delta"]["text"]
            yield text

# ChatSession for saving multi-turn conversations
class ChatSession:
    def __init__(self):
        self.dialogues = []
        self.id = datetime.now().strftime('%Y%m%d%H%M%S')

    def add_message(self, role: str, content: str):
        self.dialogues.append({"role": role, "content": content})

class ChatbotApp:
    def __init__(self):
        self.sessions: Dict[str, ChatSession] = {}
        self.current_session_id = None

    def new_session(self):
        session = ChatSession()
        self.sessions[session.id] = session
        self.current_session_id = session.id

    def select_session(self, session_id: str):
        if session_id in self.sessions:
            self.current_session_id = session_id

    def add_message(self, role: str, content: str):
        if self.current_session_id is None:
            self.new_session()
        self.sessions[self.current_session_id].add_message(role, content)

    def get_session_messages(self, session_id: str) -> List[Dict[str, str]]:
        return self.sessions[session_id].dialogues if session_id in self.sessions else []

# create chatbot app instance
if 'ChatBotApp' not in st.session_state:
    st.session_state['ChatBotApp'] = ChatbotApp()

app = st.session_state['ChatBotApp']

st.title("Chatbot")

st.sidebar.title("Conversations")

if st.sidebar.button("Start New Conversation"):
    app.new_session()

st.sidebar.subheader("History")
for session_id in app.sessions.keys():
    current_messages = app.get_session_messages(session_id)
    dialog_name = 'New Conversation'
    if len(current_messages) > 0:
        dialog_name = current_messages[0]['content'][:20]
    if st.sidebar.button(dialog_name, f"{session_id}"):
        app.select_session(session_id)

# 获取当前会话信息
if app.current_session_id:
    current_messages = app.get_session_messages(app.current_session_id)
    st.write(f"### Conversation ID: {app.current_session_id}")

    st.chat_message('assistant').write('How can I help you?')
    for msg in current_messages:
        st.chat_message(msg['role']).write(msg['content'])

    if prompt := st.chat_input():
        app.add_message('user', prompt)
        st.chat_message("user").write(prompt)
        
        # call llm
        with st.chat_message("assistant"):
            streamMsg = st.write_stream(callLLM(app.get_session_messages(app.current_session_id)))
        
        app.add_message('assistant', streamMsg)
else:
    st.write("No conversation selected. Start a new one or select an existing conversation.")
