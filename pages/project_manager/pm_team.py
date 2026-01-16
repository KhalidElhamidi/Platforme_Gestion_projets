"""
Gestion de l'équipe - Chef de Projet.
"""

import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from services.auth_service import require_auth, get_current_user_id
from services.project_service import get_user_projects_list
from services.member_service import (
    get_project_members_list, get_members_not_in_project,
    assign_member_to_project, remove_member_from_project,
    get_member_workload
)
from services.progress_service import get_member_individual_performance
from database.crud import get_all_tasks


def render_pm_team():
    """Gestion de l'équipe du chef de projet."""
    require_auth()
    user_id = get_current_user_id()
    
    st.markdown("<h1>👥 Gestion de l'équipe</h1>", unsafe_allow_html=True)
    
    projects = get_user_projects_list(user_id)
    
    if not projects:
        st.warning("Créez d'abord un projet pour gérer une équipe.")
        return
    
    # Sélection du projet
    selected_project = st.selectbox(
        "Sélectionner un projet",
        options=[p.id for p in projects],
        format_func=lambda x: next(p.name for p in projects if p.id == x)
    )
    
    if selected_project:
        render_team_management(selected_project)


def render_team_management(project_id):
    """Gestion de l'équipe d'un projet."""
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 👥 Membres actuels")
        members = get_project_members_list(project_id)
        
        if members:
            for member in members:
                col_a, col_b = st.columns([4, 1])
                with col_a:
                    st.markdown(f"👤 **{member.user_name}**")
                    st.caption(member.user_email)
                with col_b:
                    if st.button("❌", key=f"rm_{member.id}"):
                        remove_member_from_project(project_id, member.user_id)
                        st.rerun()
                st.markdown("---")
        else:
            st.info("Aucun membre dans ce projet.")
    
    with col2:
        st.markdown("### ➕ Ajouter un membre")
        available = get_members_not_in_project(project_id)
        
        if available:
            selected_member = st.selectbox(
                "Sélectionner un membre",
                options=[m.id for m in available],
                format_func=lambda x: next(m.full_name or m.username for m in available if m.id == x)
            )
            
            if st.button("➕ Ajouter au projet"):
                assign_member_to_project(project_id, selected_member)
                st.success("Membre ajouté!")
                st.rerun()
        else:
            st.info("Tous les membres sont déjà dans ce projet.")
    
    # Statistiques de l'équipe
    st.markdown("---")
    st.markdown("### 📊 Performance de l'équipe")
    
    members = get_project_members_list(project_id)
    if members:
        for member in members:
            perf = get_member_individual_performance(member.user_id)
            if perf:
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.markdown(f"**{member.user_name}**")
                with col2:
                    st.markdown(f"✅ {perf.completed_tasks}/{perf.total_tasks}")
                with col3:
                    st.markdown(f"📊 {perf.completion_rate:.0f}%")
                st.progress(perf.completion_rate / 100)
