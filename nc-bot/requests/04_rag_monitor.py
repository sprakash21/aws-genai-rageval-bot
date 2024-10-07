import plotly.express as px
import streamlit as st
from rag_application_framework.config.app_config_factory import AppConfigFactory
from rag_application_framework.db.models import inititalize
from rag_application_framework.db.psycopg_connection_factory import (
    PsycopgConnectionFactory,
)
from rag_application_framework.modules.rag_monitor_query.rag_monitor_query import (
    RagMonitorQuery,
)
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
import os


def page():
    app_config = AppConfigFactory.build_from_env()
    db_config = app_config.db_config

    factory = PsycopgConnectionFactory(
        host=db_config.host,
        port=db_config.port,
        username=db_config.user,
        password=db_config.password,
        database_name=db_config.database,
    )

    engine = create_engine(factory.get_connection_str())
    inititalize(engine)

    col1, col2 = st.columns(2)
    st.sidebar.header("Choose your filter: ")
    # Filter for sidebar on 1-hour, 24-hour, 7-days, 30-days
    filter_option = st.sidebar.selectbox(
        "Select your filter", ("1-hour", "24-hour", "2-day", "7-day")
    )
    rag_monitor_query = RagMonitorQuery(session=Session(engine), engine=engine)
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
        st.subheader("Correctness")
        fig = px.line(filtered_data, x="time_stamp", y="correctness", markers=True)
        st.plotly_chart(fig, theme="streamlit", use_container_width=True)

    cl11, cl22 = st.columns(2)

    with cl11:
        st.subheader("Context Precision")
        fig = px.line(
            filtered_data, x="time_stamp", y="context_precision", markers=True
        )
        st.plotly_chart(fig, theme="streamlit", use_container_width=True)


page()
