import requests
import logging
from fastapi import HTTPException
from ..config.settings import settings

logger = logging.getLogger(__name__)


class AIService:
    """Service for AI model interactions"""
    
    def __init__(self):
        self.model_url = settings.sql_model_url
        self.model_name = settings.sql_model_name
    
    def generate_sql_query(self, question: str) -> str:
        """Generate SQL query using the AI model"""
        try:
            # Prepare the prompt for SQLCoder with actual database schema
            schema_context = """
            Database Schema:
            
            Table: duplicates
            Columns: i1 (BIGINT), i2 (BIGINT), provider_id_1 (TEXT), provider_id_2 (TEXT), 
                    name_1 (TEXT), name_2 (TEXT), score (DOUBLE), name_score (DOUBLE), 
                    npi_match (TINYINT(1)), addr_score (DOUBLE), phone_match (TINYINT(1)), 
                    license_score (DOUBLE)
            Description: Contains duplicate provider records with similarity scores
            
            Table: merged_roster
            Columns: provider_id (TEXT), npi (BIGINT), first_name (TEXT), last_name (TEXT), 
                    credential (TEXT), full_name (TEXT), primary_specialty (TEXT), 
                    practice_address_line1 (TEXT), practice_address_line2 (TEXT), 
                    practice_city (TEXT), practice_state (TEXT), practice_zip (TEXT), 
                    practice_phone (TEXT), mailing_address_line1 (TEXT), 
                    mailing_address_line2 (TEXT), mailing_city (TEXT), mailing_state (TEXT), 
                    mailing_zip (TEXT), license_number (TEXT), license_state (TEXT), 
                    license_expiration (TEXT), accepting_new_patients (TEXT), 
                    board_certified (TINYINT(1)), years_in_practice (BIGINT), 
                    medical_school (TEXT), residency_program (TEXT), last_updated (TEXT), 
                    taxonomy_code (TEXT), status (TEXT), npi_present (TINYINT(1))
            Description: Contains healthcare provider information and demographics
            """
            
            system_prompt = """You are a SQL assistant for a healthcare provider database. Generate only valid MySQL queries based on the schema provided. Focus on:
            - Provider data quality analysis
            - Duplicate detection and resolution
            - Compliance reporting (license expiration, missing data)
            - Provider demographics and distribution
            - Data validation and integrity checks
            
            Return only the SQL query without explanations, comments, or formatting."""
            
            prompt = f"""{schema_context}
            
            Question: {question}
            
            Generate a MySQL query to answer this question. Return only the SQL query.
            """
            
            # Call the AI model
            url = f"{self.model_url}/engines/llama.cpp/v1/chat/completions"
            response = requests.post(
                url,
                headers={"Content-Type": "application/json"},
                json={
                    "model": self.model_name,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 500,
                    "temperature": 0.1,
                    "stop": ["--", "/*", "Question:"]
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                sql_query = result.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
                
                # Clean up the SQL query
                sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
                
                # Remove any trailing semicolon for safety
                if sql_query.endswith(";"):
                    sql_query = sql_query[:-1]
                
                return sql_query
            else:
                logger.error(f"AI model error: {response.status_code} - {response.text}")
                raise HTTPException(status_code=500, detail="Failed to generate SQL query")
                
        except requests.exceptions.Timeout:
            logger.error("AI model timeout")
            raise HTTPException(status_code=500, detail="AI model request timeout")
        except Exception as e:
            logger.error(f"Error calling AI model: {str(e)}")
            raise HTTPException(status_code=500, detail=f"AI model error: {str(e)}")
    
    def check_health(self) -> str:
        """Check AI model health"""
        try:
            response = requests.get(f"{self.model_url}/health", timeout=5.0)
            return "connected" if response.status_code == 200 else "error"
        except Exception:
            return "unavailable"


# Global AI service instance
ai_service = AIService()
