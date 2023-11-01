import streamlit as st
import plotly.express as px
import pandas as pd
import os
import warnings
from src.models import engine
from sqlalchemy.orm import Session
from src.helpers.rag_monitor_helper import RagMonitorQuery

col1, col2 = st.columns(2)
st.sidebar.header("Choose your filter: ")
# Filter for sidebar on 1-hour, 24-hour, 7-days, 30-days
filter_option = st.sidebar.selectbox(
    "Select your filter", ("1-hour", "24-hour", "2-day", "7-day")
)
rag_monitor_query = RagMonitorQuery(session=Session(engine))
print("Filter Option Choosen", filter_option)
filtered_data = rag_monitor_query.get_rag_scores(filter_option)

with col1:
    st.subheader("Inference Latency (s)")
    fig = px.line(filtered_data, x="time_stamp", y="total_duration", markers=True)
    st.plotly_chart(fig, theme="streamlit", use_container_width=True)

with col2:
    st.subheader("Answer Relevancy")
    fig = px.line(filtered_data, x="time_stamp", y="answer_relevancy", markers=True)
    st.plotly_chart(fig, theme="streamlit", use_container_width=True)

cl1, cl2 = st.columns(2)
with cl1:
    st.subheader("Faithfulness")
    fig = px.line(filtered_data, x="time_stamp", y="faithfulness", markers=True)
    st.plotly_chart(fig, theme="streamlit", use_container_width=True)

with cl2:
    st.subheader("Harmfulness")
    fig = px.line(filtered_data, x="time_stamp", y="harmfulness", markers=True)
    st.plotly_chart(fig, theme="streamlit", use_container_width=True)

cl11, cl22 = st.columns(2)

with cl11:
    st.subheader("Context Precision")
    fig = px.line(filtered_data, x="time_stamp", y="context_precision", markers=True)
    st.plotly_chart(fig, theme="streamlit", use_container_width=True)

with cl22:
    st.subheader("Score Correlation")
    corr_df = filtered_data[["context_precision", "answer_relevancy"]]
    fig = px.imshow(corr_df.corr())
    st.plotly_chart(fig, theme="streamlit", use_container_width=True)
