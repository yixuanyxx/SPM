# Report Service Documentation

## Report Types

### 1. Personal Reports
**Endpoint**: `GET /reports/personal/<user_id>`

**Query Parameters**:
- `format`: json (default), pdf, excel
- `start_date`: YYYY-MM-DD (optional)
- `end_date`: YYYY-MM-DD (optional)

**Features**:
- Individual performance metrics
- Task completion rates and timelines
- Project involvement overview
- Personal workload analysis

### 2. Team Reports
**Endpoint**: `GET /reports/team/<manager_user_id>`

**Query Parameters**:
- `format`: json (default), pdf, excel
- `start_date`: YYYY-MM-DD (optional)
- `end_date`: YYYY-MM-DD (optional)

### 3. Department Reports
**Endpoint**: `GET /reports/department/<director_user_id>`

**Query Parameters**:
- `format`: json (default), pdf, excel
- `start_date`: YYYY-MM-DD (optional)
- `end_date`: YYYY-MM-DD (optional)

## Export Formats

### JSON Response
```json
{
  "Code": 200,
  "Message": "Report generated successfully",
  "data": {
    "manager_report": { /* Personal metrics */ },
    "team_report": { /* Team statistics */ },
    "detailed_workload_analysis": {
      "members_workload": [
        {
          "member_name": "John Doe",
          "member_role": "developer",
          "projects_breakdown": [
            {
              "project_name": "Mobile App",
              "total_tasks": 8,
              "completed_tasks": 5,
              "in_progress_tasks": 2,
              "overdue_tasks": 1,
              "estimated_hours": 32,
              "completion_percentage": 62.5
            }
          ],
          "total_projects": 2,
          "total_tasks": 15,
          "workload_score": 85.3,
          "availability_status": "Busy",
          "scheduling_conflicts": ["2 overdue tasks affecting schedule"]
        }
      ],
      "project_distribution": { /* Project-member mappings */ },
      "workload_summary": {
        "total_estimated_hours": 340,
        "average_workload_per_member": 42.5,
        "total_projects": 5,
        "members_count": 8,
        "high_workload_members": 3,
        "available_members": 2
      },
      "scheduling_insights": [
        "3 members are overloaded and may need task redistribution",
        "2 members have capacity for additional tasks",
        "1 projects have only one assigned member (risk of bottlenecks)"
      ]
    }
  }
}
```

### Workload Scoring System
- **0-40%**: Available (Green) - Can take on additional tasks
- **40-70%**: Moderate (Yellow) - Balanced workload
- **70-90%**: Busy (Orange) - Near capacity
- **90-100%**: Overloaded (Red) - Requires task redistribution

### Scheduling Conflict Detection
- **Multiple High-Priority Tasks**: Identifies when members have > 2 high-priority tasks
- **Overdue Tasks**: Flags members with overdue tasks affecting schedules
- **Timeline Conflicts**: Detects overlapping deadlines
- **Single-Member Projects**: Identifies bottleneck risks

### Project Distribution Analysis
- **Member Count per Project**: Shows project staffing levels
- **Task Distribution**: Workload balance across project members
- **Completion Rates**: Project progress by member contribution
- **Risk Assessment**: Identifies understaffed or over-dependent projects

## Date Filtering Examples

### Monthly Report
```
GET /reports/team/123?start_date=2024-10-01&end_date=2024-10-31&format=pdf
```

### Quarterly Analysis
```
GET /reports/department/456?start_date=2024-07-01&end_date=2024-09-30&format=excel
```

### Project-Specific Timeframe
```
GET /reports/personal/789?start_date=2024-09-15&end_date=2024-10-15&format=json
```

## Integration with Other Services

### Microservices Dependencies
- **Users Service** (Port 5003): User information and authentication
- **Tasks Service** (Port 5002): Task data and completion tracking
- **Projects Service** (Port 5001): Project information and assignments
- **Teams Service** (Port 5004): Team structure and member relationships
- **Department Service** (Port 5005): Department hierarchy and management
