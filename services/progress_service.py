"""
Service de calcul de progression et de performance.
"""

from datetime import date, datetime, timedelta
from typing import List, Dict, Any
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import crud
from database.models import DashboardStats, MemberPerformance


def get_dashboard_statistics() -> DashboardStats:
    """Récupère les statistiques globales pour le tableau de bord."""
    return crud.get_dashboard_stats()


def get_all_members_performance() -> List[MemberPerformance]:
    """Récupère les performances de tous les membres."""
    return crud.get_member_performance()


def get_member_individual_performance(user_id: int) -> MemberPerformance:
    """Récupère la performance d'un membre spécifique."""
    performances = crud.get_member_performance(user_id)
    return performances[0] if performances else None


def calculate_project_health(project_id: int) -> Dict[str, Any]:
    """
    Calcule la "santé" d'un projet basé sur plusieurs métriques.
    
    Returns:
        Dict avec score (0-100), status (good/warning/danger), et détails
    """
    stats = crud.get_project_stats(project_id)
    project = crud.get_project_by_id(project_id)
    
    if not project or stats['total_tasks'] == 0:
        return {
            'score': 0,
            'status': 'unknown',
            'message': 'Aucune tâche dans ce projet',
            'details': {}
        }
    
    score = 100
    issues = []
    
    # Pénalité pour tâches en retard (max -30 points)
    overdue_ratio = stats['overdue_tasks'] / stats['total_tasks']
    overdue_penalty = min(overdue_ratio * 100, 30)
    score -= overdue_penalty
    if stats['overdue_tasks'] > 0:
        issues.append(f"{stats['overdue_tasks']} tâche(s) en retard")
    
    # Pénalité pour tâches bloquées (max -20 points)
    # On considère les tâches TODO qui auraient dû commencer
    blocked_tasks = crud.get_all_tasks(project_id=project_id, status='BLOCKED')
    if blocked_tasks:
        blocked_penalty = min((len(blocked_tasks) / stats['total_tasks']) * 100, 20)
        score -= blocked_penalty
        issues.append(f"{len(blocked_tasks)} tâche(s) bloquée(s)")
    
    # Bonus pour progression (+10 points si > 50%)
    if stats['progress'] >= 50:
        score = min(score + 10, 100)
    
    # Pénalité si le projet devrait être plus avancé selon les dates
    if project.start_date and project.end_date:
        expected_progress = _calculate_expected_progress(project.start_date, project.end_date)
        if expected_progress > stats['progress'] + 10:
            delay_penalty = min((expected_progress - stats['progress']) / 2, 20)
            score -= delay_penalty
            issues.append(f"Retard d'environ {int(expected_progress - stats['progress'])}%")
    
    # Déterminer le statut
    if score >= 70:
        status = 'good'
        color = '#48bb78'  # vert
    elif score >= 40:
        status = 'warning'
        color = '#ed8936'  # orange
    else:
        status = 'danger'
        color = '#f56565'  # rouge
    
    return {
        'score': max(0, round(score)),
        'status': status,
        'color': color,
        'message': 'Projet en bonne voie' if not issues else ', '.join(issues),
        'details': {
            'progress': stats['progress'],
            'overdue_tasks': stats['overdue_tasks'],
            'total_tasks': stats['total_tasks'],
            'completed_tasks': stats['completed_tasks']
        }
    }


def _calculate_expected_progress(start_date, end_date) -> float:
    """Calcule la progression attendue basée sur les dates."""
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
    
    total_days = (end_date - start_date).days
    elapsed_days = (date.today() - start_date).days
    
    if total_days <= 0:
        return 100.0
    
    expected = (elapsed_days / total_days) * 100
    return min(max(expected, 0), 100)


def get_team_velocity() -> Dict[str, Any]:
    """
    Calcule la vélocité de l'équipe (tâches complétées par semaine).
    """
    # Récupérer les tâches complétées dans les 4 dernières semaines
    conn = crud.get_connection()
    cursor = conn.cursor()
    
    weeks_data = []
    for i in range(4):
        week_end = date.today() - timedelta(days=i*7)
        week_start = week_end - timedelta(days=7)
        
        cursor.execute('''
            SELECT COUNT(*) FROM tasks 
            WHERE status = 'COMPLETED' 
            AND completed_at BETWEEN ? AND ?
        ''', (week_start.isoformat(), week_end.isoformat()))
        
        count = cursor.fetchone()[0]
        weeks_data.append({
            'week': f"S-{i}" if i > 0 else "Cette semaine",
            'tasks_completed': count,
            'start': week_start.isoformat(),
            'end': week_end.isoformat()
        })
    
    conn.close()
    
    # Calculer la moyenne
    total = sum(w['tasks_completed'] for w in weeks_data)
    avg_velocity = total / 4 if weeks_data else 0
    
    return {
        'weekly_data': list(reversed(weeks_data)),
        'average_velocity': round(avg_velocity, 1),
        'total_completed': total,
        'trend': _calculate_trend(weeks_data)
    }


def _calculate_trend(weeks_data: List[Dict]) -> str:
    """Calcule la tendance basée sur les données hebdomadaires."""
    if len(weeks_data) < 2:
        return 'stable'
    
    recent = weeks_data[0]['tasks_completed']
    previous = weeks_data[1]['tasks_completed']
    
    if recent > previous * 1.2:
        return 'up'
    elif recent < previous * 0.8:
        return 'down'
    return 'stable'


def get_progress_over_time(project_id: int = None, days: int = 30) -> List[Dict[str, Any]]:
    """
    Récupère l'évolution de la progression dans le temps.
    """
    # Simuler des données de progression (dans un vrai système, 
    # on aurait un historique des snapshots)
    conn = crud.get_connection()
    cursor = conn.cursor()
    
    data = []
    for i in range(days, -1, -1):
        check_date = date.today() - timedelta(days=i)
        
        query = '''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'COMPLETED' OR completed_at <= ? THEN 1 ELSE 0 END) as completed
            FROM tasks
        '''
        params = [check_date.isoformat()]
        
        if project_id:
            query += " WHERE project_id = ?"
            params.append(project_id)
        
        cursor.execute(query, params)
        row = cursor.fetchone()
        
        if row and row['total'] > 0:
            progress = (row['completed'] / row['total']) * 100
        else:
            progress = 0
        
        data.append({
            'date': check_date.isoformat(),
            'progress': round(progress, 1)
        })
    
    conn.close()
    return data


def get_workload_distribution() -> Dict[str, Any]:
    """
    Analyse la distribution de la charge de travail.
    """
    members = crud.get_member_performance()
    
    if not members:
        return {
            'balanced': True,
            'message': 'Aucun membre actif',
            'distribution': []
        }
    
    total_tasks = sum(m.total_tasks for m in members)
    avg_tasks = total_tasks / len(members) if members else 0
    
    distribution = []
    max_deviation = 0
    
    for member in members:
        deviation = abs(member.total_tasks - avg_tasks)
        max_deviation = max(max_deviation, deviation)
        
        distribution.append({
            'name': member.user_name,
            'tasks': member.total_tasks,
            'completed': member.completed_tasks,
            'completion_rate': member.completion_rate
        })
    
    # La charge est déséquilibrée si l'écart max dépasse 50% de la moyenne
    balanced = max_deviation <= (avg_tasks * 0.5) if avg_tasks > 0 else True
    
    return {
        'balanced': balanced,
        'message': 'Charge équilibrée' if balanced else 'Charge déséquilibrée',
        'average_tasks': round(avg_tasks, 1),
        'distribution': distribution
    }


def get_deadline_forecast(project_id: int) -> Dict[str, Any]:
    """
    Prévoit si le projet sera terminé à temps.
    """
    project = crud.get_project_by_id(project_id)
    stats = crud.get_project_stats(project_id)
    velocity = get_team_velocity()
    
    if not project or stats['total_tasks'] == 0:
        return {
            'on_track': None,
            'message': 'Données insuffisantes'
        }
    
    remaining_tasks = stats['total_tasks'] - stats['completed_tasks']
    weekly_velocity = velocity['average_velocity']
    
    if weekly_velocity > 0:
        weeks_needed = remaining_tasks / weekly_velocity
        estimated_completion = date.today() + timedelta(weeks=weeks_needed)
    else:
        estimated_completion = None
    
    if project.end_date:
        end_date = datetime.strptime(project.end_date, "%Y-%m-%d").date() \
            if isinstance(project.end_date, str) else project.end_date
        
        if estimated_completion:
            on_track = estimated_completion <= end_date
            days_diff = (end_date - estimated_completion).days
        else:
            on_track = False
            days_diff = None
    else:
        on_track = None
        days_diff = None
    
    return {
        'on_track': on_track,
        'estimated_completion': estimated_completion.isoformat() if estimated_completion else None,
        'days_difference': days_diff,
        'remaining_tasks': remaining_tasks,
        'weekly_velocity': weekly_velocity,
        'message': _get_forecast_message(on_track, days_diff)
    }


def _get_forecast_message(on_track: bool, days_diff: int) -> str:
    """Génère un message de prévision."""
    if on_track is None:
        return "Impossible de faire une prévision"
    
    if on_track:
        if days_diff and days_diff > 0:
            return f"En avance d'environ {days_diff} jours"
        return "Dans les délais"
    else:
        if days_diff and days_diff < 0:
            return f"En retard d'environ {abs(days_diff)} jours"
        return "Risque de retard"
