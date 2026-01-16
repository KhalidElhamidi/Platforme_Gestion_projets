"""
Mes tâches - Interface membre.
"""

import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from services.auth_service import require_auth, get_current_user_id
from services.task_service import get_user_assigned_tasks, get_priority_color, get_status_color
from config import TASK_STATUS, TASK_PRIORITY


def render_my_tasks():
    """Affiche les tâches du membre."""
    require_auth()
    user_id = get_current_user_id()
    
    st.markdown("<h1>✅ Mes tâches</h1>", unsafe_allow_html=True)
    
    # Filtres
    col1, col2 = st.columns(2)
    with col1:
        status_filter = st.selectbox(
            "Statut",
            options=[None] + list(TASK_STATUS.keys()),
            format_func=lambda x: "Tous" if x is None else TASK_STATUS[x]
        )
    with col2:
        show_completed = st.checkbox("Afficher terminées", value=False)
    
    tasks = get_user_assigned_tasks(user_id, status=status_filter)
    
    if not show_completed:
        tasks = [t for t in tasks if t.status != 'COMPLETED']
    
    if not tasks:
        st.info("Aucune tâche assignée.")
        return
    
    # Tâches en retard d'abord
    overdue = [t for t in tasks if t.is_overdue]
    normal = [t for t in tasks if not t.is_overdue]
    
    if overdue:
        st.error(f"⚠️ {len(overdue)} tâche(s) en retard")
        for task in overdue:
            render_task_card(task, is_overdue=True)
    
    st.markdown(f"**{len(normal)} tâche(s)**")
    for task in normal:
        render_task_card(task)


def render_task_card(task, is_overdue=False):
    """Affiche une carte de tâche."""
    priority_color = get_priority_color(task.priority)
    status_color = get_status_color(task.status)
    
    border_color = "#f56565" if is_overdue else priority_color
    
    with st.container():
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            prefix = "🔴 " if is_overdue else ""
            st.markdown(f"""
                <div style="border-left: 4px solid {border_color}; padding-left: 1rem;">
                    <h4>{prefix}{task.title}</h4>
                    <p style="color: #718096;">📁 {task.project_name or 'N/A'}</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"**{TASK_PRIORITY[task.priority]}**")
            st.markdown(f"📅 {task.deadline or 'Pas de deadline'}")
        
        with col3:
            st.markdown(f"**{task.progress}%**")
            st.markdown(TASK_STATUS[task.status])
        
        st.progress(task.progress / 100)
        st.markdown("---")
