import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="BNPL AI Support — Observability Dashboard", page_icon="📊", layout="wide")
st.title("📊 BNPL AI Support — Agent Health Dashboard")
st.caption("Live metrics from the Tabby Support AI Agent's conversation logs")

uploaded_file = st.file_uploader("Upload conversation_log.csv", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["date"] = df["timestamp"].dt.date

    # ---- Topic categorization ----
    def categorize_topic(question):
        q = question.lower()
        if "refund" in q:
            return "Refunds"
        elif "fee" in q or "late payment" in q or "miss" in q:
            return "Fees & Late Payments"
        elif "payment method" in q or "card" in q or "bank transfer" in q:
            return "Payment Methods"
        elif "declined" in q or "decline" in q:
            return "Account Issues"
        elif "18" in q or "eligib" in q or "age" in q:
            return "Eligibility"
        else:
            return "General"

    df["topic"] = df["question"].apply(categorize_topic)

    # ---- Cost estimation ----
    BLENDED_RATE_PER_1M = 0.35
    df["estimated_cost"] = (df["tokens_used"] / 1_000_000) * BLENDED_RATE_PER_1M

    # ---- Top metric cards ----
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Questions", len(df))
    escalation_rate = (df["response_type"] == "escalate").sum() / len(df) * 100
    col2.metric("Escalation Rate", f"{escalation_rate:.1f}%")
    col3.metric("Avg Response Time", f"{df['response_time_sec'].mean():.2f}s")
    col4.metric("Est. Total Cost", f"${df['estimated_cost'].sum():.4f}")

    st.divider()

    # ---- Charts ----
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.subheader("Daily Question Volume")
        daily_counts = df.groupby("date").size()
        fig1, ax1 = plt.subplots(figsize=(5, 3))
        daily_counts.plot(kind="bar", color="#4A90D9", ax=ax1)
        ax1.set_xlabel("Date")
        ax1.set_ylabel("Questions")
        st.pyplot(fig1)

    with chart_col2:
        st.subheader("Response Types")
        fig2, ax2 = plt.subplots(figsize=(4, 4))
        df["response_type"].value_counts().plot(kind="pie", autopct='%1.1f%%', ax=ax2,
                                                    colors=["#4A90D9", "#E74C3C", "#F39C12"])
        ax2.set_ylabel("")
        st.pyplot(fig2)

    st.subheader("Common Topics")
    fig3, ax3 = plt.subplots(figsize=(8, 3))
    df["topic"].value_counts().plot(kind="barh", color="#8E44AD", ax=ax3)
    ax3.set_xlabel("Count")
    st.pyplot(fig3)

    st.divider()

    # ---- Recent conversations table ----
    st.subheader("Recent Conversations")
    st.dataframe(
        df[["timestamp", "question", "response_type", "response_time_sec", "tokens_used"]].sort_values("timestamp", ascending=False),
        use_container_width=True
    )
else:
    st.info("👆 Upload your conversation_log.csv to see the dashboard.")
