from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough,RunnableLambda
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.output_parsers import StrOutputParser 

from config.config import Config


class RAGChainBuilder:
    def __init__(self, vector_store):
        self.vector_store = vector_store
        self.model = ChatGroq(
            model=Config.RAG_MODEL,
            temperature=0.5
        )
        self.history_store = {}

    def _get_history(self, session_id: str) -> BaseChatMessageHistory:
        if session_id not in self.history_store:
            self.history_store[session_id] = ChatMessageHistory()
        return self.history_store[session_id]

    def build_chain(self):
        retriever = self.vector_store.as_retriever(search_kwargs={"k": 3})

        rewrite_prompt = ChatPromptTemplate.from_messages([
            ("system", "Rewrite the user question as a standalone question."),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}")
        ])

        qa_prompt = ChatPromptTemplate.from_messages([
            ("system", 
             "You are an e-commerce assistant. "
             "Answer ONLY using the provided context.\n\n{context}"),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}")
        ])

        # Question rewriter
        rewrite_chain = rewrite_prompt | self.model | StrOutputParser()

        # Retriever pipeline
        retrieval_chain = (
            rewrite_chain
            | retriever
        )

        # Final RAG chain
        rag_chain = (
            {
                "context": retrieval_chain,
                "input": RunnablePassthrough(),
                "chat_history": RunnableLambda(lambda x: x["chat_history"]),
                
            }
            | qa_prompt
            | self.model
        )

        return RunnableWithMessageHistory(
            rag_chain,
            self._get_history, 
            input_messages_key="input",
            history_messages_key="chat_history"
        )
