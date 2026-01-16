"""
Service de génération de rapports et exports.
"""

import io
import csv
from datetime import date, datetime
from typing import List, Dict, Any
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import crud
from database.models import Project, Task, MemberPerformance


def generate_project_report(project_id: int) -> Dict[str, Any]:
    """
    Génère un rapport complet pour un projet.
    """
    project = crud.get_project_by_id(project_id)
    if not project:
        return None
    
    stats = crud.get_project_stats(project_id)
    milestones = crud.get_project_milestones(project_id)
    members = crud.get_project_members(project_id)
    tasks = crud.get_all_tasks(project_id=project_id)
    
    # Calculer les statistiques par priorité
    priority_stats = {'LOW': 0, 'MEDIUM': 0, 'HIGH': 0, 'CRITICAL': 0}
    for task in tasks:
        priority_stats[task.priority] = priority_stats.get(task.priority, 0) + 1
    
    # Calculer les statistiques par membre
    member_stats = {}
    for task in tasks:
        if task.assigned_to:
            if task.assigned_to not in member_stats:
                member_stats[task.assigned_to] = {
                    'name': task.assigned_to_name,
                    'total': 0,
                    'completed': 0
                }
            member_stats[task.assigned_to]['total'] += 1
            if task.status == 'COMPLETED':
                member_stats[task.assigned_to]['completed'] += 1
    
    return {
        'project': project,
        'stats': stats,
        'milestones': milestones,
        'members': members,
        'tasks': tasks,
        'priority_stats': priority_stats,
        'member_stats': list(member_stats.values()),
        'generated_at': datetime.now().isoformat()
    }


def generate_team_performance_report() -> Dict[str, Any]:
    """
    Génère un rapport de performance de l'équipe.
    """
    members_performance = crud.get_member_performance()
    dashboard_stats = crud.get_dashboard_stats()
    overdue_tasks = crud.get_overdue_tasks()
    recent_activities = crud.get_recent_activities(limit=50)
    
    # Classement des membres par taux de complétion
    ranked_members = sorted(
        members_performance, 
        key=lambda m: m.completion_rate, 
        reverse=True
    )
    
    return {
        'dashboard_stats': dashboard_stats,
        'members_performance': members_performance,
        'ranked_members': ranked_members,
        'overdue_tasks': overdue_tasks,
        'recent_activities': recent_activities,
        'generated_at': datetime.now().isoformat()
    }


def export_project_to_csv(project_id: int) -> str:
    """
    Exporte les tâches d'un projet au format CSV.
    
    Returns:
        Contenu CSV en string
    """
    tasks = crud.get_all_tasks(project_id=project_id)
    project = crud.get_project_by_id(project_id)
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # En-têtes
    writer.writerow([
        'ID', 'Titre', 'Description', 'Statut', 'Priorité', 
        'Progression (%)', 'Assigné à', 'Deadline', 'Créé le'
    ])
    
    # Données
    for task in tasks:
        writer.writerow([
            task.id,
            task.title,
            task.description or '',
            task.status,
            task.priority,
            task.progress,
            task.assigned_to_name or 'Non assigné',
            task.deadline or '',
            task.created_at or ''
        ])
    
    return output.getvalue()


def export_all_projects_to_csv() -> str:
    """
    Exporte tous les projets au format CSV.
    """
    projects = crud.get_all_projects()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # En-têtes
    writer.writerow([
        'ID', 'Nom', 'Description', 'Statut', 'Date début', 
        'Date fin', 'Progression (%)', 'Nombre tâches', 'Nombre membres'
    ])
    
    # Données
    for project in projects:
        writer.writerow([
            project.id,
            project.name,
            project.description or '',
            project.status,
            project.start_date or '',
            project.end_date or '',
            project.progress,
            project.task_count,
            project.member_count
        ])
    
    return output.getvalue()


def export_team_performance_to_csv() -> str:
    """
    Exporte les performances de l'équipe au format CSV.
    """
    performances = crud.get_member_performance()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # En-têtes
    writer.writerow([
        'ID', 'Nom', 'Total tâches', 'Complétées', 'En cours',
        'En retard', 'Taux de complétion (%)', 'Progression moyenne (%)'
    ])
    
    # Données
    for perf in performances:
        writer.writerow([
            perf.user_id,
            perf.user_name,
            perf.total_tasks,
            perf.completed_tasks,
            perf.in_progress_tasks,
            perf.overdue_tasks,
            perf.completion_rate,
            perf.average_progress
        ])
    
    return output.getvalue()


def generate_pdf_report(project_id: int = None) -> bytes:
    """
    Génère un rapport PDF.
    
    Note: Nécessite reportlab. Si non disponible, retourne None.
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib import colors
    except ImportError:
        return None
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []
    
    # Titre
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30
    )
    
    if project_id:
        project = crud.get_project_by_id(project_id)
        stats = crud.get_project_stats(project_id)
        tasks = crud.get_all_tasks(project_id=project_id)
        
        elements.append(Paragraph(f"Rapport du projet: {project.name}", title_style))
        elements.append(Spacer(1, 12))
        
        # Informations générales
        elements.append(Paragraph("Informations générales", styles['Heading2']))
        info_data = [
            ["Statut", project.status],
            ["Date de début", str(project.start_date) if project.start_date else "Non définie"],
            ["Date de fin", str(project.end_date) if project.end_date else "Non définie"],
            ["Budget", f"{project.budget:,.2f} €" if project.budget else "Non défini"],
            ["Progression", f"{project.progress}%"]
        ]
        info_table = Table(info_data, colWidths=[5*cm, 10*cm])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(info_table)
        elements.append(Spacer(1, 20))

        # Équipe du projet
        members = crud.get_project_members(project_id)
        if members:
            elements.append(Paragraph("Équipe du projet", styles['Heading2']))
            member_data = [["Nom", "Rôle", "Email", "Date d'assignation"]]

            for member in members:
                assigned_date = "-"
                if member.assigned_at:
                    if isinstance(member.assigned_at, str):
                        assigned_date = member.assigned_at[:10]
                    else:
                        assigned_date = member.assigned_at.strftime('%Y-%m-%d')
                
                member_data.append([
                    member.user_name,
                    member.role_in_project,
                    member.user_email,
                    assigned_date
                ])
            
            member_table = Table(member_data, colWidths=[5*cm, 4*cm, 6*cm, 4*cm])
            member_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('PADDING', (0, 0), (-1, -1), 6),
            ]))
            elements.append(member_table)
            elements.append(Spacer(1, 20))
        
        # Statistiques des tâches
        elements.append(Paragraph("Statistiques des tâches", styles['Heading2']))
        stats_data = [
            ["Total", "Complétées", "En cours", "À faire", "En retard"],
            [stats['total_tasks'], stats['completed_tasks'], stats['in_progress_tasks'],
             stats['todo_tasks'], stats['overdue_tasks']]
        ]
        stats_table = Table(stats_data)
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(stats_table)
        elements.append(Spacer(1, 20))
        
        # Liste des tâches détaillée
        if tasks:
            elements.append(Paragraph("Détail des tâches", styles['Heading2']))
            task_data = [["Titre", "Assigné à", "Statut", "Prio.", "Avancement", "Deadline"]]
            for task in tasks:
                assignee = task.assigned_to_name if task.assigned_to_name else "Non assigné"
                deadline = str(task.deadline) if task.deadline else "-"
                title = task.title[:25] + "..." if len(task.title) > 25 else task.title
                
                task_data.append([
                    title,
                    assignee,
                    task.status,
                    task.priority,
                    f"{task.progress}%",
                    deadline
                ])
            
            # Ajustement des largeurs de colonnes pour A4 (21cm - marges)
            task_table = Table(task_data, colWidths=[5*cm, 3.5*cm, 2.5*cm, 1.5*cm, 2*cm, 2.5*cm])
            task_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('PADDING', (0, 0), (-1, -1), 4),
                ('ALIGN', (3, 1), (5, -1), 'CENTER'), # Centrer Prio, Avancement, Deadline
            ]))
            elements.append(task_table)
    
    else:
        # Rapport global
        dashboard_stats = crud.get_dashboard_stats()
        projects = crud.get_all_projects()
        
        elements.append(Paragraph("Rapport Global - Gestion de Projets", title_style))
        elements.append(Paragraph(f"Généré le: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
        elements.append(Spacer(1, 20))
        
        # Statistiques globales
        elements.append(Paragraph("Vue d'ensemble", styles['Heading2']))
        overview_data = [
            ["Projets actifs", dashboard_stats.active_projects],
            ["Total projets", dashboard_stats.total_projects],
            ["Tâches totales", dashboard_stats.total_tasks],
            ["Tâches complétées", dashboard_stats.completed_tasks],
            ["Tâches en retard", dashboard_stats.overdue_tasks],
            ["Membres actifs", dashboard_stats.total_members],
        ]
        overview_table = Table(overview_data, colWidths=[8*cm, 5*cm])
        overview_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(overview_table)
        elements.append(Spacer(1, 20))
        
        # Liste des projets
        if projects:
            elements.append(Paragraph("Liste des projets", styles['Heading2']))
            proj_data = [["Nom", "Statut", "Progression", "Tâches"]]
            for proj in projects:
                proj_data.append([
                    proj.name[:25] + "..." if len(proj.name) > 25 else proj.name,
                    proj.status,
                    f"{proj.progress}%",
                    proj.task_count
                ])
            proj_table = Table(proj_data, colWidths=[7*cm, 3*cm, 2.5*cm, 2*cm])
            proj_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('PADDING', (0, 0), (-1, -1), 5),
            ]))
            elements.append(proj_table)
    
    elements.append(Spacer(1, 30))
    elements.append(Paragraph(
        "Rapport généré automatiquement par le système de Gestion de Projets",
        styles['Italic']
    ))
    
    doc.build(elements)
    return buffer.getvalue()


def get_activity_timeline(days: int = 7) -> List[Dict[str, Any]]:
    """
    Récupère une timeline des activités récentes.
    """
    activities = crud.get_recent_activities(limit=100)
    
    # Grouper par jour
    timeline = {}
    for activity in activities:
        if activity.timestamp:
            day = activity.timestamp.split('T')[0] if 'T' in str(activity.timestamp) else str(activity.timestamp)[:10]
            if day not in timeline:
                timeline[day] = []
            timeline[day].append({
                'action': activity.action,
                'user': activity.user_name,
                'entity_type': activity.entity_type,
                'details': activity.details,
                'time': activity.timestamp
            })
    
    return [
        {'date': day, 'activities': acts}
        for day, acts in sorted(timeline.items(), reverse=True)
    ][:days]
