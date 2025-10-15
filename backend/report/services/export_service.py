import os
import io
from typing import Dict, Any, List
from datetime import datetime
import pandas as pd
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

from models.report import ReportData, TeamReportData


class ExportService:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        
        # Custom styles
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=colors.darkblue,
            alignment=1  # Center alignment
        )
        
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.darkblue,
            spaceAfter=12
        )

    def export_personal_report_pdf(self, report_data: ReportData) -> bytes:
        """Export personal report as PDF organized by projects"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []

        # Title
        title = f"Personal Report - {report_data.user_name} ({report_data.user_role.capitalize()})"
        story.append(Paragraph(title, self.title_style))
        story.append(Spacer(1, 20))

        # Summary Overview
        story.append(Paragraph("Summary Overview", self.heading_style))
        
        summary_data = [
            ['Metric', 'Value'],
            ['Total Projects', str(report_data.total_projects)],
            ['Total Tasks', str(report_data.total_tasks)],
            ['Completed Tasks', str(report_data.completed_tasks)],
            ['Completion Rate', f"{report_data.completion_percentage:.1f}%"],
            ['Overdue Tasks', str(getattr(report_data, 'overdue_tasks', 0))],
            ['Average Task Duration', f"{report_data.average_task_duration:.1f} days" if report_data.average_task_duration else "N/A"]
        ]
        
        summary_table = Table(summary_data, colWidths=[2.5*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 20))

        # Projects and Tasks Details
        projects_breakdown = getattr(report_data, 'projects_breakdown', [])
        if projects_breakdown:
            story.append(Paragraph("Projects and Tasks Details", self.heading_style))
            
            for project in projects_breakdown:
                project_name = project.get('project_name', 'Unknown Project')
                
                # Project Header
                story.append(Paragraph(f"Project: {project_name}", self.styles['Heading2']))
                
                # Project Summary
                project_summary = [
                    ['Project Metric', 'Value'],
                    ['Total Tasks', str(project.get('total_tasks', 0))],
                    ['Completed Tasks', str(project.get('completed_tasks', 0))],
                    ['Completion Rate', f"{project.get('completion_percentage', 0):.1f}%"],
                    ['Overdue Tasks', str(project.get('overdue_tasks', 0))],
                    ['Average Duration', f"{project.get('average_task_duration', 0):.1f} days" if project.get('average_task_duration') else "N/A"],
                    ['Projected Completion', project.get('projected_completion_date', 'N/A')]
                ]
                
                project_table = Table(project_summary, colWidths=[2*inch, 2.5*inch])
                project_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(project_table)
                story.append(Spacer(1, 15))
                
                # Tasks in this project
                task_details = project.get('task_details', [])
                if task_details:
                    story.append(Paragraph(f"Tasks in {project_name} ({len(task_details)} tasks)", self.styles['Heading3']))
                    
                    task_data = [['Task Name', 'Status', 'Owner', 'Collaborators', 'Due Date', 'Duration', 'Notes']]
                    
                    for task in task_details:
                        # Get task information
                        task_name = task.get('task_name', 'Unknown')
                        status = task.get('status', 'Unknown')
                        owner = task.get('owner_name', 'Unknown')
                        collaborators = ", ".join(task.get('collaborators', [])) if task.get('collaborators') else "None"
                        due_date = task.get('due_date', '')[:10] if task.get('due_date') else 'N/A'
                        
                        # Duration and status notes
                        completion_days = task.get('completion_days')
                        duration_text = f"{completion_days}d" if completion_days else "Ongoing"
                        
                        notes = []
                        if task.get('is_overdue'):
                            notes.append(f"Overdue {task.get('days_overdue', 0)}d")
                        if task.get('was_completed_late'):
                            notes.append("Late completion")
                        if task.get('priority') == 'High':
                            notes.append("High priority")
                        
                        notes_text = "; ".join(notes) if notes else "On track"
                        
                        task_data.append([
                            task_name,
                            status,
                            owner,
                            collaborators,
                            due_date,
                            duration_text,
                            notes_text
                        ])
                    
                    task_table = Table(task_data, colWidths=[1.5*inch, 0.8*inch, 0.8*inch, 1.2*inch, 0.8*inch, 0.6*inch, 1.3*inch])
                    task_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.darkgrey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 8),
                        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                        ('FONTSIZE', (0, 1), (-1, -1), 7),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP')
                    ]))
                    story.append(task_table)
                    story.append(Spacer(1, 20))

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

        # Project Focus & Critical Tasks - Comprehensive Information
        if report_data.project_stats:
            story.append(Paragraph("Project Portfolio & Task Distribution", self.heading_style))
            
            # Show all projects, not just top 3
            for project in report_data.project_stats:
                project_name = project.get('project_name', 'Unknown Project')
                project_status = "On Track" if project['completion_percentage'] >= 70 and project.get('overdue_percentage', 0) < 20 else \
                                "At Risk" if project.get('overdue_percentage', 0) < 40 else "Critical"
                
                story.append(Paragraph(f"{project_name} | Status: {project_status}", self.styles['Heading3']))
                
                # Comprehensive project information
                project_summary = [
                    ['Tasks Progress', f"{project['completed_tasks']}/{project['total_tasks']} tasks completed ({project['completion_percentage']:.0f}%)"],
                    ['Task Status Distribution', f"In Progress: {project.get('in_progress_tasks', 0)}, Under Review: {project.get('under_review_tasks', 0)}"],
                    ['Overdue Tasks', f"{project.get('overdue_tasks', 0)} tasks" + (f" ({project.get('overdue_percentage', 0):.0f}%)" if project.get('overdue_tasks', 0) > 0 else " (None)")],
                    ['Late Completions', f"{project.get('late_completions', 0)} tasks"],
                    ['On-Time Completion Rate', f"{project.get('on_time_completion_rate', 0):.1f}%"],
                ]
                
                if project.get('average_task_duration'):
                    project_summary.append(['Average Task Duration', f"{project['average_task_duration']:.1f} days"])
                
                if project.get('projected_completion_date') and project['projected_completion_date'] != 'Completed':
                    project_summary.append(['Estimated Completion', project['projected_completion_date'][:10]])
                elif project['projected_completion_date'] == 'Completed':
                    project_summary.append(['Status', 'Project Completed'])
                
                # Show team members working on this project
                task_assignees = project.get('task_assignees', {})
                if task_assignees:
                    assignee_names = []
                    for assignee_info in task_assignees.values():
                        name = assignee_info.get('owner_name', 'Unknown')
                        task_count = len(assignee_info.get('tasks', []))
                        assignee_names.append(f"{name} ({task_count} tasks)")
                    
                    if len(assignee_names) <= 3:
                        assignees_text = ", ".join(assignee_names)
                    else:
                        assignees_text = ", ".join(assignee_names[:3]) + f" and {len(assignee_names) - 3} others"
                    
                    project_summary.append(['Team Members', assignees_text])
                
                proj_table = Table(project_summary, colWidths=[1.8*inch, 4.2*inch])
                proj_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, -1), colors.lightcyan),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP')
                ]))
                story.append(proj_table)
                story.append(Spacer(1, 12))
        
        # Critical Tasks & Action Items - Complete list with full information
        task_details = getattr(report_data, 'task_details', [])
        critical_tasks = [task for task in task_details if 
                         task.get('is_overdue') or 
                         task.get('priority') == 'High' or 
                         task.get('status') in ['Under Review']]
        
        if critical_tasks:
            story.append(Paragraph("Action Required - All Critical Tasks", self.heading_style))
            
            action_data = [['Task Name', 'Project', 'Priority', 'Status', 'Due Date', 'Action Needed']]
            
            # Show ALL critical tasks, not limited to 8
            for task in critical_tasks:
                action_needed = "OVERDUE!" if task.get('is_overdue') else \
                               "Review Required" if task.get('status') == 'Under Review' else \
                               "High Priority" if task.get('priority') == 'High' else ""
                               
                due_date = task.get('due_date', '')[:10] if task.get('due_date') else 'N/A'
                task_name = task.get('task_name', 'Unknown')
                project_name = task.get('project_name', 'No Project')
                
                action_data.append([
                    task_name,  # Don't truncate task names
                    project_name,
                    task.get('priority', 'Normal'),
                    task.get('status', 'Unknown'),
                    due_date,
                    action_needed
                ])
            
            # Adjust table column widths to prevent truncation
            action_table = Table(action_data, colWidths=[2.2*inch, 1.3*inch, 0.7*inch, 0.8*inch, 0.7*inch, 1.0*inch])
            action_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.red),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'TOP')
            ]))
            story.append(action_table)
            story.append(Spacer(1, 20))

        # Comprehensive Task Details - Complete Information with No Truncation
        task_details = getattr(report_data, 'task_details', [])
        if task_details:
            story.append(Paragraph("Complete Task Portfolio & Performance Analysis", self.heading_style))
            
            # Group tasks by status for organized viewing
            task_groups = {}
            for task in task_details:
                status = task.get('status', 'Unknown')
                if status not in task_groups:
                    task_groups[status] = []
                task_groups[status].append(task)
            
            # Display each status group with complete information
            for status, tasks in task_groups.items():
                if tasks:
                    story.append(Paragraph(f"{status} Tasks ({len(tasks)})", self.styles['Heading3']))
                    
                    # Comprehensive task table with all relevant details - no truncation
                    task_detail_data = [['Task Name', 'Project', 'Owner', 'Collaborators', 'Duration', 'Due Date', 'Completed', 'Status Notes']]
                    
                    for task in tasks:
                        # Get full task name - no truncation
                        task_name = task.get('task_name', 'Unknown')
                        
                        # Get project name
                        project_name = task.get('project_name', 'No Project')
                        
                        # Get owner name
                        owner_name = task.get('owner_name', 'Unknown')
                        
                        # Get all collaborators (full list as requested)
                        collaborators = task.get('collaborators', [])
                        collaborators_text = "None"
                        if collaborators:
                            collaborators_text = ", ".join(collaborators)
                        
                        # Get completion duration
                        completion_days = task.get('completion_days')
                        duration_text = f"{completion_days} days" if completion_days else "In Progress"
                        
                        # Get due date
                        due_date = task.get('due_date', '')[:10] if task.get('due_date') else 'N/A'
                        
                        # Get completion date
                        completed_date = task.get('completed_at', '')[:10] if task.get('completed_at') else 'N/A'
                        
                        # Status notes
                        status_notes = []
                        if task.get('is_overdue'):
                            days_overdue = task.get('days_overdue', 0)
                            status_notes.append(f"Overdue by {days_overdue} days")
                        if task.get('was_completed_late'):
                            status_notes.append("Completed late")
                        if task.get('priority') == 'High':
                            status_notes.append("High priority")
                        
                        status_notes_text = "; ".join(status_notes) if status_notes else "On track"
                        
                        task_detail_data.append([
                            task_name,
                            project_name,
                            owner_name,
                            collaborators_text,
                            duration_text,
                            due_date,
                            completed_date,
                            status_notes_text
                        ])
                    
                    # Use wider table with proper column widths to prevent truncation
                    task_table = Table(task_detail_data, colWidths=[1.5*inch, 1.0*inch, 0.8*inch, 1.2*inch, 0.7*inch, 0.8*inch, 0.8*inch, 1.2*inch])
                    task_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 8),
                        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                        ('FONTSIZE', (0, 1), (-1, -1), 7),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP')
                    ]))
                    story.append(task_table)
                    story.append(Spacer(1, 15))

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    def _generate_member_personal_report_content(self, member_report):
        """Generate personal report content for a team member"""
        elements = []
        
        # Member header
        member_title = Paragraph(f"{member_report.user_name}", 
                               ParagraphStyle('MemberTitle', 
                                            parent=getSampleStyleSheet()['Heading2'],
                                            fontSize=16,
                                            textColor=colors.darkblue,
                                            spaceAfter=15))
        elements.append(member_title)
        
        # Member overview
        member_overview = [
            ['Name', member_report.user_name],
            ['Role', member_report.user_role or 'N/A'],
            ['Total Projects', str(member_report.total_projects)],
            ['Total Tasks', str(member_report.total_tasks)],
            ['Completed Tasks', str(member_report.completed_tasks)],
            ['In Progress Tasks', str(getattr(member_report, 'in_progress_tasks', member_report.total_tasks - member_report.completed_tasks))],
            ['Overdue Tasks', str(member_report.overdue_tasks)],
            ['Completion %', f"{member_report.completion_percentage:.1f}%"]
        ]
        
        # Add team information if available (for department reports)
        if hasattr(member_report, 'team_id') and member_report.team_id:
            team_display = f"Team {member_report.team_id}"
            if hasattr(member_report, 'team_name') and member_report.team_name:
                team_display = f"{member_report.team_name} (ID: {member_report.team_id})"
            member_overview.insert(2, ['Team', team_display])
        
        overview_table = Table(member_overview, colWidths=[2*inch, 3*inch])
        overview_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(overview_table)
        elements.append(Spacer(1, 20))
        
        # Projects Section
        if hasattr(member_report, 'projects_breakdown') and member_report.projects_breakdown:
            projects_title = Paragraph("Projects & Tasks", 
                                     ParagraphStyle('ProjectsTitle',
                                                  parent=getSampleStyleSheet()['Heading3'],
                                                  fontSize=14,
                                                  textColor=colors.darkgreen))
            elements.append(projects_title)
            elements.append(Spacer(1, 10))
            
            for project in member_report.projects_breakdown:
                # Project header
                project_header = Paragraph(f"Project: {project.get('project_name', 'Unknown Project')}", 
                                         ParagraphStyle('ProjectHeader',
                                                      parent=getSampleStyleSheet()['Heading4'],
                                                      fontSize=12,
                                                      textColor=colors.darkred))
                elements.append(project_header)
                elements.append(Spacer(1, 8))
                
                # Project summary
                project_summary = [
                    ['Total Tasks', str(project.get('total_tasks', 0))],
                    ['Completed', str(project.get('completed_tasks', 0))],
                    ['In Progress', str(project.get('in_progress_tasks', 0))],
                    ['Overdue', str(project.get('overdue_tasks', 0))],
                    ['Completion %', f"{project.get('completion_percentage', 0):.1f}%"],
                    ['Projected Completion', project.get('projected_completion_date', 'N/A')]
                ]
                
                project_table = Table(project_summary, colWidths=[1.5*inch, 2*inch])
                project_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, -1), colors.lightgreen),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                elements.append(project_table)
                elements.append(Spacer(1, 10))
                
                # Tasks in project
                project_tasks = project.get('task_details', [])  # Changed from 'tasks' to 'task_details'
                if project_tasks:
                    task_header = Paragraph("Tasks in Project", 
                                          ParagraphStyle('TaskHeader',
                                                       parent=getSampleStyleSheet()['Heading5'],
                                                       fontSize=10))
                    elements.append(task_header)
                    elements.append(Spacer(1, 5))
                    
                    # Task table headers
                    task_data = [['Task Name', 'Status', 'Priority', 'Owner', 'Collaborators', 'Due Date', 'Duration (days)']]
                    
                    for task in project_tasks:
                        # Get collaborators list
                        collaborators = task.get('collaborators', [])
                        collab_names = []
                        if collaborators:
                            for collab in collaborators:
                                if isinstance(collab, dict):
                                    collab_names.append(collab.get('name', 'Unknown'))
                                else:
                                    collab_names.append(str(collab))
                        collab_str = ', '.join(collab_names) if collab_names else 'None'
                        
                        task_data.append([
                            task.get('task_name', 'Unknown')[:30] + "..." if len(task.get('task_name', '')) > 30 else task.get('task_name', 'Unknown'),
                            task.get('status', 'Unknown'),
                            task.get('priority', 'Normal'),
                            task.get('owner_name', 'Unknown'),
                            collab_str[:20] + "..." if len(collab_str) > 20 else collab_str,
                            task.get('due_date', 'N/A')[:10] if task.get('due_date') else 'N/A',
                            str(task.get('duration_days', 'N/A'))
                        ])
                    
                    task_table = Table(task_data, colWidths=[1.2*inch, 0.8*inch, 0.6*inch, 0.8*inch, 0.8*inch, 0.7*inch, 0.6*inch])
                    task_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.lightcoral),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                        ('FONTSIZE', (0, 0), (-1, -1), 7),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP')
                    ]))
                    elements.append(task_table)
                    elements.append(Spacer(1, 15))
        
        return elements

    def export_team_report_pdf(self, manager_report: ReportData = None, team_report: TeamReportData = None, detailed_workload: Dict[str, Any] = None) -> bytes:
        """Export team report as compilation of personal reports"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []

        # Title - differentiate between team and department reports
        if team_report.dept_name and not team_report.team_name:
            # This is a department report
            title = f"Department Report: {team_report.dept_name} (by Teams)"
            overview_title = "Department Overview (Team Breakdown)"
        else:
            # This is a team report
            title = f"Team Report: {team_report.team_name or team_report.dept_name}"
            overview_title = "Team Overview"
        
        story.append(Paragraph(title, self.title_style))
        story.append(Spacer(1, 20))

        # Team/Department Overview
        story.append(Paragraph(overview_title, self.heading_style))
        
        team_overview = [
            ['Team/Department', team_report.team_name or team_report.dept_name or 'Unknown'],
            ['Team Size', str(len(team_report.member_reports))],
            ['Total Projects', str(team_report.total_team_projects)],
            ['Total Tasks', str(team_report.total_team_tasks)],
            ['Team Completion Rate', f"{team_report.team_completion_percentage:.1f}%"],
            ['Team Overdue Rate', f"{getattr(team_report, 'team_overdue_percentage', 0):.1f}%"],
            ['Avg Task Duration', f"{team_report.team_average_task_duration:.1f} days" if team_report.team_average_task_duration else "N/A"]
        ]
        
        overview_table = Table(team_overview, colWidths=[2.5*inch, 2*inch])
        overview_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(overview_table)
        story.append(Spacer(1, 30))
        
        # Member Personal Reports Section
        if team_report.dept_name and not team_report.team_name:
            # This is a department report
            member_section_title = "Member Personal Reports (Organized by Teams)"
        else:
            # This is a team report
            member_section_title = "Member Personal Reports"
            
        member_title = Paragraph(member_section_title, 
                                ParagraphStyle('MemberTitle', 
                                             parent=getSampleStyleSheet()['Heading1'],
                                             fontSize=14,
                                             textColor=colors.darkgreen))
        story.append(member_title)
        story.append(Spacer(1, 15))
        
        # Generate personal report for each member
        for i, member_report in enumerate(team_report.member_reports):
            if i > 0:
                story.append(PageBreak())  # New page for each member
            
            # Add member's personal report content
            member_elements = self._generate_member_personal_report_content(member_report)
            story.extend(member_elements)

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    def export_personal_report_excel(self, report_data: ReportData) -> bytes:
        """Export concise personal report as Excel with focused dashboards"""
        buffer = io.BytesIO()
        
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            # Performance Dashboard Sheet
            performance_data = []
            
            # KPI Section
            performance_data.extend([
                ['PERFORMANCE DASHBOARD', ''],
                ['Name', report_data.user_name],
                ['Role', report_data.user_role.capitalize() if report_data.user_role else 'Unknown'],
                ['', ''],
                ['KEY METRICS', ''],
                ['Task Completion Rate', f"{report_data.completion_percentage:.1f}%"],
                ['Tasks Completed', f"{report_data.completed_tasks}/{report_data.total_tasks}"],
                ['Overdue Tasks', f"{getattr(report_data, 'overdue_tasks', 0)} ({getattr(report_data, 'overdue_percentage', 0):.1f}%)"],
                ['Active Projects', str(report_data.total_projects)],
                ['Avg Task Duration', f"{report_data.average_task_duration:.1f} days" if report_data.average_task_duration else "N/A"],
                ['', ''],
                ['TASK STATUS BREAKDOWN', '']
            ])
            
            # Task status breakdown
            for status, count in report_data.task_stats.items():
                performance_data.append([f"{status} Tasks", str(count)])
            
            # Performance indicators
            performance_data.extend([
                ['', ''],
                ['PERFORMANCE INDICATORS', ''],
                ['Overall Status', 
                 '🟢 Excellent' if report_data.completion_percentage >= 80 and getattr(report_data, 'overdue_percentage', 0) < 15 else
                 '🟡 Good' if report_data.completion_percentage >= 60 else '🔴 Needs Improvement'],
                ['Efficiency Rating',
                 '🟢 High' if report_data.average_task_duration and report_data.average_task_duration <= 5 else
                 '🟡 Medium' if report_data.average_task_duration and report_data.average_task_duration <= 10 else '🔴 Low']
            ])
            
            dashboard_df = pd.DataFrame(performance_data, columns=['Metric', 'Value'])
            dashboard_df.to_excel(writer, sheet_name='Dashboard', index=False)

            # Project Focus Sheet (Consolidated project info)
            if report_data.project_stats:
                project_focus_data = []
                for project in report_data.project_stats:
                    project_focus_data.append({
                        'Project': project['project_name'],
                        'Progress': f"{project['completed_tasks']}/{project['total_tasks']} ({project['completion_percentage']:.1f}%)",
                        'Overdue': f"{project.get('overdue_tasks', 0)} ({project.get('overdue_percentage', 0):.1f}%)",
                        'In Progress': project.get('in_progress_tasks', 0),
                        'Under Review': project.get('under_review_tasks', 0),
                        'Avg Duration': f"{project['average_task_duration']:.1f} days" if project['average_task_duration'] else "N/A",
                        'Est. Completion': project['projected_completion_date'] if project['projected_completion_date'] else "N/A",
                        'Status': '🟢 On Track' if project['completion_percentage'] >= 70 and project.get('overdue_percentage', 0) < 20 else
                                '🟡 At Risk' if project.get('overdue_percentage', 0) < 40 else '🔴 Critical'
                    })
                
                project_focus_df = pd.DataFrame(project_focus_data)
                project_focus_df.to_excel(writer, sheet_name='Projects', index=False)

            # ⚠️ Action Items Sheet (Critical tasks only)
            task_details = getattr(report_data, 'task_details', [])
            critical_tasks = [task for task in task_details if 
                             task.get('is_overdue') or 
                             task.get('priority') == 'High' or 
                             task.get('status') in ['Under Review']]
            
            if critical_tasks:
                action_items_data = []
                for task in critical_tasks:
                    action_items_data.append({
                        'Task Name': task.get('task_name'),
                        'Priority': task.get('priority'),
                        'Status': task.get('status'),
                        'Owner': task.get('owner_name', 'Unknown'),
                        'Collaborators': ", ".join(task.get('collaborators', [])) if task.get('collaborators') else "None",
                        'Due Date': task.get('due_date', '')[:10] if task.get('due_date') else '',
                        'Days Overdue': task.get('days_overdue', 0) if task.get('is_overdue') else 0,
                        'Action Required': 'OVERDUE!' if task.get('is_overdue') else 
                                          'Review Required' if task.get('status') == 'Under Review' else 
                                          'High Priority'
                    })
                
                action_items_df = pd.DataFrame(action_items_data)
                action_items_df.to_excel(writer, sheet_name='⚠️ Action Items', index=False)
            
            # Complete Task History Sheet (Who did what, when, how long)
            if task_details:
                comprehensive_task_data = []
                for task in task_details:
                    # Get completion duration
                    completion_days = task.get('completion_days')
                    duration_text = f"{completion_days} days" if completion_days else "In Progress"
                    
                    # Get overdue status with details
                    overdue_status = "No"
                    overdue_details = ""
                    if task.get('is_overdue'):
                        days_overdue = task.get('days_overdue', 0)
                        overdue_status = "Yes"
                        overdue_details = f"{days_overdue} days overdue"
                    elif task.get('status') == 'Completed':
                        was_late = task.get('was_completed_late')
                        overdue_status = "Completed Late" if was_late else "On Time"
                        overdue_details = "Completed after due date" if was_late else "Completed on time"
                    else:
                        overdue_details = "On track"
                    
                    comprehensive_task_data.append({
                        'Task Name': task.get('task_name'),
                        'Status': task.get('status'),
                        'Priority': task.get('priority'),
                        'Task Owner': task.get('owner_name', 'Unknown'),
                        'All Collaborators': ", ".join(task.get('collaborators', [])) if task.get('collaborators') else "None",
                        'Created Date': task.get('created_at', '')[:10] if task.get('created_at') else '',
                        'Due Date': task.get('due_date', '')[:10] if task.get('due_date') else '',
                        'Completed Date': task.get('completed_at', '')[:10] if task.get('completed_at') else '',
                        'Duration (Days)': duration_text,
                        'Is Overdue': overdue_status,
                        'Overdue Details': overdue_details,
                        'Days Overdue': task.get('days_overdue', 0) if task.get('is_overdue') else 0
                    })
                
                comprehensive_df = pd.DataFrame(comprehensive_task_data)
                comprehensive_df.to_excel(writer, sheet_name='Complete Task History', index=False)

        buffer.seek(0)
        return buffer.getvalue()

    def export_team_report_excel(self, manager_report: ReportData = None, team_report: TeamReportData = None, detailed_workload: Dict[str, Any] = None) -> bytes:
        """Export concise team performance dashboard as Excel"""
        buffer = io.BytesIO()
        
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            # Team Dashboard Sheet
            dashboard_data = []
            
            # Team Overview Section
            dashboard_data.extend([
                ['TEAM PERFORMANCE DASHBOARD', ''],
                ['Team/Department', team_report.team_name or team_report.dept_name],
                ['Team Size', len(team_report.member_reports)],
                ['', ''],
                ['TEAM METRICS', ''],
                ['Total Tasks', team_report.total_team_tasks],
                ['Team Completion Rate', f"{team_report.team_completion_percentage:.1f}%"],
                ['Team Overdue Rate', f"{getattr(team_report, 'team_overdue_percentage', 0):.1f}%"],
                ['Active Projects', team_report.total_team_projects],
                ['Avg Task Duration', f"{team_report.team_average_task_duration:.1f} days" if team_report.team_average_task_duration else "N/A"],
                ['', ''],
                ['PERFORMANCE RATING', ''],
                ['Team Status', 
                 '🟢 High Performing' if team_report.team_completion_percentage >= 75 and getattr(team_report, 'team_overdue_percentage', 0) < 20 else
                 '🟡 Moderate Performance' if team_report.team_completion_percentage >= 50 else '🔴 Needs Improvement']
            ])
            
            # Task status breakdown
            team_task_stats = getattr(team_report, 'team_task_stats', {})
            if team_task_stats:
                dashboard_data.extend([['', ''], ['TASK STATUS BREAKDOWN', '']])
                for status, count in team_task_stats.items():
                    dashboard_data.append([f"{status} Tasks", count])
            
            dashboard_df = pd.DataFrame(dashboard_data, columns=['Metric', 'Value'])
            dashboard_df.to_excel(writer, sheet_name='Team Dashboard', index=False)

            # Team Members Performance Sheet
            member_performance_data = []
            for member in team_report.member_reports:
                performance_rating = "🟢 Excellent" if member.completion_percentage >= 80 and getattr(member, 'overdue_percentage', 0) < 15 else \
                                   "🟡 Good" if member.completion_percentage >= 60 else "🔴 Needs Support"
                
                member_performance_data.append({
                    'Member Name': member.user_name,
                    'Role': member.user_role.capitalize() if member.user_role else 'Unknown',
                    'Total Tasks': member.total_tasks,
                    'Completed': member.completed_tasks,
                    'Completion %': f"{member.completion_percentage:.1f}%",
                    'Overdue Tasks': getattr(member, 'overdue_tasks', 0),
                    'Overdue %': f"{getattr(member, 'overdue_percentage', 0):.1f}%",
                    'Active Projects': member.total_projects,
                    'Avg Duration': f"{member.average_task_duration:.1f} days" if member.average_task_duration else "N/A",
                    'Performance': performance_rating
                })
            
            member_performance_df = pd.DataFrame(member_performance_data)
            member_performance_df.to_excel(writer, sheet_name='Team Performance', index=False)

            # 🚨 Team Action Items Sheet (Critical tasks across team)
            team_critical_tasks = []
            for member in team_report.member_reports:
                member_task_details = getattr(member, 'task_details', [])
                for task in member_task_details:
                    if task.get('is_overdue') or task.get('priority') == 'High' or task.get('status') == 'Under Review':
                        action_needed = "OVERDUE!" if task.get('is_overdue') else \
                                       "Review Required" if task.get('status') == 'Under Review' else \
                                       "High Priority"
                        
                        team_critical_tasks.append({
                            'Member': member.user_name,
                            'Role': member.user_role.capitalize() if member.user_role else 'Unknown',
                            'Task Name': task.get('task_name'),
                            'Status': task.get('status'),
                            'Priority': task.get('priority'),
                            'Task Owner': task.get('owner_name', member.user_name),
                            'All Collaborators': ", ".join(task.get('collaborators', [])) if task.get('collaborators') else "None",
                            'Due Date': task.get('due_date', '')[:10] if task.get('due_date') else '',
                            'Days Overdue': task.get('days_overdue', 0) if task.get('is_overdue') else 0,
                            'Action Required': action_needed
                        })
            
            if team_critical_tasks:
                critical_df = pd.DataFrame(team_critical_tasks)
                critical_df.to_excel(writer, sheet_name='🚨 Action Items', index=False)

            # Project Overview Sheet - Comprehensive Project Information
            team_project_stats = getattr(team_report, 'team_project_stats', [])
            if team_project_stats:
                project_overview_data = []
                for project in team_project_stats:
                    project_status = "On Track" if project['completion_percentage'] >= 70 and project.get('overdue_percentage', 0) < 20 else \
                                   "At Risk" if project.get('overdue_percentage', 0) < 40 else "Critical"
                    
                    # Get team members working on this project
                    task_assignees = project.get('task_assignees', {})
                    team_members = []
                    for assignee_info in task_assignees.values():
                        name = assignee_info.get('owner_name', 'Unknown')
                        task_count = len(assignee_info.get('tasks', []))
                        team_members.append(f"{name} ({task_count} tasks)")
                    team_members_text = ", ".join(team_members) if team_members else "No assignments"
                    
                    project_overview_data.append({
                        'Project Name': project['project_name'],
                        'Status': project_status,
                        'Total Tasks': project['total_tasks'],
                        'Completed Tasks': project['completed_tasks'],
                        'Completion Percentage': f"{project['completion_percentage']:.1f}%",
                        'Overdue Tasks': project.get('overdue_tasks', 0),
                        'Overdue Percentage': f"{project.get('overdue_percentage', 0):.1f}%",
                        'In Progress Tasks': project.get('in_progress_tasks', 0),
                        'Under Review Tasks': project.get('under_review_tasks', 0),
                        'Late Completions': project.get('late_completions', 0),
                        'On-Time Completion Rate': f"{project.get('on_time_completion_rate', 0):.1f}%",
                        'Average Task Duration': f"{project['average_task_duration']:.1f} days" if project['average_task_duration'] else "N/A",
                        'Projected Completion': project['projected_completion_date'] if project['projected_completion_date'] else "N/A",
                        'Assigned Team Members': team_members_text
                    })
                
                project_overview_df = pd.DataFrame(project_overview_data)
                project_overview_df.to_excel(writer, sheet_name='Projects Overview', index=False)

            # Comprehensive Team Task History Sheet (Who did what, when, how long)
            team_task_history = []
            team_members = getattr(team_report, 'team_members', [])
            for member in team_members:
                member_tasks = getattr(member, 'task_details', [])
                for task in member_tasks:
                    # Get completion duration
                    completion_days = task.get('completion_days')
                    duration_text = f"{completion_days} days" if completion_days else "In Progress"
                    
                    # Get overdue status with details
                    overdue_status = "No"
                    overdue_details = ""
                    if task.get('is_overdue'):
                        days_overdue = task.get('days_overdue', 0)
                        overdue_status = "Yes"
                        overdue_details = f"{days_overdue} days overdue"
                    elif task.get('status') == 'Completed':
                        was_late = task.get('was_completed_late')
                        overdue_status = "Completed Late" if was_late else "On Time"
                        overdue_details = "Completed after due date" if was_late else "Completed on time"
                    else:
                        overdue_details = "On track"
                    
                    team_task_history.append({
                        'Team Member': member.user_name,
                        'Member Role': member.user_role.capitalize() if member.user_role else 'Unknown',
                        'Task Name': task.get('task_name'),
                        'Project Name': task.get('project_name', 'No Project'),
                        'Status': task.get('status'),
                        'Priority': task.get('priority'),
                        'Task Owner': task.get('owner_name', 'Unknown'),
                        'All Collaborators': ", ".join(task.get('collaborators', [])) if task.get('collaborators') else "None",
                        'Created Date': task.get('created_at', '')[:10] if task.get('created_at') else '',
                        'Due Date': task.get('due_date', '')[:10] if task.get('due_date') else '',
                        'Completed Date': task.get('completed_at', '')[:10] if task.get('completed_at') else '',
                        'Duration (Days)': duration_text,
                        'Is Overdue': overdue_status,
                        'Overdue Details': overdue_details,
                        'Days Overdue': task.get('days_overdue', 0) if task.get('is_overdue') else 0
                    })
            
            if team_task_history:
                comprehensive_team_df = pd.DataFrame(team_task_history)
                comprehensive_team_df.to_excel(writer, sheet_name='Complete Team Task History', index=False)

            # Detailed Workload Analysis Sheets
            if detailed_workload:
                # Workload Summary Sheet
                workload_summary = detailed_workload.get('workload_summary', {})
                if workload_summary:
                    summary_data = []
                    summary_data.append(['TEAM WORKLOAD SUMMARY', ''])
                    summary_data.append(['Total Estimated Hours', f"{workload_summary.get('total_estimated_hours', 0)} hours"])
                    summary_data.append(['Average per Member', f"{workload_summary.get('average_workload_per_member', 0)} hours"])
                    summary_data.append(['Total Projects', str(workload_summary.get('total_projects', 0))])
                    summary_data.append(['Members Count', str(workload_summary.get('members_count', 0))])
                    summary_data.append(['High Workload Members', str(workload_summary.get('high_workload_members', 0))])
                    summary_data.append(['Available Members', str(workload_summary.get('available_members', 0))])
                    
                    summary_df = pd.DataFrame(summary_data, columns=['Metric', 'Value'])
                    summary_df.to_excel(writer, sheet_name='Workload Summary', index=False)
                
                # Individual Member Workload Sheet
                members_workload = detailed_workload.get('members_workload', [])
                if members_workload:
                    member_workload_data = []
                    for member in members_workload:
                        member_workload_data.append({
                            'Member Name': member.get('member_name'),
                            'Role': member.get('member_role'),
                            'Total Projects': member.get('total_projects', 0),
                            'Total Tasks': member.get('total_tasks', 0),
                            'Estimated Weekly Hours': member.get('estimated_weekly_hours', 0),
                            'Workload Score (%)': member.get('workload_score', 0),
                            'Availability Status': member.get('availability_status'),
                            'Scheduling Conflicts': "; ".join(member.get('scheduling_conflicts', []))
                        })
                    
                    member_workload_df = pd.DataFrame(member_workload_data)
                    member_workload_df.to_excel(writer, sheet_name='Member Workload', index=False)
                
                # Project Distribution Sheet
                project_distribution = detailed_workload.get('project_distribution', {})
                if project_distribution:
                    project_dist_data = []
                    for project_id, project_info in project_distribution.items():
                        project_members = project_info.get('members', [])
                        for member_info in project_members:
                            project_dist_data.append({
                                'Project ID': project_id,
                                'Project Name': project_info.get('project_name'),
                                'Member Name': member_info.get('member_name'),
                                'Member Role': member_info.get('member_role'),
                                'Tasks Count': member_info.get('tasks_count', 0),
                                'Completion Rate (%)': f"{member_info.get('completion_rate', 0):.1f}",
                                'Estimated Hours': member_info.get('estimated_hours', 0)
                            })
                    
                    if project_dist_data:
                        project_dist_df = pd.DataFrame(project_dist_data)
                        project_dist_df.to_excel(writer, sheet_name='Project Distribution', index=False)

            # Member Project Breakdown Sheets
            for member in team_report.member_reports:
                projects_breakdown = getattr(member, 'projects_breakdown', [])
                if projects_breakdown:
                    member_project_data = []
                    for project in projects_breakdown:
                        member_project_data.append({
                            'Project Name': project.get('project_name', 'Unknown Project'),
                            'Total Tasks': project.get('total_tasks', 0),
                            'Completed Tasks': project.get('completed_tasks', 0),
                            'In Progress': project.get('in_progress_tasks', 0),
                            'Overdue Tasks': project.get('overdue_tasks', 0),
                            'High Priority': project.get('high_priority_tasks', 0),
                            'Completion %': f"{project.get('completion_percentage', 0):.1f}%"
                        })
                    
                    if member_project_data:
                        member_projects_df = pd.DataFrame(member_project_data)
                        sheet_name = f"📁 {member.user_name[:20]} Projects"  # Limit sheet name length
                        member_projects_df.to_excel(writer, sheet_name=sheet_name, index=False)
                
                # Member Task Details Sheet
                task_details = getattr(member, 'task_details', [])
                if task_details:
                    member_task_data = []
                    for task in task_details:
                        member_task_data.append({
                            'Task Name': task.get('task_name'),
                            'Project': task.get('project_name', 'Unknown Project'),
                            'Status': task.get('status'),
                            'Priority': task.get('priority'),
                            'Owner': task.get('owner_name'),
                            'Collaborators': ", ".join(task.get('collaborators', [])) if task.get('collaborators') else "None",
                            'Created Date': task.get('created_at', '')[:10] if task.get('created_at') else '',
                            'Due Date': task.get('due_date', '')[:10] if task.get('due_date') else '',
                            'Completed Date': task.get('completed_at', '')[:10] if task.get('completed_at') else '',
                            'Duration (Days)': f"{task.get('completion_days')} days" if task.get('completion_days') else "In Progress",
                            'Is Overdue': 'Yes' if task.get('is_overdue') else 'No',
                            'Days Overdue': task.get('days_overdue', 0) if task.get('is_overdue') else 0
                        })
                    
                    if member_task_data:
                        member_tasks_df = pd.DataFrame(member_task_data)
                        sheet_name = f"{member.user_name[:20]} Tasks"  # Limit sheet name length
                        member_tasks_df.to_excel(writer, sheet_name=sheet_name, index=False)

        buffer.seek(0)
        return buffer.getvalue()