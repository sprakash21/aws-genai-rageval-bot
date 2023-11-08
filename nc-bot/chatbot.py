import boto3
import streamlit as st
import src.models as db_models
from src.helpers.inference_helper import Llama2InferenceHelper

st.sidebar.markdown("# Chatbot 💬")
st.title("Chatbot 💬")
st.caption("🚀 RAGTrack - A chatbot which is works on answering on your pdf data")
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "How can I help you?"}
    ]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"], unsafe_allow_html=True)

if prompt := st.chat_input("Ask me some Question?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)


def prepare_source_docs(docs):
    mk_txt = "<details style='border:1px dotted'><summary><span style='color:DodgerBlue;'>I Referenced following documents for generation:</span>: </summary><br>"
    temp_list = list()
    for doc in docs:
        if hasattr(doc, "metadata"):
            source_s3_full_uri = doc.metadata["source"]
            if source_s3_full_uri not in temp_list:
                temp_list.append(source_s3_full_uri)
                bucket_name = source_s3_full_uri.split("/")[2]

                s3_client = boto3.client("s3")

                s3_file_key = "/".join(source_s3_full_uri.split("/")[3:])

                presigned_source_url = s3_client.generate_presigned_url(
                    "get_object",
                    Params={"Bucket": bucket_name, "Key": s3_file_key},
                    ExpiresIn=600,
                )

                mk_txt += f"<a href={presigned_source_url}>{s3_file_key}</a><br>"
    mk_txt += f"</details>"
    return mk_txt


# New response generation
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # A collection name is fixed for the application and can be extended
            inference_helper = Llama2InferenceHelper(collection_name="llm_collection")
            response = inference_helper.inference(prompt)
            st.write(response["result"], unsafe_allow_html=True)
            source_docs = prepare_source_docs(response["source_documents"])
            st.write(source_docs, unsafe_allow_html=True)
    message = {
        "role": "assistant",
        "content": response["result"] + "<br>" + source_docs,
    }
    st.session_state.messages.append(message)
