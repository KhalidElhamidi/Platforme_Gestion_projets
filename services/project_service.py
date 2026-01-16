"""
Service de gestion des projets.
"""

from datetime import date, datetime
from typing import List, Optional, Dict, Any
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import crud
from database.models import Project, Milestone


def create_new_project(name: str, description: str = None, 
                       start_date: date = None, end_date: date = None,
                       created_by: int = None, budget: float = None) -> Optional[int]:
    """Crée un nouveau projet avec validation."""
    if not name or len(name.strip()) < 3:
        raise ValueError("Le nom du projet doit contenir au moins 3 caractères.")
    
    if start_date and end_date and start_date > end_date:
        raise ValueError("La date de début doit être antérieure à la date de fin.")
    
    return crud.create_project(
        name=name.strip(),
        description=description,
        start_date=start_date,
        end_date=end_date,
        created_by=created_by,
        budget=budget
    )


def get_project_details(project_id: int) -> Optional[Project]:
    """Récupère les détails complets d'un projet."""
    return crud.get_project_by_id(project_id)


def get_all_projects_with_stats() -> List[Project]:
    """Récupère tous les projets avec leurs statistiques."""
    return crud.get_all_projects()


def get_user_projects_list(user_id: int) -> List[Project]:
    """Récupère les projets d'un utilisateur."""
    return crud.get_user_projects(user_id)


def update_project_info(project_id: int, **kwargs) -> bool:
    """Met à jour les informations d'un projet."""
    if 'name' in kwargs and len(kwargs['name'].strip()) < 3:
        raise ValueError("Le nom du projet doit contenir au moins 3 caractères.")
    
    if 'start_date' in kwargs and 'end_date' in kwargs:
        if kwargs['start_date'] and kwargs['end_date'] and kwargs['start_date'] > kwargs['end_date']:
            raise ValueError("La date de début doit être antérieure à la date de fin.")
    
    return crud.update_project(project_id, **kwargs)


def update_project_status(project_id: int, status: str) -> bool:
    """Met à jour le statut d'un projet."""
    valid_statuses = ["NOT_STARTED", "IN_PROGRESS", "ON_HOLD", "COMPLETED", "CANCELLED"]
    if status not in valid_statuses:
        raise ValueError(f"Statut invalide. Valeurs possibles: {', '.join(valid_statuses)}")
    
    return crud.update_project(project_id, status=status)


def delete_project_and_related(project_id: int) -> bool:
    """Supprime un projet et toutes ses données associées."""
    return crud.delete_project(project_id)


def create_project_milestone(project_id: int, name: str, 
                            description: str = None, due_date: date = None) -> Optional[int]:
    """Crée un milestone pour un projet."""
    if not name or len(name.strip()) < 2:
        raise ValueError("Le nom du milestone doit contenir au moins 2 caractères.")
    
    return crud.create_milestone(
        project_id=project_id,
        name=name.strip(),
        description=description,
        due_date=due_date
    )


def get_project_milestones_list(project_id: int) -> List[Milestone]:
    """Récupère les milestones d'un projet."""
    return crud.get_project_milestones(project_id)


def update_milestone_info(milestone_id: int, **kwargs) -> bool:
    """Met à jour un milestone."""
    return crud.update_milestone(milestone_id, **kwargs)


def delete_milestone(milestone_id: int) -> bool:
    """Supprime un milestone."""
    return crud.delete_milestone(milestone_id)


def get_project_summary(project_id: int) -> Dict[str, Any]:
    """Génère un résumé complet d'un projet."""
    project = crud.get_project_by_id(project_id)
    if not project:
        return None
    
    stats = crud.get_project_stats(project_id)
    milestones = crud.get_project_milestones(project_id)
    members = crud.get_project_members(project_id)
    
    return {
        'project': project,
        'stats': stats,
        'milestones': milestones,
        'members': members,
        'is_on_track': stats['overdue_tasks'] == 0,
        'days_remaining': _calculate_days_remaining(project.end_date) if project.end_date else None
    }


def _calculate_days_remaining(end_date) -> int:
    """Calcule le nombre de jours restants avant la fin du projet."""
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
    return (end_date - date.today()).days


def get_projects_by_status() -> Dict[str, List[Project]]:
    """Récupère les projets groupés par statut."""
    all_projects = crud.get_all_projects()
    grouped = {
        'NOT_STARTED': [],
        'IN_PROGRESS': [],
        'ON_HOLD': [],
        'COMPLETED': [],
        'CANCELLED': []
    }
    
    for project in all_projects:
        if project.status in grouped:
            grouped[project.status].append(project)
    
    return grouped
