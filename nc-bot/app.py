from datetime import datetime
from botocore.exceptions import ClientError
import streamlit as st
from rag_application_framework.aws.aws_client_factory import AwsClientFactory
from rag_application_framework.aws.aws_session_factory import AwsSessionFactory
from rag_application_framework.config.app_config_factory import AuthConfig
from rag_application_framework.config.app_config import  SessionToken
from rag_application_framework.aws.cognito_pool import CognitoIdpApi

st.set_page_config(
    page_title="Home",
    page_icon="👋",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "auth_session" not in st.session_state:
    st.session_state.auth_session = None


def get_cognito_api():
    boto3_session = AwsSessionFactory.create_session_from_config(
        AuthConfig.aws_config
    )
    cognito_api = AwsClientFactory.build_from_boto_session(
        boto3_session,
        CognitoIdpApi,
    )
    return cognito_api


def login():
    """Login template"""
    st.header("Log in")
    # Insert a form in the container
    with st.form("login"):
        st.markdown("#### Enter your credentials")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
    if submit:
        auth_config = AuthConfig.get_cognito_pool_config()
        auth_config.username = username
        auth_config.password = password
        cognito_api = get_cognito_api()
        try:
            response = cognito_api.initiate_authentication(username=auth_config.username,
                                                           password=auth_config.password,
                                                           client_id=auth_config.client_id,
                                                           client_secret=auth_config.client_secret)

            st.session_state.auth_session = SessionToken(access_token=response["AuthenticationResult"]["AccessToken"],
                                                         refresh_token=response["AuthenticationResult"]["RefreshToken"],
                                                         expiry_time=response["AuthenticationResult"]["ExpiresIn"]
                                                        )
            st.rerun()
        except ClientError as e:
            st.error(f'Error during login {e.response["Error"]["Message"]}', icon="🚨")


def logout():
    access_token = st.session_state.auth_session.access_token
    cognito_api = get_cognito_api()
    response = cognito_api.global_logout(access_token=access_token)
    st.session_state.auth_session = None
    st.rerun()

# Set the pages


auth_session = st.session_state.auth_session
logout_page = st.Page(logout, title="Log out", icon=":material/logout:")
chatbot = st.Page(
    "requests/02_chatbot.py",
    title="Chatbot",
    icon=":material/support_agent:",
    default=(auth_session is not None),
)

data_uploader = st.Page(
    "requests/03_data_uploader.py",
    title="Data Uploader",
    icon=":material/upload_file:"

)

rag_monitor = st.Page(
    "requests/04_rag_monitor.py",
    title="Tracking RAG",
    icon=":material/monitor_heart:"
)

app_pages = [chatbot, data_uploader, rag_monitor]
account_pages = [logout_page]

page_dict = {}
if auth_session:
    page_dict["Application"] = app_pages


if len(page_dict) > 0:
    pg = st.navigation({"Account": account_pages} | page_dict)
else:
    pg = st.navigation([st.Page(login)])

pg.run()
