"""
hsn_agent package
=================

This package exposes a single ADK-compatible agent whose job is to validate one
or more HSN codes and suggest HSN codes based on product descriptions.  
The heavy lifting lives in `hsn_agent.validate` (function `validate_hsn_code` and `suggest_hsn_codes`).  
All we do here is wrap that function in a thin BaseAgent-derived class and export an 
*instance* named `root_agent`, which ADK 1.1.1 searches for automatically.

Directory layout expected by this file
--------------------------------------

hsn_agent/
│
├── __init__.py      ← *you are here*
├── validate.py      ← contains validate_hsn_code(...) and suggest_hsn_codes(...)
└── data/
    └── hsn_codes.csv
"""

from typing import Dict, Union, AsyncGenerator
import asyncio
import re
import json

# ADK 1.1.1 ships BaseAgent in google.adk.agents
from google.adk.agents import BaseAgent
from google.adk.events import Event
from google.adk.runners import InvocationContext
import google.genai.types as genai_types

# Your standalone validator and suggestion functions
from .validate import validate_hsn_code, suggest_hsn_codes


class ValidateHSNAgent(BaseAgent):
    """
    HSN Code Validation and Suggestion Agent that can:
    1. Validate single or multiple HSN codes
    2. Suggest HSN codes based on product descriptions
    
    This agent forwards requests to helper functions and returns structured results.

    NOTE:
    -----
    • ADK instantiates this class **without arguments**.
    • Parameters coming from the user arrive as keyword args to `run()`.
    """
    
    def __init__(self):
        super().__init__(
            name="HSN_Code_Validation_Agent",
            description="An intelligent agent for validating HSN codes and suggesting codes based on product descriptions. Supports batch processing and hierarchical validation."
        )

    # The signature **must** match the parameter schema in agent.yaml
    def run(self, *, query: str, action: str = "validate") -> Dict:
        """
        Parameters
        ----------
        query : str
            For validation: Comma-separated HSN codes, e.g. "17019930, 01"
            For suggestion: Product description, e.g. "live horses for breeding"
        action : str
            Either "validate" or "suggest" (default: "validate")

        Returns
        -------
        dict
            For validation: {input_code: {"valid": bool, "nearest": str | None, "description": str | None}}
            For suggestion: {"suggestions": [{"code": str, "description": str, "confidence": float}]}
        """
        if action.lower() == "suggest":
            return suggest_hsn_codes(query)
        else:
            return validate_hsn_code(query)

    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        """
        ADK async implementation - required for web interface
        """
        # Extract user input from context
        user_message = ""
        if hasattr(ctx, 'user_content') and ctx.user_content:
            # Extract text from user content
            if hasattr(ctx.user_content, 'text'):
                user_message = ctx.user_content.text
            elif hasattr(ctx.user_content, 'content'):
                user_message = str(ctx.user_content.content)
            else:
                user_message = str(ctx.user_content)
        
        # Default values
        query = ""
        action = "validate"
        
        # Simple parsing of user input to extract parameters
        if "action:" in user_message.lower():
            parts = user_message.lower().split("action:")
            if len(parts) > 1:
                action_part = parts[1].strip().split()[0]  # Get first word after action:
                if action_part in ["validate", "suggest"]:
                    action = action_part
        
        # Extract query - look for "query:" or just use numbers/text
        if "query:" in user_message.lower():
            query_match = re.search(r'query:\s*([^\n\r]+)', user_message, re.IGNORECASE)
            if query_match:
                query = query_match.group(1).strip()
        else:
            # Auto-detect: if contains digits, likely validation; otherwise suggestion
            if re.search(r'\d', user_message):
                action = "validate"
                # Extract all sequences that look like HSN codes (2-8 digits, possibly with commas/spaces)
                hsn_matches = re.findall(r'\b\d{2,8}\b', user_message)
                if hsn_matches:
                    query = ", ".join(hsn_matches)
                else:
                    query = user_message.strip()
            else:
                action = "suggest"
                query = user_message.strip()
        
        try:
            # Call the synchronous run method with keyword arguments
            result = await asyncio.get_event_loop().run_in_executor(
                None, lambda: self.run(query=query, action=action)
            )
            
            # Format the result as readable text for display
            if action == "validate":
                response_text = "HSN Code Validation Results:\n\n"
                for code, details in result.items():
                    status = "Valid" if details['valid'] else "Invalid"
                    response_text += f"**{code}**: {status}\n"
                    if details['valid']:
                        response_text += f"   Description: {details['description']}\n"
                    else:
                        response_text += f"   Error: {details['error']}\n"
                        if details.get('nearest'):
                            response_text += f"   Suggested: {details['nearest']} - {details.get('nearest_description', '')}\n"
                    response_text += "\n"
                    
            elif action == "suggest":
                response_text = "HSN Code Suggestions:\n\n"
                
                # Handle both list and dict results
                if isinstance(result, list):
                    # List format from suggest_hsn_codes
                    for i, suggestion in enumerate(result, 1):
                        confidence_pct = suggestion['confidence'] * 100
                        response_text += f"{i}. {suggestion['code']} (Confidence: {confidence_pct:.1f}%)\n"
                        response_text += f"   {suggestion['description']}\n\n"
                    
                    if not result:
                        response_text = "No HSN code suggestions found for the given query."
                        
                elif isinstance(result, dict) and 'suggestions' in result:
                    # Dict format with suggestions key
                    suggestions = result['suggestions']
                    for i, suggestion in enumerate(suggestions, 1):
                        confidence_pct = suggestion['confidence'] * 100
                        response_text += f"{i}. {suggestion['code']} (Confidence: {confidence_pct:.1f}%)\n"
                        response_text += f"   {suggestion['description']}\n\n"
                    
                    if not suggestions:
                        response_text = "No HSN code suggestions found for the given query."
                else:
                    response_text = "No HSN code suggestions found for the given query."
            
            # Create Event with the formatted response using proper Content structure
            content = genai_types.Content(
                parts=[genai_types.Part(text=response_text)],
                role='model'
            )
            
            yield Event(
                author="agent",
                content=content,
                custom_metadata={
                    "result": json.dumps(result),
                    "action": action,
                    "query": query
                }
            )
            
        except Exception as e:
            error_text = f"Error processing request: {str(e)}"
            
            # Create error content
            error_content = genai_types.Content(
                parts=[genai_types.Part(text=error_text)],
                role='model'
            )
            
            yield Event(
                author="agent", 
                content=error_content,
                custom_metadata={
                    "error": str(e),
                    "action": action,
                    "query": query,
                    "user_input": str(user_message)
                }
            )


# ---------------------------------------------------------------------------
# ADK looks for a variable named `root_agent` in this package.
# It *must* be an INSTANCE (not the class) of a subclass of BaseAgent.
# ---------------------------------------------------------------------------
root_agent = ValidateHSNAgent()
