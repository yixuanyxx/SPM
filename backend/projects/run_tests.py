#!/usr/bin/env python3
"""
Simple Test Runner - Only Model and Controller Tests

This runs only the essential tests:
- Project Model tests (data validation)
- Project Controller tests (API endpoints)
"""

import os
import sys
import subprocess

def check_environment():
    """Check if required environment variables are set for integration tests."""
    url = os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_SERVICE_KEY", "")
    
    if not url or not key:
        print("Warning: SUPABASE_URL and SUPABASE_SERVICE_KEY not set")
        print("Integration tests will be skipped")
        print("Set them with:")
        print("  set SUPABASE_URL=https://your-project.supabase.co")
        print("  set SUPABASE_SERVICE_KEY=your-service-key")
        return False
    
    print(f"Environment variables set:")
    print(f"   SUPABASE_URL: {url[:30]}...")
    print(f"   SUPABASE_SERVICE_KEY: {key[:10]}...")
    return True

def run_model_tests():
    """Run project model tests (no environment variables needed)."""
    print("\nRunning Project Model Tests...")
    try:
        # Add current directory to Python path to find tests module
        env = os.environ.copy()
        env['PYTHONPATH'] = os.getcwd()
        
        result = subprocess.run([sys.executable, "-m", "unittest", 
                               "tests.test_project_model", "-v"],
                              capture_output=True, text=True, env=env)
        
        print("Model Test Results:")
        print(result.stdout)
        
        if result.stderr:
            print("Errors/Warnings:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("[SUCCESS] All model tests passed!")
            return True
        else:
            print("[ERROR] Some model tests failed")
            return False
    except Exception as e:
        print(f"[ERROR] Error running model tests: {e}")
        return False

def run_controller_tests():
    """Run project controller integration tests."""
    print("\nRunning Project Controller Tests...")
    try:
        # Add current directory to Python path to find tests module
        env = os.environ.copy()
        env['PYTHONPATH'] = os.getcwd()
        
        result = subprocess.run([sys.executable, "-m", "unittest", 
                               "tests.test_project_controller_integration", "-v"],
                              capture_output=True, text=True, env=env)
        
        print("Controller Test Results:")
        print(result.stdout)
        
        if result.stderr:
            print("Errors/Warnings:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("[SUCCESS] All controller tests passed!")
            return True
        else:
            print("[ERROR] Some controller tests failed")
            return False
    except Exception as e:
        print(f"[ERROR] Error running controller tests: {e}")
        return False

def main():
    """Main function."""
    print("Simple Test Runner - Model + Controller Only")
    print("=" * 50)
    
    # Always run model tests (no environment needed)
    model_success = run_model_tests()
    
    # Check if we can run controller tests
    has_env = check_environment()
    
    if has_env:
        controller_success = run_controller_tests()
    else:
        print("\n[SKIP] Skipping controller tests (no environment variables)")
        controller_success = True  # Don't fail the run
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Summary:")
    print(f"  Model Tests: {'[PASSED]' if model_success else '[FAILED]'}")
    if has_env:
        print(f"  Controller Tests: {'[PASSED]' if controller_success else '[FAILED]'}")
    else:
        print("  Controller Tests: [SKIPPED]")
    
    if model_success and controller_success:
        print("\n[SUCCESS] All tests completed successfully!")
    else:
        print("\n[WARNING] Some tests failed. Check the output above.")

if __name__ == "__main__":
    main()

