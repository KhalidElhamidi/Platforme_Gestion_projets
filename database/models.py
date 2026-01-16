"""
Modèles de données pour l'application de gestion de projets.
Utilise des dataclasses Python pour représenter les entités.
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, List


@dataclass
class User:
    """Représente un utilisateur du système."""
    id: int
    username: str
    email: str
    password_hash: str
    role: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def from_row(cls, row):
        """Crée un User à partir d'une ligne de base de données."""
        if row is None:
            return None
        return cls(
            id=row['id'],
            username=row['username'],
            email=row['email'],
            password_hash=row['password_hash'],
            role=row['role'],
            full_name=row['full_name'],
            avatar_url=row['avatar_url'],
            is_active=bool(row['is_active']),
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )


@dataclass
class Project:
    """Représente un projet."""
    id: int
    name: str
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: str = "NOT_STARTED"
    budget: Optional[float] = None
    created_by: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    # Champs calculés
    progress: float = 0.0
    task_count: int = 0
    member_count: int = 0

    @classmethod
    def from_row(cls, row):
        """Crée un Project à partir d'une ligne de base de données."""
        if row is None:
            return None
        return cls(
            id=row['id'],
            name=row['name'],
            description=row['description'],
            start_date=row['start_date'],
            end_date=row['end_date'],
            status=row['status'],
            budget=row['budget'],
            created_by=row['created_by'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )


@dataclass
class Milestone:
    """Représente un jalon (milestone) d'un projet."""
    id: int
    project_id: int
    name: str
    description: Optional[str] = None
    due_date: Optional[date] = None
    status: str = "PENDING"
    created_at: Optional[datetime] = None
    # Champs calculés
    progress: float = 0.0
    task_count: int = 0

    @classmethod
    def from_row(cls, row):
        """Crée un Milestone à partir d'une ligne de base de données."""
        if row is None:
            return None
        return cls(
            id=row['id'],
            project_id=row['project_id'],
            name=row['name'],
            description=row['description'],
            due_date=row['due_date'],
            status=row['status'],
            created_at=row['created_at']
        )


@dataclass
class Task:
    """Représente une tâche."""
    id: int
    project_id: int
    title: str
    milestone_id: Optional[int] = None
    description: Optional[str] = None
    priority: str = "MEDIUM"
    status: str = "TODO"
    progress: int = 0
    assigned_to: Optional[int] = None
    deadline: Optional[date] = None
    estimated_hours: Optional[float] = None
    actual_hours: Optional[float] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    # Champs pour l'affichage
    assigned_to_name: Optional[str] = None
    project_name: Optional[str] = None
    is_overdue: bool = False

    @classmethod
    def from_row(cls, row):
        """Crée une Task à partir d'une ligne de base de données."""
        if row is None:
            return None
        task = cls(
            id=row['id'],
            project_id=row['project_id'],
            title=row['title'],
            milestone_id=row['milestone_id'],
            description=row['description'],
            priority=row['priority'],
            status=row['status'],
            progress=row['progress'],
            assigned_to=row['assigned_to'],
            deadline=row['deadline'],
            estimated_hours=row['estimated_hours'],
            actual_hours=row['actual_hours'],
            created_at=row['created_at'],
            updated_at=row['updated_at'],
            completed_at=row['completed_at']
        )
        # Vérifier si la tâche est en retard
        if task.deadline and task.status != "COMPLETED":
            deadline_date = datetime.strptime(task.deadline, "%Y-%m-%d").date() if isinstance(task.deadline, str) else task.deadline
            task.is_overdue = deadline_date < date.today()
        return task


@dataclass
class ProjectMember:
    """Représente l'association d'un membre à un projet."""
    id: int
    project_id: int
    user_id: int
    role_in_project: str = "member"
    assigned_at: Optional[datetime] = None
    # Champs pour l'affichage
    user_name: Optional[str] = None
    user_email: Optional[str] = None

    @classmethod
    def from_row(cls, row):
        """Crée un ProjectMember à partir d'une ligne de base de données."""
        if row is None:
            return None
        return cls(
            id=row['id'],
            project_id=row['project_id'],
            user_id=row['user_id'],
            role_in_project=row['role_in_project'],
            assigned_at=row['assigned_at']
        )


@dataclass
class TaskComment:
    """Représente un commentaire sur une tâche."""
    id: int
    task_id: int
    user_id: int
    comment: str
    created_at: Optional[datetime] = None
    # Champs pour l'affichage
    user_name: Optional[str] = None

    @classmethod
    def from_row(cls, row):
        """Crée un TaskComment à partir d'une ligne de base de données."""
        if row is None:
            return None
        return cls(
            id=row['id'],
            task_id=row['task_id'],
            user_id=row['user_id'],
            comment=row['comment'],
            created_at=row['created_at']
        )


@dataclass
class ActivityLog:
    """Représente une entrée dans le journal d'activité."""
    id: int
    user_id: Optional[int]
    action: str
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    details: Optional[str] = None
    timestamp: Optional[datetime] = None
    # Champs pour l'affichage
    user_name: Optional[str] = None

    @classmethod
    def from_row(cls, row):
        """Crée un ActivityLog à partir d'une ligne de base de données."""
        if row is None:
            return None
        return cls(
            id=row['id'],
            user_id=row['user_id'],
            action=row['action'],
            entity_type=row['entity_type'],
            entity_id=row['entity_id'],
            details=row['details'],
            timestamp=row['timestamp']
        )


@dataclass
class DashboardStats:
    """Statistiques pour le tableau de bord."""
    total_projects: int = 0
    active_projects: int = 0
    completed_projects: int = 0
    total_tasks: int = 0
    completed_tasks: int = 0
    in_progress_tasks: int = 0
    overdue_tasks: int = 0
    total_members: int = 0
    overall_progress: float = 0.0


@dataclass
class MemberPerformance:
    """Performance d'un membre de l'équipe."""
    user_id: int
    user_name: str
    total_tasks: int = 0
    completed_tasks: int = 0
    in_progress_tasks: int = 0
    overdue_tasks: int = 0
    completion_rate: float = 0.0
    average_progress: float = 0.0
