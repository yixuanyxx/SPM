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
from openpyxl.styles import PatternFill

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
                    ['Task Status Distribution', f"Ongoing: {project.get('in_progress_tasks', 0)}, Under Review: {project.get('under_review_tasks', 0)}"],
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
                        duration_text = f"{completion_days} days" if completion_days else "Ongoing"
                        
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
            ['Ongoing Tasks', str(getattr(member_report, 'in_progress_tasks', member_report.total_tasks - member_report.completed_tasks))],
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
                    ['Ongoing', str(project.get('in_progress_tasks', 0))],
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
                    highlighted_rows = []  # Track which rows need highlighting
                    
                    for i, task in enumerate(project_tasks):
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
                        
                        # Check if this member is owner or collaborator
                        is_member_task = False
                        member_name = member_report.user_name
                        
                        # Check if member is owner
                        if task.get('owner_name') == member_name:
                            is_member_task = True
                        
                        # Check if member is collaborator
                        if not is_member_task and collaborators:
                            for collab in collaborators:
                                if isinstance(collab, dict):
                                    if collab.get('name') == member_name:
                                        is_member_task = True
                                        break
                                elif str(collab) == member_name:
                                    is_member_task = True
                                    break
                        
                        # Add highlight indicator for member tasks
                        task_name = task.get('task_name', 'Unknown')[:30] + "..." if len(task.get('task_name', '')) > 30 else task.get('task_name', 'Unknown')
                        if is_member_task:
                            task_name = "★ " + task_name  # Add star to highlight member tasks
                            highlighted_rows.append(i + 1)  # +1 because row 0 is header
                        
                        task_data.append([
                            task_name,
                            task.get('status', 'Unknown'),
                            task.get('priority', 'Normal'),
                            task.get('owner_name', 'Unknown'),
                            collab_str[:20] + "..." if len(collab_str) > 20 else collab_str,
                            task.get('due_date', 'N/A')[:10] if task.get('due_date') else 'N/A',
                            str(task.get('duration_days', 'N/A'))
                        ])
                    
                    task_table = Table(task_data, colWidths=[1.2*inch, 0.8*inch, 0.6*inch, 0.8*inch, 0.8*inch, 0.7*inch, 0.6*inch])
                    
                    # Base table style
                    table_style = [
                        ('BACKGROUND', (0, 0), (-1, 0), colors.lightcoral),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                        ('FONTSIZE', (0, 0), (-1, -1), 7),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP')
                    ]
                    
                    # Highlight member task rows
                    for row_idx in highlighted_rows:
                        table_style.append(('BACKGROUND', (0, row_idx), (-1, row_idx), colors.lightblue))
                        table_style.append(('TEXTCOLOR', (0, row_idx), (-1, row_idx), colors.darkblue))
                    
                    task_table.setStyle(TableStyle(table_style))
                    elements.append(task_table)
                    
                    # Add legend for task highlighting
                    if highlighted_rows:
                        legend = Paragraph("★ = Tasks where this member is owner or collaborator", 
                                         ParagraphStyle('Legend',
                                                      parent=getSampleStyleSheet()['Normal'],
                                                      fontSize=8,
                                                      textColor=colors.darkblue,
                                                      leftIndent=10))
                        elements.append(Spacer(1, 5))
                        elements.append(legend)
                    
                    elements.append(Spacer(1, 15))
        
        return elements

    def export_team_report_pdf(self, manager_report: ReportData = None, team_report: TeamReportData = None, detailed_workload: Dict[str, Any] = None) -> bytes:
        """Export team report with overview section and detailed member sections showing all project tasks with highlighting"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []

        # ========== SECTION 1: OVERVIEW ==========
        # Title - differentiate between team and department reports
        if team_report.dept_name and not team_report.team_name:
            title = f"Department Report: {team_report.dept_name}"
            overview_title = "Department Overview"
        else:
            title = f"Team Report: {team_report.team_name or team_report.dept_name}"
            overview_title = "Team Overview"
        
        story.append(Paragraph(title, self.title_style))
        story.append(Spacer(1, 20))

        # Team/Department Overview
        story.append(Paragraph(overview_title, self.heading_style))
        
        # Determine the label for team/department row
        entity_label = 'Department' if (team_report.dept_name and not team_report.team_name) else 'Team'
        entity_value = team_report.dept_name if (team_report.dept_name and not team_report.team_name) else (team_report.team_name or 'Unknown')
        size_label = 'Department Size' if (team_report.dept_name and not team_report.team_name) else 'Team Size'
        
        team_overview = [
            ['Metric', 'Value'],
            [entity_label, entity_value],
            [size_label, str(len(team_report.member_reports))],
            ['Total Projects', str(team_report.total_team_projects)],
            ['Total Tasks', str(team_report.total_team_tasks)],
            ['Team Completion Rate', f"{team_report.team_completion_percentage:.1f}%"],
            ['Team Overdue Rate', f"{getattr(team_report, 'team_overdue_percentage', 0):.1f}%"],
            ['Avg Task Duration', f"{team_report.team_average_task_duration:.1f} days" if team_report.team_average_task_duration else "N/A"]
        ]
        
        overview_table = Table(team_overview, colWidths=[2.5*inch, 2.5*inch])
        overview_table.setStyle(TableStyle([
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
        story.append(overview_table)
        story.append(Spacer(1, 30))
        
        # ========== MEMBER SECTIONS (One per member, grouped by team for departments) ==========
        # Get enriched project stats from team report
        team_project_stats = getattr(team_report, 'team_project_stats', [])
        
        # For department reports, group members by team
        is_department_report = team_report.dept_name and not team_report.team_name
        
        if is_department_report:
            # Group members by team
            teams_dict = {}
            for member in team_report.member_reports:
                team_id = getattr(member, 'team_id', None)
                team_name = getattr(member, 'team_name', None)
                
                # Handle missing team info
                if not team_id:
                    team_id = 'no_team'
                    team_name = 'No Team Assigned'
                elif not team_name:
                    # If team_id exists but team_name is None, use fallback
                    team_name = f'Team {team_id}'
                
                if team_id not in teams_dict:
                    teams_dict[team_id] = {
                        'team_name': team_name,
                        'members': []
                    }
                teams_dict[team_id]['members'].append(member)
            
            # Process each team with its members
            for team_idx, (team_id, team_data) in enumerate(teams_dict.items()):
                if team_idx > 0:
                    story.append(PageBreak())
                
                # Team header for department reports
                team_header = Paragraph(f"TEAM: {team_data['team_name']}", 
                                       ParagraphStyle('TeamHeader',
                                                    parent=getSampleStyleSheet()['Heading1'],
                                                    fontSize=18,
                                                    textColor=colors.darkred,
                                                    spaceAfter=20))
                story.append(team_header)
                story.append(Spacer(1, 10))
                
                # Process members in this team
                for local_member_idx, member in enumerate(team_data['members'], 1):
                    if local_member_idx > 1:
                        story.append(Spacer(1, 30))  # Space between members in same team
                    
                    # Process this member (inline member processing)
                    self._add_member_section_to_pdf(story, member, local_member_idx, team_project_stats, is_department_report)
        else:
            # Regular team report - process members directly
            for member_idx, member in enumerate(team_report.member_reports, 1):
                if member_idx > 1:
                    story.append(PageBreak())  # New page for each member in team reports
                
                # Process this member
                self._add_member_section_to_pdf(story, member, member_idx, team_project_stats, is_department_report)
        
        # Build and return PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    def _add_member_section_to_pdf(self, story, member, member_idx, team_project_stats, is_department_report):
        """Add a member section to the PDF story"""
        # Member Header
        member_title = Paragraph(f"Member {member_idx}: {member.user_name}", 
                                ParagraphStyle('MemberTitle',
                                             parent=getSampleStyleSheet()['Heading1'],
                                             fontSize=16,
                                             textColor=colors.darkblue,
                                             spaceAfter=15))
        story.append(member_title)
        
        # Member Performance Summary
        member_info = [
            ['Metric', 'Value'],
            ['Role', member.user_role.capitalize() if member.user_role else 'Unknown'],
        ]
        
        # Add team info for department reports
        if is_department_report:
            team_name = getattr(member, 'team_name', None)
            if not team_name:
                team_id = getattr(member, 'team_id', None)
                team_name = f'Team {team_id}' if team_id else 'No Team Assigned'
            member_info.append(['Team', team_name])
        
        member_info.extend([
            ['Total Projects', member.total_projects],
            ['Total Tasks', member.total_tasks],
            ['Completed Tasks', member.completed_tasks],
            ['Completion Rate', f"{member.completion_percentage:.1f}%"],
            ['Overdue Tasks', getattr(member, 'overdue_tasks', 0)],
            ['Average Task Duration', f"{member.average_task_duration:.1f} days" if member.average_task_duration else "N/A"]
        ])
        
        member_info_table = Table(member_info, colWidths=[2.5*inch, 2.5*inch])
        member_info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(member_info_table)
        story.append(Spacer(1, 20))
        
        # Projects this member is involved in
        member_user_id = member.user_id
        
        # Ensure member_user_id is an integer for comparison
        try:
            member_user_id = int(member_user_id)
        except (ValueError, TypeError):
            pass  # Keep original type if conversion fails
        
        projects_found = 0
        for project in team_project_stats:
            project_id = project.get('project_id')
            member_involvement = project.get('member_involvement', {})
            
            # Check if this member is involved in the project
            if member_user_id in member_involvement:
                projects_found += 1
                involved_task_ids = member_involvement[member_user_id]['involved_tasks']
                
                # Project Header
                project_title = Paragraph(f"PROJECT: {project.get('project_name', 'Unknown Project')}", 
                                         ParagraphStyle('ProjectTitle',
                                                      parent=getSampleStyleSheet()['Heading2'],
                                                      fontSize=12,
                                                      textColor=colors.darkgreen,
                                                      spaceAfter=10))
                story.append(project_title)
                
                # Project-level metrics
                project_metrics = [
                    ['Metric', 'Value'],
                    ['Total Tasks', project.get('total_tasks', 0)],
                    ['Completed Tasks', project.get('completed_tasks', 0)],
                    ['Ongoing Tasks', project.get('in_progress_tasks', 0)],
                    ['Under Review Tasks', project.get('under_review_tasks', 0)],
                    ['Overdue Tasks', project.get('overdue_tasks', 0)],
                    ['Completion Rate', f"{project.get('completion_percentage', 0):.1f}%"],
                    ['Average Task Duration', f"{project.get('average_task_duration'):.1f} days" if project.get('average_task_duration') else "N/A"],
                    ['Projected Completion', project.get('projected_completion_date') if project.get('projected_completion_date') else "Completion date cannot be projected"]
                ]
                
                project_metrics_table = Table(project_metrics, colWidths=[2*inch, 2*inch])
                project_metrics_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightgreen),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 8),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(project_metrics_table)
                story.append(Spacer(1, 12))
                
                # ALL Tasks in this project (with highlighting)
                all_project_tasks = project.get('all_tasks', [])
                if all_project_tasks:
                    tasks_header = Paragraph("All Tasks in Project (★ = Member is owner/collaborator)", 
                                            ParagraphStyle('TasksHeader',
                                                         parent=getSampleStyleSheet()['Heading3'],
                                                         fontSize=10,
                                                         spaceAfter=8))
                    story.append(tasks_header)
                    
                    # Task table
                    task_data = [['Task Name', 'Status', 'Priority', 'Owner', 'Collaborators', 'Due Date', 'Duration']]
                    
                    # Track which rows need highlighting
                    highlighted_rows = []
                    
                    for task_idx, task in enumerate(all_project_tasks):
                        task_id = task.get('id')
                        is_member_involved = task_id in involved_task_ids
                        
                        # Get task details - NO TRUNCATION
                        task_name = task.get('task_name', 'Unknown Task')
                        if is_member_involved:
                            task_name = f"★ {task_name}"
                            highlighted_rows.append(task_idx + 1)  # +1 because row 0 is header
                        
                        # Get owner name - NO TRUNCATION
                        owner_name = task.get('owner_name', 'Unknown')
                        
                        # Get collaborators - show ALL names from collaborator_names field
                        collab_names = task.get('collaborator_names', [])
                        if not collab_names:
                            # Fallback: try to build from collaborators IDs
                            collaborators = task.get('collaborators', []) or []
                            if isinstance(collaborators, list) and collaborators:
                                collab_names = [f'User {c}' for c in collaborators]
                        
                        collab_str = ', '.join(collab_names) if collab_names else 'None'
                        
                        # Duration
                        completion_days = task.get('completion_days')
                        duration_text = f"{completion_days}d" if completion_days else "Ongoing"
                        
                        task_data.append([
                            task_name,
                            task.get('status', 'Unknown'),
                            task.get('priority', 'Normal'),
                            owner_name,
                            collab_str,
                            task.get('due_date', '')[:10] if task.get('due_date') else 'N/A',
                            duration_text
                        ])
                    
                    # Create task table - wider columns for full names
                    task_table = Table(task_data, colWidths=[2.2*inch, 0.7*inch, 0.6*inch, 1.0*inch, 1.2*inch, 0.7*inch, 0.6*inch])
                    
                    # Base style
                    table_style = [
                        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 7),
                        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                        ('FONTSIZE', (0, 1), (-1, -1), 6),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP')
                    ]
                    
                    # Add yellow highlighting for member's tasks
                    for row_idx in highlighted_rows:
                        table_style.append(('BACKGROUND', (0, row_idx), (-1, row_idx), colors.yellow))
                        table_style.append(('TEXTCOLOR', (0, row_idx), (-1, row_idx), colors.black))
                    
                    task_table.setStyle(TableStyle(table_style))
                    story.append(task_table)
                    story.append(Spacer(1, 15))

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
                        'Ongoing': project.get('in_progress_tasks', 0),
                        'Under Review': project.get('under_review_tasks', 0),
                        'Avg Duration': f"{project['average_task_duration']:.1f} days" if project['average_task_duration'] else "N/A",
                        'Est. Completion': project['projected_completion_date'] if project['projected_completion_date'] else "N/A",
                        'Status': '🟢 On Track' if project['completion_percentage'] >= 70 and project.get('overdue_percentage', 0) < 20 else
                                '🟡 At Risk' if project.get('overdue_percentage', 0) < 40 else '🔴 Critical'
                    })
                
                project_focus_df = pd.DataFrame(project_focus_data)
                project_focus_df.to_excel(writer, sheet_name='Projects', index=False)

            # Action Items Sheet (Critical tasks only)
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
                    duration_text = f"{completion_days} days" if completion_days else "Ongoing"
                    
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
        """Export team report with Overview tab and individual member tabs showing all project tasks with highlighting"""
        buffer = io.BytesIO()
        
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            # ========== TAB 1: OVERVIEW ==========
            dashboard_data = []
            
            # Team Overview Section
            dashboard_data.extend([
                ['TEAM PERFORMANCE DASHBOARD', ''],
                ['Department' if team_report.dept_name and not team_report.team_name else 'Team', 
                 team_report.dept_name or team_report.team_name or 'Unknown'],
                ['Department Size' if team_report.dept_name and not team_report.team_name else 'Team Size', 
                 len(team_report.member_reports)],
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
            dashboard_df.to_excel(writer, sheet_name='Overview', index=False)
            
            # ========== TEAM MEMBER TABS (One per member) ==========
            # Get enriched project stats from team report
            team_project_stats = getattr(team_report, 'team_project_stats', [])
            
            # Detect if this is a department report
            is_department_report = team_report.dept_name and not team_report.team_name
            
            # Group members by team if this is a department report
            members_to_process = []
            if is_department_report:
                # Group members by team_id
                teams_dict = {}
                for member in team_report.member_reports:
                    team_id = getattr(member, 'team_id', None)
                    team_name = getattr(member, 'team_name', None)
                    
                    # Handle missing team info
                    if not team_id:
                        team_id = 'no_team'
                        team_name = 'No Team Assigned'
                    elif not team_name:
                        # If team_id exists but team_name is None, use fallback
                        team_name = f'Team {team_id}'
                    
                    if team_id not in teams_dict:
                        teams_dict[team_id] = {
                            'team_name': team_name,
                            'members': []
                        }
                    teams_dict[team_id]['members'].append(member)
                
                # Process teams in order, adding team headers
                for team_id, team_data in teams_dict.items():
                    # Add a team header placeholder with member list
                    members_to_process.append({
                        'is_team_header': True,
                        'team_name': team_data['team_name'],
                        'team_members': team_data['members']  # Pass the actual members
                    })
                    # Add team members
                    members_to_process.extend(team_data['members'])
            else:
                # Regular team report - just process members as-is
                members_to_process = team_report.member_reports
            
            for member_idx, member in enumerate(members_to_process, 1):
                # Skip team headers in member processing (we'll create a sheet for them)
                if isinstance(member, dict) and member.get('is_team_header'):
                    # Create a team header sheet with member list
                    team_header_sheet = f"TEAM - {member['team_name'][:20]}"
                    team_header_data = [
                        [f"TEAM: {member['team_name']}", ''],
                        ['', ''],
                        ['Team Members:', ''],
                        ['', '']
                    ]
                    
                    # Add list of team members
                    team_members = member.get('team_members', [])
                    for idx, team_member in enumerate(team_members, 1):
                        team_header_data.append([
                            f"{idx}. {team_member.user_name}",
                            team_member.user_role.capitalize() if team_member.user_role else 'Unknown'
                        ])
                    
                    team_df = pd.DataFrame(team_header_data, columns=['Member', 'Role'])
                    team_df.to_excel(writer, sheet_name=team_header_sheet, index=False)
                    continue
                
                sheet_name = f"Member {member_idx} - {member.user_name[:18]}"  # Limit name length for Excel
                
                # Member Info Section
                member_info_data = []
                
                # Add team info for department reports
                if is_department_report:
                    team_name = getattr(member, 'team_name', None)
                    if not team_name:
                        team_id = getattr(member, 'team_id', None)
                        team_name = f'Team {team_id}' if team_id else 'No Team Assigned'
                    
                    member_info_data.extend([
                        [f'MEMBER {member_idx}: {member.user_name}', '', '', '', '', '', '', '', '', ''],
                        ['Team', team_name, '', '', '', '', '', '', '', ''],
                        ['Role', member.user_role.capitalize() if member.user_role else 'Unknown', '', '', '', '', '', '', '', ''],
                    ])
                else:
                    member_info_data.extend([
                        [f'MEMBER {member_idx}: {member.user_name}', '', '', '', '', '', '', '', '', ''],
                        ['Role', member.user_role.capitalize() if member.user_role else 'Unknown', '', '', '', '', '', '', '', ''],
                    ])
                
                member_info_data.extend([
                    ['', '', '', '', '', '', '', '', '', ''],
                    ['MEMBER PERFORMANCE', '', '', '', '', '', '', '', '', ''],
                    ['Total Projects', member.total_projects, '', '', '', '', '', '', '', ''],
                    ['Total Tasks', member.total_tasks, '', '', '', '', '', '', '', ''],
                    ['Completed Tasks', member.completed_tasks, '', '', '', '', '', '', '', ''],
                    ['Completion Rate', f"{member.completion_percentage:.1f}%", '', '', '', '', '', '', '', ''],
                    ['Overdue Tasks', getattr(member, 'overdue_tasks', 0), '', '', '', '', '', '', '', ''],
                    ['Average Task Duration', f"{member.average_task_duration:.1f} days" if member.average_task_duration else "N/A", '', '', '', '', '', '', '', ''],
                    ['', '', '', '', '', '', '', '', '', ''],
                    ['', '', '', '', '', '', '', '', '', '']
                ])
                
                # Projects this member is involved in
                member_user_id = member.user_id
                member_projects = []
                
                for project in team_project_stats:
                    project_id = project.get('project_id')
                    member_involvement = project.get('member_involvement', {})
                    
                    # Check if this member is involved in the project
                    if member_user_id in member_involvement:
                        involved_task_ids = member_involvement[member_user_id]['involved_tasks']
                        
                        # Get all tasks for this project
                        all_project_tasks = project.get('all_tasks', [])
                        
                        # Add project header
                        member_info_data.append([f"PROJECT: {project.get('project_name', 'Unknown Project')}", '', '', '', '', '', '', '', '', ''])
                        member_info_data.append(['', '', '', '', '', '', '', '', '', ''])
                        
                        # Project-level metrics
                        member_info_data.extend([
                            ['Project Metrics', '', '', '', '', '', '', '', '', ''],
                            ['Total Tasks in Project', project.get('total_tasks', 0), '', '', '', '', '', '', '', ''],
                            ['Completed Tasks', project.get('completed_tasks', 0), '', '', '', '', '', '', '', ''],
                            ['Ongoing Tasks', project.get('in_progress_tasks', 0), '', '', '', '', '', '', '', ''],
                            ['Under Review Tasks', project.get('under_review_tasks', 0), '', '', '', '', '', '', '', ''],
                            ['Overdue Tasks', project.get('overdue_tasks', 0), '', '', '', '', '', '', '', ''],
                            ['Completion Rate', f"{project.get('completion_percentage', 0):.1f}%", '', '', '', '', '', '', '', ''],
                            ['Average Task Duration', f"{project.get('average_task_duration'):.1f} days" if project.get('average_task_duration') else "N/A", '', '', '', '', '', '', '', ''],
                            ['Projected Completion', project.get('projected_completion_date') if project.get('projected_completion_date') else "Completion date cannot be projected", '', '', '', '', '', '', '', ''],
                            ['', '', '', '', '', '', '', '', '', '']
                        ])
                        
                        # ALL Tasks in this project (with highlighting)
                        if all_project_tasks:
                            member_info_data.append(['ALL TASKS IN THIS PROJECT', '', '', '', '', '', '', '', '', ''])
                            member_info_data.append(['(★ = This member is owner or collaborator)', '', '', '', '', '', '', '', '', ''])
                            member_info_data.append(['', '', '', '', '', '', '', '', '', ''])
                            
                            # Task table headers
                            member_info_data.append([
                                'Task Name',
                                'Status',
                                'Priority',
                                'Owner',
                                'Collaborators',
                                'Created Date',
                                'Due Date',
                                'Completed Date',
                                'Duration',
                                'Member Involved'
                            ])
                            
                            # Add all tasks
                            for task in all_project_tasks:
                                task_id = task.get('id')
                                is_member_involved = task_id in involved_task_ids
                                
                                # Get owner name - NO TRUNCATION
                                owner_id = task.get('owner_id')
                                owner_name = task.get('owner_name', 'Unknown')
                                
                                # Get collaborators - show ALL names from collaborator_names field
                                collab_names = task.get('collaborator_names', [])
                                if not collab_names:
                                    # Fallback: try to build from collaborators IDs
                                    collaborators = task.get('collaborators', []) or []
                                    if isinstance(collaborators, list) and collaborators:
                                        collab_names = [f'User {c}' for c in collaborators]
                                
                                collab_str = ', '.join(collab_names) if collab_names else 'None'
                                
                                # Duration calculation
                                completion_days = task.get('completion_days')
                                if not completion_days:
                                    # Calculate if needed
                                    created_at = task.get('created_at')
                                    completed_at = task.get('completed_at')
                                    if created_at and completed_at:
                                        try:
                                            from dateutil import parser as dateparser
                                            created_date = dateparser.parse(created_at)
                                            completed_date = dateparser.parse(completed_at)
                                            completion_days = (completed_date - created_date).days
                                        except:
                                            completion_days = None
                                
                                duration_text = f"{completion_days} days" if completion_days else "Ongoing"
                                
                                # Mark task name with star if member is involved
                                task_name = task.get('task_name', 'Unknown Task')
                                if is_member_involved:
                                    task_name = f"★ {task_name}"
                                
                                member_info_data.append([
                                    task_name,
                                    task.get('status', 'Unknown'),
                                    task.get('priority', 'Normal'),
                                    owner_name,
                                    collab_str,
                                    task.get('created_at', '')[:10] if task.get('created_at') else 'N/A',
                                    task.get('due_date', '')[:10] if task.get('due_date') else 'N/A',
                                    task.get('completed_at', '')[:10] if task.get('completed_at') else 'N/A',
                                    duration_text,
                                    '★ YES' if is_member_involved else 'No'
                                ])
                            
                            member_info_data.append(['', '', '', '', '', '', '', '', '', ''])
                            member_info_data.append(['', '', '', '', '', '', '', '', '', ''])
                
                # Create DataFrame and write to Excel
                member_df = pd.DataFrame(member_info_data)
                member_df.to_excel(writer, sheet_name=sheet_name, index=False, header=False)
                
                # Apply formatting - highlight member involved tasks
                worksheet = writer.sheets[sheet_name]
                from openpyxl.styles import PatternFill, Font
                
                # Yellow fill for highlighted rows
                highlight_fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")
                bold_font = Font(bold=True)
                
                # Go through rows and highlight where member is involved
                for row_idx, row_data in enumerate(member_info_data, start=1):
                    if len(row_data) > 0 and isinstance(row_data[0], str):
                        # Check if this is a task row with member involvement
                        if row_data[0].startswith('★'):
                            # Highlight entire row
                            for col_idx in range(1, 11):  # 10 columns
                                cell = worksheet.cell(row=row_idx, column=col_idx)
                                cell.fill = highlight_fill

        buffer.seek(0)
        return buffer.getvalue()