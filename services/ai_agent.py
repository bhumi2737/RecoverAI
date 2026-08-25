import os
import json
from groq import Groq
from pydantic import BaseModel, Field
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv()

class AIActionRecommendation(BaseModel):
    action: str = Field(description="Must be one of: SEND_PAYMENT_LINK, WAIT, ESCALATE_TO_HUMAN, STOP")
    reason: str = Field(description="Clear explanation based on the provided evidence")
    confidence: float = Field(description="Confidence score between 0.0 and 1.0")
    evidence: List[str] = Field(description="List of facts used to make the decision")

class AIAgent:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            try:
                import streamlit as st
                self.api_key = st.secrets.get("GROQ_API_KEY")
            except Exception:
                pass
        self.client = None
        self.error_message = None
        if self.api_key and self.api_key != "your_groq_api_key_here":
            try:
                self.client = Groq(api_key=self.api_key)
            except Exception as e:
                self.error_message = f"Groq Init Error: {str(e)}"
                print(f"Failed to initialize Groq client: {e}")
                self.client = None
        else:
            self.error_message = "API key not found or is default placeholder."
        self.model = "llama-3.1-8b-instant" # A valid Groq model

    def recommend_action(self, case_info: dict) -> AIActionRecommendation:
        """
        Takes case information and asks the LLM for a recommended action.
        Uses a deterministic fallback if the API fails or is not configured.
        """
        if not self.client:
            return self._fallback_recommendation(case_info, "Groq API key not configured")

        system_prompt = """
        You are an AI Revenue Recovery Agent. Your job is to analyze failed payment cases and recommend the best next action.
        You MUST only output valid JSON matching this schema:
        {
            "action": "SEND_PAYMENT_LINK | WAIT | ESCALATE_TO_HUMAN | STOP",
            "reason": "String explaining why",
            "confidence": 0.0 to 1.0,
            "evidence": ["Fact 1", "Fact 2"]
        }
        
        Rules:
        - If recovery probability > 0.6 and no previous attempts, recommend SEND_PAYMENT_LINK.
        - If multiple previous attempts or very low probability, recommend STOP or ESCALATE_TO_HUMAN.
        - Network errors often just need a WAIT and retry or SEND_PAYMENT_LINK.
        """

        def json_serial(obj):
            from datetime import datetime, date
            if isinstance(obj, (datetime, date)):
                return obj.isoformat()
            return str(obj)

        user_prompt = f"Case Information:\n{json.dumps(case_info, indent=2, default=json_serial)}\n\nProvide your JSON recommendation:"

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model=self.model,
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            result_text = chat_completion.choices[0].message.content
            
            # Validate with Pydantic
            recommendation = AIActionRecommendation.model_validate_json(result_text)
            
            # Ensure action is valid
            valid_actions = ["SEND_PAYMENT_LINK", "WAIT", "ESCALATE_TO_HUMAN", "STOP"]
            if recommendation.action not in valid_actions:
                raise ValueError(f"Invalid action: {recommendation.action}")
                
            return recommendation
            
        except Exception as e:
            print(f"AI Agent error: {e}")
            return self._fallback_recommendation(case_info, f"API Error: {str(e)}")

    def _fallback_recommendation(self, case_info: dict, error_reason: str) -> AIActionRecommendation:
        """Deterministic fallback if AI fails"""
        prob = case_info.get("recovery_probability", 0.0)
        attempts = case_info.get("previous_recovery_attempts", 0)
        
        if attempts >= 2:
            action = "STOP"
            reason = "Maximum recovery attempts reached (Fallback rule)"
        elif prob > 0.6:
            action = "SEND_PAYMENT_LINK"
            reason = "High recovery probability (Fallback rule)"
        elif prob < 0.3:
            action = "STOP"
            reason = "Low recovery probability (Fallback rule)"
        else:
            action = "ESCALATE_TO_HUMAN"
            reason = "Borderline case requiring review (Fallback rule)"
            
        return AIActionRecommendation(
            action=action,
            reason=f"{reason}. Note: Using deterministic fallback because {error_reason}",
            confidence=0.5,
            evidence=["Fallback triggered due to AI unavailability"]
        )

    def chat_with_agent(self, case_info: dict, user_message: str, history: list) -> str:
        """Allows conversational interaction about a specific case."""
        if not self.client:
            err = self.error_message or "Unknown initialization error"
            return f"I'm sorry, I am currently operating in offline fallback mode because the Groq API key is missing. ({err}) I cannot chat right now."
            
        def json_serial(obj):
            from datetime import datetime, date
            if isinstance(obj, (datetime, date)):
                return obj.isoformat()
            return str(obj)
            
        system_prompt = f"""
        You are the RecoverAI Agent. The user is asking you questions about the following payment recovery case:
        {json.dumps(case_info, indent=2, default=json_serial)}
        
        Answer their questions helpfully and concisely. Explain your reasoning if asked.
        """
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add history
        for msg in history:
            messages.append({"role": msg["role"], "content": msg["content"]})
            
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        try:
            chat_completion = self.client.chat.completions.create(
                messages=messages,
                model=self.model,
                temperature=0.3,
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            print(f"AI Chat error: {e}")
            return f"Sorry, I encountered an error while trying to respond: {str(e)}"
            
    def generate_outreach_message(self, case_info: dict) -> str:
        """Generates a hyper-personalized outreach message using GenAI."""
        if not self.client:
            return "Hi there, we noticed your recent payment didn't go through. Please click here to update your payment method. [Fallback Mode]"
            
        system_prompt = """
        You are an expert customer success manager. Your goal is to draft a short, polite, and highly personalized email/SMS to recover a failed payment.
        
        Rules:
        - Keep it under 3 sentences.
        - Tone should be helpful and professional, not aggressive.
        - Reference the specific failure reason if appropriate (e.g. 'expired card').
        - If the user is high value, add a VIP touch.
        """
        
        user_prompt = f"Draft a recovery message for this case:\n{json.dumps(case_info, indent=2)}"
        
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model=self.model,
                temperature=0.7,
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            print(f"Outreach generation error: {e}")
            return "Hi there, we noticed your recent payment didn't go through. Please click here to update your payment method. [Fallback Mode]"
