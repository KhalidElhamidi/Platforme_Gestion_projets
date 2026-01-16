"""
Gestion des équipes - Administrateur.
"""

import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from services.auth_service import require_admin
from services.project_service import get_all_projects_with_stats
from services.member_service import (
    get_project_members_list, get_members_not_in_project,
    assign_member_to_project, remove_member_from_project,
    get_all_members_list
)
from services.progress_service import get_all_members_performance
from components.charts import create_workload_distribution_chart, create_completion_rate_chart


def render_teams_page():
    """Gestion des équipes (admin)."""
    require_admin()
    
    st.markdown("<h1>👥 Gestion des équipes</h1>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📋 Équipes par projet", "📊 Performance globale"])
    
    with tab1:
        render_teams_by_project()
    
    with tab2:
        render_global_performance()


def render_teams_by_project():
    """Affiche les équipes par projet."""
    projects = get_all_projects_with_stats()
    
    if not projects:
        st.info("Aucun projet créé.")
        return
    
    selected_project = st.selectbox(
        "Sélectionner un projet",
        options=[p.id for p in projects],
        format_func=lambda x: next(p.name for p in projects if p.id == x)
    )
    
    if selected_project:
        render_project_team(selected_project)


def render_project_team(project_id):
    """Gestion de l'équipe d'un projet."""
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 👥 Membres du projet")
        members = get_project_members_list(project_id)
        
        if members:
            for member in members:
                col_a, col_b = st.columns([4, 1])
                with col_a:
                    st.markdown(f"👤 **{member.user_name}**")
                    st.caption(f"{member.user_email} | {member.role_in_project}")
                with col_b:
                    if st.button("❌", key=f"rm_team_{member.id}"):
                        remove_member_from_project(project_id, member.user_id)
                        st.rerun()
        else:
            st.info("Aucun membre assigné.")
    
    with col2:
        st.markdown("### ➕ Ajouter un membre")
        available = get_members_not_in_project(project_id)
        
        if available:
            selected = st.selectbox(
                "Membre",
                options=[m.id for m in available],
                format_func=lambda x: next(m.full_name or m.username for m in available if m.id == x),
                key=f"add_team_{project_id}"
            )
            
            role_in_project = st.selectbox(
                "Rôle dans le projet",
                options=["member", "lead"],
                format_func=lambda x: "Membre" if x == "member" else "Team Lead"
            )
            
            if st.button("➕ Ajouter"):
                assign_member_to_project(project_id, selected, role_in_project)
                st.success("Membre ajouté!")
                st.rerun()
        else:
            st.info("Tous les membres sont assignés.")


def render_global_performance():
    """Performance globale de toutes les équipes."""
    st.markdown("### 📊 Performance des membres")
    
    performances = get_all_members_performance()
    
    if not performances:
        st.info("Aucune donnée de performance.")
        return
    
    # Graphiques
    col1, col2 = st.columns(2)
    
    with col1:
        perf_data = [
            {'name': p.user_name, 'tasks': p.total_tasks, 
             'completed': p.completed_tasks, 'completion_rate': p.completion_rate}
            for p in performances
        ]
        fig = create_workload_distribution_chart(perf_data)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = create_completion_rate_chart(perf_data)
        st.plotly_chart(fig, use_container_width=True)
    
    # Tableau détaillé
    st.markdown("### 📋 Détail par membre")
    
    for perf in performances:
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
        
        with col1:
            st.markdown(f"**{perf.user_name}**")
        with col2:
            st.markdown(f"📋 {perf.total_tasks}")
        with col3:
            st.markdown(f"✅ {perf.completed_tasks}")
        with col4:
            color = "#48bb78" if perf.completion_rate >= 70 else "#ed8936" if perf.completion_rate >= 40 else "#f56565"
            st.markdown(f"<span style='color:{color}'>{perf.completion_rate:.0f}%</span>", unsafe_allow_html=True)
        
        st.progress(perf.completion_rate / 100)
