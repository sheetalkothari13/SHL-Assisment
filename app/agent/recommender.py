import json
from google import genai
from google.genai import types
from typing import List, Dict, Tuple, Optional
from app.config import settings
from app.logging_config import logger
from app.exceptions import AgentException
from app.agent.prompts import build_system_prompt
from app.agent.parser import extract_recommendations_from_response

class AssessmentRecommenderAgent:
    def __init__(self):
        # Initialize Gemini client using the new google.genai SDK
        self.client = genai.Client(api_key=settings.gemini_api_key)
        self.model_name = settings.gemini_model
        self.system_prompt = build_system_prompt()
        logger.info("Conversational Agent engine successfully initialized.")

    def _should_end_conversation(self, messages: List[Dict], response: str) -> bool:
        """Determine if the conversation should end"""
        # End if we've provided recommendations and the user seems satisfied
        if "recommendations:" in response.lower() or "here are" in response.lower():
            # Check if this looks like a final recommendation set
            if any(keyword in response.lower() for keyword in ["shortlist", "final", "selection", "best fit"]):
                return True
        
        return False

    def check_out_of_scope(self, messages: List[Dict]) -> Optional[str]:
        """Check for out-of-scope requests before calling Claude"""
        if not messages:
            return None

        last_user_message = next(
            (msg["content"].lower() for msg in reversed(messages) if msg["role"] == "user"),
            ""
        )
        
        # Reject off-topic requests
        off_topic_keywords = [
            "legal", "lawsuit", "compliance", "hire me", "give me a job",
            "write my resume", "interview tips", "salary", "benefits"
        ]
        
        if any(keyword in last_user_message for keyword in off_topic_keywords):
            return (
                "I appreciate the question, but I can only help with SHL assessment selection. "
                "For legal, salary, or HR policy questions, please consult your HR department."
            )
        return None

    def chat(self, messages: List[Dict]) -> Tuple[str, List[Dict], bool]:
        """
        Process a conversation turn and return response, recommendations, and end status.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            
        Returns:
            Tuple of (reply_text, recommendations, end_of_conversation)
        """
        # 1. Check for out-of-scope queries
        refusal = self.check_out_of_scope(messages)
        if refusal:
            return refusal, [], False

        try:
            # 2. Call Gemini API
            logger.info("Calling Google Gemini API...")

            # Convert messages to Gemini contents format
            contents = []
            for msg in messages:
                role = "user" if msg["role"] == "user" else "model"
                contents.append(
                    types.Content(role=role, parts=[types.Part(text=msg["content"])])
                )

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=self.system_prompt,
                    max_output_tokens=1000,
                )
            )

            reply_text = response.text
            logger.info("Google Gemini API reply received successfully.")
            
            # 3. Extract recommendations from the response
            reply_text, recommendations = extract_recommendations_from_response(reply_text)
            
            # 4. Determine if conversation should end
            end_of_conversation = self._should_end_conversation(messages, reply_text)
            
            return reply_text, recommendations, end_of_conversation
            
        except Exception as e:
            logger.error(f"Error encountered during agent chat: {str(e)}")
            return (
                f"I encountered an error processing your request: {str(e)}. Please check your Gemini API key, model configuration, or try again.",
                [],
                False
            )

    def process_conversation(self, messages: List[Dict]) -> Dict:
        """
        Process full conversation history and return formatted response.
        
        Args:
            messages: Full conversation history
            
        Returns:
            Dict with reply, recommendations, and end_of_conversation flag
        """
        reply, recommendations, end_of_conv = self.chat(messages)
        
        return {
            "reply": reply,
            "recommendations": recommendations,
            "end_of_conversation": end_of_conv
        }
