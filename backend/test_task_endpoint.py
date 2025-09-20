#!/usr/bin/env python3
"""
Test script for the updated task endpoint with subtask support.
Run this to verify that the get_tasks_by_user endpoint works correctly.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tasks.services.task_service import TaskService
from tasks.repo.supa_task_repo import SupabaseTaskRepo

def test_task_service():
    """Test the TaskService.get_by_user method"""
    print("Testing TaskService.get_by_user...")
    
    try:
        # Initialize the service
        repo = SupabaseTaskRepo()
        service = TaskService(repo)
        
        # Test with a sample user ID (you should replace this with a real user ID from your database)
        test_user_id = 1  # Replace with an actual user ID
        
        result = service.get_by_user(test_user_id)
        
        print(f"✅ Service test successful!")
        print(f"Status: {result.get('status')}")
        print(f"Number of parent tasks: {len(result.get('data', []))}")
        
        # Print structure of first task if available
        if result.get('data'):
            first_task = result['data'][0]
            print(f"First task structure:")
            print(f"  - ID: {first_task.get('id')}")
            print(f"  - Name: {first_task.get('name')}")
            print(f"  - Status: {first_task.get('status')}")
            print(f"  - Subtasks count: {len(first_task.get('subtasks', []))}")
            
            if first_task.get('subtasks'):
                print(f"  - First subtask: {first_task['subtasks'][0].get('name')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Service test failed: {str(e)}")
        return False

def test_repository_methods():
    """Test the new repository methods"""
    print("\nTesting Repository methods...")
    
    try:
        repo = SupabaseTaskRepo()
        test_user_id = 1  # Replace with an actual user ID
        
        # Test find_parent_tasks_by_user
        parent_tasks = repo.find_parent_tasks_by_user(test_user_id)
        print(f"✅ Parent tasks found: {len(parent_tasks)}")
        
        # Test find_subtasks_by_parent if we have parent tasks
        if parent_tasks:
            first_parent_id = parent_tasks[0]['id']
            subtasks = repo.find_subtasks_by_parent(first_parent_id)
            print(f"✅ Subtasks for parent {first_parent_id}: {len(subtasks)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Repository test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Testing updated task management backend...\n")
    
    # Test repository methods
    repo_success = test_repository_methods()
    
    # Test service methods
    service_success = test_task_service()
    
    if repo_success and service_success:
        print("\n✅ All tests passed! The backend is ready for integration with TaskView.vue")
    else:
        print("\n❌ Some tests failed. Please check the error messages above.")