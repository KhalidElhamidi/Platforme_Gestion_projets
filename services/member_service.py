"""
Service de gestion des membres.
"""

from datetime import date
from typing import List, Optional, Dict, Any
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import crud
from database.models import User, ProjectMember
from config import ROLE_ADMIN, ROLE_PROJECT_MANAGER, ROLE_MEMBER


def create_new_member(username: str, email: str, password: str,
                      full_name: str = None, role: str = ROLE_MEMBER) -> Optional[int]:
    """Crée un nouveau membre avec validation."""
    if not username or len(username.strip()) < 3:
        raise ValueError("Le nom d'utilisateur doit contenir au moins 3 caractères.")
    
    if not email or '@' not in email:
        raise ValueError("L'email n'est pas valide.")
    
    if not password or len(password) < 6:
        raise ValueError("Le mot de passe doit contenir au moins 6 caractères.")
    
    valid_roles = [ROLE_ADMIN, ROLE_PROJECT_MANAGER, ROLE_MEMBER]
    if role not in valid_roles:
        raise ValueError(f"Rôle invalide. Valeurs possibles: {', '.join(valid_roles)}")
    
    return crud.create_user(
        username=username.strip().lower(),
        email=email.strip().lower(),
        password=password,
        role=role,
        full_name=full_name
    )


def get_member_details(user_id: int) -> Optional[User]:
    """Récupère les détails d'un membre."""
    return crud.get_user_by_id(user_id)


def get_all_members_list(include_admins: bool = False) -> List[User]:
    """Récupère tous les membres."""
    if include_admins:
        return crud.get_all_users()
    return crud.get_members()


def update_member_info(user_id: int, **kwargs) -> bool:
    """Met à jour les informations d'un membre."""
    if 'username' in kwargs and len(kwargs['username'].strip()) < 3:
        raise ValueError("Le nom d'utilisateur doit contenir au moins 3 caractères.")
    
    if 'email' in kwargs and '@' not in kwargs['email']:
        raise ValueError("L'email n'est pas valide.")
    
    if 'password' in kwargs and len(kwargs['password']) < 6:
        raise ValueError("Le mot de passe doit contenir au moins 6 caractères.")
    
    return crud.update_user(user_id, **kwargs)


def deactivate_member(user_id: int) -> bool:
    """Désactive un membre."""
    return crud.delete_user(user_id)


def activate_member(user_id: int) -> bool:
    """Réactive un membre."""
    return crud.update_user(user_id, is_active=True)


def assign_member_to_project(project_id: int, user_id: int, 
                             role_in_project: str = "member") -> bool:
    """Assigne un membre à un projet."""
    return crud.add_project_member(project_id, user_id, role_in_project)


def remove_member_from_project(project_id: int, user_id: int) -> bool:
    """Retire un membre d'un projet."""
    return crud.remove_project_member(project_id, user_id)


def get_project_members_list(project_id: int) -> List[ProjectMember]:
    """Récupère les membres d'un projet."""
    return crud.get_project_members(project_id)


def is_member_in_project(project_id: int, user_id: int) -> bool:
    """Vérifie si un membre fait partie d'un projet."""
    return crud.is_project_member(project_id, user_id)


def get_member_workload(user_id: int) -> Dict[str, Any]:
    """Calcule la charge de travail d'un membre."""
    tasks = crud.get_user_tasks(user_id)
    projects = crud.get_user_projects(user_id)
    
    workload = {
        'total_tasks': len(tasks),
        'in_progress': 0,
        'todo': 0,
        'completed': 0,
        'overdue': 0,
        'total_projects': len(projects),
        'tasks_by_priority': {
            'LOW': 0,
            'MEDIUM': 0,
            'HIGH': 0,
            'CRITICAL': 0
        }
    }
    
    for task in tasks:
        if task.status == 'IN_PROGRESS':
            workload['in_progress'] += 1
        elif task.status == 'TODO':
            workload['todo'] += 1
        elif task.status == 'COMPLETED':
            workload['completed'] += 1
        
        if task.is_overdue:
            workload['overdue'] += 1
        
        workload['tasks_by_priority'][task.priority] = \
            workload['tasks_by_priority'].get(task.priority, 0) + 1
    
    return workload


def get_members_not_in_project(project_id: int) -> List[User]:
    """Récupère les membres qui ne font pas partie d'un projet."""
    all_members = crud.get_members()
    project_member_ids = [m.user_id for m in crud.get_project_members(project_id)]
    
    return [m for m in all_members if m.id not in project_member_ids]


def get_members_for_task_assignment(project_id: int) -> List[User]:
    """Récupère les membres disponibles pour l'assignation de tâches d'un projet."""
    # Retourne les membres du projet + les admins
    project_members = crud.get_project_members(project_id)
    member_ids = [m.user_id for m in project_members]
    
    # Ajouter les admins qui peuvent aussi être assignés
    all_users = crud.get_all_users()
    
    available = []
    for user in all_users:
        if user.id in member_ids or user.role == ROLE_ADMIN:
            available.append(user)
    
    return available
