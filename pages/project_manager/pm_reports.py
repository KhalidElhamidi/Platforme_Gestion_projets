"""
Rapports du projet - Chef de Projet.
"""

import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from services.auth_service import require_auth, get_current_user_id
from services.project_service import get_user_projects_list
from services.report_service import generate_project_report, export_project_to_csv
from services.member_service import get_project_members_list
from components.charts import create_member_performance_chart


def render_pm_reports():
    """Rapports pour le chef de projet."""
    require_auth()
    user_id = get_current_user_id()
    
    st.markdown("<h1>📋 Rapports du projet</h1>", unsafe_allow_html=True)
    
    projects = get_user_projects_list(user_id)
    
    if not projects:
        st.warning("Aucun projet disponible.")
        return
    
    # Sélection du projet
    selected_project = st.selectbox(
        "Sélectionner un projet",
        options=[p.id for p in projects],
        format_func=lambda x: next(p.name for p in projects if p.id == x)
    )
    
    if selected_project:
        render_project_report(selected_project)


def render_project_report(project_id):
    """Affiche le rapport d'un projet."""
    st.markdown("---")
    
    report = generate_project_report(project_id)
    
    if not report:
        st.error("Impossible de générer le rapport.")
        return
    
    # Informations générales
    project = report['project']
    stats = report['stats']
    
    st.markdown(f"## 📁 {project.name}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Informations**")
        st.markdown(f"- **Statut:** {project.status}")
        st.markdown(f"- **Début:** {project.start_date or 'Non défini'}")
        st.markdown(f"- **Fin:** {project.end_date or 'Non défini'}")
        st.markdown(f"- **Progression:** {project.progress:.0f}%")
    
    with col2:
        st.markdown("**Statistiques**")
        st.markdown(f"- **Tâches totales:** {stats['total_tasks']}")
        st.markdown(f"- **Complétées:** {stats['completed_tasks']}")
        st.markdown(f"- **En retard:** {stats['overdue_tasks']}")
        st.markdown(f"- **Membres:** {stats['members']}")
    
    # Performance par membre
    st.markdown("### 👥 Performance de l'équipe")
    
    if report['member_stats']:
        for ms in report['member_stats']:
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.markdown(f"**{ms['name']}**")
            with col2:
                st.markdown(f"✅ {ms['completed']}/{ms['total']}")
            with col3:
                rate = (ms['completed'] / ms['total'] * 100) if ms['total'] > 0 else 0
                st.markdown(f"{rate:.0f}%")
    
    # Export
    st.markdown("---")
    st.markdown("### 📥 Exporter")
    
    csv_data = export_project_to_csv(project_id)
    st.download_button(
        "📥 Télécharger les tâches (CSV)",
        data=csv_data,
        file_name=f"projet_{project_id}_taches.csv",
        mime="text/csv"
    )
