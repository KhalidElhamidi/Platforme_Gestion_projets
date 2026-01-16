"""
Formulaires réutilisables pour l'interface.
"""

import streamlit as st
from datetime import date, datetime
from typing import Optional, List, Tuple
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import PROJECT_STATUS, TASK_STATUS, TASK_PRIORITY, MILESTONE_STATUS
from database.models import Project, Task, User, Milestone


def render_project_form(project: Optional[Project] = None, key_prefix: str = "project") -> Tuple[dict, bool]:
    """
    Affiche un formulaire de création/modification de projet.
    
    Args:
        project: Projet existant pour modification (None pour création)
        key_prefix: Préfixe pour les clés Streamlit
    
    Returns:
        Tuple (données du formulaire, soumis)
    """
    with st.form(f"{key_prefix}_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input(
                "Nom du projet *",
                value=project.name if project else "",
                key=f"{key_prefix}_name"
            )
            
            start_date = st.date_input(
                "Date de début",
                value=datetime.strptime(project.start_date, "%Y-%m-%d").date() 
                      if project and project.start_date else date.today(),
                key=f"{key_prefix}_start"
            )
            
            status_options = list(PROJECT_STATUS.keys())
            status_labels = list(PROJECT_STATUS.values())
            current_status_idx = status_options.index(project.status) if project else 0
            status = st.selectbox(
                "Statut",
                options=status_options,
                format_func=lambda x: PROJECT_STATUS[x],
                index=current_status_idx,
                key=f"{key_prefix}_status"
            )
        
        with col2:
            budget = st.number_input(
                "Budget (optionnel)",
                value=project.budget if project and project.budget else 0.0,
                min_value=0.0,
                step=1000.0,
                key=f"{key_prefix}_budget"
            )
            
            end_date = st.date_input(
                "Date de fin",
                value=datetime.strptime(project.end_date, "%Y-%m-%d").date() 
                      if project and project.end_date else None,
                key=f"{key_prefix}_end"
            )
        
        description = st.text_area(
            "Description",
            value=project.description if project else "",
            key=f"{key_prefix}_desc"
        )
        
        submitted = st.form_submit_button(
            "💾 Enregistrer" if project else "➕ Créer le projet",
            use_container_width=True,
            type="primary"
        )
        
        data = {
            'name': name,
            'description': description,
            'start_date': start_date,
            'end_date': end_date,
            'status': status,
            'budget': budget if budget > 0 else None
        }
        
        return data, submitted


def render_task_form(task: Optional[Task] = None, 
                     project_id: int = None,
                     members: List[User] = None,
                     milestones: List[Milestone] = None,
                     key_prefix: str = "task") -> Tuple[dict, bool]:
    """
    Affiche un formulaire de création/modification de tâche.
    """
    with st.form(f"{key_prefix}_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input(
                "Titre de la tâche *",
                value=task.title if task else "",
                key=f"{key_prefix}_title"
            )
            
            priority_options = list(TASK_PRIORITY.keys())
            current_priority_idx = priority_options.index(task.priority) if task else 1  # MEDIUM par défaut
            priority = st.selectbox(
                "Priorité",
                options=priority_options,
                format_func=lambda x: f"{'🔴' if x == 'CRITICAL' else '🟠' if x == 'HIGH' else '🟡' if x == 'MEDIUM' else '🟢'} {TASK_PRIORITY[x]}",
                index=current_priority_idx,
                key=f"{key_prefix}_priority"
            )
            
            status_options = list(TASK_STATUS.keys())
            current_status_idx = status_options.index(task.status) if task else 0
            status = st.selectbox(
                "Statut",
                options=status_options,
                format_func=lambda x: TASK_STATUS[x],
                index=current_status_idx,
                key=f"{key_prefix}_status"
            )
        
        with col2:
            deadline = st.date_input(
                "Deadline",
                value=datetime.strptime(task.deadline, "%Y-%m-%d").date() 
                      if task and task.deadline else None,
                key=f"{key_prefix}_deadline"
            )
            
            # Sélection du membre
            if members:
                member_options = [None] + [m.id for m in members]
                member_labels = ["Non assigné"] + [m.full_name or m.username for m in members]
                current_member_idx = 0
                if task and task.assigned_to:
                    try:
                        current_member_idx = member_options.index(task.assigned_to)
                    except ValueError:
                        pass
                assigned_to = st.selectbox(
                    "Assigné à",
                    options=member_options,
                    format_func=lambda x: member_labels[member_options.index(x)],
                    index=current_member_idx,
                    key=f"{key_prefix}_assigned"
                )
            else:
                assigned_to = None
            
            # Sélection du milestone
            if milestones:
                milestone_options = [None] + [m.id for m in milestones]
                milestone_labels = ["Aucun milestone"] + [m.name for m in milestones]
                current_ms_idx = 0
                if task and task.milestone_id:
                    try:
                        current_ms_idx = milestone_options.index(task.milestone_id)
                    except ValueError:
                        pass
                milestone_id = st.selectbox(
                    "Milestone",
                    options=milestone_options,
                    format_func=lambda x: milestone_labels[milestone_options.index(x)],
                    index=current_ms_idx,
                    key=f"{key_prefix}_milestone"
                )
            else:
                milestone_id = None
        
        description = st.text_area(
            "Description",
            value=task.description if task else "",
            key=f"{key_prefix}_desc"
        )
        
        col3, col4 = st.columns(2)
        with col3:
            estimated_hours = st.number_input(
                "Heures estimées",
                value=task.estimated_hours if task and task.estimated_hours else 0.0,
                min_value=0.0,
                step=0.5,
                key=f"{key_prefix}_est_hours"
            )
        
        with col4:
            progress = st.slider(
                "Progression (%)",
                min_value=0,
                max_value=100,
                value=task.progress if task else 0,
                key=f"{key_prefix}_progress"
            )
        
        submitted = st.form_submit_button(
            "💾 Enregistrer" if task else "➕ Créer la tâche",
            use_container_width=True,
            type="primary"
        )
        
        data = {
            'title': title,
            'description': description,
            'priority': priority,
            'status': status,
            'deadline': deadline,
            'assigned_to': assigned_to,
            'milestone_id': milestone_id,
            'estimated_hours': estimated_hours if estimated_hours > 0 else None,
            'progress': progress,
            'project_id': project_id
        }
        
        return data, submitted


def render_member_form(user: Optional[User] = None, key_prefix: str = "member") -> Tuple[dict, bool]:
    """
    Affiche un formulaire de création/modification de membre.
    """
    with st.form(f"{key_prefix}_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            full_name = st.text_input(
                "Nom complet *",
                value=user.full_name if user else "",
                key=f"{key_prefix}_fullname"
            )
            
            username = st.text_input(
                "Nom d'utilisateur *",
                value=user.username if user else "",
                key=f"{key_prefix}_username",
                disabled=user is not None  # Ne pas modifier pour un utilisateur existant
            )
        
        with col2:
            email = st.text_input(
                "Email *",
                value=user.email if user else "",
                key=f"{key_prefix}_email"
            )
            
            if not user:
                password = st.text_input(
                    "Mot de passe *",
                    type="password",
                    key=f"{key_prefix}_password"
                )
            else:
                password = None
        
        role_options = ["member", "admin"]
        role_labels = ["👤 Membre", "👑 Administrateur"]
        current_role_idx = role_options.index(user.role) if user else 0
        role = st.selectbox(
            "Rôle",
            options=role_options,
            format_func=lambda x: role_labels[role_options.index(x)],
            index=current_role_idx,
            key=f"{key_prefix}_role"
        )
        
        submitted = st.form_submit_button(
            "💾 Enregistrer" if user else "➕ Créer le membre",
            use_container_width=True,
            type="primary"
        )
        
        data = {
            'full_name': full_name,
            'username': username,
            'email': email,
            'password': password,
            'role': role
        }
        
        return data, submitted


def render_milestone_form(milestone: Optional[Milestone] = None, 
                          project_id: int = None,
                          key_prefix: str = "milestone") -> Tuple[dict, bool]:
    """
    Affiche un formulaire de création/modification de milestone.
    """
    with st.form(f"{key_prefix}_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input(
                "Nom du milestone *",
                value=milestone.name if milestone else "",
                key=f"{key_prefix}_name"
            )
        
        with col2:
            due_date = st.date_input(
                "Date d'échéance",
                value=datetime.strptime(milestone.due_date, "%Y-%m-%d").date() 
                      if milestone and milestone.due_date else None,
                key=f"{key_prefix}_due"
            )
        
        description = st.text_area(
            "Description",
            value=milestone.description if milestone else "",
            key=f"{key_prefix}_desc"
        )
        
        if milestone:
            status_options = list(MILESTONE_STATUS.keys())
            current_status_idx = status_options.index(milestone.status) if milestone.status in status_options else 0
            status = st.selectbox(
                "Statut",
                options=status_options,
                format_func=lambda x: MILESTONE_STATUS[x],
                index=current_status_idx,
                key=f"{key_prefix}_status"
            )
        else:
            status = "PENDING"
        
        submitted = st.form_submit_button(
            "💾 Enregistrer" if milestone else "➕ Créer le milestone",
            use_container_width=True,
            type="primary"
        )
        
        data = {
            'name': name,
            'description': description,
            'due_date': due_date,
            'status': status,
            'project_id': project_id
        }
        
        return data, submitted


def render_progress_update_form(task: Task, key_prefix: str = "progress") -> Tuple[dict, bool]:
    """
    Affiche un formulaire de mise à jour de progression.
    """
    with st.form(f"{key_prefix}_form"):
        st.markdown(f"### 📋 {task.title}")
        
        if task.description:
            st.markdown(f"*{task.description}*")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**Priorité:** {TASK_PRIORITY.get(task.priority, task.priority)}")
            st.markdown(f"**Statut actuel:** {TASK_STATUS.get(task.status, task.status)}")
        
        with col2:
            if task.deadline:
                st.markdown(f"**Deadline:** {task.deadline}")
            if task.project_name:
                st.markdown(f"**Projet:** {task.project_name}")
        
        st.markdown("---")
        
        progress = st.slider(
            "Nouvelle progression (%)",
            min_value=0,
            max_value=100,
            value=task.progress,
            key=f"{key_prefix}_value"
        )
        
        # Auto-déterminer le statut
        if progress == 0:
            new_status = "TODO"
        elif progress == 100:
            new_status = "COMPLETED"
        else:
            new_status = "IN_PROGRESS"
        
        st.info(f"Le statut sera automatiquement mis à jour vers: **{TASK_STATUS[new_status]}**")
        
        comment = st.text_area(
            "Ajouter un commentaire (optionnel)",
            key=f"{key_prefix}_comment"
        )
        
        submitted = st.form_submit_button(
            "🔄 Mettre à jour",
            use_container_width=True,
            type="primary"
        )
        
        data = {
            'task_id': task.id,
            'progress': progress,
            'status': new_status,
            'comment': comment if comment else None
        }
        
        return data, submitted


def render_filters(filter_type: str = "tasks", key_prefix: str = "filter") -> dict:
    """
    Affiche des filtres pour les listes.
    """
    filters = {}
    
    with st.expander("🔍 Filtres", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        if filter_type == "tasks":
            with col1:
                status_filter = st.multiselect(
                    "Statut",
                    options=list(TASK_STATUS.keys()),
                    format_func=lambda x: TASK_STATUS[x],
                    key=f"{key_prefix}_status"
                )
                filters['status'] = status_filter if status_filter else None
            
            with col2:
                priority_filter = st.multiselect(
                    "Priorité",
                    options=list(TASK_PRIORITY.keys()),
                    format_func=lambda x: TASK_PRIORITY[x],
                    key=f"{key_prefix}_priority"
                )
                filters['priority'] = priority_filter if priority_filter else None
            
            with col3:
                overdue_only = st.checkbox(
                    "En retard uniquement",
                    key=f"{key_prefix}_overdue"
                )
                filters['overdue_only'] = overdue_only
        
        elif filter_type == "projects":
            with col1:
                status_filter = st.multiselect(
                    "Statut",
                    options=list(PROJECT_STATUS.keys()),
                    format_func=lambda x: PROJECT_STATUS[x],
                    key=f"{key_prefix}_status"
                )
                filters['status'] = status_filter if status_filter else None
    
    return filters


def render_confirmation_dialog(title: str, message: str, key: str) -> bool:
    """
    Affiche un dialogue de confirmation.
    """
    with st.expander(f"⚠️ {title}", expanded=True):
        st.warning(message)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Confirmer", key=f"{key}_confirm", type="primary"):
                return True
        with col2:
            if st.button("❌ Annuler", key=f"{key}_cancel"):
                return False
    return None
