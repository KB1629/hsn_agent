#!/usr/bin/env python3
"""
HSN Code Validation and Suggestion Agent Demo

This demo showcases the complete functionality of the HSN Code Validation
and Suggestion Agent built with Google's ADK framework.
"""

from hsn_agent import root_agent

def print_header(title):
    """Print a formatted header for demo sections"""
    print("=" * 80)
    print(f"{title}")
    print("=" * 80)

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{title}")
    print("-" * len(title))

def demo_validation():
    """Demonstrate HSN code validation capabilities"""
    print_section("HSN CODE VALIDATION DEMO")
    
    test_cases = [
        ("VALID CODES TEST", "01, 0101, 17019930"),
        ("FORMAT VALIDATION TEST", "abc, 123456789, 01"),
        ("HIERARCHICAL VALIDATION TEST", "010110, 999999, 0104")
    ]
    
    print("\nTesting various validation scenarios:")
    
    for i, (test_name, codes) in enumerate(test_cases, 1):
        print(f"\n{i}. {test_name}")
        print(f"Input: {codes}")
        try:
            result = root_agent.run(query=codes, action="validate")
            print(f"Result: {result}")
        except Exception as e:
            print(f"Error: {e}")

def demo_suggestions():
    """Demonstrate HSN code suggestion capabilities"""
    print_section("HSN CODE SUGGESTION DEMO")
    
    test_queries = [
        ("ANIMAL PRODUCTS", "live horses for breeding"),
        ("SPECIFIC PRODUCTS", "mobile phones and smartphones"),
        ("GENERAL CATEGORY", "agricultural products")
    ]
    
    for i, (category, query) in enumerate(test_queries, 1):
        print(f"\n{i}. {category}")
        print(f"Query: '{query}'")
        try:
            result = root_agent.run(query=query, action="suggest")
            print(f"Suggestions: {result}")
        except Exception as e:
            print(f"Error: {e}")

def demo_edge_cases():
    """Demonstrate edge case handling and robustness"""
    print_section("EDGE CASES AND ROBUSTNESS")
    
    print("\nTesting robustness with edge cases:")
    
    print("\n1. EMPTY INPUTS")
    test_cases = [
        ("", "validate"),
        ("", "suggest")
    ]
    
    for query, action in test_cases:
        try:
            result = root_agent.run(query=query, action=action)
            print(f"Empty {action}: {result}")
        except Exception as e:
            print(f"Empty {action} error: {e}")
    
    print("\n2. MIXED VALID/INVALID CODES")
    try:
        result = root_agent.run(query="01, invalid_code, 0101", action="validate")
        print(f"Mixed validation: {result}")
    except Exception as e:
        print(f"Mixed validation error: {e}")

def show_features():
    """Display implemented features summary"""
    features = {
        "ADK Framework Integration": "BaseAgent implementation with proper ADK structure",
        "Format Validation": "Numeric check, length constraints (2-8 digits)",
        "Existence Validation": "Exact match against 21K+ HSN codes dataset",
        "Hierarchical Validation": "Parent code discovery for invalid codes",
        "Suggestion Algorithm": "Text similarity + keyword matching with confidence scores",
        "Batch Processing": "Multiple comma-separated codes support",
        "Error Handling": "Detailed error messages and validation feedback",
        "Web Interface": "ADK web UI integration",
        "Comprehensive Dataset": "21,582 HSN codes with descriptions"
    }
    
    print("\nIMPLEMENTED FEATURES:")
    for feature, description in features.items():
        print(f"  {feature}: {description}")

def main():
    """Run the complete demo"""
    try:
        print_header("HSN Code Validation and Suggestion Agent Demo")
        
        print("Google ADK Framework Implementation")
        print("This demo showcases validation and suggestion capabilities")
        print("of the HSN Code Agent with comprehensive error handling.")
        
        # Run all demo sections
        demo_validation()
        demo_suggestions()
        demo_edge_cases()
        show_features()
        
        print_header("DEMO COMPLETED SUCCESSFULLY!")
        
        print("\nThe HSN Code Validation and Suggestion Agent is ready for use.")
        print("You can now:")
        print("1. Run individual tests with specific HSN codes")
        print("2. Test product description-based suggestions")
        print("3. Use the web interface for interactive testing")
        
        print("\nReady for ADK web interface: run 'adk web'")
        print("Access at: http://localhost:8000/dev-ui/?app=hsn_agent")
        
    except Exception as e:
        print(f"\nDemo failed: {e}")

if __name__ == "__main__":
    main() 