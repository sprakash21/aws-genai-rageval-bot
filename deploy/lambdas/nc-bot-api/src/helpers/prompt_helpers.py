from langchain.prompts import PromptTemplate

def build_llama2_prompt(messages):
    start_prompt = "<s>[INST] "
    end_prompt = " [/INST]"
    conversation = []
    for index, message in enumerate(messages):
        if message["role"] == "system" and index == 0:
            conversation.append(f"<<SYS>>\n{message['content']}\n<</SYS>>\n\n")
        elif message["role"] == "user":
            conversation.append(message["content"].strip())
        else:
            conversation.append(f" [/INST] {message['content'].strip()}</s><s>[INST] ")

    return start_prompt + "".join(conversation) + end_prompt

def create_prompt_template():
    template = """
    <s> [INST] 
    <<SYS>>
    You are an assistant for question-answering tasks. 
    Use the following pieces of retrieved context to answer the question. 
    If you don't know the answer, just say that you don't know. 
    Use three sentences maximum and keep the answer concise. 
    If the question seems like not a question, just say you don't know the answer for the question asked. 
    <</SYS>> 
    Question: {question} 
    Context: {context} 
    Answer: [/INST]<s>
    """
    rag_prompt_custom = PromptTemplate(input_variables=['question', 'context'], template=template)
    return rag_prompt_custom
