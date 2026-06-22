#!/usr/bin/env python3
"""
Test script for Shakespeare Translator API.

Usage:
    python test_api.py

Tests transformation functionality without needing the server running.
Uses transformer module directly.
"""

from transformer import transformer
import json


def test_basic_transformation():
    """Test basic text transformation."""
    print("=" * 60)
    print("  TEST 1: Basic Transformation")
    print("=" * 60)
    
    text = "Hey, what's up? I'm just hanging out with my friends."
    result = transformer.transform(text)
    
    print(f"\n📝 Original:\n   {result['original']}")
    print(f"\n🎭 Shakespearean:\n   {result['transformed']}")
    
    if result.get("usage"):
        print(f"\n📊 Usage:")
        print(f"   Input tokens:  {result['usage']['input_tokens']}")
        print(f"   Output tokens: {result['usage']['output_tokens']}")
        print(f"   Total tokens:  {result['usage']['total_tokens']}")
    
    return bool(result.get("transformed"))


def test_formal_text():
    """Test transformation of formal text."""
    print("\n" + "=" * 60)
    print("  TEST 2: Formal Text")
    print("=" * 60)
    
    text = "Ladies and gentlemen, welcome to our conference on modern technology."
    result = transformer.transform(text)
    
    print(f"\n📝 Original:\n   {result['original']}")
    print(f"\n🎭 Shakespearean:\n   {result['transformed']}")
    
    return bool(result.get("transformed"))


def test_slang():
    """Test transformation of modern slang."""
    print("\n" + "=" * 60)
    print("  TEST 3: Modern Slang")
    print("=" * 60)
    
    text = "That new startup is totally fire and definitely going to make it big."
    result = transformer.transform(text)
    
    print(f"\n📝 Original:\n   {result['original']}")
    print(f"\n🎭 Shakespearean:\n   {result['transformed']}")
    
    return bool(result.get("transformed"))


def test_short_text():
    """Test transformation of short text."""
    print("\n" + "=" * 60)
    print("  TEST 4: Short Text")
    print("=" * 60)
    
    text = "No way!"
    result = transformer.transform(text)
    
    print(f"\n📝 Original:\n   {result['original']}")
    print(f"\n🎭 Shakespearean:\n   {result['transformed']}")
    
    return bool(result.get("transformed"))


def test_empty_text():
    """Test handling of empty text."""
    print("\n" + "=" * 60)
    print("  TEST 5: Empty Text (Error Handling)")
    print("=" * 60)
    
    result = transformer.transform("")
    
    if result.get("error"):
        print(f"\n✅ Error handled correctly:")
        print(f"   {result['error']}")
        return True
    
    return False


def main():
    """Run all tests."""
    print("\n")
    print("🎭 Shakespeare Translator — API Test Suite")
    print()
    
    tests = [
        ("Basic Transformation", test_basic_transformation),
        ("Formal Text", test_formal_text),
        ("Modern Slang", test_slang),
        ("Short Text", test_short_text),
        ("Empty Text (Error Handling)", test_empty_text),
    ]
    
    results = {}
    for name, test_func in tests:
        try:
            passed = test_func()
            results[name] = "✅ PASS" if passed else "❌ FAIL"
        except Exception as e:
            results[name] = f"❌ ERROR: {str(e)}"
    
    # Summary
    print("\n" + "=" * 60)
    print("  TEST SUMMARY")
    print("=" * 60)
    for test_name, status in results.items():
        print(f"  {test_name:<35} {status}")
    
    passed = sum(1 for s in results.values() if "PASS" in s)
    total = len(results)
    
    print(f"\n  {passed}/{total} tests passed")
    print()


if __name__ == "__main__":
    main()
