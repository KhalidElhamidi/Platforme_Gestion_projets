"""
Mes projets - Chef de Projet.
"""

import streamlit as st
from datetime import date
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from services.auth_service import require_auth, get_current_user_id
from services.project_service import (
    create_new_project, get_user_projects_list, get_project_details,
    update_project_info, create_project_milestone, get_project_milestones_list
)
from database.crud import get_project_stats
from components.forms import render_project_form, render_milestone_form
from components.charts import create_progress_gauge
from config import PROJECT_STATUS


def render_pm_projects():
    """Affiche les projets du chef de projet."""
    require_auth()
    user_id = get_current_user_id()
    
    st.markdown("<h1>📁 Mes projets</h1>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📋 Mes projets", "➕ Nouveau projet"])
    
    with tab1:
        render_my_projects_list(user_id)
    
    with tab2:
        render_create_project(user_id)


def render_my_projects_list(user_id):
    """Liste des projets du chef de projet."""
    projects = get_user_projects_list(user_id)
    
    if not projects:
        st.info("Vous n'avez pas encore de projets.")
        return
    
    st.markdown(f"**{len(projects)} projet(s)**")
    
    for project in projects:
        render_project_card(project)


def render_project_card(project):
    """Affiche une carte de projet."""
    stats = get_project_stats(project.id)
    
    with st.container():
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            st.markdown(f"### {project.name}")
            st.markdown(f"*{project.description or 'Pas de description'}*")
            st.markdown(f"📊 {project.progress:.0f}% | ✅ {stats['completed_tasks']}/{stats['total_tasks']} tâches")
        
        with col2:
            st.markdown(f"**{PROJECT_STATUS.get(project.status, project.status)}**")
            if project.end_date:
                st.markdown(f"📅 {project.end_date}")
        
        with col3:
            if st.button("✏️ Gérer", key=f"manage_{project.id}"):
                st.session_state.selected_pm_project = project.id
                st.rerun()
        
        st.progress(project.progress / 100)
        st.markdown("---")
    
    # Détails du projet si sélectionné
    if st.session_state.get('selected_pm_project') == project.id:
        render_project_management(project.id)


def render_project_management(project_id):
    """Gestion détaillée d'un projet."""
    project = get_project_details(project_id)
    
    with st.expander(f"⚙️ Gestion de {project.name}", expanded=True):
        if st.button("❌ Fermer"):
            st.session_state.selected_pm_project = None
            st.rerun()
        
        tab1, tab2 = st.tabs(["✏️ Modifier", "🎯 Milestones"])
        
        with tab1:
            data, submitted = render_project_form(project=project, key_prefix=f"pm_edit_{project_id}")
            if submitted:
                update_project_info(project_id, **data)
                st.success("Projet mis à jour!")
                st.rerun()
        
        with tab2:
            milestones = get_project_milestones_list(project_id)
            for ms in milestones:
                st.markdown(f"🎯 **{ms.name}** - {ms.progress:.0f}%")
            
            st.markdown("---")
            data, submitted = render_milestone_form(project_id=project_id, key_prefix=f"pm_ms_{project_id}")
            if submitted and data['name']:
                create_project_milestone(project_id, data['name'], data['description'], data['due_date'])
                st.success("Milestone créé!")
                st.rerun()


def render_create_project(user_id):
    """Formulaire de création de projet."""
    st.markdown("### ➕ Créer un nouveau projet")
    
    data, submitted = render_project_form(key_prefix="pm_new")
    
    if submitted and data['name']:
        project_id = create_new_project(
            name=data['name'],
            description=data['description'],
            start_date=data['start_date'],
            end_date=data['end_date'],
            created_by=user_id,
            budget=data['budget']
        )
        if project_id:
            st.success(f"Projet '{data['name']}' créé!")
            st.rerun()
