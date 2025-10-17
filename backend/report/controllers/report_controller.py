from flask import Blueprint, request, jsonify, send_file
from services.report_service import ReportService
from services.export_service import ExportService
from models.report import ReportData, TeamReportData
from datetime import datetime
import io

report_bp = Blueprint("reports", __name__)
report_service = ReportService()
export_service = ExportService()

@report_bp.route("/reports/personal/<int:user_id>", methods=["GET"])
def generate_personal_report(user_id: int):
    """
    Generate personal report for staff showing their own stats.
    
    Parameters:
    - user_id: ID of the user requesting the report
    
    Query Parameters:
    - save: 'true' to save the report, 'false' (default) to generate only
    - format: 'json' (default), 'pdf', or 'excel'
    - start_date: Start date for filtering (YYYY-MM-DD format)
    - end_date: End date for filtering (YYYY-MM-DD format)
    
    RETURNS:
    {
        "status": 200,
        "message": "Personal report generated for [User Name]",
        "data": { ... report data ... }
    }
    
    For PDF/Excel format, returns the file as binary data
    
    RESPONSES:
        200: Report successfully generated
        404: User not found
        500: Internal Server Error
    """
    try:
        # Get format, save, and date parameters from query parameters
        export_format = request.args.get('format', 'json').lower()
        save_report = request.args.get('save', 'false').lower() == 'true'
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Validate date format if provided
        if start_date:
            try:
                datetime.strptime(start_date, '%Y-%m-%d')
            except ValueError:
                return jsonify({"Message": "Invalid start_date format. Use YYYY-MM-DD", "Code": 400}), 400
        
        if end_date:
            try:
                datetime.strptime(end_date, '%Y-%m-%d')
            except ValueError:
                return jsonify({"Message": "Invalid end_date format. Use YYYY-MM-DD", "Code": 400}), 400
        
        # Generate report data with date filtering
        result = report_service.generate_personal_report(user_id, save_report=save_report, start_date=start_date, end_date=end_date)
        
        if result.get("status") != 200:
            return jsonify({"Message": result.get("message"), "Code": result.get("status")}), result.get("status")
        
        # Return based on requested format
        if export_format == 'json':
            result["Code"] = result.pop("status", 200)
            return jsonify(result), 200
            
        elif export_format == 'pdf':
            report_data = ReportData(**result["data"])
            pdf_data = export_service.export_personal_report_pdf(report_data)
            
            return send_file(
                io.BytesIO(pdf_data),
                mimetype='application/pdf',
                as_attachment=True,
                download_name=f'personal_report_{user_id}_{datetime.now().strftime("%Y%m%d")}.pdf'
            )
            
        elif export_format == 'excel':
            report_data = ReportData(**result["data"])
            excel_data = export_service.export_personal_report_excel(report_data)
            
            return send_file(
                io.BytesIO(excel_data),
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name=f'personal_report_{user_id}_{datetime.now().strftime("%Y%m%d")}.xlsx'
            )
            
        else:
            return jsonify({"Message": "Invalid format. Use 'json', 'pdf', or 'excel'", "Code": 400}), 400
            
    except Exception as e:
        return jsonify({"Message": str(e), "Code": 500}), 500

@report_bp.route("/reports/team/<int:manager_user_id>", methods=["GET"])
def generate_team_report(manager_user_id: int):
    """
    Generate team report for managers showing their team members' stats and detailed workload analysis.
    
    Parameters:
    - manager_user_id: ID of the manager requesting the report
    
    Query Parameters:
    - save: 'true' to save the report, 'false' (default) to generate only
    - format: 'json' (default), 'pdf', or 'excel'
    - start_date: Start date for filtering (YYYY-MM-DD format)
    - end_date: End date for filtering (YYYY-MM-DD format)
    
    RETURNS:
    {
        "status": 200,
        "message": "Team report generated for manager [Manager Name]",
        "data": {
            "manager_report": { ... manager's personal stats ... },
            "team_report": { ... team statistics and member reports ... },
            "detailed_workload_analysis": { ... workload and scheduling analysis ... }
        }
    }
    
    For PDF/Excel format, returns the file as binary data
    
    RESPONSES:
        200: Report successfully generated
        403: User is not a manager
        404: Manager not found or not assigned to team
        500: Internal Server Error
    """
    try:
        from datetime import datetime
        
        # Get format, save, and date parameters from query parameters
        export_format = request.args.get('format', 'json').lower()
        save_report = request.args.get('save', 'false').lower() == 'true'
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Validate date format if provided
        if start_date:
            try:
                datetime.strptime(start_date, '%Y-%m-%d')
            except ValueError:
                return jsonify({"Message": "Invalid start_date format. Use YYYY-MM-DD", "Code": 400}), 400
        
        if end_date:
            try:
                datetime.strptime(end_date, '%Y-%m-%d')
            except ValueError:
                return jsonify({"Message": "Invalid end_date format. Use YYYY-MM-DD", "Code": 400}), 400
        
        # Generate report data with date filtering and detailed workload analysis
        result = report_service.generate_team_report(manager_user_id, save_report=save_report, start_date=start_date, end_date=end_date)
        
        if result.get("status") != 200:
            return jsonify({"Message": result.get("message"), "Code": result.get("status")}), result.get("status")
        
        # Return based on requested format
        if export_format == 'json':
            result["Code"] = result.pop("status", 200)
            return jsonify(result), 200
            
        elif export_format == 'pdf':
            team_data = result["data"]["team_report"]
            detailed_workload = result["data"].get("detailed_workload_analysis")
            
            # Reconstruct TeamReportData
            team_report = TeamReportData(
                team_id=team_data.get("team_id"),
                dept_id=team_data.get("dept_id"),
                team_name=team_data.get("team_name"),
                dept_name=team_data.get("dept_name"),
                member_reports=[ReportData(**member) for member in team_data.get("member_reports", [])],
                total_team_tasks=team_data.get("total_team_tasks", 0),
                total_team_projects=team_data.get("total_team_projects", 0),
                team_completion_percentage=team_data.get("team_completion_percentage", 0.0),
                team_average_task_duration=team_data.get("team_average_task_duration")
            )
            
            pdf_data = export_service.export_team_report_pdf(None, team_report, detailed_workload)
            
            return send_file(
                io.BytesIO(pdf_data),
                mimetype='application/pdf',
                as_attachment=True,
                download_name=f'team_report_{manager_user_id}_{datetime.now().strftime("%Y%m%d")}.pdf'
            )
            
        elif export_format == 'excel':
            team_data = result["data"]["team_report"]
            detailed_workload = result["data"].get("detailed_workload_analysis")
            
            # Reconstruct TeamReportData
            team_report = TeamReportData(
                team_id=team_data.get("team_id"),
                dept_id=team_data.get("dept_id"),
                team_name=team_data.get("team_name"),
                dept_name=team_data.get("dept_name"),
                member_reports=[ReportData(**member) for member in team_data.get("member_reports", [])],
                total_team_tasks=team_data.get("total_team_tasks", 0),
                total_team_projects=team_data.get("total_team_projects", 0),
                team_completion_percentage=team_data.get("team_completion_percentage", 0.0),
                team_average_task_duration=team_data.get("team_average_task_duration")
            )
            
            excel_data = export_service.export_team_report_excel(None, team_report, detailed_workload)
            
            return send_file(
                io.BytesIO(excel_data),
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name=f'team_report_{manager_user_id}_{datetime.now().strftime("%Y%m%d")}.xlsx'
            )
            
        else:
            return jsonify({"Message": "Invalid format. Use 'json', 'pdf', or 'excel'", "Code": 400}), 400
            
    except Exception as e:
        return jsonify({"Message": str(e), "Code": 500}), 500

@report_bp.route("/reports/department/<int:director_user_id>", methods=["GET"])
def generate_department_report(director_user_id: int):
    """
    Generate department report for directors showing their department members' stats and detailed workload analysis.
    
    Parameters:
    - director_user_id: ID of the director requesting the report
    
    Query Parameters:
    - save: 'true' to save the report, 'false' (default) to generate only
    - format: 'json' (default), 'pdf', or 'excel'
    - start_date: Start date for filtering (YYYY-MM-DD format)
    - end_date: End date for filtering (YYYY-MM-DD format)
    
    RETURNS:
    {
        "status": 200,
        "message": "Department report generated for director [Director Name]",
        "data": {
            "director_report": { ... director's personal stats ... },
            "department_report": { ... department statistics and member reports ... },
            "detailed_workload_analysis": { ... workload and scheduling analysis ... }
        }
    }
    
    For PDF/Excel format, returns the file as binary data
    
    RESPONSES:
        200: Report successfully generated
        403: User is not a director
        404: Director not found or not assigned to department
        500: Internal Server Error
    """
    try:
        from datetime import datetime
        
        # Get format, save, and date parameters from query parameters
        export_format = request.args.get('format', 'json').lower()
        save_report = request.args.get('save', 'false').lower() == 'true'
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Validate date format if provided
        if start_date:
            try:
                datetime.strptime(start_date, '%Y-%m-%d')
            except ValueError:
                return jsonify({"Message": "Invalid start_date format. Use YYYY-MM-DD", "Code": 400}), 400
        
        if end_date:
            try:
                datetime.strptime(end_date, '%Y-%m-%d')
            except ValueError:
                return jsonify({"Message": "Invalid end_date format. Use YYYY-MM-DD", "Code": 400}), 400
        
        # Generate report data with date filtering and detailed workload analysis
        result = report_service.generate_department_report(director_user_id, save_report=save_report, start_date=start_date, end_date=end_date)
        
        if result.get("status") != 200:
            return jsonify({"Message": result.get("message"), "Code": result.get("status")}), result.get("status")
        
        # Return based on requested format
        if export_format == 'json':
            result["Code"] = result.pop("status", 200)
            return jsonify(result), 200
            
        elif export_format == 'pdf':
            dept_data = result["data"]["department_report"]
            detailed_workload = result["data"].get("detailed_workload_analysis")
            
            # Reconstruct TeamReportData (using same structure for department)
            dept_report = TeamReportData(
                team_id=dept_data.get("team_id"),
                dept_id=dept_data.get("dept_id"),
                team_name=dept_data.get("team_name"),
                dept_name=dept_data.get("dept_name"),
                member_reports=[ReportData(**member) for member in dept_data.get("member_reports", [])],
                total_team_tasks=dept_data.get("total_team_tasks", 0),
                total_team_projects=dept_data.get("total_team_projects", 0),
                team_completion_percentage=dept_data.get("team_completion_percentage", 0.0),
                team_average_task_duration=dept_data.get("team_average_task_duration")
            )
            
            pdf_data = export_service.export_team_report_pdf(None, dept_report, detailed_workload)
            
            return send_file(
                io.BytesIO(pdf_data),
                mimetype='application/pdf',
                as_attachment=True,
                download_name=f'department_report_{director_user_id}_{datetime.now().strftime("%Y%m%d")}.pdf'
            )
            
        elif export_format == 'excel':
            dept_data = result["data"]["department_report"]
            detailed_workload = result["data"].get("detailed_workload_analysis")
            
            # Reconstruct TeamReportData (using same structure for department)
            dept_report = TeamReportData(
                team_id=dept_data.get("team_id"),
                dept_id=dept_data.get("dept_id"),
                team_name=dept_data.get("team_name"),
                dept_name=dept_data.get("dept_name"),
                member_reports=[ReportData(**member) for member in dept_data.get("member_reports", [])],
                total_team_tasks=dept_data.get("total_team_tasks", 0),
                total_team_projects=dept_data.get("total_team_projects", 0),
                team_completion_percentage=dept_data.get("team_completion_percentage", 0.0),
                team_average_task_duration=dept_data.get("team_average_task_duration")
            )
            
            excel_data = export_service.export_team_report_excel(None, dept_report, detailed_workload)
            
            return send_file(
                io.BytesIO(excel_data),
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name=f'department_report_{director_user_id}_{datetime.now().strftime("%Y%m%d")}.xlsx'
            )
            
        else:
            return jsonify({"Message": "Invalid format. Use 'json', 'pdf', or 'excel'", "Code": 400}), 400
            
    except Exception as e:
        return jsonify({"Message": str(e), "Code": 500}), 500

@report_bp.route("/reports/saved/<int:user_id>", methods=["GET"])
def get_saved_reports(user_id: int):
    """
    Get all saved reports for a user.
    
    Parameters:
    - user_id: ID of the user requesting their saved reports
    
    Query Parameters:
    - type: Filter by report type ('personal', 'team', 'department')
    
    RETURNS:
    {
        "status": 200,
        "message": "Found X saved reports",
        "data": [ ... list of saved reports ... ]
    }
    
    RESPONSES:
        200: Reports retrieved successfully
        500: Internal Server Error
    """
    try:
        report_type = request.args.get('type')
        result = report_service.get_saved_reports(user_id, report_type)
        
        result["Code"] = result.pop("status", 200)
        return jsonify(result), result["Code"]
        
    except Exception as e:
        return jsonify({"Message": str(e), "Code": 500}), 500

@report_bp.route("/reports/saved/view/<int:report_id>", methods=["GET"])
def get_saved_report(report_id: int):
    """
    Get a specific saved report.
    
    Parameters:
    - report_id: ID of the report to retrieve
    
    Query Parameters:
    - user_id: ID of the user requesting the report (required)
    - format: 'json' (default), 'pdf', or 'excel'
    
    RETURNS:
    {
        "status": 200,
        "message": "Report retrieved successfully",
        "data": { ... report data ... }
    }
    
    For PDF/Excel format, returns the file as binary data
    
    RESPONSES:
        200: Report retrieved successfully
        403: Access denied
        404: Report not found
        500: Internal Server Error
    """
    try:
        user_id = request.args.get('user_id', type=int)
        if not user_id:
            return jsonify({"Message": "user_id parameter is required", "Code": 400}), 400
        
        export_format = request.args.get('format', 'json').lower()
        
        result = report_service.get_saved_report(report_id, user_id)
        
        if result.get("status") != 200:
            return jsonify({"Message": result.get("message"), "Code": result.get("status")}), result.get("status")
        
        # Return based on requested format
        if export_format == 'json':
            result["Code"] = result.pop("status", 200)
            return jsonify(result), 200
            
        elif export_format in ['pdf', 'excel']:
            # Get the report data and reconstruct for export
            report_data = result["data"]["report_data"]
            report_type = result["data"]["report_type"]
            
            if report_type == 'personal':
                report_obj = ReportData(**report_data)
                if export_format == 'pdf':
                    pdf_data = export_service.export_personal_report_pdf(report_obj)
                    return send_file(
                        io.BytesIO(pdf_data),
                        mimetype='application/pdf',
                        as_attachment=True,
                        download_name=f'saved_report_{report_id}_{datetime.now().strftime("%Y%m%d")}.pdf'
                    )
                else:
                    excel_data = export_service.export_personal_report_excel(report_obj)
                    return send_file(
                        io.BytesIO(excel_data),
                        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                        as_attachment=True,
                        download_name=f'saved_report_{report_id}_{datetime.now().strftime("%Y%m%d")}.xlsx'
                    )
            
            elif report_type in ['team', 'department']:
                manager_data = report_data.get("manager_report") or report_data.get("director_report")
                team_data = report_data.get("team_report") or report_data.get("department_report")
                
                manager_report = ReportData(**manager_data)
                team_report = TeamReportData(
                    team_id=team_data.get("team_id"),
                    dept_id=team_data.get("dept_id"),
                    team_name=team_data.get("team_name"),
                    dept_name=team_data.get("dept_name"),
                    member_reports=[ReportData(**member) for member in team_data.get("member_reports", [])],
                    total_team_tasks=team_data.get("total_team_tasks", 0),
                    total_team_projects=team_data.get("total_team_projects", 0),
                    team_completion_percentage=team_data.get("team_completion_percentage", 0.0),
                    team_average_task_duration=team_data.get("team_average_task_duration")
                )
                
                if export_format == 'pdf':
                    pdf_data = export_service.export_team_report_pdf(manager_report, team_report)
                    return send_file(
                        io.BytesIO(pdf_data),
                        mimetype='application/pdf',
                        as_attachment=True,
                        download_name=f'saved_report_{report_id}_{datetime.now().strftime("%Y%m%d")}.pdf'
                    )
                else:
                    excel_data = export_service.export_team_report_excel(manager_report, team_report)
                    return send_file(
                        io.BytesIO(excel_data),
                        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                        as_attachment=True,
                        download_name=f'saved_report_{report_id}_{datetime.now().strftime("%Y%m%d")}.xlsx'
                    )
            
            return jsonify({"Message": "Invalid report type for export", "Code": 400}), 400
            
        else:
            return jsonify({"Message": "Invalid format. Use 'json', 'pdf', or 'excel'", "Code": 400}), 400
            
    except Exception as e:
        return jsonify({"Message": str(e), "Code": 500}), 500

@report_bp.route("/reports/saved/delete/<int:report_id>", methods=["DELETE"])
def delete_saved_report(report_id: int):
    """
    Delete a saved report.
    
    Parameters:
    - report_id: ID of the report to delete
    
    Query Parameters:
    - user_id: ID of the user requesting the deletion (required)
    
    RETURNS:
    {
        "status": 200,
        "message": "Report X deleted successfully"
    }
    
    RESPONSES:
        200: Report deleted successfully
        403: Access denied (not report owner)
        404: Report not found
        500: Internal Server Error
    """
    try:
        user_id = request.args.get('user_id', type=int)
        if not user_id:
            return jsonify({"Message": "user_id parameter is required", "Code": 400}), 400
        
        result = report_service.delete_saved_report(report_id, user_id)
        
        result["Code"] = result.pop("status", 200)
        return jsonify(result), result["Code"]
        
    except Exception as e:
        return jsonify({"Message": str(e), "Code": 500}), 500

@report_bp.route("/reports/saved/team/<int:manager_user_id>", methods=["GET"])
def get_team_saved_reports(manager_user_id: int):
    """
    Get all saved reports for a manager's team.
    
    Parameters:
    - manager_user_id: ID of the manager requesting team reports
    
    RETURNS:
    {
        "status": 200,
        "message": "Found X team reports",
        "data": [ ... list of team reports ... ]
    }
    
    RESPONSES:
        200: Reports retrieved successfully
        403: User is not a manager
        404: Manager not found or not assigned to team
        500: Internal Server Error
    """
    try:
        result = report_service.get_team_saved_reports(manager_user_id)
        
        result["Code"] = result.pop("status", 200)
        return jsonify(result), result["Code"]
        
    except Exception as e:
        return jsonify({"Message": str(e), "Code": 500}), 500

@report_bp.route("/reports/saved/department/<int:director_user_id>", methods=["GET"])
def get_department_saved_reports(director_user_id: int):
    """
    Get all saved reports for a director's department.
    
    Parameters:
    - director_user_id: ID of the director requesting department reports
    
    RETURNS:
    {
        "status": 200,
        "message": "Found X department reports",
        "data": [ ... list of department reports ... ]
    }
    
    RESPONSES:
        200: Reports retrieved successfully
        403: User is not a director
        404: Director not found or not assigned to department
        500: Internal Server Error
    """
    try:
        result = report_service.get_department_saved_reports(director_user_id)
        
        result["Code"] = result.pop("status", 200)
        return jsonify(result), result["Code"]
        
    except Exception as e:
        return jsonify({"Message": str(e), "Code": 500}), 500

@report_bp.route("/reports/health", methods=["GET"])
def health_check():
    """
    Health check endpoint for the report service.
    
    RETURNS:
    {
        "message": "Report service is running",
        "timestamp": "2024-01-01T12:00:00Z",
        "Code": 200
    }
    """
    return jsonify({
        "message": "Report service is running",
        "timestamp": datetime.now().isoformat(),
        "Code": 200
    }), 200