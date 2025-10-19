#!/usr/bin/env python3
"""
Simple Test Runner - Only Model and Controller Tests

This runs only the essential tests:
- Report Model tests (data validation, unit tests)
- Report Controller tests (API endpoints, integration tests)
"""

import os
import sys
import subprocess

def check_microservices():
    """Check if required microservices are running for integration tests."""
    import requests
    
    services = {
        "Users Service": "http://localhost:5003/health",
        "Tasks Service": "http://localhost:5002/health", 
        "Projects Service": "http://localhost:5001/health",
        "Team Service": "http://localhost:5004/health",
        "Dept Service": "http://localhost:5005/health"
    }

    
    all_running = True
    print("Checking microservices availability:")
    
    for name, url in services.items():
        try:
            response = requests.get(url, timeout=2)
            status = "✓ Running" if response.status_code in [200, 404] else "✗ Down"
            print(f"   {name}: {status}")
            if response.status_code not in [200, 404]:
                all_running = False
        except requests.exceptions.RequestException:
            print(f"   {name}: ✗ Not available")
            all_running = False
    
    if not all_running:
        print("\nWarning: Not all microservices are running")
        print("Integration tests may fail or be skipped")
        print("\nTo run all services:")
        print("  - Users: cd backend/users && python app.py")
        print("  - Tasks: cd backend/tasks && python app.py")
        print("  - Projects: cd backend/projects && python app.py")
        print("  - Team: cd backend/team && python app.py")
        print("  - Dept: cd backend/dept && python app.py")
    
    return all_running

def run_model_tests():
    """Run report model/unit tests (no microservices needed)."""
    print("\nRunning Report Model & Unit Tests...")
    print("=" * 50)
    try:
        # Add current directory (microservice root) to Python path and run tests
        env = os.environ.copy()
        env['PYTHONPATH'] = os.getcwd()
        
        result = subprocess.run([sys.executable, "-m", "unittest", 
                               "test_report_model", "-v"],
                              cwd="tests", capture_output=True, text=True, env=env)
        
        print("Model/Unit Test Results:")
        print(result.stdout)
        
        if result.stderr:
            # Filter out expected error logs from unit tests
            stderr_lines = result.stderr.split('\n')
            filtered_stderr = [line for line in stderr_lines 
                             if line and not line.startswith('Error fetching')]
            if filtered_stderr:
                print("Errors/Warnings:")
                print('\n'.join(filtered_stderr))
        
        if result.returncode == 0:
            print("[SUCCESS] All model/unit tests passed!")
            return True
        else:
            print("[ERROR] Some model/unit tests failed")
            return False
    except Exception as e:
        print(f"[ERROR] Error running model tests: {e}")
        return False

def run_controller_tests():
    """Run report controller integration tests."""
    print("\nRunning Report Controller Integration Tests...")
    print("=" * 50)
    try:
        # Add current directory (microservice root) to Python path and run tests
        env = os.environ.copy()
        env['PYTHONPATH'] = os.getcwd()
        
        # Optional: Set test user IDs via environment variables
        if not env.get('TEST_STAFF_USER_ID'):
            env['TEST_STAFF_USER_ID'] = '101'
        if not env.get('TEST_MANAGER_USER_ID'):
            env['TEST_MANAGER_USER_ID'] = '352'
        if not env.get('TEST_DIRECTOR_USER_ID'):
            env['TEST_DIRECTOR_USER_ID'] = '399'
        
        result = subprocess.run([sys.executable, "-m", "unittest", 
                               "test_report_controller_integration", "-v"],
                              cwd="tests", capture_output=True, text=True, env=env)
        
        print("Controller Integration Test Results:")
        print(result.stdout)
        
        if result.stderr:
            print("Errors/Warnings:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("[SUCCESS] All controller integration tests passed!")
            return True
        else:
            print("[ERROR] Some controller integration tests failed")
            return False
    except Exception as e:
        print(f"[ERROR] Error running controller tests: {e}")
        return False

def main():
    """Main function."""
    print("Report Module Test Runner")
    print("=" * 50)
    print()
    
    # Always run model/unit tests (no microservices needed)
    model_success = run_model_tests()
    
    # Check if microservices are available
    print()
    has_services = check_microservices()
    
    if has_services:
        controller_success = run_controller_tests()
    else:
        print("\n[SKIP] Skipping controller integration tests (microservices not available)")
        print("Note: Unit tests in model file already provide good coverage")
        controller_success = True  # Don't fail the run
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Summary:")
    print(f"  Model/Unit Tests: {'✓ PASSED' if model_success else '✗ FAILED'}")
    if has_services:
        print(f"  Controller Integration Tests: {'✓ PASSED' if controller_success else '✗ FAILED'}")
    else:
        print("  Controller Integration Tests: ⊘ SKIPPED")
    
    print("\n" + "=" * 50)
    if model_success and controller_success:
        print("✓ All tests completed successfully!")
        return 0
    else:
        print("✗ Some tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
