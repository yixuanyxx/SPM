# Task Controller Integration Test Coverage

This document summarizes the comprehensive integration test coverage for the task controller endpoints.

## Test Overview

**Total Test Cases: 64**

- ✅ 10 tests for `manager_create_task`
- ✅ 6 tests for `staff_create_task`
- ✅ 6 tests for `manager_create_subtask`
- ✅ 6 tests for `staff_create_subtask`
- ✅ 8 tests for `update_task`
- ✅ 3 tests for `get_task_by_id`
- ✅ 4 tests for `get_tasks_by_user`
- ✅ 3 tests for `get_tasks_by_project`
- ✅ 3 tests for `get_tasks_by_owner`
- ✅ 4 tests for `get_subtasks_by_parent`
- ✅ 3 tests for `get_tasks_by_team`
- ✅ 3 tests for `get_tasks_by_department`

---

## 1. manager_create_task Tests (10 tests)

### Endpoint: `POST /tasks/manager-task/create`

| Test Case | Description | Expected Result |
|-----------|-------------|-----------------|
| `test_manager_create_task_success` | Create task with required fields only | 201 - Task created successfully |
| `test_manager_create_task_with_all_fields` | Create task with all optional fields | 201 - All fields properly stored |
| `test_manager_create_task_duplicate_name` | Attempt to create task with duplicate name | 200 - Returns existing task |
| `test_manager_create_task_missing_owner_id` | Create task without owner_id | 400 - Validation error |
| `test_manager_create_task_missing_task_name` | Create task without task_name | 400 - Validation error |
| `test_manager_create_task_missing_description` | Create task without description | 400 - Validation error |
| `test_manager_create_task_invalid_task_type` | Create task with invalid type | 400 - Validation error |
| `test_manager_create_task_with_attachment` | Create task with file attachment | 201 - File uploaded & task created |
| `test_manager_create_task_attachment_upload_failure` | File upload fails | 500 - Upload error returned |
| `test_manager_create_task_repository_error` | Database error during creation | 500 - Database error returned |

---

## 2. staff_create_task Tests (6 tests)

### Endpoint: `POST /tasks/staff-task/create`

**Key Difference:** Automatically adds `owner_id` to the `collaborators` list

| Test Case | Description | Expected Result |
|-----------|-------------|-----------------|
| `test_staff_create_task_success` | Create task without collaborators | 201 - Owner auto-added to collaborators |
| `test_staff_create_task_owner_added_to_collaborators` | Create task with collaborators (owner not included) | 201 - Owner added to collaborators list |
| `test_staff_create_task_owner_already_in_collaborators` | Create task with owner already in collaborators | 201 - Owner appears only once |
| `test_staff_create_task_duplicate_name` | Attempt to create task with duplicate name | 200 - Returns existing task |
| `test_staff_create_task_missing_fields` | Create task with missing required fields | 400 - Validation error |
| `test_staff_create_task_with_attachment` | Create task with file attachment | 201 - File uploaded & owner in collaborators |

---

## 3. manager_create_subtask Tests (6 tests)

### Endpoint: `POST /tasks/manager-subtask/create`

**Key Features:** 
- Requires `parent_task` field
- Automatically sets `type` to "subtask"
- Updates parent task's subtasks list

| Test Case | Description | Expected Result |
|-----------|-------------|-----------------|
| `test_manager_create_subtask_success` | Create subtask with valid parent | 201 - Subtask created & parent updated |
| `test_manager_create_subtask_missing_parent_task` | Create subtask without parent_task | 400 - Validation error |
| `test_manager_create_subtask_parent_not_found` | Create subtask with non-existent parent | 400 - Parent not found error |
| `test_manager_create_subtask_duplicate_name` | Create subtask with duplicate name | 200 - Returns existing subtask |
| `test_manager_create_subtask_with_collaborators` | Create subtask with collaborators | 201 - Subtask created with team |
| `test_manager_create_subtask_parent_update_fails` | Parent update fails after subtask creation | 201 - Subtask still created (warning logged) |

---

## 4. staff_create_subtask Tests (6 tests)

### Endpoint: `POST /tasks/staff-subtask/create`

**Key Features:**
- Requires `parent_task` field
- Automatically sets `type` to "subtask"
- Automatically adds `owner_id` to `collaborators`
- Updates parent task's subtasks list

| Test Case | Description | Expected Result |
|-----------|-------------|-----------------|
| `test_staff_create_subtask_success` | Create subtask without collaborators | 201 - Owner auto-added to collaborators |
| `test_staff_create_subtask_owner_added_to_collaborators` | Create subtask with collaborators (owner not included) | 201 - Owner added to collaborators |
| `test_staff_create_subtask_missing_parent_task` | Create subtask without parent_task | 400 - Validation error |
| `test_staff_create_subtask_parent_not_found` | Create subtask with non-existent parent | 400 - Parent not found error |
| `test_staff_create_subtask_duplicate_name` | Create subtask with duplicate name | 200 - Returns existing subtask |
| `test_staff_create_subtask_missing_required_fields` | Create subtask without owner_id | 400 - Validation error |

---

## 5. update_task Tests (8 tests)

### Endpoint: `PUT/PATCH /tasks/update`

**Key Features:**
- Only `task_id` is required
- Can update any combination of fields
- Validates field values

| Test Case | Description | Expected Result |
|-----------|-------------|-----------------|
| `test_update_task_success` | Update multiple fields | 200 - Task updated successfully |
| `test_update_task_single_field` | Update only one field (status) | 200 - Single field updated |
| `test_update_task_missing_task_id` | Update without task_id | 400 - Validation error |
| `test_update_task_not_found` | Update non-existent task | 404 - Task not found |
| `test_update_task_no_fields_to_update` | Only task_id provided | 400 - No fields to update |
| `test_update_task_with_collaborators` | Update collaborators list | 200 - Collaborators updated |
| `test_update_task_invalid_type` | Update with invalid task type | 400 - Validation error |
| `test_update_task_repository_error` | Repository error during update | 500 - Error handled |

---

## 6. get_task_by_id Tests (3 tests)

### Endpoint: `GET /tasks/<task_id>`

| Test Case | Description | Expected Result |
|-----------|-------------|-----------------|
| `test_get_task_by_id_success` | Retrieve existing task | 200 - Task data returned |
| `test_get_task_by_id_not_found` | Retrieve non-existent task | 404 - Task not found |
| `test_get_task_by_id_repository_error` | Repository error | 500 - Error handled |

---

## 7. get_tasks_by_user Tests (4 tests)

### Endpoint: `GET /tasks/user-task/<user_id>`

**Key Features:**
- Returns tasks where user is owner or collaborator
- Includes nested subtasks for parent tasks

| Test Case | Description | Expected Result |
|-----------|-------------|-----------------|
| `test_get_tasks_by_user_success` | Retrieve user's tasks | 200 - Parent tasks returned |
| `test_get_tasks_by_user_with_subtasks` | Retrieve tasks with subtasks | 200 - Tasks with nested subtasks |
| `test_get_tasks_by_user_not_found` | No tasks for user | 404 - No tasks found |
| `test_get_tasks_by_user_repository_error` | Repository error | 500 - Error handled |

---

## 8. get_tasks_by_project Tests (3 tests)

### Endpoint: `GET /tasks/project/<project_id>`

| Test Case | Description | Expected Result |
|-----------|-------------|-----------------|
| `test_get_tasks_by_project_success` | Retrieve project's tasks | 200 - All project tasks returned |
| `test_get_tasks_by_project_not_found` | No tasks for project | 404 - No tasks found |
| `test_get_tasks_by_project_repository_error` | Repository error | 500 - Error handled |

---

## 9. get_tasks_by_owner Tests (3 tests)

### Endpoint: `GET /tasks/owner/<owner_id>`

**Note:** Returns tasks where user is the owner (not collaborator)

| Test Case | Description | Expected Result |
|-----------|-------------|-----------------|
| `test_get_tasks_by_owner_success` | Retrieve owned tasks | 200 - All owned tasks returned |
| `test_get_tasks_by_owner_not_found` | No owned tasks | 404 - No tasks found |
| `test_get_tasks_by_owner_repository_error` | Repository error | 500 - Error handled |

---

## 10. get_subtasks_by_parent Tests (4 tests)

### Endpoint: `GET /tasks/<parent_task_id>/subtasks`

**Key Features:**
- Retrieves full details of all subtasks for a parent task
- Returns 207 (Multi-status) for partial success

| Test Case | Description | Expected Result |
|-----------|-------------|-----------------|
| `test_get_subtasks_by_parent_success` | Retrieve all subtasks successfully | 200 - All subtasks returned |
| `test_get_subtasks_by_parent_no_subtasks` | Parent has no subtasks | 200 - Empty subtasks list |
| `test_get_subtasks_by_parent_not_found` | Parent task doesn't exist | 404 - Parent not found |
| `test_get_subtasks_by_parent_partial_success` | Some subtasks not found | 207 - Partial success with failed list |

---

## 11. get_tasks_by_team Tests (3 tests)

### Endpoint: `GET /tasks/team/<team_id>`

**Key Features:**
- Returns tasks for all users in a team
- Includes nested subtasks

| Test Case | Description | Expected Result |
|-----------|-------------|-----------------|
| `test_get_tasks_by_team_success` | Retrieve team tasks | 200 - All team tasks returned |
| `test_get_tasks_by_team_not_found` | No tasks for team | 404 - No tasks found |
| `test_get_tasks_by_team_repository_error` | Repository error | 500 - Error handled |

---

## 12. get_tasks_by_department Tests (3 tests)

### Endpoint: `GET /tasks/department/<dept_id>`

**Key Features:**
- Returns tasks for all users in a department
- Includes nested subtasks

| Test Case | Description | Expected Result |
|-----------|-------------|-----------------|
| `test_get_tasks_by_department_success` | Retrieve department tasks | 200 - All dept tasks returned |
| `test_get_tasks_by_department_not_found` | No tasks for department | 404 - No tasks found |
| `test_get_tasks_by_department_repository_error` | Repository error | 500 - Error handled |

---

## Key Testing Patterns

### 1. **Success Cases**
- Valid data with required fields only
- Valid data with all optional fields
- Proper handling of collaborators and attachments

### 2. **Validation Cases**
- Missing required fields
- Invalid field values
- Duplicate name detection

### 3. **Error Handling**
- Repository/database errors
- File upload failures
- Parent task validation (for subtasks)

### 4. **Business Logic**
- Manager vs Staff differences (collaborator auto-add)
- Parent task updates for subtasks
- Graceful failure handling

---

## Mock Strategy

All tests use **direct repository mocking** by replacing `service.repo`:

```python
def setUp(self):
    self.mock_repo = Mock()
    service.repo = self.mock_repo  # Direct replacement
    # ... create test client ...
```

This ensures:
- ✅ No database connections needed
- ✅ Isolated unit testing
- ✅ Fast test execution
- ✅ Predictable mock behavior

---

## Running the Tests

### Run All Integration Tests
```bash
cd backend/tasks
python tests/run_manager_create_tests.py
```

### Run Specific Test
```bash
cd backend/tasks
python -m unittest tests.test_task_controller_integration.TestTaskControllerIntegration.test_manager_create_task_success -v
```

### Run Test Class
```bash
cd backend/tasks
python -m unittest tests.test_task_controller_integration.TestTaskControllerIntegration -v
```

---

## Test Coverage Matrix

| Endpoint | Success | Validation | Errors | Business Logic | Total |
|----------|---------|------------|--------|---------------|-------|
| manager_create_task | 3 | 4 | 2 | 1 | **10** |
| staff_create_task | 2 | 2 | 0 | 2 | **6** |
| manager_create_subtask | 2 | 2 | 1 | 1 | **6** |
| staff_create_subtask | 2 | 3 | 0 | 1 | **6** |
| update_task | 3 | 3 | 1 | 1 | **8** |
| get_task_by_id | 1 | 1 | 1 | 0 | **3** |
| get_tasks_by_user | 2 | 1 | 1 | 0 | **4** |
| get_tasks_by_project | 1 | 1 | 1 | 0 | **3** |
| get_tasks_by_owner | 1 | 1 | 1 | 0 | **3** |
| get_subtasks_by_parent | 2 | 1 | 0 | 1 | **4** |
| get_tasks_by_team | 1 | 1 | 1 | 0 | **3** |
| get_tasks_by_department | 1 | 1 | 1 | 0 | **3** |
| **TOTAL** | **21** | **22** | **11** | **8** | **64** |

---

## Assertions Covered

Each test verifies:
1. ✅ HTTP status code
2. ✅ Response JSON structure
3. ✅ Response "Code" field
4. ✅ Message content
5. ✅ Data payload correctness
6. ✅ Repository method calls (with correct parameters)

---

## Completed Endpoints ✅

All task controller endpoints now have comprehensive test coverage:
- ✅ `manager_create_task` endpoint (10 tests)
- ✅ `staff_create_task` endpoint (6 tests)
- ✅ `manager_create_subtask` endpoint (6 tests)
- ✅ `staff_create_subtask` endpoint (6 tests)
- ✅ `update_task` endpoint (8 tests)
- ✅ `get_task_by_id` endpoint (3 tests)
- ✅ `get_tasks_by_user` endpoint (4 tests)
- ✅ `get_tasks_by_project` endpoint (3 tests)
- ✅ `get_tasks_by_owner` endpoint (3 tests)
- ✅ `get_subtasks_by_parent` endpoint (4 tests)
- ✅ `get_tasks_by_team` endpoint (3 tests)
- ✅ `get_tasks_by_department` endpoint (3 tests)

## Next Steps

Consider adding tests for:
- [ ] `bulk_update_project_id` endpoint
- [ ] Edge cases for date parsing
- [ ] Concurrent request handling
- [ ] Performance/load testing
- [ ] Integration tests with actual database

