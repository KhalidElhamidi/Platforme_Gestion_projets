"""
Tableau de bord administrateur.
"""

import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from services.auth_service import require_admin, get_current_user
from services.progress_service import (
    get_dashboard_statistics, 
    get_all_members_performance,
    get_team_velocity,
    get_workload_distribution
)
from database.crud import get_all_projects, get_overdue_tasks, get_recent_activities
from components.charts import (
    create_progress_gauge,
    create_tasks_by_status_chart,
    create_tasks_pie_chart,
    create_member_performance_chart,
    create_velocity_chart,
    create_projects_overview_chart,
    create_completion_rate_chart
)
from config import PROJECT_STATUS, TASK_STATUS


def render_dashboard():
    """Affiche le tableau de bord administrateur."""
    require_admin()
    
    st.markdown("""
        <h1 style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        ">📊 Tableau de bord</h1>
    """, unsafe_allow_html=True)
    
    # Récupérer les statistiques
    stats = get_dashboard_statistics()
    
    # Métriques principales
    st.markdown("### 📈 Vue d'ensemble")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
            <div style="
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 1.5rem;
                border-radius: 12px;
                color: white;
                text-align: center;
            ">
                <div style="font-size: 2rem; font-weight: bold;">""" + str(stats.total_projects) + """</div>
                <div style="opacity: 0.9;">Projets totaux</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div style="
                background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
                padding: 1.5rem;
                border-radius: 12px;
                color: white;
                text-align: center;
            ">
                <div style="font-size: 2rem; font-weight: bold;">""" + str(stats.completed_tasks) + """</div>
                <div style="opacity: 0.9;">Tâches terminées</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div style="
                background: linear-gradient(135deg, #4299e1 0%, #3182ce 100%);
                padding: 1.5rem;
                border-radius: 12px;
                color: white;
                text-align: center;
            ">
                <div style="font-size: 2rem; font-weight: bold;">""" + str(stats.in_progress_tasks) + """</div>
                <div style="opacity: 0.9;">Tâches en cours</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        overdue_color = "#f56565" if stats.overdue_tasks > 0 else "#48bb78"
        st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, {overdue_color} 0%, {overdue_color}dd 100%);
                padding: 1.5rem;
                border-radius: 12px;
                color: white;
                text-align: center;
            ">
                <div style="font-size: 2rem; font-weight: bold;">{stats.overdue_tasks}</div>
                <div style="opacity: 0.9;">Tâches en retard</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Graphiques principaux
    col1, col2 = st.columns(2)
    
    with col1:
        # Jauge de progression globale
        fig = create_progress_gauge(stats.overall_progress, "Progression globale")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Tâches par statut
        tasks_data = {
            'TODO': stats.total_tasks - stats.completed_tasks - stats.in_progress_tasks,
            'IN_PROGRESS': stats.in_progress_tasks,
            'COMPLETED': stats.completed_tasks
        }
        fig = create_tasks_pie_chart(tasks_data, "Répartition des tâches")
        st.plotly_chart(fig, use_container_width=True)
    
    # Section des projets
    st.markdown("### 📁 Aperçu des projets")
    
    projects = get_all_projects()
    if projects:
        fig = create_projects_overview_chart(projects)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aucun projet créé pour le moment.")
    
    # Vélocité et performance
    st.markdown("### 🚀 Performance de l'équipe")
    
    col1, col2 = st.columns(2)
    
    with col1:
        velocity = get_team_velocity()
        if velocity['weekly_data']:
            fig = create_velocity_chart(velocity['weekly_data'])
            st.plotly_chart(fig, use_container_width=True)
            
            # Indicateur de tendance
            trend_icon = "📈" if velocity['trend'] == 'up' else "📉" if velocity['trend'] == 'down' else "➡️"
            st.metric(
                "Vélocité moyenne",
                f"{velocity['average_velocity']:.1f} tâches/semaine",
                delta=f"{trend_icon} Tendance {velocity['trend']}"
            )
    
    with col2:
        performances = get_all_members_performance()
        if performances:
            perf_data = [
                {'name': p.user_name, 'completion_rate': p.completion_rate}
                for p in performances
            ]
            fig = create_completion_rate_chart(perf_data)
            st.plotly_chart(fig, use_container_width=True)
    
    # Tâches en retard
    overdue_tasks = get_overdue_tasks()
    if overdue_tasks:
        st.markdown("### ⚠️ Tâches en retard")
        
        for task in overdue_tasks[:5]:
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.markdown(f"**{task.title}**")
                    st.caption(f"Projet: {task.project_name or 'N/A'}")
                with col2:
                    st.markdown(f"📅 {task.deadline}")
                with col3:
                    st.markdown(f"👤 {task.assigned_to_name or 'Non assigné'}")
                st.markdown("---")
    
   
