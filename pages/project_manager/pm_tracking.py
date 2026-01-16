"""
Suivi de l'avancement - Chef de Projet.
"""

import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from services.auth_service import require_auth, get_current_user_id
from services.project_service import get_user_projects_list
from services.progress_service import calculate_project_health, get_progress_over_time
from database.crud import get_project_stats, get_all_tasks
from components.charts import create_progress_gauge, create_progress_timeline, create_tasks_by_status_chart
from config import TASK_STATUS


def render_pm_tracking():
    """Suivi de l'avancement pour le chef de projet."""
    require_auth()
    user_id = get_current_user_id()
    
    st.markdown("<h1>📈 Suivi de l'avancement</h1>", unsafe_allow_html=True)
    
    projects = get_user_projects_list(user_id)
    
    if not projects:
        st.warning("Aucun projet à suivre.")
        return
    
    # Sélection du projet
    selected_project = st.selectbox(
        "Sélectionner un projet",
        options=[p.id for p in projects],
        format_func=lambda x: next(p.name for p in projects if p.id == x)
    )
    
    if selected_project:
        render_project_tracking(selected_project)


def render_project_tracking(project_id):
    """Affiche le suivi d'un projet."""
    st.markdown("---")
    
    stats = get_project_stats(project_id)
    health = calculate_project_health(project_id)
    
    # Métriques
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total tâches", stats['total_tasks'])
    with col2:
        st.metric("Complétées", stats['completed_tasks'])
    with col3:
        st.metric("En cours", stats['in_progress_tasks'])
    with col4:
        st.metric("En retard", stats['overdue_tasks'],
                  delta=f"-{stats['overdue_tasks']}" if stats['overdue_tasks'] > 0 else None,
                  delta_color="inverse")
    
    st.markdown("---")
    
    # Graphiques
    col1, col2 = st.columns(2)
    
    with col1:
        fig = create_progress_gauge(stats['progress'], "Progression")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        tasks_data = {
            'TODO': stats['todo_tasks'],
            'IN_PROGRESS': stats['in_progress_tasks'],
            'COMPLETED': stats['completed_tasks']
        }
        fig = create_tasks_by_status_chart(tasks_data)
        st.plotly_chart(fig, use_container_width=True)
    
    # Santé du projet
    st.markdown("### 🏥 Santé du projet")
    
    health_color = health['color']
    st.markdown(f"""
        <div style="
            background: {health_color}20;
            border-left: 4px solid {health_color};
            padding: 1rem;
            border-radius: 8px;
        ">
            <h3 style="color: {health_color}; margin: 0;">Score: {health['score']}/100</h3>
            <p>{health['message']}</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Timeline
    st.markdown("### 📅 Évolution")
    progress_data = get_progress_over_time(project_id, days=14)
    if progress_data:
        fig = create_progress_timeline(progress_data)
        st.plotly_chart(fig, use_container_width=True)
