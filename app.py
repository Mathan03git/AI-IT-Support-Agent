
import streamlit as st
import requests

# =====================================================
# CONFIGURATION
# =====================================================

API_BASE_URL = "http://127.0.0.1:8000"

API_URL = f"{API_BASE_URL}/ask"
HISTORY_URL = f"{API_BASE_URL}/history"
LOG_ANALYZE_URL = f"{API_BASE_URL}/analyze-log"
LOG_HISTORY_URL = f"{API_BASE_URL}/log-history"

st.set_page_config(
    page_title="AI IT Support Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =====================================================
# CUSTOM DESIGN
# =====================================================

st.markdown("""
<style>

/* MAIN BACKGROUND */
.stApp {
    background:
        radial-gradient(ellipse at top left, #25205c 0%, transparent 45%),
        radial-gradient(ellipse at bottom right, #123d59 0%, transparent 40%),
        linear-gradient(135deg, #080b18, #10152b, #15112b);
    color: #f4f5ff;
}

/* ==============================
   STREAMLIT HEADER
============================== */
header[data-testid="stHeader"] {
    background: linear-gradient(
        180deg,
        #10152b,
        #11152b
    ) !important;
    border-bottom: 1px solid #34345e;
}

[data-testid="stToolbar"] {
    top: 0.25rem !important;
    right: 1rem !important;
}

/* CONTENT WIDTH */
.block-container {
    padding-top: 2.4rem;
    padding-bottom: 2rem;
    max-width: 1500px;
}

/* SIDEBAR */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #11152b, #17152e);
    border-right: 1px solid #34345e;
}

/* TEXT */
h1, h2, h3, h4 {
    color: #ffffff !important;
    font-weight: 700 !important;
}

p, label, li {
    color: #c4c9e8;
}

/* HEADER */
.main-title {
    font-size: 38px;
    font-weight: 850;
    background: linear-gradient(90deg, #ffffff, #a78bfa, #67e8f9);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    padding: 8px 0;
}

.subtitle {
    color: #9ca9d2;
    font-size: 15px;
}

/* HEADER STATUS */
.status-pill {
    display: inline-block;
    margin-top: 15px;
    padding: 8px 16px;
    border-radius: 30px;
    background: rgba(34, 197, 94, 0.12);
    border: 1px solid rgba(34, 197, 94, 0.4);
    color: #4ade80;
    font-size: 12px;
    font-weight: 700;
    white-space: nowrap;
}

/* DASHBOARD CARDS */
[data-testid="stMetric"] {
    background: linear-gradient(145deg, #202747, #171d38);
    border: 1px solid #424b7a;
    border-radius: 18px;
    padding: 20px;
    box-shadow: 0 8px 25px rgba(0,0,0,0.25);
    transition: 0.25s ease;
}

[data-testid="stMetric"]:hover {
    border-color: #9b87ff;
    transform: translateY(-3px);
    box-shadow: 0 8px 25px rgba(112, 91, 255, 0.18);
}

[data-testid="stMetricLabel"] {
    color: #aab4dc !important;
}

[data-testid="stMetricValue"] {
    color: #ffffff !important;
    font-weight: 800;
}

/* CUSTOM CARDS */
.assistant-card {
    background: linear-gradient(135deg, #222c50, #29204d);
    border: 1px solid #6253a6;
    border-radius: 20px;
    padding: 25px;
    margin: 15px 0;
    box-shadow: 0 10px 35px rgba(0,0,0,0.25);
}

.user-card {
    background: linear-gradient(135deg, #41317b, #253e70);
    border: 1px solid #8170db;
    padding: 18px;
    border-radius: 18px;
    margin: 12px 0;
}

/* BUTTONS */
div.stButton > button {
    background: linear-gradient(110deg, #6d4aff, #3978db);
    color: white !important;
    border: 1px solid #8d7aff;
    border-radius: 12px;
    padding: 10px 16px;
    font-weight: 650;
    transition: 0.25s ease;
}

div.stButton > button:hover {
    background: linear-gradient(110deg, #895fff, #36b9dc);
    border-color: #b3a6ff;
    box-shadow: 0 5px 20px rgba(111, 83, 255, 0.35);
}

/* CHAT INPUT */
[data-testid="stChatInput"] {
    background: #1b2340;
    border: 1px solid #6458a7;
    border-radius: 18px;
}

/* FILE UPLOADER */
[data-testid="stFileUploader"] {
    background: linear-gradient(135deg, #1c2544, #28204a);
    border: 1px dashed #8c7cff;
    border-radius: 18px;
    padding: 16px;
}

/* EXPANDERS */
[data-testid="stExpander"] {
    background: #19213b;
    border: 1px solid #424b76;
    border-radius: 14px;
    margin-bottom: 10px;
}

/* TABS */
button[data-baseweb="tab"] {
    color: #b9c2e8;
    font-weight: 650;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: #a78bfa;
}

/* ALERTS */
[data-testid="stAlert"] {
    border-radius: 14px;
}

/* CHART */
[data-testid="stVegaLiteChart"],
[data-testid="stArrowVegaLiteChart"] {
    background: #1b2340;
    border: 1px solid #424b76;
    border-radius: 18px;
    padding: 12px;
}

/* DIVIDER */
hr {
    border-color: #363e69;
}

/* FOOTER */
footer {
    visibility: hidden;
}

</style>
""", unsafe_allow_html=True)


# =====================================================
# SESSION STATE
# =====================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "active_chat" not in st.session_state:
    st.session_state.active_chat = "New Chat"

if "last_log_result" not in st.session_state:
    st.session_state.last_log_result = None


# =====================================================
# API FUNCTIONS
# =====================================================

def load_history():
    try:
        response = requests.get(
            HISTORY_URL,
            timeout=10
        )
        response.raise_for_status()

        return response.json().get("history", [])

    except requests.exceptions.RequestException:
        return []


def load_log_history():
    try:
        response = requests.get(
            LOG_HISTORY_URL,
            timeout=10
        )
        response.raise_for_status()

        return response.json().get("history", [])

    except requests.exceptions.RequestException:
        return []


# Load database history
history = load_history()
log_history = load_log_history()


# =====================================================
# HEADER
# =====================================================

header_left, header_right = st.columns([4, 1])

with header_left:
    st.markdown("""
    <div class="main-title">
        AI IT Support Agent
    </div>
    <div class="subtitle">
        Intelligent IT troubleshooting and monitoring platform
    </div>
    """, unsafe_allow_html=True)

with header_right:
    st.markdown(
        '<div class="status-pill">● AI PLATFORM</div>',
        unsafe_allow_html=True
    )

st.divider()


# =====================================================
# SIDEBAR
# =====================================================

with st.sidebar:

    st.markdown("## AI IT Support")
    st.caption("YOUR INTELLIGENT IT ASSISTANT")

    st.divider()

    st.markdown("### Platform")

    st.write("Python")
    st.write("FastAPI")
    st.write("RAG Architecture")
    st.write("Ollama LLM")
    st.write("SQLite Database")

    st.divider()

    st.markdown("### Quick Actions")

    if st.button("＋ New Conversation", use_container_width=True):

        st.session_state.messages = []
        st.session_state.active_chat = "New Chat"

        st.rerun()

    st.divider()

    st.caption("AI MODEL")
    st.write("Llama 3.2:3B")

    st.caption("EMBEDDING MODEL")
    st.write("all-MiniLM-L6-v2")

    st.divider()

    st.caption("AI IT SUPPORT AGENT")
    st.caption("Version 1.0")


# =====================================================
# MAIN TABS
# =====================================================

dashboard_tab, analyzer_tab, history_tab, chat_tab = st.tabs([
    "Dashboard",
    "Log Analyzer",
    "Analysis History",
    "AI Assistant"
])


# =====================================================
# 1. IT MONITORING DASHBOARD
# =====================================================

with dashboard_tab:

    st.markdown("## IT Monitoring Dashboard")

    st.caption(
        "Overview of log analysis activity and system monitoring."
    )

    # Calculate total statistics from database history

    total_errors = sum(
        int(item.get("error_count", 0) or 0)
        for item in log_history
    )

    total_warnings = sum(
        int(item.get("warning_count", 0) or 0)
        for item in log_history
    )

    total_info = sum(
        int(item.get("info_count", 0) or 0)
        for item in log_history
    )

    total_analyses = len(log_history)

    # Metrics

    metric1, metric2, metric3, metric4 = st.columns(4)

    metric1.metric(
        "Total Analyses",
        total_analyses
    )

    metric2.metric(
        "Total Errors",
        total_errors
    )

    metric3.metric(
        "Total Warnings",
        total_warnings
    )

    metric4.metric(
        "Information Logs",
        total_info
    )

    st.divider()

    # Severity chart

    st.markdown("### Log Severity Overview")

    severity_data = {
        "Severity": ["Errors", "Warnings", "Info"],
        "Count": [
            total_errors,
            total_warnings,
            total_info
        ]
    }

    st.bar_chart(
        severity_data,
        x="Severity",
        y="Count",
        color="#9174E8"
    )

    st.divider()

    # Recent activity

    st.markdown("### Recent Log Analysis")

    if log_history:

        for item in log_history[:5]:

            filename = item.get("filename", "Unknown file")

            created_at = item.get(
                "created_at",
                "Date unavailable"
            )

            with st.expander(f"Log File: {filename}"):

                st.write(f"**Date:** {created_at}")

                col1, col2, col3 = st.columns(3)

                col1.metric(
                    "Errors",
                    item.get("error_count", 0)
                )

                col2.metric(
                    "Warnings",
                    item.get("warning_count", 0)
                )

                col3.metric(
                    "Info",
                    item.get("info_count", 0)
                )

    else:

        st.info(
            "No log analysis available. Upload a log file to get started."
        )


# =====================================================
# 2. AI LOG FILE ANALYZER
# =====================================================

with analyzer_tab:

    st.markdown("## AI-Powered Log Analyzer")

    st.caption(
        "Upload your application log file. "
        "The AI will identify errors, warnings and possible root causes."
    )

    st.markdown("""
    <div class="assistant-card">
        <h3>Log File Intelligence</h3>
        <p>
        Upload your application logs and let the AI assistant
        investigate potential system issues.
        </p>
        <p>
        Supported formats: <b>.log</b> and <b>.txt</b>
        &nbsp; | &nbsp; Maximum file size: <b>2 MB</b>
        </p>
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Choose your log file",
        type=["log", "txt"],
        key="log_file_uploader"
    )

    if uploaded_file is not None:

        log_content = uploaded_file.getvalue()

        st.info(
            f"Selected file: {uploaded_file.name}"
        )

        if st.button(
            "Analyze Log File",
            key="analyze_log_button",
            use_container_width=True
        ):

            if not log_content:

                st.warning("The uploaded file is empty.")

            elif len(log_content) > 2 * 1024 * 1024:

                st.error(
                    "File size must be 2 MB or smaller."
                )

            else:

                try:

                    with st.spinner(
                        "Llama 3.2 is analyzing your log file..."
                    ):

                        response = requests.post(
                            LOG_ANALYZE_URL,
                            files={
                                "uploaded_file": (
                                    uploaded_file.name,
                                    log_content,
                                    uploaded_file.type or "text/plain"
                                )
                            },
                            timeout=260
                        )

                        response.raise_for_status()

                        result = response.json()

                    # Save result in session state
                    st.session_state.last_log_result = result

                    st.success(
                        result.get(
                            "message",
                            "Log analysis completed successfully."
                        )
                    )

                    # Refresh dashboard and history
                    log_history = load_log_history()

                except requests.exceptions.Timeout:

                    st.error(
                        "Analysis timed out. Please try again."
                    )

                except requests.exceptions.ConnectionError:

                    st.error(
                        "Cannot connect to FastAPI. "
                        "Make sure your backend is running."
                    )

                except requests.exceptions.HTTPError as error:

                    try:
                        detail = response.json().get(
                            "detail",
                            str(error)
                        )
                    except ValueError:
                        detail = str(error)

                    st.error(f"API Error: {detail}")

                except Exception as error:

                    st.error(
                        f"Unexpected error: {error}"
                    )

    # Display latest analysis outside the upload button block
    # so it remains visible during Streamlit reruns.

    if st.session_state.last_log_result:

        latest = st.session_state.last_log_result

        st.divider()

        st.markdown("### Latest Analysis")

        st.write(
            f"**File:** {latest.get('filename', 'Uploaded file')}"
        )

        statistics = latest.get("statistics", {})

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Errors",
            statistics.get("errors", 0)
        )

        col2.metric(
            "Warnings",
            statistics.get("warnings", 0)
        )

        col3.metric(
            "Info",
            statistics.get("info", 0)
        )

        st.markdown("### AI Diagnosis")

        st.markdown(
            latest.get(
                "analysis",
                "No analysis was returned."
            )
        )

        with st.expander("View Uploaded Log Content"):

            if uploaded_file is not None:

                text_content = uploaded_file.getvalue().decode(
                    "utf-8",
                    errors="replace"
                )

                st.code(
                    text_content,
                    language="text"
                )

            else:

                st.caption(
                    "Upload the file again to view its original content."
                )


# =====================================================
# 3. ANALYSIS HISTORY
# =====================================================

with history_tab:

    st.markdown("## Log Analysis History")

    st.caption(
        "Previously analyzed log files stored in your SQLite database."
    )

    if st.button(
        "Refresh Analysis History",
        key="refresh_log_history"
    ):

        log_history = load_log_history()

    if log_history:

        st.markdown(
            f"**Total saved analyses:** {len(log_history)}"
        )

        for item in log_history:

            filename = item.get(
                "filename",
                "Unknown file"
            )

            created_at = item.get(
                "created_at",
                "Date unavailable"
            )

            with st.expander(
                f"{filename} | {created_at}"
            ):

                col1, col2, col3 = st.columns(3)

                col1.metric(
                    "Errors",
                    item.get("error_count", 0)
                )

                col2.metric(
                    "Warnings",
                    item.get("warning_count", 0)
                )

                col3.metric(
                    "Info",
                    item.get("info_count", 0)
                )

                st.markdown("### Saved AI Analysis")

                st.markdown(
                    item.get(
                        "analysis",
                        "Analysis details unavailable."
                    )
                )

    else:

        st.info(
            "No analysis history found. "
            "Upload your first log file in the Log Analyzer tab."
        )


# =====================================================
# 4. AI SUPPORT CHAT
# =====================================================

with chat_tab:

    st.markdown("## AI IT Support Assistant")

    st.caption(
        "Ask technical questions and get AI-powered troubleshooting guidance."
    )

    # Load saved conversations

    st.markdown("### Conversation History")

    if history:

        history_options = {
            f"#{item['id']} - {item['question'][:45]}": item
            for item in history
        }

        selected_conversation = st.selectbox(
            "Select a previous conversation",
            options=["Current Conversation"] + list(history_options.keys()),
            key="conversation_selector"
        )

        if selected_conversation != "Current Conversation":

            selected = history_options[selected_conversation]

            if st.button(
                "Load Conversation",
                key="load_conversation"
            ):

                st.session_state.messages = [
                    {
                        "role": "user",
                        "content": selected["question"]
                    },
                    {
                        "role": "assistant",
                        "content": selected["answer"]
                    }
                ]

                st.session_state.active_chat = selected_conversation

                st.rerun()

    else:

        st.caption("No saved conversations yet.")

    st.divider()

    # Welcome screen

    if not st.session_state.messages:

        st.markdown("""
        <div class="assistant-card">
            <h3>Welcome to AI IT Support Agent</h3>
            <p>
            Your intelligent troubleshooting assistant is ready.
            Describe your IT problem and receive helpful guidance.
            </p>
            <p><b>Try asking:</b></p>
            <ul>
                <li>My application cannot connect to the database.</li>
                <li>My system is consuming too much memory.</li>
                <li>My application crashes during startup.</li>
                <li>How do I troubleshoot a server connection error?</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    # Display existing messages

    for message in st.session_state.messages:

        with st.chat_message(message["role"]):

            st.markdown(message["content"])

    # Chat input

    question = st.chat_input(
        "Describe your IT problem..."
    )

    if question:

        st.session_state.messages.append({
            "role": "user",
            "content": question
        })

        with st.spinner(
            "AI is analyzing your IT problem..."
        ):

            try:

                response = requests.post(
                    API_URL,
                    json={
                        "question": question
                    },
                    timeout=240
                )

                response.raise_for_status()

                result = response.json()

                answer = result.get(
                    "answer",
                    "The AI returned an empty response."
                )

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })

                st.rerun()

            except requests.exceptions.ConnectionError:

                st.error(
                    "Cannot connect to FastAPI. "
                    "Check whether the backend is running."
                )

            except requests.exceptions.Timeout:

                st.error(
                    "The AI response timed out. Please try again."
                )

            except requests.exceptions.RequestException as error:

                st.error(
                    f"API error: {error}"
                )

            except ValueError:

                st.error(
                    "Invalid response received from the API."
                )


# =====================================================
# FOOTER
# =====================================================

st.divider()

st.markdown("""
<div style="text-align:center; padding:15px; color:#929bbd;">
    <b>AI IT Support Agent</b><br>
    Python &nbsp;|&nbsp; FastAPI &nbsp;|&nbsp; RAG
    &nbsp;|&nbsp; Ollama &nbsp;|&nbsp; SQLite
    <br><br>
    Intelligent IT Troubleshooting Platform
</div>
""", unsafe_allow_html=True)




