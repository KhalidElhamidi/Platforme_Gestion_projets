"""
Gestion des tâches - Interface administrateur.
"""

import streamlit as st
from datetime import date
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from services.auth_service import require_admin
from services.task_service import (
    create_new_task, get_all_tasks_list, get_task_details,
    update_task_info, delete_task_by_id, get_overdue_tasks_list,
    get_priority_color, get_status_color
)
from services.project_service import get_all_projects_with_stats, get_project_milestones_list
from services.member_service import get_members_for_task_assignment
from database.crud import get_all_projects
from components.forms import render_task_form
from config import TASK_STATUS, TASK_PRIORITY


def render_tasks_page():
    """Affiche la page de gestion des tâches."""
    require_admin()
    
    st.markdown("""
        <h1 style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        ">✅ Gestion des tâches</h1>
    """, unsafe_allow_html=True)
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["📋 Toutes les tâches", "⚠️ En retard", "➕ Nouvelle tâche"])
    
    with tab1:
        render_all_tasks()
    
    with tab2:
        render_overdue_tasks()
    
    with tab3:
        render_create_task_form()


def render_all_tasks():
    """Affiche toutes les tâches avec filtres."""
    # Filtres
    col1, col2, col3, col4 = st.columns(4)
    
    projects = get_all_projects()
    
    with col1:
        project_filter = st.selectbox(
            "Projet",
            options=[None] + [p.id for p in projects],
            format_func=lambda x: "Tous les projets" if x is None else next(p.name for p in projects if p.id == x),
            key="task_project_filter"
        )
    
    with col2:
        status_filter = st.selectbox(
            "Statut",
            options=[None] + list(TASK_STATUS.keys()),
            format_func=lambda x: "Tous les statuts" if x is None else TASK_STATUS[x],
            key="task_status_filter"
        )
    
    with col3:
        priority_filter = st.selectbox(
            "Priorité",
            options=[None] + list(TASK_PRIORITY.keys()),
            format_func=lambda x: "Toutes les priorités" if x is None else TASK_PRIORITY[x],
            key="task_priority_filter"
        )
    
    with col4:
        search = st.text_input("🔍 Rechercher", key="task_search")
    
    # Récupérer les tâches
    tasks = get_all_tasks_list(project_id=project_filter, status=status_filter)
    
    # Filtrer par priorité et recherche
    if priority_filter:
        tasks = [t for t in tasks if t.priority == priority_filter]
    if search:
        tasks = [t for t in tasks if search.lower() in t.title.lower()]
    
    st.markdown(f"**{len(tasks)} tâche(s) trouvée(s)**")
    st.markdown("---")
    
    # Afficher les tâches
    if not tasks:
        st.info("Aucune tâche trouvée.")
        return
    
    for task in tasks:
        render_task_card(task)


def render_task_card(task):
    """Affiche une carte de tâche."""
    priority_color = get_priority_color(task.priority)
    status_color = get_status_color(task.status)
    
    with st.container():
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
        
        with col1:
            # Indicateur de retard
            overdue_badge = "🔴 " if task.is_overdue else ""
            
            st.markdown(f"""
                <div style="border-left: 4px solid {priority_color}; padding-left: 1rem;">
                    <h4 style="margin: 0;">{overdue_badge}{task.title}</h4>
                    <p style="color: #718096; margin: 0.25rem 0; font-size: 0.9rem;">
                        📁 {task.project_name or 'N/A'} | 👤 {task.assigned_to_name or 'Non assigné'}
                    </p>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
                <div style="
                    background: {status_color}20;
                    color: {status_color};
                    padding: 0.25rem 0.5rem;
                    border-radius: 12px;
                    text-align: center;
                    font-size: 0.8rem;
                ">
                    {TASK_STATUS.get(task.status, task.status)}
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"📊 **{task.progress}%**")
            if task.deadline:
                st.caption(f"📅 {task.deadline}")
        
        with col4:
            if st.button("✏️", key=f"edit_task_{task.id}"):
                st.session_state.editing_task_id = task.id
                st.rerun()
            if st.button("🗑️", key=f"del_task_{task.id}"):
                if delete_task_by_id(task.id):
                    st.success("Tâche supprimée!")
                    st.rerun()
        
        # Barre de progression
        st.progress(task.progress / 100)
        st.markdown("---")
    
    # Formulaire d'édition si sélectionné
    if st.session_state.get('editing_task_id') == task.id:
        render_edit_task_modal(task)


def render_edit_task_modal(task):
    """Affiche le modal d'édition de tâche."""
    with st.expander(f"✏️ Modifier: {task.title}", expanded=True):
        if st.button("❌ Fermer", key=f"close_edit_{task.id}"):
            st.session_state.editing_task_id = None
            st.rerun()
        
        # Récupérer les données nécessaires
        members = get_members_for_task_assignment(task.project_id)
        milestones = get_project_milestones_list(task.project_id)
        
        data, submitted = render_task_form(
            task=task,
            project_id=task.project_id,
            members=members,
            milestones=milestones,
            key_prefix=f"edit_task_{task.id}"
        )
        
        if submitted:
            try:
                success = update_task_info(
                    task.id,
                    title=data['title'],
                    description=data['description'],
                    priority=data['priority'],
                    status=data['status'],
                    deadline=data['deadline'],
                    assigned_to=data['assigned_to'],
                    milestone_id=data['milestone_id'],
                    estimated_hours=data['estimated_hours'],
                    progress=data['progress']
                )
                if success:
                    st.success("✅ Tâche mise à jour!")
                    st.session_state.editing_task_id = None
                    st.rerun()
            except ValueError as e:
                st.error(str(e))


def render_overdue_tasks():
    """Affiche les tâches en retard."""
    tasks = get_overdue_tasks_list()
    
    if not tasks:
        st.success("🎉 Aucune tâche en retard! Excellent travail!")
        return
    
    st.warning(f"⚠️ {len(tasks)} tâche(s) en retard")
    
    for task in tasks:
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.markdown(f"""
                    <div style="border-left: 4px solid #f56565; padding-left: 1rem;">
                        <h4 style="margin: 0; color: #c53030;">🔴 {task.title}</h4>
                        <p style="color: #718096; margin: 0;">
                            📁 {task.project_name} | 👤 {task.assigned_to_name or 'Non assigné'}
                        </p>
                    </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"📅 **Deadline:** {task.deadline}")
                days_late = (date.today() - date.fromisoformat(str(task.deadline))).days
                st.error(f"{days_late} jour(s) de retard")
            
            with col3:
                st.markdown(f"📊 {task.progress}%")
            
            st.markdown("---")


def render_create_task_form():
    """Affiche le formulaire de création de tâche."""
    st.markdown("### ➕ Créer une nouvelle tâche")
    
    # Sélection du projet
    projects = get_all_projects()
    
    if not projects:
        st.warning("⚠️ Créez d'abord un projet avant d'ajouter des tâches.")
        return
    
    selected_project = st.selectbox(
        "Sélectionner un projet *",
        options=[p.id for p in projects],
        format_func=lambda x: next(p.name for p in projects if p.id == x),
        key="new_task_project"
    )
    
    # Récupérer les membres et milestones du projet
    members = get_members_for_task_assignment(selected_project)
    milestones = get_project_milestones_list(selected_project)
    
    data, submitted = render_task_form(
        project_id=selected_project,
        members=members,
        milestones=milestones,
        key_prefix="new_task"
    )
    
    if submitted:
        if not data['title']:
            st.error("Le titre de la tâche est requis.")
        else:
            try:
                task_id = create_new_task(
                    project_id=selected_project,
                    title=data['title'],
                    description=data['description'],
                    priority=data['priority'],
                    assigned_to=data['assigned_to'],
                    deadline=data['deadline'],
                    milestone_id=data['milestone_id'],
                    estimated_hours=data['estimated_hours']
                )
                if task_id:
                    st.success(f"✅ Tâche '{data['title']}' créée avec succès!")
                    st.rerun()
                else:
                    st.error("Erreur lors de la création de la tâche.")
            except ValueError as e:
                st.error(str(e))
