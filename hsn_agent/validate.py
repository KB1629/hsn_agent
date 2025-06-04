"""
validate_hsn_code(code: str)  ->  dict
suggest_hsn_codes(description: str) -> dict

Standalone validator and suggestion functions that work with google-adk 1.1.1
(no decorators / classes required).
"""
from pathlib import Path
import csv
import re
from typing import Dict, List, Tuple
from difflib import SequenceMatcher

# ---------- locate the CSV once, at import time ----------
DATA_DIR  = Path(__file__).with_suffix("").with_name("data")   # …/hsn_agent/data
DATA_FILE = DATA_DIR / "hsn_codes.csv"                        # …/hsn_agent/data/hsn_codes.csv
VALID_CODES: set[str] = set()
HSN_DATA: dict[str, str] = {}  # code -> description mapping
# ---------------------------------------------------------

# Load HSN codes and descriptions
with DATA_FILE.open(newline="", encoding="utf-8") as f:
    reader = csv.reader(f)
    next(reader)  # Skip header if present
    for row in reader:
        if row and len(row) >= 2:
            code = row[0].strip().strip('"')
            description = row[1].strip() if len(row) > 1 else ""
            if code:  # Only add non-empty codes
                VALID_CODES.add(code)
                HSN_DATA[code] = description

def is_valid_hsn_format(code: str) -> Tuple[bool, str]:
    """
    Validate HSN code format.
    
    Args:
        code: HSN code to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not code:
        return False, "Empty code"
    
    # Remove any whitespace
    code = code.strip()
    
    # Check if it's numeric
    if not code.isdigit():
        return False, "HSN code must be numeric"
    
    # Check length (typically 2-8 digits)
    if len(code) < 2:
        return False, "HSN code too short (minimum 2 digits)"
    if len(code) > 8:
        return False, "HSN code too long (maximum 8 digits)"
    
    return True, ""

def get_similarity_score(text1: str, text2: str) -> float:
    """Calculate similarity score between two text strings."""
    return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()

def suggest_hsn_codes(description: str, max_suggestions: int = 5) -> dict:
    """
    Suggest HSN codes based on product description.
    
    Args:
        description: Product or service description
        max_suggestions: Maximum number of suggestions to return
        
    Returns:
        dict: {"suggestions": [{"code": str, "description": str, "confidence": float}]}
    """
    if not description or not description.strip():
        return {
            "suggestions": [],
            "error": "Empty description provided"
        }
    
    description = description.strip().lower()
    suggestions = []
    
    # Search for matching descriptions
    for code, desc in HSN_DATA.items():
        if desc:  # Only consider codes with descriptions
            similarity = get_similarity_score(description, desc)
            
            # Also check for keyword matches
            desc_words = set(desc.lower().split())
            query_words = set(description.split())
            keyword_overlap = len(desc_words.intersection(query_words)) / max(len(query_words), 1)
            
            # Combine similarity scores
            final_score = (similarity * 0.7) + (keyword_overlap * 0.3)
            
            if final_score > 0.1:  # Minimum threshold
                suggestions.append({
                    "code": code,
                    "description": desc,
                    "confidence": round(final_score, 3)
                })
    
    # Sort by confidence score (descending)
    suggestions.sort(key=lambda x: x["confidence"], reverse=True)
    
    return {
        "suggestions": suggestions[:max_suggestions],
        "query": description
    }

def validate_hsn_code(code: str) -> dict:
    """
    Args
    ----
    code : str
        Comma-separated HSN codes, e.g. "17019930, 01".

    Returns
    -------
    dict
        {input_code: {"valid": bool, "nearest": str | None, "description": str | None, "error": str | None}}
    """
    out: dict[str, dict] = {}

    for raw in code.split(","):
        c = raw.strip()
        if not c:
            continue

        # Format validation first
        is_valid_format, format_error = is_valid_hsn_format(c)
        if not is_valid_format:
            out[c] = {
                "valid": False,
                "nearest": None,
                "description": None,
                "error": f"Format error: {format_error}"
            }
            continue

        # Check if exact code exists
        if c in VALID_CODES:
            out[c] = {
                "valid": True,
                "nearest": c,
                "description": HSN_DATA.get(c, ""),
                "error": None
            }
            continue

        # Hierarchical validation - find nearest ancestor
        ancestor = c[:-1]
        while ancestor and ancestor not in VALID_CODES:
            ancestor = ancestor[:-1]

        if ancestor:
            out[c] = {
                "valid": False,
                "nearest": ancestor,
                "description": HSN_DATA.get(ancestor, ""),
                "error": f"Code not found, but parent '{ancestor}' exists"
            }
        else:
            out[c] = {
                "valid": False,
                "nearest": None,
                "description": None,
                "error": "Code not found and no valid parent codes exist"
            }

    return out
