"""
Mes projets - Interface membre.
"""

import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from services.auth_service import require_auth, get_current_user_id
from services.project_service import get_user_projects_list
from database.crud import get_project_stats
from components.charts import create_progress_gauge
from config import PROJECT_STATUS


def render_my_projects():
    """Affiche les projets du membre."""
    require_auth()
    user_id = get_current_user_id()
    
    st.markdown("<h1>📁 Mes projets</h1>", unsafe_allow_html=True)
    
    projects = get_user_projects_list(user_id)
    
    if not projects:
        st.info("Vous n'êtes assigné à aucun projet pour le moment.")
        return
    
    st.markdown(f"**{len(projects)} projet(s)**")
    
    for project in projects:
        render_project_card(project)


def render_project_card(project):
    """Affiche une carte de projet."""
    stats = get_project_stats(project.id)
    
    with st.container():
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"### {project.name}")
            st.markdown(f"*{project.description or 'Pas de description'}*")
            
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric("Progression", f"{project.progress:.0f}%")
            with col_b:
                st.metric("Tâches", stats['total_tasks'])
            with col_c:
                st.metric("Complétées", stats['completed_tasks'])
        
        with col2:
            status_label = PROJECT_STATUS.get(project.status, project.status)
            st.markdown(f"**Statut:** {status_label}")
            if project.end_date:
                st.markdown(f"📅 Fin: {project.end_date}")
        
        st.progress(project.progress / 100)
        st.markdown("---")
