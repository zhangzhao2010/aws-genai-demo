"""simple_chatbot_stream.py"""
import streamlit as st
import boto3
import json

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

st.chat_message('assistant').write('How can I help you?')

if "messages" not in st.session_state:
    st.session_state["messages"] = []

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    # call llm
    with st.chat_message("assistant"):
        streamMsg = st.write_stream(callLLM(st.session_state.messages))
    
    msg = {"role": "assistant", "content": streamMsg}
    st.session_state.messages.append(msg)