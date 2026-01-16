"""
Service de gestion des tâches.
"""

from datetime import date, datetime
from typing import List, Optional, Dict, Any
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import crud
from database.models import Task, TaskComment


def create_new_task(project_id: int, title: str, description: str = None,
                    priority: str = "MEDIUM", assigned_to: int = None,
                    deadline: date = None, milestone_id: int = None,
                    estimated_hours: float = None) -> Optional[int]:
    """Crée une nouvelle tâche avec validation."""
    if not title or len(title.strip()) < 3:
        raise ValueError("Le titre de la tâche doit contenir au moins 3 caractères.")
    
    valid_priorities = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    if priority not in valid_priorities:
        raise ValueError(f"Priorité invalide. Valeurs possibles: {', '.join(valid_priorities)}")
    
    return crud.create_task(
        project_id=project_id,
        title=title.strip(),
        description=description,
        priority=priority,
        assigned_to=assigned_to,
        deadline=deadline,
        milestone_id=milestone_id,
        estimated_hours=estimated_hours
    )


def get_task_details(task_id: int) -> Optional[Task]:
    """Récupère les détails complets d'une tâche."""
    return crud.get_task_by_id(task_id)


def get_all_tasks_list(project_id: int = None, status: str = None,
                       assigned_to: int = None) -> List[Task]:
    """Récupère les tâches avec filtres."""
    return crud.get_all_tasks(project_id=project_id, status=status, assigned_to=assigned_to)


def get_user_assigned_tasks(user_id: int, status: str = None) -> List[Task]:
    """Récupère les tâches assignées à un utilisateur."""
    return crud.get_user_tasks(user_id, status=status)


def get_overdue_tasks_list() -> List[Task]:
    """Récupère les tâches en retard."""
    return crud.get_overdue_tasks()


def update_task_info(task_id: int, user_id: int = None, **kwargs) -> bool:
    """Met à jour les informations d'une tâche."""
    if 'title' in kwargs and len(kwargs['title'].strip()) < 3:
        raise ValueError("Le titre de la tâche doit contenir au moins 3 caractères.")
    
    if 'priority' in kwargs:
        valid_priorities = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        if kwargs['priority'] not in valid_priorities:
            raise ValueError(f"Priorité invalide. Valeurs possibles: {', '.join(valid_priorities)}")
    
    if 'status' in kwargs:
        valid_statuses = ["TODO", "IN_PROGRESS", "REVIEW", "COMPLETED", "BLOCKED"]
        if kwargs['status'] not in valid_statuses:
            raise ValueError(f"Statut invalide. Valeurs possibles: {', '.join(valid_statuses)}")
    
    return crud.update_task(task_id, user_id=user_id, **kwargs)


def update_task_status(task_id: int, status: str, user_id: int = None) -> bool:
    """Met à jour le statut d'une tâche."""
    valid_statuses = ["TODO", "IN_PROGRESS", "REVIEW", "COMPLETED", "BLOCKED"]
    if status not in valid_statuses:
        raise ValueError(f"Statut invalide. Valeurs possibles: {', '.join(valid_statuses)}")
    
    return crud.update_task(task_id, user_id=user_id, status=status)


def update_task_progress_value(task_id: int, progress: int, user_id: int = None,
                               comment: str = None) -> bool:
    """Met à jour la progression d'une tâche."""
    if progress < 0 or progress > 100:
        raise ValueError("La progression doit être entre 0 et 100%.")
    
    return crud.update_task_progress(task_id, progress, user_id=user_id, comment=comment)


def assign_task_to_member(task_id: int, member_id: int) -> bool:
    """Assigne une tâche à un membre."""
    return crud.update_task(task_id, assigned_to=member_id)


def delete_task_by_id(task_id: int) -> bool:
    """Supprime une tâche."""
    return crud.delete_task(task_id)


def add_comment_to_task(task_id: int, user_id: int, comment: str) -> Optional[int]:
    """Ajoute un commentaire à une tâche."""
    if not comment or len(comment.strip()) < 1:
        raise ValueError("Le commentaire ne peut pas être vide.")
    
    return crud.add_task_comment(task_id, user_id, comment.strip())


def get_task_comments_list(task_id: int) -> List[TaskComment]:
    """Récupère les commentaires d'une tâche."""
    return crud.get_task_comments(task_id)


def get_tasks_summary_by_project(project_id: int) -> Dict[str, Any]:
    """Génère un résumé des tâches d'un projet."""
    tasks = crud.get_all_tasks(project_id=project_id)
    
    summary = {
        'total': len(tasks),
        'by_status': {
            'TODO': 0,
            'IN_PROGRESS': 0,
            'REVIEW': 0,
            'COMPLETED': 0,
            'BLOCKED': 0
        },
        'by_priority': {
            'LOW': 0,
            'MEDIUM': 0,
            'HIGH': 0,
            'CRITICAL': 0
        },
        'overdue': 0,
        'avg_progress': 0.0
    }
    
    total_progress = 0
    for task in tasks:
        summary['by_status'][task.status] = summary['by_status'].get(task.status, 0) + 1
        summary['by_priority'][task.priority] = summary['by_priority'].get(task.priority, 0) + 1
        if task.is_overdue:
            summary['overdue'] += 1
        total_progress += task.progress
    
    if tasks:
        summary['avg_progress'] = round(total_progress / len(tasks), 1)
    
    return summary


def get_tasks_grouped_by_status(project_id: int = None) -> Dict[str, List[Task]]:
    """Récupère les tâches groupées par statut."""
    tasks = crud.get_all_tasks(project_id=project_id)
    
    grouped = {
        'TODO': [],
        'IN_PROGRESS': [],
        'REVIEW': [],
        'COMPLETED': [],
        'BLOCKED': []
    }
    
    for task in tasks:
        if task.status in grouped:
            grouped[task.status].append(task)
    
    return grouped


def can_user_update_task(task: Task, user_id: int, is_admin: bool) -> bool:
    """Vérifie si un utilisateur peut modifier une tâche."""
    if is_admin:
        return True
    
    # Un membre peut seulement modifier ses propres tâches
    return task.assigned_to == user_id


def get_priority_color(priority: str) -> str:
    """Retourne la couleur associée à une priorité."""
    colors = {
        'LOW': '#48bb78',      # vert
        'MEDIUM': '#4299e1',   # bleu
        'HIGH': '#ed8936',     # orange
        'CRITICAL': '#f56565'  # rouge
    }
    return colors.get(priority, '#718096')


def get_status_color(status: str) -> str:
    """Retourne la couleur associée à un statut."""
    colors = {
        'TODO': '#718096',        # gris
        'IN_PROGRESS': '#4299e1', # bleu
        'REVIEW': '#9f7aea',      # violet
        'COMPLETED': '#48bb78',   # vert
        'BLOCKED': '#f56565'      # rouge
    }
    return colors.get(status, '#718096')
