import streamlit as st

pages = [
    st.Page("simple_chatbot.py", title="Simple Chatbot"),
    st.Page("simple_chatbot_stream.py", title="Simple Chatbot Stream"),
    st.Page("chatbot.py", title="Chatbot"),
]

pg = st.navigation(pages)
pg.run()