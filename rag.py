"""
RAG (Retrieval-Augmented Generation) module for the AI Booking Assistant.
Handles PDF upload, text extraction, chunking, embeddings, and retrieval.
"""

import os
import logging
from typing import List, Tuple
import numpy as np
from PyPDF2 import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
import streamlit as st

logger = logging.getLogger(__name__)

# Constants
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
VECTOR_STORE_PATH = "faiss_index"


def extract_text_from_pdf(pdf_file) -> str:
    """Extract text from uploaded PDF file."""
    try:
        pdf_reader = PdfReader(pdf_file)
        text = ""
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()
        logger.info(f"Extracted {len(text)} characters from PDF")
        return text
    except Exception as e:
        logger.error(f"Error extracting PDF text: {e}")
        raise


def chunk_text(text: str) -> List[str]:
    """Split text into chunks for embedding."""
    try:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP
        )
        chunks = splitter.split_text(text)
        logger.info(f"Text split into {len(chunks)} chunks")
        return chunks
    except Exception as e:
        logger.error(f"Error chunking text: {e}")
        raise


def create_or_load_vector_store(texts: List[str] = None) -> FAISS:
    """Create a new vector store from texts or load existing one."""
    try:
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

        # Load existing vector store if available
        if os.path.exists(VECTOR_STORE_PATH) and texts is None:
            logger.info("Loading existing FAISS index")
            vector_store = FAISS.load_local(
                VECTOR_STORE_PATH, embeddings, allow_dangerous_deserialization=True
            )
            return vector_store

        # Create new vector store from texts
        if texts:
            logger.info(f"Creating new FAISS index with {len(texts)} texts")
            vector_store = FAISS.from_texts(texts, embeddings)
            vector_store.save_local(VECTOR_STORE_PATH)
            return vector_store

        # If no existing store and no texts provided, create empty store
        logger.info("Creating empty FAISS index")
        vector_store = FAISS.from_texts([""], embeddings)
        vector_store.save_local(VECTOR_STORE_PATH)
        return vector_store

    except Exception as e:
        logger.error(f"Error creating/loading vector store: {e}")
        raise


def add_documents_to_store(texts: List[str]):
    """Add new documents to existing vector store."""
    try:
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

        if os.path.exists(VECTOR_STORE_PATH):
            vector_store = FAISS.load_local(
                VECTOR_STORE_PATH, embeddings, allow_dangerous_deserialization=True
            )
            logger.info(f"Adding {len(texts)} new texts to existing store")
            vector_store.add_texts(texts)
        else:
            logger.info(f"Creating new store with {len(texts)} texts")
            vector_store = FAISS.from_texts(texts, embeddings)

        vector_store.save_local(VECTOR_STORE_PATH)
        logger.info("Vector store updated")
        return vector_store

    except Exception as e:
        logger.error(f"Error adding documents to store: {e}")
        raise


def retrieve_relevant_chunks(query: str, k: int = 3) -> List[str]:
    """Retrieve relevant chunks from vector store based on query."""
    try:
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

        if not os.path.exists(VECTOR_STORE_PATH):
            logger.warning("Vector store not found")
            return []

        vector_store = FAISS.load_local(
            VECTOR_STORE_PATH, embeddings, allow_dangerous_deserialization=True
        )
        docs = vector_store.similarity_search(query, k=k)

        chunks = [doc.page_content for doc in docs]
        logger.info(f"Retrieved {len(chunks)} relevant chunks for query")
        return chunks

    except Exception as e:
        logger.error(f"Error retrieving chunks: {e}")
        return []


def answer_with_rag(
    query: str, conversation_history: List[Tuple[str, str]]
) -> str:
    """
    Answer user query using RAG with retrieved documents.
    Falls back to regular LLM response if no documents are retrieved.
    """
    try:
        # Retrieve relevant chunks
        relevant_chunks = retrieve_relevant_chunks(query, k=3)

        # Create prompt
        if relevant_chunks:
            context = "\n\n".join(relevant_chunks)
            system_prompt = f"""You are a helpful booking assistant. 
Use the provided context to answer questions accurately. 
If the context doesn't contain relevant information, say so and provide general help.

Context from documents:
{context}

Answer the user's question based on the context above."""
        else:
            system_prompt = """You are a helpful booking assistant. 
Help users with their booking inquiries and questions."""

        # Format conversation history for context
        messages = []
        for user_msg, assistant_msg in conversation_history[-5:]:  # Last 5 exchanges
            messages.append({"role": "user", "content": user_msg})
            messages.append({"role": "assistant", "content": assistant_msg})

        messages.append({"role": "user", "content": query})

        # Get response from LLM
        llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)
        prompt = ChatPromptTemplate.from_messages(
            [("system", system_prompt)] + [(msg["role"], msg["content"]) for msg in messages]
        )

        response = llm.invoke(prompt.format_messages())
        return response.content

    except Exception as e:
        logger.error(f"Error in RAG answering: {e}")
        return "I apologize, but I encountered an error processing your request. Please try again."


def detect_booking_intent(query: str) -> bool:
    """
    Detect if user query contains booking intent.
    Returns True if booking-related intent is detected.
    """
    booking_keywords = [
        "book",
        "booking",
        "appointment",
        "schedule",
        "reserve",
        "reservation",
        "service",
        "date",
        "time",
        "contact",
        "information",
    ]

    query_lower = query.lower()
    return any(keyword in query_lower for keyword in booking_keywords)
