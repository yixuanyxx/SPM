#!/usr/bin/env python3
"""
Simple Test Runner - Notification Model Tests Only

This runs only the notification model tests:
- Notification Model tests (data validation and serialization)
"""

import os
import sys
import subprocess

def run_model_tests():
    """Run notification model tests (no environment variables needed)."""
    print("\nRunning Notification Model Tests...")
    try:
        # Add current directory (microservice root) to Python path and run tests
        env = os.environ.copy()
        env['PYTHONPATH'] = os.getcwd()
        
        result = subprocess.run([sys.executable, "-m", "unittest", 
                               "test_notification_model", "-v"],
                              cwd="tests", capture_output=True, text=True, env=env)
        
        print("Model Test Results:")
        print(result.stdout)
        
        if result.stderr:
            print("Errors/Warnings:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("[SUCCESS] All notification model tests passed!")
            return True
        else:
            print("[ERROR] Some notification model tests failed")
            return False
    except Exception as e:
        print(f"[ERROR] Error running notification model tests: {e}")
        return False

def main():
    """Main function."""
    print("Simple Test Runner - Notification Model Tests Only")
    print("=" * 50)
    
    # Run model tests (no environment needed)
    model_success = run_model_tests()
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Summary:")
    print(f"  Notification Model Tests: {'[PASSED]' if model_success else '[FAILED]'}")
    
    if model_success:
        print("\n[SUCCESS] All notification model tests completed successfully!")
        return 0
    else:
        print("\n[FAILURE] Some notification model tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
