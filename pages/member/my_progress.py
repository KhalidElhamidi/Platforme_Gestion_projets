"""
Mon progrès - Interface membre.
"""

import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from services.auth_service import require_auth, get_current_user_id, get_current_user
from services.progress_service import get_member_individual_performance
from services.member_service import get_member_workload
from database.crud import get_user_tasks, get_user_projects
from components.charts import create_progress_gauge, create_tasks_pie_chart
from config import TASK_STATUS


def render_my_progress():
    """Affiche le progrès personnel du membre."""
    require_auth()
    user_id = get_current_user_id()
    user = get_current_user()
    
    st.markdown(f"<h1>📈 Mon progrès</h1>", unsafe_allow_html=True)
    st.markdown(f"Bonjour **{user.full_name or user.username}**!")
    
    # Performance
    performance = get_member_individual_performance(user_id)
    workload = get_member_workload(user_id)
    
    # Métriques principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total tâches", workload['total_tasks'])
    with col2:
        st.metric("Complétées", workload['completed'])
    with col3:
        st.metric("En cours", workload['in_progress'])
    with col4:
        overdue_delta = f"-{workload['overdue']}" if workload['overdue'] > 0 else "0"
        st.metric("En retard", workload['overdue'], delta=overdue_delta)
    
    # Graphiques
    col1, col2 = st.columns(2)
    
    with col1:
        if performance and performance.total_tasks > 0:
            fig = create_progress_gauge(
                performance.completion_rate,
                "Taux de complétion"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Pas encore de tâches assignées")
    
    with col2:
        if workload['total_tasks'] > 0:
            task_data = {
                'TODO': workload['todo'],
                'IN_PROGRESS': workload['in_progress'],
                'COMPLETED': workload['completed']
            }
            fig = create_tasks_pie_chart(task_data, "Répartition")
            st.plotly_chart(fig, use_container_width=True)
    
    # Projets
    st.markdown("### 📁 Mes projets")
    projects = get_user_projects(user_id)
    
    if projects:
        for proj in projects:
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"**{proj.name}**")
            with col2:
                st.markdown(f"{proj.progress:.0f}%")
            st.progress(proj.progress / 100)
    else:
        st.info("Aucun projet assigné")
    
    # Tâches récentes
    st.markdown("### ✅ Tâches récentes")
    tasks = get_user_tasks(user_id)
    
    completed_tasks = [t for t in tasks if t.status == 'COMPLETED'][:5]
    
    if completed_tasks:
        for task in completed_tasks:
            st.markdown(f"✅ ~~{task.title}~~ - *{task.project_name}*")
    else:
        st.info("Aucune tâche complétée récemment")
