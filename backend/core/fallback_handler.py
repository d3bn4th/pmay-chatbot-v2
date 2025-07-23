"""
Robust fallback mechanism for the PMAY chatbot.
Handles cases when the RAG system cannot find relevant information or encounters errors.
"""

import re
import random
from typing import Dict, List, Optional, Tuple
from enum import Enum

class FallbackType(Enum):
    """Types of fallback responses."""
    NO_DOCUMENTS = "no_documents"
    NO_RELEVANT_TEXT = "no_relevant_text"
    RERANKING_FAILED = "reranking_failed"
    LLM_ERROR = "llm_error"
    GENERAL_ERROR = "general_error"
    AMBIGUOUS_QUESTION = "ambiguous_question"

class FallbackHandler:
    """Handles fallback responses for various error scenarios."""
    
    def __init__(self):
        self.fallback_responses = {
            FallbackType.NO_DOCUMENTS: [
                "I apologize, but I couldn't find specific information about that in my knowledge base. Could you please rephrase your question or ask about a different aspect of PMAY?",
                "I don't have specific information about that in my current knowledge base. Please try asking about PMAY eligibility, application process, or required documents.",
                "I'm unable to find relevant information for your question. Could you please ask about PMAY-U scheme details, eligibility criteria, or the application process?",
                "I don't have enough information to answer that specific question. Please ask me about PMAY-U scheme information, eligibility, or how to apply.",
                "I couldn't locate the specific information you're looking for. Please try asking about PMAY-U benefits, eligibility requirements, or application procedures."
            ],
            
            FallbackType.NO_RELEVANT_TEXT: [
                "I found some information but it doesn't seem directly relevant to your question. Could you please rephrase your question or ask about PMAY eligibility, application process, or required documents?",
                "The information I have doesn't quite match your question. Please try asking about PMAY-U scheme details, eligibility criteria, or the application process.",
                "I couldn't find information that directly answers your question. Please ask me about PMAY-U benefits, eligibility requirements, or application procedures."
            ],
            
            FallbackType.RERANKING_FAILED: [
                "I'm having trouble processing your question right now. Please try asking about PMAY eligibility, application process, or required documents.",
                "I encountered an issue while processing your request. Please try rephrasing your question about PMAY-U scheme information.",
                "I'm experiencing some technical difficulties. Please ask me about PMAY-U benefits, eligibility, or how to apply."
            ],
            
            FallbackType.LLM_ERROR: [
                "I'm having trouble generating a response right now. Please try asking about PMAY eligibility, application process, or required documents.",
                "I encountered an error while processing your request. Please try asking about PMAY-U scheme information or eligibility criteria.",
                "I'm experiencing some technical difficulties. Please ask me about PMAY-U benefits or application procedures."
            ],
            
            FallbackType.GENERAL_ERROR: [
                "I apologize for the inconvenience. Please try asking about PMAY eligibility, application process, or required documents.",
                "I'm having some technical difficulties. Please try asking about PMAY-U scheme information or eligibility criteria.",
                "I encountered an unexpected error. Please ask me about PMAY-U benefits or application procedures."
            ],
            
            FallbackType.AMBIGUOUS_QUESTION: [
                "Your question is a bit unclear. Could you please provide more specific details about what you'd like to know about PMAY?",
                "I need more information to help you properly. Please ask about specific aspects like PMAY eligibility, application process, or required documents.",
                "Could you please clarify your question? I can help you with PMAY-U scheme information, eligibility criteria, or application procedures."
            ]
        }
        
        # Common PMAY-related topics for suggestions
        self.pmay_topics = [
            "PMAY eligibility criteria",
            "How to apply for PMAY",
            "Required documents for PMAY application",
            "PMAY benefits and subsidies",
            "PMAY application status check",
            "PMAY scheme details",
            "PMAY urban vs rural",
            "PMAY income limits",
            "PMAY loan process",
            "PMAY official website"
        ]
    
    def get_fallback_response(self, fallback_type: FallbackType, user_question: str = "") -> str:
        """
        Get an appropriate fallback response based on the error type.
        
        Args:
            fallback_type: Type of fallback needed
            user_question: Original user question for context
            
        Returns:
            Fallback response string
        """
        responses = self.fallback_responses.get(fallback_type, self.fallback_responses[FallbackType.GENERAL_ERROR])
        base_response = random.choice(responses)
        
        # Add helpful suggestions for certain fallback types
        if fallback_type in [FallbackType.NO_DOCUMENTS, FallbackType.NO_RELEVANT_TEXT]:
            suggestions = self._get_relevant_suggestions(user_question)
            if suggestions:
                base_response += f"\n\n**You might want to ask about:**\n- {suggestions[0]}\n- {suggestions[1]}\n- {suggestions[2]}"
        
        return base_response
    
    def _get_relevant_suggestions(self, user_question: str) -> List[str]:
        """
        Get relevant topic suggestions based on the user's question.
        
        Args:
            user_question: Original user question
            
        Returns:
            List of relevant topic suggestions
        """
        normalized_question = user_question.lower()
        
        # Map keywords to relevant topics
        keyword_mapping = {
            'eligibility': ['PMAY eligibility criteria', 'Income limits for PMAY', 'Who can apply for PMAY'],
            'apply': ['How to apply for PMAY', 'PMAY application process', 'Required documents for PMAY'],
            'documents': ['Required documents for PMAY', 'PMAY application documents', 'Document checklist for PMAY'],
            'loan': ['PMAY loan process', 'Home loan under PMAY', 'PMAY credit linked subsidy'],
            'benefits': ['PMAY benefits and subsidies', 'PMAY scheme benefits', 'What you get under PMAY'],
            'status': ['PMAY application status check', 'How to track PMAY application', 'PMAY application tracking'],
            'website': ['PMAY official website', 'Where to apply for PMAY', 'PMAY online application'],
            'income': ['PMAY income limits', 'Income criteria for PMAY', 'PMAY eligibility based on income'],
            'urban': ['PMAY urban scheme', 'PMAY-U benefits', 'Urban housing under PMAY'],
            'rural': ['PMAY rural scheme', 'PMAY-G benefits', 'Rural housing under PMAY']
        }
        
        # Find matching keywords
        matching_topics = []
        for keyword, topics in keyword_mapping.items():
            if keyword in normalized_question:
                matching_topics.extend(topics)
        
        # If no specific matches, return general topics
        if not matching_topics:
            return random.sample(self.pmay_topics, 3)
        
        # Return up to 3 relevant topics
        return random.sample(matching_topics, min(3, len(matching_topics)))
    
    def get_enhanced_fallback_response(self, fallback_type: FallbackType, user_question: str = "", 
                                     documents_found: int = 0, error_details: str = "") -> str:
        """
        Get an enhanced fallback response with additional context and suggestions.
        
        Args:
            fallback_type: Type of fallback needed
            user_question: Original user question
            documents_found: Number of documents found (if applicable)
            error_details: Additional error details (if applicable)
            
        Returns:
            Enhanced fallback response string
        """
        base_response = self.get_fallback_response(fallback_type, user_question)
        
        # Add context-specific information
        if documents_found == 0 and fallback_type == FallbackType.NO_DOCUMENTS:
            base_response += "\n\n**Note:** I couldn't find any relevant documents in my knowledge base for your question."
        elif documents_found > 0 and fallback_type == FallbackType.NO_RELEVANT_TEXT:
            base_response += f"\n\n**Note:** I found {documents_found} documents but none seemed directly relevant to your question."
        
        # Add helpful next steps
        base_response += "\n\n**What you can do:**\n- Try rephrasing your question with more specific PMAY-related terms\n- Ask about eligibility, application process, or required documents\n- Check the official PMAY website for the most up-to-date information"
        
        return base_response
    
    def should_use_fallback(self, documents: List, relevant_text: str, 
                          reranking_success: bool = True, llm_success: bool = True) -> Tuple[bool, FallbackType]:
        """
        Determine if a fallback response should be used and what type.
        
        Args:
            documents: List of documents from vector store
            relevant_text: Relevant text after reranking
            reranking_success: Whether reranking was successful
            llm_success: Whether LLM call was successful
            
        Returns:
            Tuple of (should_use_fallback, fallback_type)
        """
        if not llm_success:
            return True, FallbackType.LLM_ERROR
        
        if not reranking_success:
            return True, FallbackType.RERANKING_FAILED
        
        if not documents:
            return True, FallbackType.NO_DOCUMENTS
        
        if not relevant_text:
            return True, FallbackType.NO_RELEVANT_TEXT
        
        return False, FallbackType.GENERAL_ERROR

# Global instance
fallback_handler = FallbackHandler() 