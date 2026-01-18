import streamlit as st
import requests
import os

# --- Configuration ---
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth:8000")
MAIN_SERVICE_URL = os.getenv("MAIN_SERVICE_URL", "http://main:8001")

st.set_page_config(page_title="LangChain Assistant", layout="wide")

# --- Session State ---
if "token" not in st.session_state:
    st.session_state.token = None
if "username" not in st.session_state:
    st.session_state.username = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- Authentication ---
def login():
    st.header("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        try:
            resp = requests.post(f"{AUTH_SERVICE_URL}/login", json={"username": username, "password": password})
            if resp.status_code == 200:
                data = resp.json()
                st.session_state.token = data["access_token"]  # In this exam, token IS the username effectively
                st.session_state.username = username
                st.success("Logged in successfully!")
                st.rerun()
            else:
                st.error(resp.json().get("detail", "Login failed"))
        except requests.RequestException as e:
            st.error(f"Connection error: {e}")

def signup():
    st.header("Signup")
    username = st.text_input("New Username")
    password = st.text_input("New Password", type="password")
    if st.button("Signup"):
        try:
            resp = requests.post(f"{AUTH_SERVICE_URL}/signup", json={"username": username, "password": password})
            if resp.status_code == 200:
                st.success("Account created! Please login.")
            else:
                st.error(resp.json().get("detail", "Signup failed"))
        except requests.RequestException as e:
            st.error(f"Connection error: {e}")

def logout():
    st.session_state.token = None
    st.session_state.username = None
    st.session_state.chat_history = []
    st.rerun()

# --- Main App ---
def main_app():
    st.sidebar.title(f"Welcome, {st.session_state.username}")
    if st.sidebar.button("Logout"):
        logout()
    
    page = st.sidebar.radio("Navigation", ["Analyze Code", "Generate Test", "Explain Test", "Full Pipeline", "Chat", "History"])

    headers = {"Authorization": f"Bearer {st.session_state.token}"}

    if page == "Analyze Code":
        st.header("Analyze Python Code")
        code = st.text_area("Enter Python Code", height=200)
        if st.button("Analyze"):
            if code:
                with st.spinner("Analyzing..."):
                    try:
                        resp = requests.post(f"{MAIN_SERVICE_URL}/analyze", json={"code": code}, headers=headers)
                        if resp.status_code == 200:
                            result = resp.json()
                            st.write(f"**Optimal:** {result['is_optimal']}")
                            if result['issues']:
                                st.subheader("Issues")
                                for issue in result['issues']:
                                    st.write(f"- {issue}")
                            if result['suggestions']:
                                st.subheader("Suggestions")
                                for suggestion in result['suggestions']:
                                    st.write(f"- {suggestion}")
                        else:
                            st.error(f"Error: {resp.text}")
                    except requests.RequestException as e:
                        st.error(f"Connection error: {e}")
            else:
                st.warning("Please enter code.")

    elif page == "Generate Test":
        st.header("Generate Unit Test")
        code = st.text_area("Enter Python Function", height=200)
        if st.button("Generate"):
            if code:
                with st.spinner("Generating test..."):
                    try:
                        resp = requests.post(f"{MAIN_SERVICE_URL}/generate_test", json={"code": code}, headers=headers)
                        if resp.status_code == 200:
                            result = resp.json()
                            st.code(result['test_code'], language='python')
                        else:
                            st.error(f"Error: {resp.text}")
                    except requests.RequestException as e:
                        st.error(f"Connection error: {e}")
            else:
                st.warning("Please enter code.")

    elif page == "Explain Test":
        st.header("Explain Unit Test")
        test_code = st.text_area("Enter Test Code", height=200)
        if st.button("Explain"):
            if test_code:
                with st.spinner("Explaining..."):
                    try:
                        resp = requests.post(f"{MAIN_SERVICE_URL}/explain_test", json={"test_code": test_code}, headers=headers)
                        if resp.status_code == 200:
                            result = resp.json()
                            st.markdown(result['explanation'])
                        else:
                            st.error(f"Error: {resp.text}")
                    except requests.RequestException as e:
                        st.error(f"Connection error: {e}")
            else:
                st.warning("Please enter test code.")

    elif page == "Full Pipeline":
        st.header("Full Pipeline (Analyze -> Generate -> Explain)")
        code = st.text_area("Enter Python Code", height=200)
        if st.button("Run Pipeline"):
            if code:
                with st.spinner("Running pipeline..."):
                    try:
                        resp = requests.post(f"{MAIN_SERVICE_URL}/full_pipeline", json={"code": code}, headers=headers)
                        if resp.status_code == 200:
                            result = resp.json()
                            
                            st.subheader("Analysis")
                            if "analysis" in result:
                                analysis = result["analysis"]
                                st.write(f"**Optimal:** {analysis.get('is_optimal')}")
                                if analysis.get('issues'):
                                    st.write("**Issues:**")
                                    for issue in analysis['issues']:
                                        st.write(f"- {issue}")
                            
                            if "test_code" in result:
                                st.subheader("Generated Test")
                                st.code(result["test_code"], language="python")
                            
                            if "explanation" in result:
                                st.subheader("Explanation")
                                st.markdown(result["explanation"])
                                
                            if not result.get("test_code") and analysis.get("is_optimal") == False:
                                st.info("Pipeline stopped because code was not optimal.")

                        else:
                            st.error(f"Error: {resp.text}")
                    except requests.RequestException as e:
                        st.error(f"Connection error: {e}")
            else:
                st.warning("Please enter code.")

    elif page == "Chat":
        st.header("Chat with Assistant")
        
        # Display chat history from session state (local cache of what we've seen)
        # But per requirements we might want to fetch history from server too?
        # The /history endpoint returns all history.
        
        if "messages" not in st.session_state:
             st.session_state.messages = []

        # Display chat messages from history on app rerun
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("What is up?"):
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""
                try:
                    resp = requests.post(f"{MAIN_SERVICE_URL}/chat", json={"message": prompt}, headers=headers)
                    if resp.status_code == 200:
                         full_response = resp.json()["response"]
                         message_placeholder.markdown(full_response)
                         st.session_state.messages.append({"role": "assistant", "content": full_response})
                    else:
                        st.error(f"Error: {resp.text}")
                except requests.RequestException as e:
                     st.error(f"Connection error: {e}")

    elif page == "History":
        st.header("Session History (from Server)")
        if st.button("Refresh History"):
            try:
                resp = requests.get(f"{MAIN_SERVICE_URL}/history", headers=headers)
                if resp.status_code == 200:
                    history = resp.json()
                    for msg in history:
                        st.text(f"{msg['role'].upper()}: {msg['content']}")
                        st.markdown("---")
                else:
                    st.error(f"Error: {resp.text}")
            except requests.RequestException as e:
                st.error(f"Connection error: {e}")


# --- Entry Point ---
if not st.session_state.token:
    tab1, tab2 = st.tabs(["Login", "Signup"])
    with tab1:
        login()
    with tab2:
        signup()
else:
    main_app()
