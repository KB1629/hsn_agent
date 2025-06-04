#!/usr/bin/env python3
"""
Test script for HSN Code Validation and Suggestion Agent
"""

import json
from hsn_agent.validate import validate_hsn_code, suggest_hsn_codes

def test_validation():
    """Test HSN code validation functionality"""
    print("=" * 60)
    print("TESTING HSN CODE VALIDATION")
    print("=" * 60)
    
    # Test cases for validation
    test_codes = [
        "01",           # Valid 2-digit code
        "0101",         # Valid 4-digit code  
        "01011010",     # Valid 8-digit code
        "999999",       # Invalid code
        "abc123",       # Invalid format
        "1",            # Too short
        "123456789",    # Too long
        "01, 0101, 999999"  # Multiple codes
    ]
    
    for code in test_codes:
        print(f"\nTesting code: '{code}'")
        result = validate_hsn_code(code)
        print(json.dumps(result, indent=2))

def test_suggestion():
    """Test HSN code suggestion functionality"""
    print("\n" + "=" * 60)
    print("TESTING HSN CODE SUGGESTION")
    print("=" * 60)
    
    # Test cases for suggestions
    test_descriptions = [
        "live horses",
        "bovine animals",
        "meat products",
        "live poultry chickens",
        "empty description test"
    ]
    
    for description in test_descriptions:
        print(f"\nSuggesting codes for: '{description}'")
        result = suggest_hsn_codes(description)
        print(json.dumps(result, indent=2))

def test_agent_integration():
    """Test the complete agent functionality"""
    print("\n" + "=" * 60)
    print("TESTING AGENT INTEGRATION")
    print("=" * 60)
    
    try:
        from hsn_agent import root_agent
        
        # Test validation through agent
        print("\n--- Testing Agent Validation ---")
        validation_result = root_agent.run(query="01, 0101, 999999", action="validate")
        print(json.dumps(validation_result, indent=2))
        
        # Test suggestion through agent
        print("\n--- Testing Agent Suggestion ---")
        suggestion_result = root_agent.run(query="live horses for breeding", action="suggest")
        print(json.dumps(suggestion_result, indent=2))
        
        print("\nAgent integration test PASSED")
    except Exception as e:
        print(f"\nAgent integration test FAILED: {e}")

if __name__ == "__main__":
    test_validation()
    test_suggestion() 
    test_agent_integration()
    print("\n" + "=" * 60)
    print("TEST COMPLETED")
    print("=" * 60) 