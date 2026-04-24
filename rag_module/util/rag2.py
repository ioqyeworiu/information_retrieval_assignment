import os
from uuid import uuid4
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnableLambda
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_postgres import PGVector, PostgresChatMessageHistory
from langchain_huggingface import HuggingFaceEmbeddings
import psycopg
from fastapi import Request
from dotenv import load_dotenv

load_dotenv(override=True)

class RAGModel2:
    def __init__(self, session_id, request: Request):
        self.session_id = session_id
        self.llm = ChatOpenAI(
            model=os.getenv("GEMINI_MODEL_NAME"),
            base_url=os.getenv("GEMINI_URL_BASE"),
            api_key=os.getenv("GEMINI_API_KEY"),
            temperature=0.1
        )
        # self.llm = ChatOpenAI(
        #     model=os.getenv("CHAT_MODEL_NAME"),
        #     base_url="https://pmquan30102004--llm-service-serve.modal.run/v1",
        #     api_key="abc",
        #     max_tokens=32768,
        #     temperature=0.1
        # )
        self.embeddings = request.app.state.embeddings
        self.vector_store_1 = request.app.state.vector_store_1
        self.vector_store_2 = request.app.state.vector_store_2

    def get_retriever1(self):
        return self.vector_store_1.as_retriever(search_type="similarity", k=20)
    
    def get_retriever2(self):
        return self.vector_store_2.as_retriever(search_type="similarity", k=20)
    
    def get_query_generator_and_retrievers(self):
        prompt_1 = ChatPromptTemplate.from_template(
            "Rewrite the question for knowledge base search: {question}"
        )
        prompt_2 = ChatPromptTemplate.from_template(
            "Rewrite the question for user's goal, favourite, age, gender, practice plan search: {question}"
        )
        query_generator = RunnableParallel(
            query_1=prompt_1 | self.llm,
            query_2=prompt_2 | self.llm,
        )
        retriever_1 = self.get_retriever1()
        retriever_2 = self.get_retriever2()
        retrievers = RunnableParallel(
            docs_1=lambda q:
                retriever_1.invoke(q["query_1"].content),

            docs_2=lambda q:
                retriever_2.invoke(q["query_2"].content),
        )
        return query_generator, retrievers
    
    def merge_docs(self, results):
        docs = []
        docs.extend(results["docs_1"])
        docs.extend(results["docs_2"])
        return docs
    
    def build_context(self, docs):
        return "\n\n".join(d.page_content for d in docs)

    def generate_answer(self, input_dict):
        answer_prompt = ChatPromptTemplate.from_template(
            """
        Answer the question relevant to gym and fitness using the context. 
        just answer the question based on the context, do not use any other knowledge.
        If the question is not relevant to the gym and fitness domain, just say you are fitness expert so require user ask some thing relevant to gym and fitness then suggest some questions relevant to user's profile.

        Context:
        {context}

        Question:
        {question}
        """
        )

        query_generator, retrievers = self.get_query_generator_and_retrievers()

        question = input_dict["input"]
        queries = query_generator.invoke(
            {
                "question": question
            }
        )
        results = retrievers.invoke(
            queries
        )
        docs = self.merge_docs(results)
        context = self.build_context(docs)
        response = (answer_prompt | self.llm).invoke(
            {
                "context": context,
                "question": question
            }
        )
        return response
    
    def get_rag_chain(self):
        return RunnableLambda(self.generate_answer)

    def get_history(self):
        return PostgresChatMessageHistory(
            os.getenv("historical_conversation_collection_name"),
            self.session_id,
            sync_connection = psycopg.connect(os.getenv("db_connection_string"))
        )
    
    def get_chat_chain(self):
        return RunnableWithMessageHistory(
            self.get_rag_chain(),
            self.get_history,
            input_messages_key="input",
            history_messages_key="chat_history"
        )