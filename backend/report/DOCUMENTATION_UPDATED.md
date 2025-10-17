# Report Service Documentation

## Overview
The Report Service provides comprehensive reporting capabilities for Staff Performance Management (SPM) system, generating detailed reports for individuals, teams, and departments with advanced workload analysis and scheduling insights.

## Enhanced Features (Latest Update)

### 🎯 Date Range Filtering
- **Flexible Time Periods**: Generate reports for any custom date range
- **Query Parameters**: `start_date` and `end_date` (YYYY-MM-DD format)
- **Use Cases**: Monthly reports, quarterly reviews, project-specific timeframes

### 📊 Detailed Workload Analysis
- **Project Breakdown**: Shows which projects each member is working on
- **Task Distribution**: Tasks per project for each team member
- **Workload Scoring**: 0-100 capacity utilization scoring
- **Availability Status**: Available, Moderate, Busy, Overloaded classifications
- **Scheduling Conflicts**: Identifies potential conflicts and bottlenecks

### 💼 Comprehensive Member Insights
- **Role-based Analysis**: Workload distribution by team roles
- **Project Concentration**: Identifies single-member project risks
- **Timeline Conflicts**: Overlapping high-priority tasks detection
- **Capacity Planning**: Recommendations for task redistribution

## Report Types

### 1. Personal Reports
**Endpoint**: `GET /reports/personal/<user_id>`

**Query Parameters**:
- `format`: json (default), pdf, excel
- `save`: true/false (default: false)
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
- `save`: true/false (default: false)
- `start_date`: YYYY-MM-DD (optional)
- `end_date`: YYYY-MM-DD (optional)

**Enhanced Features**:
- **Manager Performance**: Manager's personal metrics
- **Team Overview**: Aggregated team statistics
- **Member Workload Analysis**: Detailed breakdown per team member including:
  - Projects each member is working on
  - Tasks per project for each member
  - Workload distribution and capacity utilization
  - Scheduling conflict identification
- **Project Distribution**: Shows project-member assignments and risks
- **Scheduling Insights**: Actionable recommendations for workload balancing

### 3. Department Reports
**Endpoint**: `GET /reports/department/<director_user_id>`

**Query Parameters**:
- `format`: json (default), pdf, excel
- `save`: true/false (default: false)
- `start_date`: YYYY-MM-DD (optional)
- `end_date`: YYYY-MM-DD (optional)

**Enhanced Features**:
- **Director Performance**: Director's personal metrics
- **Department Overview**: Department-wide statistics
- **Comprehensive Member Analysis**: Detailed workload breakdown for all department members
- **Cross-Team Project Analysis**: Project distribution across multiple teams
- **Department-wide Scheduling**: Identifies bottlenecks and capacity issues across teams

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

### PDF Export
- **Performance Dashboard**: Visual KPIs with status indicators
- **Member Workload Tables**: Detailed breakdown per member
- **Project Distribution Analysis**: Project-member assignment matrices
- **Comprehensive Task History**: Complete task tracking with timelines
- **Scheduling Recommendations**: Actionable insights for workload management

### Excel Export
- **📊 Dashboard**: Executive summary with key metrics
- **👥 Team Members**: Individual member performance sheets
- **⚠️ Action Items**: Critical tasks requiring immediate attention
- **🎯 Projects**: Project-level performance overview
- **📋 Complete Task History**: Comprehensive task tracking
- **💼 Workload Analysis**: Detailed capacity and scheduling analysis
- **📈 Project Distribution**: Member-project assignment breakdown

## Workload Analysis Details

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

### Database Integration
- **Supabase**: Report persistence and historical tracking
- **Service Key Authentication**: Secure cross-service communication
- **Date Filtering**: Efficient query optimization for time-based reports

## Performance Optimizations

### Efficient Data Retrieval
- **Parallel Service Calls**: Concurrent fetching from multiple microservices
- **Client-side Filtering**: Fallback filtering when services don't support date ranges
- **Caching Strategies**: Optimized for repeated report generation

### Export Performance
- **Streaming Excel Generation**: Memory-efficient large dataset handling
- **PDF Optimization**: Compressed output with visual indicators
- **Progressive Loading**: Background processing for large reports

## Error Handling

### Common Error Responses
- **400**: Invalid date format or parameters
- **403**: Insufficient permissions (non-managers accessing team reports)
- **404**: User, team, or department not found
- **500**: Service communication errors or data processing issues

### Troubleshooting
1. **Date Format**: Ensure YYYY-MM-DD format for date parameters
2. **Service Availability**: Verify all dependent microservices are running
3. **Database Connection**: Check Supabase connectivity and authentication
4. **Memory Issues**: For large reports, consider using streaming exports

## Best Practices

### Report Generation
- **Regular Scheduling**: Generate reports at consistent intervals
- **Date Range Selection**: Use appropriate timeframes for meaningful analysis
- **Format Selection**: Choose format based on intended use (JSON for APIs, PDF for presentations, Excel for analysis)

### Workload Management
- **Regular Review**: Monitor workload scores and availability status
- **Proactive Redistribution**: Address overloaded members before deadlines
- **Capacity Planning**: Use availability data for future task assignments
- **Project Staffing**: Ensure adequate member coverage for critical projects

## API Rate Limits and Considerations

### Performance Guidelines
- **Large Teams**: Reports for teams > 20 members may take longer to process
- **Extended Date Ranges**: Longer timeframes increase processing time
- **Export Formats**: PDF and Excel generation is more resource-intensive than JSON
- **Concurrent Requests**: Limit simultaneous report generation for optimal performance