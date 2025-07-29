#!/usr/bin/env python3
"""
Simple test runner for 3MTT Chatbot
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and return success status"""
    print(f"\n🔍 {description}")
    print("-" * 50)
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        if result.stdout:
            print(result.stdout)
        
        if result.stderr:
            print("STDERR:", result.stderr)
        
        if result.returncode == 0:
            print(f"✅ {description} - PASSED")
            return True
        else:
            print(f"❌ {description} - FAILED")
            return False
    
    except Exception as e:
        print(f"❌ {description} - ERROR: {e}")
        return False

def main():
    """Run all tests and checks"""
    print("🚀 3MTT Chatbot Production Readiness Tests")
    print("=" * 60)
    
    tests = [
        ("python -m pytest tests/ -v", "Unit Tests"),
        ("python -c \"import app; print('✅ App imports successfully')\"", "Import Test"),
        ("python -c \"from app import app; client = app.test_client(); resp = client.get('/health'); print(f'Health check: {resp.status_code}')\"", "Health Check"),
    ]
    
    # Check if optional tools are available
    optional_tests = [
        ("flake8 app.py --max-line-length=100", "Code Style Check"),
        ("bandit -r app.py", "Security Scan"),
        ("safety check", "Dependency Security Check"),
    ]
    
    passed = 0
    total = len(tests)
    
    # Run core tests
    for command, description in tests:
        if run_command(command, description):
            passed += 1
    
    # Run optional tests if tools are available
    for command, description in optional_tests:
        tool = command.split()[0]
        if subprocess.run(f"which {tool}", shell=True, capture_output=True).returncode == 0:
            if run_command(command, description):
                passed += 1
            total += 1
        else:
            print(f"\n⚠️  {description} - SKIPPED (tool not installed)")
    
    # Summary
    print("\n" + "=" * 60)
    print(f"📊 TEST SUMMARY: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - Ready for production!")
        return 0
    else:
        print("⚠️  Some tests failed - Review issues before production deployment")
        return 1

if __name__ == "__main__":
    sys.exit(main())