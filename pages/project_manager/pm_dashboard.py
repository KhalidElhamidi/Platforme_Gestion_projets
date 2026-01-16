"""
Tableau de bord Chef de Projet.
"""

import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from services.auth_service import require_auth, is_project_manager, get_current_user_id
from services.project_service import get_user_projects_list
from database.crud import get_project_stats, get_user_tasks, get_overdue_tasks
from components.charts import (
    create_progress_gauge, create_tasks_pie_chart,
    create_projects_overview_chart
)
from config import TASK_STATUS


def render_pm_dashboard():
    """Affiche le tableau de bord du chef de projet."""
    require_auth()
    user_id = get_current_user_id()
    
    st.markdown("<h1>📊 Tableau de bord - Chef de Projet</h1>", unsafe_allow_html=True)
    
    # Récupérer les projets gérés
    projects = get_user_projects_list(user_id)
    
    if not projects:
        st.info("Vous n'avez pas encore de projets. Créez votre premier projet!")
        return
    
    # Statistiques globales des projets du chef
    total_tasks = 0
    completed_tasks = 0
    in_progress_tasks = 0
    overdue_tasks = 0
    
    for project in projects:
        stats = get_project_stats(project.id)
        total_tasks += stats['total_tasks']
        completed_tasks += stats['completed_tasks']
        in_progress_tasks += stats['in_progress_tasks']
        overdue_tasks += stats['overdue_tasks']
    
    # Métriques principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📁 Mes projets", len(projects))
    with col2:
        st.metric("✅ Tâches terminées", completed_tasks)
    with col3:
        st.metric("🔄 En cours", in_progress_tasks)
    with col4:
        st.metric("⚠️ En retard", overdue_tasks, 
                  delta=f"-{overdue_tasks}" if overdue_tasks > 0 else None,
                  delta_color="inverse")
    
    st.markdown("---")
    
    # Graphiques
    col1, col2 = st.columns(2)
    
    with col1:
        # Progression globale
        if total_tasks > 0:
            progress = (completed_tasks / total_tasks) * 100
        else:
            progress = 0
        fig = create_progress_gauge(progress, "Progression globale")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Répartition des tâches
        if total_tasks > 0:
            tasks_data = {
                'TODO': total_tasks - completed_tasks - in_progress_tasks,
                'IN_PROGRESS': in_progress_tasks,
                'COMPLETED': completed_tasks
            }
            fig = create_tasks_pie_chart(tasks_data, "Répartition des tâches")
            st.plotly_chart(fig, use_container_width=True)
    
    # Aperçu des projets
    st.markdown("### 📁 Mes projets")
    
    if projects:
        fig = create_projects_overview_chart(projects)
        st.plotly_chart(fig, use_container_width=True)
    
    # Tâches en retard
    st.markdown("### ⚠️ Actions requises")
    
    all_overdue = []
    for project in projects:
        tasks = get_overdue_tasks()
        for task in tasks:
            if task.project_id == project.id:
                all_overdue.append(task)
    
    if all_overdue:
        for task in all_overdue[:5]:
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.markdown(f"🔴 **{task.title}**")
            with col2:
                st.markdown(f"📅 {task.deadline}")
            with col3:
                st.markdown(f"👤 {task.assigned_to_name or 'Non assigné'}")
    else:
        st.success("✅ Aucune tâche en retard!")
