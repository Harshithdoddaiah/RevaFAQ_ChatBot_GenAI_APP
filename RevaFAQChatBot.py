import streamlit as st
import os

st.set_page_config(page_title="RevaFAQ Chatbot", layout="centered")
st.title("🤖 RevaFAQ Chatbot")

# Set environment variables (You may move these to st.secrets or OS env vars)
os.environ["AZURE_AI_SEARCH_SERVICE_NAME"] = "revafaqaisearch"
os.environ["AZURE_AI_SEARCH_INDEX_NAME"] = "azuretable-index"
os.environ["AZURE_AI_SEARCH_API_KEY"] = st.secrets["AZURE_AI_SEARCH_API_KEY"]

# --- LangChain Imports ---
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import AzureChatOpenAI
from langchain_community.retrievers import AzureAISearchRetriever

# --- Step 1: Set up Retriever from Azure AI Search ---
retriever = AzureAISearchRetriever(
    content_key="Answer",  # Name of the column with answer text in Azure Table Storage
    top_k=3,
    index_name="azuretable-index"
)

# --- Step 2: Prompt Template for the LLM ---
prompt = ChatPromptTemplate.from_template(
    """You are a helpful assistant answering based only on the context below.

Context: {context}

Question: {question}"""
)

# --- Step 3: Azure OpenAI GPT LLM ---
llm = AzureChatOpenAI(
    api_version="2025-01-01-preview",
    azure_endpoint=st.secrets["AZURE_OPENAI_ENDPOINT"],
    api_key=st.secrets["AZURE_OPENAI_API_KEY"],
    deployment_name=st.secrets["AZURE_DEPLOYMENT_NAME"]  # ✅ Replace with your real deployment name
)

# --- Step 4: Langchain Chain (Retriever → Prompt → LLM) ---
chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# --- Step 5: Initialize Chat History ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Step 6: Show Chat History ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Step 7: Chat Input and Response ---
if user_question := st.chat_input("How can I help you?"):
    # Display user input
    st.session_state.messages.append({"role": "user", "content": user_question})
    with st.chat_message("user"):
        st.markdown(user_question)

    # Get response from LangChain chain
    with st.chat_message("assistant"):
        try:
            response = chain.invoke(user_question)
            st.markdown(response)
        except Exception as e:
            response = f"❌ Error: {str(e)}"
            st.error(response)

        # Add assistant reply to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})