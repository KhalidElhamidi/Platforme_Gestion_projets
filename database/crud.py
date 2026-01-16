"""
Opérations CRUD (Create, Read, Update, Delete) pour la base de données.
"""

import sqlite3
from datetime import datetime, date
from typing import List, Optional, Dict, Any
import bcrypt

from .db_setup import get_connection
from .models import (
    User, Project, Milestone, Task, ProjectMember, 
    TaskComment, ActivityLog, DashboardStats, MemberPerformance
)


# ================== UTILISATEURS ==================

def create_user(username: str, email: str, password: str, role: str = "member", 
                full_name: str = None) -> Optional[int]:
    """Crée un nouvel utilisateur."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, role, full_name)
            VALUES (?, ?, ?, ?, ?)
        ''', (username, email, password_hash, role, full_name))
        conn.commit()
        user_id = cursor.lastrowid
        log_activity(user_id, "USER_CREATED", "user", user_id, f"Utilisateur {username} créé")
        return user_id
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()


def get_user_by_id(user_id: int) -> Optional[User]:
    """Récupère un utilisateur par son ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return User.from_row(row)


def get_user_by_email(email: str) -> Optional[User]:
    """Récupère un utilisateur par son email."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    row = cursor.fetchone()
    conn.close()
    return User.from_row(row)


def get_user_by_username(username: str) -> Optional[User]:
    """Récupère un utilisateur par son nom d'utilisateur."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    return User.from_row(row)


def get_all_users(role: str = None, active_only: bool = True) -> List[User]:
    """Récupère tous les utilisateurs."""
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE 1=1"
    params = []
    if role:
        query += " AND role = ?"
        params.append(role)
    if active_only:
        query += " AND is_active = 1"
    query += " ORDER BY full_name, username"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [User.from_row(row) for row in rows]


def get_members() -> List[User]:
    """Récupère tous les membres (non-admin)."""
    return get_all_users(role="member")


def update_user(user_id: int, **kwargs) -> bool:
    """Met à jour un utilisateur."""
    conn = get_connection()
    cursor = conn.cursor()
    
    allowed_fields = ['username', 'email', 'role', 'full_name', 'avatar_url', 'is_active']
    updates = []
    values = []
    
    for field, value in kwargs.items():
        if field in allowed_fields:
            updates.append(f"{field} = ?")
            values.append(value)
    
    if 'password' in kwargs:
        updates.append("password_hash = ?")
        values.append(bcrypt.hashpw(kwargs['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8'))
    
    if not updates:
        return False
    
    updates.append("updated_at = ?")
    values.append(datetime.now().isoformat())
    values.append(user_id)
    
    cursor.execute(f"UPDATE users SET {', '.join(updates)} WHERE id = ?", values)
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    
    if success:
        log_activity(user_id, "USER_UPDATED", "user", user_id)
    
    return success


def delete_user(user_id: int) -> bool:
    """Supprime un utilisateur (désactivation)."""
    return update_user(user_id, is_active=False)


def verify_password(email: str, password: str) -> Optional[User]:
    """Vérifie le mot de passe d'un utilisateur."""
    user = get_user_by_email(email)
    if user and bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
        return user
    # Essayer aussi avec le nom d'utilisateur
    user = get_user_by_username(email)
    if user and bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
        return user
    return None


# ================== PROJETS ==================

def create_project(name: str, description: str = None, start_date: date = None,
                   end_date: date = None, created_by: int = None, budget: float = None) -> Optional[int]:
    """Crée un nouveau projet."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO projects (name, description, start_date, end_date, created_by, budget)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, description, start_date, end_date, created_by, budget))
        conn.commit()
        project_id = cursor.lastrowid
        log_activity(created_by, "PROJECT_CREATED", "project", project_id, f"Projet '{name}' créé")
        return project_id
    except Exception as e:
        print(f"Erreur création projet: {e}")
        return None
    finally:
        conn.close()


def get_project_by_id(project_id: int) -> Optional[Project]:
    """Récupère un projet par son ID avec les statistiques."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
    row = cursor.fetchone()
    if row:
        project = Project.from_row(row)
        # Calculer les statistiques
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE project_id = ?", (project_id,))
        project.task_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM project_members WHERE project_id = ?", (project_id,))
        project.member_count = cursor.fetchone()[0]
        project.progress = calculate_project_progress(project_id)
        conn.close()
        return project
    conn.close()
    return None


def get_all_projects(status: str = None) -> List[Project]:
    """Récupère tous les projets."""
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM projects WHERE 1=1"
    params = []
    if status:
        query += " AND status = ?"
        params.append(status)
    query += " ORDER BY created_at DESC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    projects = []
    for row in rows:
        project = Project.from_row(row)
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE project_id = ?", (project.id,))
        project.task_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM project_members WHERE project_id = ?", (project.id,))
        project.member_count = cursor.fetchone()[0]
        project.progress = calculate_project_progress(project.id)
        projects.append(project)
    
    conn.close()
    return projects


def get_user_projects(user_id: int) -> List[Project]:
    """Récupère les projets auxquels un utilisateur participe."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT DISTINCT p.* FROM projects p
        LEFT JOIN project_members pm ON p.id = pm.project_id
        WHERE pm.user_id = ? OR p.created_by = ?
        ORDER BY p.created_at DESC
    ''', (user_id, user_id))
    rows = cursor.fetchall()
    
    projects = []
    for row in rows:
        project = Project.from_row(row)
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE project_id = ?", (project.id,))
        project.task_count = cursor.fetchone()[0]
        project.progress = calculate_project_progress(project.id)
        projects.append(project)
    
    conn.close()
    return projects


def update_project(project_id: int, **kwargs) -> bool:
    """Met à jour un projet."""
    conn = get_connection()
    cursor = conn.cursor()
    
    allowed_fields = ['name', 'description', 'start_date', 'end_date', 'status', 'budget']
    updates = []
    values = []
    
    for field, value in kwargs.items():
        if field in allowed_fields:
            updates.append(f"{field} = ?")
            values.append(value)
    
    if not updates:
        return False
    
    updates.append("updated_at = ?")
    values.append(datetime.now().isoformat())
    values.append(project_id)
    
    cursor.execute(f"UPDATE projects SET {', '.join(updates)} WHERE id = ?", values)
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    
    if success:
        log_activity(None, "PROJECT_UPDATED", "project", project_id)
    
    return success


def delete_project(project_id: int) -> bool:
    """Supprime un projet."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    
    if success:
        log_activity(None, "PROJECT_DELETED", "project", project_id)
    
    return success


def calculate_project_progress(project_id: int) -> float:
    """Calcule le pourcentage d'avancement d'un projet basé sur ses tâches."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT COUNT(*) as total, 
               SUM(CASE WHEN status = 'COMPLETED' THEN 1 ELSE 0 END) as completed,
               AVG(progress) as avg_progress
        FROM tasks WHERE project_id = ?
    ''', (project_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row and row['total'] > 0:
        # Moyenne pondérée entre tâches complétées et progression moyenne
        completed_ratio = (row['completed'] / row['total']) * 100
        avg_progress = row['avg_progress'] or 0
        return round((completed_ratio + avg_progress) / 2, 1)
    return 0.0


# ================== MILESTONES ==================

def create_milestone(project_id: int, name: str, description: str = None, 
                     due_date: date = None) -> Optional[int]:
    """Crée un nouveau milestone."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO milestones (project_id, name, description, due_date)
            VALUES (?, ?, ?, ?)
        ''', (project_id, name, description, due_date))
        conn.commit()
        milestone_id = cursor.lastrowid
        log_activity(None, "MILESTONE_CREATED", "milestone", milestone_id, f"Milestone '{name}' créé")
        return milestone_id
    except Exception as e:
        print(f"Erreur création milestone: {e}")
        return None
    finally:
        conn.close()


def get_project_milestones(project_id: int) -> List[Milestone]:
    """Récupère les milestones d'un projet."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM milestones WHERE project_id = ? ORDER BY due_date, created_at
    ''', (project_id,))
    rows = cursor.fetchall()
    
    milestones = []
    for row in rows:
        milestone = Milestone.from_row(row)
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE milestone_id = ?", (milestone.id,))
        milestone.task_count = cursor.fetchone()[0]
        cursor.execute("SELECT AVG(progress) FROM tasks WHERE milestone_id = ?", (milestone.id,))
        avg = cursor.fetchone()[0]
        milestone.progress = round(avg, 1) if avg else 0.0
        milestones.append(milestone)
    
    conn.close()
    return milestones


def update_milestone(milestone_id: int, **kwargs) -> bool:
    """Met à jour un milestone."""
    conn = get_connection()
    cursor = conn.cursor()
    
    allowed_fields = ['name', 'description', 'due_date', 'status']
    updates = []
    values = []
    
    for field, value in kwargs.items():
        if field in allowed_fields:
            updates.append(f"{field} = ?")
            values.append(value)
    
    if not updates:
        return False
    
    values.append(milestone_id)
    cursor.execute(f"UPDATE milestones SET {', '.join(updates)} WHERE id = ?", values)
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success


def delete_milestone(milestone_id: int) -> bool:
    """Supprime un milestone."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM milestones WHERE id = ?", (milestone_id,))
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success


# ================== TÂCHES ==================

def create_task(project_id: int, title: str, description: str = None, 
                priority: str = "MEDIUM", assigned_to: int = None,
                deadline: date = None, milestone_id: int = None,
                estimated_hours: float = None) -> Optional[int]:
    """Crée une nouvelle tâche."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO tasks (project_id, milestone_id, title, description, priority, 
                             assigned_to, deadline, estimated_hours)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (project_id, milestone_id, title, description, priority, 
              assigned_to, deadline, estimated_hours))
        conn.commit()
        task_id = cursor.lastrowid
        log_activity(assigned_to, "TASK_CREATED", "task", task_id, f"Tâche '{title}' créée")
        return task_id
    except Exception as e:
        print(f"Erreur création tâche: {e}")
        return None
    finally:
        conn.close()


def get_task_by_id(task_id: int) -> Optional[Task]:
    """Récupère une tâche par son ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT t.*, u.full_name as assigned_name, p.name as project_name
        FROM tasks t
        LEFT JOIN users u ON t.assigned_to = u.id
        LEFT JOIN projects p ON t.project_id = p.id
        WHERE t.id = ?
    ''', (task_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        task = Task.from_row(row)
        task.assigned_to_name = row['assigned_name']
        task.project_name = row['project_name']
        return task
    return None


def get_all_tasks(project_id: int = None, status: str = None, 
                  assigned_to: int = None) -> List[Task]:
    """Récupère les tâches avec filtres optionnels."""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = '''
        SELECT t.*, u.full_name as assigned_name, p.name as project_name
        FROM tasks t
        LEFT JOIN users u ON t.assigned_to = u.id
        LEFT JOIN projects p ON t.project_id = p.id
        WHERE 1=1
    '''
    params = []
    
    if project_id:
        query += " AND t.project_id = ?"
        params.append(project_id)
    if status:
        query += " AND t.status = ?"
        params.append(status)
    if assigned_to:
        query += " AND t.assigned_to = ?"
        params.append(assigned_to)
    
    query += " ORDER BY t.deadline, t.priority DESC, t.created_at DESC"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    tasks = []
    for row in rows:
        task = Task.from_row(row)
        task.assigned_to_name = row['assigned_name']
        task.project_name = row['project_name']
        tasks.append(task)
    
    return tasks


def get_user_tasks(user_id: int, status: str = None) -> List[Task]:
    """Récupère les tâches assignées à un utilisateur."""
    return get_all_tasks(assigned_to=user_id, status=status)


def get_overdue_tasks() -> List[Task]:
    """Récupère les tâches en retard."""
    conn = get_connection()
    cursor = conn.cursor()
    today = date.today().isoformat()
    cursor.execute('''
        SELECT t.*, u.full_name as assigned_name, p.name as project_name
        FROM tasks t
        LEFT JOIN users u ON t.assigned_to = u.id
        LEFT JOIN projects p ON t.project_id = p.id
        WHERE t.deadline < ? AND t.status != 'COMPLETED'
        ORDER BY t.deadline
    ''', (today,))
    rows = cursor.fetchall()
    conn.close()
    
    tasks = []
    for row in rows:
        task = Task.from_row(row)
        task.assigned_to_name = row['assigned_name']
        task.project_name = row['project_name']
        task.is_overdue = True
        tasks.append(task)
    
    return tasks


def update_task(task_id: int, user_id: int = None, **kwargs) -> bool:
    """Met à jour une tâche."""
    conn = get_connection()
    cursor = conn.cursor()
    
    allowed_fields = ['title', 'description', 'priority', 'status', 'progress',
                      'assigned_to', 'deadline', 'milestone_id', 
                      'estimated_hours', 'actual_hours']
    updates = []
    values = []
    
    for field, value in kwargs.items():
        if field in allowed_fields:
            updates.append(f"{field} = ?")
            values.append(value)
    
    if not updates:
        return False
    
    # Marquer comme terminé si le statut change à COMPLETED
    if 'status' in kwargs and kwargs['status'] == 'COMPLETED':
        updates.append("completed_at = ?")
        values.append(datetime.now().isoformat())
        updates.append("progress = ?")
        values.append(100)
    
    updates.append("updated_at = ?")
    values.append(datetime.now().isoformat())
    values.append(task_id)
    
    cursor.execute(f"UPDATE tasks SET {', '.join(updates)} WHERE id = ?", values)
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    
    if success:
        log_activity(user_id, "TASK_UPDATED", "task", task_id)
    
    return success


def update_task_progress(task_id: int, progress: int, user_id: int = None, 
                         comment: str = None) -> bool:
    """Met à jour la progression d'une tâche."""
    status = "COMPLETED" if progress >= 100 else "IN_PROGRESS" if progress > 0 else "TODO"
    success = update_task(task_id, user_id=user_id, progress=progress, status=status)
    
    if success and comment:
        add_task_comment(task_id, user_id, comment)
    
    return success


def delete_task(task_id: int) -> bool:
    """Supprime une tâche."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    
    if success:
        log_activity(None, "TASK_DELETED", "task", task_id)
    
    return success


# ================== MEMBRES DE PROJET ==================

def add_project_member(project_id: int, user_id: int, 
                       role_in_project: str = "member") -> bool:
    """Ajoute un membre à un projet."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO project_members (project_id, user_id, role_in_project)
            VALUES (?, ?, ?)
        ''', (project_id, user_id, role_in_project))
        conn.commit()
        log_activity(user_id, "MEMBER_ADDED", "project", project_id)
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def remove_project_member(project_id: int, user_id: int) -> bool:
    """Retire un membre d'un projet."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM project_members WHERE project_id = ? AND user_id = ?
    ''', (project_id, user_id))
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    
    if success:
        log_activity(user_id, "MEMBER_REMOVED", "project", project_id)
    
    return success


def get_project_members(project_id: int) -> List[ProjectMember]:
    """Récupère les membres d'un projet."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT pm.*, u.full_name, u.email as user_email
        FROM project_members pm
        JOIN users u ON pm.user_id = u.id
        WHERE pm.project_id = ?
        ORDER BY u.full_name
    ''', (project_id,))
    rows = cursor.fetchall()
    conn.close()
    
    members = []
    for row in rows:
        member = ProjectMember.from_row(row)
        member.user_name = row['full_name']
        member.user_email = row['user_email']
        members.append(member)
    
    return members


def is_project_member(project_id: int, user_id: int) -> bool:
    """Vérifie si un utilisateur est membre d'un projet."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT COUNT(*) FROM project_members 
        WHERE project_id = ? AND user_id = ?
    ''', (project_id, user_id))
    count = cursor.fetchone()[0]
    conn.close()
    return count > 0


# ================== COMMENTAIRES ==================

def add_task_comment(task_id: int, user_id: int, comment: str) -> Optional[int]:
    """Ajoute un commentaire à une tâche."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO task_comments (task_id, user_id, comment)
            VALUES (?, ?, ?)
        ''', (task_id, user_id, comment))
        conn.commit()
        comment_id = cursor.lastrowid
        return comment_id
    except Exception as e:
        print(f"Erreur ajout commentaire: {e}")
        return None
    finally:
        conn.close()


def get_task_comments(task_id: int) -> List[TaskComment]:
    """Récupère les commentaires d'une tâche."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT tc.*, u.full_name as user_name
        FROM task_comments tc
        JOIN users u ON tc.user_id = u.id
        WHERE tc.task_id = ?
        ORDER BY tc.created_at DESC
    ''', (task_id,))
    rows = cursor.fetchall()
    conn.close()
    
    comments = []
    for row in rows:
        comment = TaskComment.from_row(row)
        comment.user_name = row['user_name']
        comments.append(comment)
    
    return comments


# ================== JOURNAL D'ACTIVITÉ ==================

def log_activity(user_id: int, action: str, entity_type: str = None, 
                 entity_id: int = None, details: str = None):
    """Enregistre une activité dans le journal."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO activity_log (user_id, action, entity_type, entity_id, details)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, action, entity_type, entity_id, details))
        conn.commit()
    except Exception as e:
        print(f"Erreur log activité: {e}")
    finally:
        conn.close()


def get_recent_activities(limit: int = 20, user_id: int = None) -> List[ActivityLog]:
    """Récupère les activités récentes."""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = '''
        SELECT al.*, u.full_name as user_name
        FROM activity_log al
        LEFT JOIN users u ON al.user_id = u.id
        WHERE 1=1
    '''
    params = []
    
    if user_id:
        query += " AND al.user_id = ?"
        params.append(user_id)
    
    query += f" ORDER BY al.timestamp DESC LIMIT {limit}"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    activities = []
    for row in rows:
        activity = ActivityLog.from_row(row)
        activity.user_name = row['user_name']
        activities.append(activity)
    
    return activities


# ================== STATISTIQUES ==================

def get_dashboard_stats() -> DashboardStats:
    """Récupère les statistiques pour le tableau de bord admin."""
    conn = get_connection()
    cursor = conn.cursor()
    stats = DashboardStats()
    
    # Statistiques des projets
    cursor.execute("SELECT COUNT(*) FROM projects")
    stats.total_projects = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM projects WHERE status = 'IN_PROGRESS'")
    stats.active_projects = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM projects WHERE status = 'COMPLETED'")
    stats.completed_projects = cursor.fetchone()[0]
    
    # Statistiques des tâches
    cursor.execute("SELECT COUNT(*) FROM tasks")
    stats.total_tasks = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'COMPLETED'")
    stats.completed_tasks = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'IN_PROGRESS'")
    stats.in_progress_tasks = cursor.fetchone()[0]
    
    today = date.today().isoformat()
    cursor.execute('''
        SELECT COUNT(*) FROM tasks WHERE deadline < ? AND status != 'COMPLETED'
    ''', (today,))
    stats.overdue_tasks = cursor.fetchone()[0]
    
    # Statistiques des membres
    cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'member' AND is_active = 1")
    stats.total_members = cursor.fetchone()[0]
    
    # Progression globale
    cursor.execute("SELECT AVG(progress) FROM tasks")
    avg = cursor.fetchone()[0]
    stats.overall_progress = round(avg, 1) if avg else 0.0
    
    conn.close()
    return stats


def get_member_performance(user_id: int = None) -> List[MemberPerformance]:
    """Récupère les performances des membres."""
    conn = get_connection()
    cursor = conn.cursor()
    today = date.today().isoformat()
    
    query = '''
        SELECT 
            u.id as user_id,
            u.full_name as user_name,
            COUNT(t.id) as total_tasks,
            SUM(CASE WHEN t.status = 'COMPLETED' THEN 1 ELSE 0 END) as completed_tasks,
            SUM(CASE WHEN t.status = 'IN_PROGRESS' THEN 1 ELSE 0 END) as in_progress_tasks,
            SUM(CASE WHEN t.deadline < ? AND t.status != 'COMPLETED' THEN 1 ELSE 0 END) as overdue_tasks,
            AVG(t.progress) as avg_progress
        FROM users u
        LEFT JOIN tasks t ON u.id = t.assigned_to
        WHERE u.role = 'member' AND u.is_active = 1
    '''
    params = [today]
    
    if user_id:
        query += " AND u.id = ?"
        params.append(user_id)
    
    query += " GROUP BY u.id ORDER BY completed_tasks DESC"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    performances = []
    for row in rows:
        perf = MemberPerformance(
            user_id=row['user_id'],
            user_name=row['user_name'] or "Inconnu",
            total_tasks=row['total_tasks'] or 0,
            completed_tasks=row['completed_tasks'] or 0,
            in_progress_tasks=row['in_progress_tasks'] or 0,
            overdue_tasks=row['overdue_tasks'] or 0,
            average_progress=round(row['avg_progress'], 1) if row['avg_progress'] else 0.0
        )
        if perf.total_tasks > 0:
            perf.completion_rate = round((perf.completed_tasks / perf.total_tasks) * 100, 1)
        performances.append(perf)
    
    return performances


def get_project_stats(project_id: int) -> Dict[str, Any]:
    """Récupère les statistiques d'un projet spécifique."""
    conn = get_connection()
    cursor = conn.cursor()
    today = date.today().isoformat()
    
    stats = {
        'total_tasks': 0,
        'completed_tasks': 0,
        'in_progress_tasks': 0,
        'todo_tasks': 0,
        'overdue_tasks': 0,
        'progress': 0.0,
        'members': 0
    }
    
    cursor.execute("SELECT COUNT(*) FROM tasks WHERE project_id = ?", (project_id,))
    stats['total_tasks'] = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM tasks WHERE project_id = ? AND status = 'COMPLETED'", (project_id,))
    stats['completed_tasks'] = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM tasks WHERE project_id = ? AND status = 'IN_PROGRESS'", (project_id,))
    stats['in_progress_tasks'] = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM tasks WHERE project_id = ? AND status = 'TODO'", (project_id,))
    stats['todo_tasks'] = cursor.fetchone()[0]
    
    cursor.execute('''
        SELECT COUNT(*) FROM tasks 
        WHERE project_id = ? AND deadline < ? AND status != 'COMPLETED'
    ''', (project_id, today))
    stats['overdue_tasks'] = cursor.fetchone()[0]
    
    cursor.execute("SELECT AVG(progress) FROM tasks WHERE project_id = ?", (project_id,))
    avg = cursor.fetchone()[0]
    stats['progress'] = round(avg, 1) if avg else 0.0
    
    cursor.execute("SELECT COUNT(*) FROM project_members WHERE project_id = ?", (project_id,))
    stats['members'] = cursor.fetchone()[0]
    
    conn.close()
    return stats
