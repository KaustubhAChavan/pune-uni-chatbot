from typing import Dict, Any, List, Optional
import os
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from .knowledge_base import KnowledgeBase

class ChatService:
    def __init__(self, knowledge_base: KnowledgeBase, openai_api_key: str):
        """Initialize chat service with knowledge base and OpenAI API key."""
        self.knowledge_base = knowledge_base
        self.llm = ChatOpenAI(
            openai_api_key=openai_api_key,
            model_name="gpt-4",
            temperature=0.7,
        )
        
        # Define system prompt
        self.system_prompt = """
        You are a helpful assistant for Savitribai Phule Pune University Support Hub. You provide accurate information about 
        the university's courses, admissions, facilities, faculty, research, exams, fees, scholarships and student life.
        
        When answering:
        - Be concise but thorough.
        - Provide factual information from the knowledge base.
        - If you don't know the answer, say so politely and suggest contacting the university directly.
        - Do not make up information.
        - Maintain a professional, friendly tone.
        - Address the user respectfully.
        - Format important information in a structured way with bullet points or numbered lists when appropriate.
        
        Here is relevant information from the university knowledge base to help answer the query:
        {context}
        """
        
        # Create chat prompt template
        self.chat_prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", "{question}")
        ])
    
    def get_response(self, user_query: str) -> Dict[str, Any]:
        """Get response for user query."""
        # Query knowledge base
        relevant_docs = self.knowledge_base.query_knowledge_base(user_query, k=3)
        
        # Prepare context from relevant documents
        context = "\n\n".join([f"Source: {doc['source']}\nContent: {doc['content']}" 
                              for doc in relevant_docs])
        
        # If no relevant documents found
        if not context:
            context = "No specific information found in the knowledge base."
        
        # Format prompt with context and question
        formatted_prompt = self.chat_prompt.format(
            context=context,
            question=user_query
        )
        
        # Get response from language model
        response = self.llm.invoke(formatted_prompt)
        
        # Extract sources for citation
        sources = list(set([doc['source'] for doc in relevant_docs]))
        
        return {
            "response": response.content,
            # "sources": sources
        }
    
    def get_response_for_sms(self, user_query: str) -> str:
        """Get response formatted for SMS - shorter and more concise."""
        response_data = self.get_response(user_query)
        response_text = response_data["response"]
        
        # Truncate if too long for SMS (keep under 1600 characters)
        if len(response_text) > 1500:
            response_text = response_text[:1450] + "... [Response truncated due to length]"
        
        # Add sources if available and if there's room
        sources = response_data.get("sources", [])
        if sources and len(response_text) < 1400:
            sources_text = "\n\nSources: " + ", ".join(sources[:2])
            if len(sources) > 2:
                sources_text += " and others"
            
            # Only add if it doesn't exceed SMS limit
            if len(response_text) + len(sources_text) <= 1500:
                response_text += sources_text
        
        return response_text
