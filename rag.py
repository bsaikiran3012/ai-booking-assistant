"""
RAG (Retrieval-Augmented Generation) module for the AI Booking Assistant.
Handles PDF upload, text extraction, chunking, embeddings, and retrieval.
Uses in-memory vector store instead of FAISS for Streamlit Cloud compatibility.
"""

import os
import logging
from typing import List, Tuple
import pickle
from PyPDF2 import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
import streamlit as st

logger = logging.getLogger(__name__)

# Constants
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
VECTOR_STORE_PATH = "vector_store.pkl"


class SimpleVectorStore:
    """Simple in-memory vector store for Streamlit Cloud compatibility."""
    
    def __init__(self, embeddings):
        self.embeddings = embeddings
        self.texts = []
        self.embeddings_cache = []
    
    def add_texts(self, texts: List[str]):
        """Add texts to the store."""
        for text in texts:
            if text.strip():
                self.texts.append(text)
                embedding = self.embeddings.embed_query(text)
                self.embeddings_cache.append(embedding)
    
    def similarity_search(self, query: str, k: int = 3) -> List[str]:
        """Find k most similar texts to the query."""
        if not self.texts:
            return []
        
        try:
            import numpy as np
            query_embedding = np.array(self.embeddings.embed_query(query))
            
            # Calculate similarity scores (cosine similarity)
            scores = []
            for emb in self.embeddings_cache:
                emb_array = np.array(emb)
                # Normalize vectors for cosine similarity
                if np.linalg.norm(query_embedding) > 0 and np.linalg.norm(emb_array) > 0:
                    similarity = np.dot(query_embedding, emb_array) / (
                        np.linalg.norm(query_embedding) * np.linalg.norm(emb_array)
                    )
                else:
                    similarity = 0
                scores.append(similarity)
            
            # Get top k indices
            top_k_indices = np.argsort(scores)[-k:][::-1]
            return [self.texts[i] for i in top_k_indices if scores[i] > 0]
        except Exception as e:
            logger.error(f"Error in similarity search: {e}")
            return self.texts[:k]  # Fallback: return first k texts
    
    def save(self, path: str):
        """Save store to disk."""
        try:
            with open(path, 'wb') as f:
                pickle.dump({'texts': self.texts, 'embeddings': self.embeddings_cache}, f)
        except Exception as e:
            logger.error(f"Error saving vector store: {e}")
    
    @staticmethod
    def load(path: str, embeddings):
        """Load store from disk."""
        try:
            with open(path, 'rb') as f:
                data = pickle.load(f)
            store = SimpleVectorStore(embeddings)
            store.texts = data['texts']
            store.embeddings_cache = data['embeddings']
            return store
        except Exception as e:
            logger.error(f"Error loading vector store: {e}")
            return SimpleVectorStore(embeddings)


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


def create_or_load_vector_store(texts: List[str] = None):
    """Create a new vector store from texts or load existing one."""
    try:
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

        # Load existing vector store if available
        if os.path.exists(VECTOR_STORE_PATH) and texts is None:
            logger.info("Loading existing vector store")
            vector_store = SimpleVectorStore.load(VECTOR_STORE_PATH, embeddings)
            return vector_store

        # Create new vector store from texts
        if texts:
            logger.info(f"Creating new vector store with {len(texts)} texts")
            vector_store = SimpleVectorStore(embeddings)
            vector_store.add_texts(texts)
            vector_store.save(VECTOR_STORE_PATH)
            return vector_store

        # If no existing store and no texts provided, create empty store
        logger.info("Creating empty vector store")
        vector_store = SimpleVectorStore(embeddings)
        vector_store.save(VECTOR_STORE_PATH)
        return vector_store

    except Exception as e:
        logger.error(f"Error creating/loading vector store: {e}")
        raise


def add_documents_to_store(texts: List[str]):
    """Add new documents to existing vector store."""
    try:
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

        if os.path.exists(VECTOR_STORE_PATH):
            vector_store = SimpleVectorStore.load(VECTOR_STORE_PATH, embeddings)
            logger.info(f"Adding {len(texts)} new texts to existing store")
            vector_store.add_texts(texts)
        else:
            logger.info(f"Creating new store with {len(texts)} texts")
            vector_store = SimpleVectorStore(embeddings)
            vector_store.add_texts(texts)

        vector_store.save(VECTOR_STORE_PATH)
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

        vector_store = SimpleVectorStore.load(VECTOR_STORE_PATH, embeddings)
        chunks = vector_store.similarity_search(query, k=k)
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
