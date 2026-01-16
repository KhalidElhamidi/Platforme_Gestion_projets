"""
Gestion des tâches - Chef de Projet.
"""

import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from services.auth_service import require_auth, get_current_user_id
from services.task_service import (
    create_new_task, get_all_tasks_list, update_task_info, delete_task_by_id
)
from services.project_service import get_user_projects_list, get_project_milestones_list
from services.member_service import get_members_for_task_assignment
from components.forms import render_task_form
from config import TASK_STATUS, TASK_PRIORITY


def render_pm_tasks():
    """Gestion des tâches pour le chef de projet."""
    require_auth()
    user_id = get_current_user_id()
    
    st.markdown("<h1>✅ Gestion des tâches</h1>", unsafe_allow_html=True)
    
    projects = get_user_projects_list(user_id)
    
    if not projects:
        st.warning("Créez d'abord un projet pour gérer des tâches.")
        return
    
    tab1, tab2 = st.tabs(["📋 Tâches", "➕ Nouvelle tâche"])
    
    with tab1:
        render_tasks_list(projects)
    
    with tab2:
        render_create_task(projects)


def render_tasks_list(projects):
    """Liste des tâches des projets du chef."""
    # Filtre par projet
    project_ids = [p.id for p in projects]
    project_names = {p.id: p.name for p in projects}
    
    selected_project = st.selectbox(
        "Filtrer par projet",
        options=[None] + project_ids,
        format_func=lambda x: "Tous mes projets" if x is None else project_names[x]
    )
    
    # Récupérer les tâches
    all_tasks = []
    for pid in (project_ids if selected_project is None else [selected_project]):
        tasks = get_all_tasks_list(project_id=pid)
        all_tasks.extend(tasks)
    
    if not all_tasks:
        st.info("Aucune tâche trouvée.")
        return
    
    st.markdown(f"**{len(all_tasks)} tâche(s)**")
    
    for task in all_tasks:
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
        
        with col1:
            prefix = "🔴 " if task.is_overdue else ""
            st.markdown(f"**{prefix}{task.title}**")
            st.caption(f"📁 {task.project_name} | 👤 {task.assigned_to_name or 'Non assigné'}")
        
        with col2:
            st.markdown(TASK_STATUS.get(task.status, task.status))
        
        with col3:
            st.markdown(f"{task.progress}%")
        
        with col4:
            if st.button("🗑️", key=f"del_{task.id}"):
                delete_task_by_id(task.id)
                st.rerun()
        
        st.progress(task.progress / 100)
        st.markdown("---")


def render_create_task(projects):
    """Création de tâche."""
    st.markdown("### ➕ Nouvelle tâche")
    
    selected_project = st.selectbox(
        "Projet *",
        options=[p.id for p in projects],
        format_func=lambda x: next(p.name for p in projects if p.id == x),
        key="new_task_project"
    )
    
    members = get_members_for_task_assignment(selected_project)
    milestones = get_project_milestones_list(selected_project)
    
    data, submitted = render_task_form(
        project_id=selected_project,
        members=members,
        milestones=milestones,
        key_prefix="pm_new_task"
    )
    
    if submitted and data['title']:
        task_id = create_new_task(
            project_id=selected_project,
            title=data['title'],
            description=data['description'],
            priority=data['priority'],
            assigned_to=data['assigned_to'],
            deadline=data['deadline'],
            milestone_id=data['milestone_id']
        )
        if task_id:
            st.success("Tâche créée!")
            st.rerun()
