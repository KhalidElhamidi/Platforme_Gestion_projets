"""
Gestion des projets - Interface administrateur.
"""

import streamlit as st
from datetime import date
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from services.auth_service import require_admin, get_current_user_id
from services.project_service import (
    create_new_project, get_all_projects_with_stats, get_project_details,
    update_project_info, delete_project_and_related,
    create_project_milestone, get_project_milestones_list, delete_milestone
)
from services.member_service import (
    get_all_members_list, get_project_members_list, 
    assign_member_to_project, remove_member_from_project,
    get_members_not_in_project
)
from database.crud import get_project_stats
from components.forms import render_project_form, render_milestone_form
from components.charts import create_progress_gauge, create_tasks_by_status_chart
from config import PROJECT_STATUS


def render_projects_page():
    """Affiche la page de gestion des projets."""
    require_admin()
    
    st.markdown("""
        <h1 style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        ">📁 Gestion des projets</h1>
    """, unsafe_allow_html=True)
    
    # Tabs pour différentes vues
    tab1, tab2 = st.tabs(["📋 Liste des projets", "➕ Nouveau projet"])
    
    with tab1:
        render_projects_list()
    
    with tab2:
        render_create_project_form()


def render_projects_list():
    """Affiche la liste des projets."""
    projects = get_all_projects_with_stats()
    
    if not projects:
        st.info("🎯 Aucun projet créé. Commencez par créer votre premier projet!")
        return
    
    # Filtres
    col1, col2 = st.columns([3, 1])
    with col1:
        search = st.text_input("🔍 Rechercher", placeholder="Nom du projet...")
    with col2:
        status_filter = st.selectbox(
            "Statut",
            options=["Tous"] + list(PROJECT_STATUS.values()),
            key="project_status_filter"
        )
    
    # Filtrer les projets
    filtered_projects = projects
    if search:
        filtered_projects = [p for p in filtered_projects if search.lower() in p.name.lower()]
    if status_filter != "Tous":
        status_key = [k for k, v in PROJECT_STATUS.items() if v == status_filter][0]
        filtered_projects = [p for p in filtered_projects if p.status == status_key]
    
    st.markdown(f"**{len(filtered_projects)} projet(s) trouvé(s)**")
    st.markdown("---")
    
    # Afficher les projets
    for project in filtered_projects:
        render_project_card(project)


def render_project_card(project):
    """Affiche une carte de projet."""
    status_colors = {
        'NOT_STARTED': '#718096',
        'IN_PROGRESS': '#4299e1',
        'ON_HOLD': '#ed8936',
        'COMPLETED': '#48bb78',
        'CANCELLED': '#f56565'
    }
    
    color = status_colors.get(project.status, '#718096')
    
    with st.container():
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            st.markdown(f"""
                <div style="
                    border-left: 4px solid {color};
                    padding-left: 1rem;
                ">
                    <h3 style="margin: 0;">{project.name}</h3>
                    <p style="color: #718096; margin: 0.25rem 0;">
                        {project.description[:100] + '...' if project.description and len(project.description) > 100 else project.description or 'Pas de description'}
                    </p>
                    <div style="display: flex; gap: 1rem; margin-top: 0.5rem;">
                        <span>📊 {project.progress:.0f}%</span>
                        <span>✅ {project.task_count} tâches</span>
                        <span>👥 {project.member_count} membres</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
                <div style="
                    background: {color}20;
                    color: {color};
                    padding: 0.25rem 0.75rem;
                    border-radius: 20px;
                    text-align: center;
                    font-size: 0.85rem;
                ">
                    {PROJECT_STATUS.get(project.status, project.status)}
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            if st.button("👁️ Voir", key=f"view_{project.id}"):
                st.session_state.selected_project_id = project.id
                st.session_state.show_project_detail = True
                st.rerun()
        
        st.markdown("---")
    
    # Afficher le détail si sélectionné
    if st.session_state.get('show_project_detail') and st.session_state.get('selected_project_id') == project.id:
        render_project_detail(project.id)


def render_project_detail(project_id: int):
    """Affiche le détail d'un projet."""
    project = get_project_details(project_id)
    if not project:
        st.error("Projet non trouvé")
        return
    
    stats = get_project_stats(project_id)
    
    with st.expander(f"📋 Détails de {project.name}", expanded=True):
        # Bouton fermer
        if st.button("❌ Fermer", key=f"close_{project_id}"):
            st.session_state.show_project_detail = False
            st.rerun()
        
        # Onglets de détail
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Aperçu", "✏️ Modifier", "🎯 Milestones", "👥 Membres"])
        
        with tab1:
            # Statistiques
            col1, col2 = st.columns(2)
            
            with col1:
                fig = create_progress_gauge(project.progress, "Progression")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("**Informations**")
                st.markdown(f"📅 Début: {project.start_date or 'Non défini'}")
                st.markdown(f"📅 Fin: {project.end_date or 'Non défini'}")
                st.markdown(f"💰 Budget: {project.budget or 'Non défini'} €")
                
                st.markdown("**Statistiques**")
                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric("Tâches totales", stats['total_tasks'])
                    st.metric("Complétées", stats['completed_tasks'])
                with col_b:
                    st.metric("En cours", stats['in_progress_tasks'])
                    st.metric("En retard", stats['overdue_tasks'])
        
        with tab2:
            render_edit_project_form(project)
        
        with tab3:
            render_milestones_section(project_id)
        
        with tab4:
            render_project_members_section(project_id)


def render_create_project_form():
    """Affiche le formulaire de création de projet."""
    st.markdown("### ➕ Créer un nouveau projet")
    
    data, submitted = render_project_form(key_prefix="new_project")
    
    if submitted:
        if not data['name']:
            st.error("Le nom du projet est requis.")
        else:
            try:
                project_id = create_new_project(
                    name=data['name'],
                    description=data['description'],
                    start_date=data['start_date'],
                    end_date=data['end_date'],
                    created_by=get_current_user_id(),
                    budget=data['budget']
                )
                if project_id:
                    st.success(f"✅ Projet '{data['name']}' créé avec succès!")
                    st.rerun()
                else:
                    st.error("Erreur lors de la création du projet.")
            except ValueError as e:
                st.error(str(e))


def render_edit_project_form(project):
    """Affiche le formulaire de modification de projet."""
    data, submitted = render_project_form(project=project, key_prefix=f"edit_{project.id}")
    
    if submitted:
        try:
            success = update_project_info(
                project.id,
                name=data['name'],
                description=data['description'],
                start_date=data['start_date'],
                end_date=data['end_date'],
                status=data['status'],
                budget=data['budget']
            )
            if success:
                st.success("✅ Projet mis à jour!")
                st.rerun()
            else:
                st.error("Erreur lors de la mise à jour.")
        except ValueError as e:
            st.error(str(e))
    
    # Bouton de suppression
    st.markdown("---")
    st.markdown("### ⚠️ Zone de danger")
    
    if st.button("🗑️ Supprimer ce projet", key=f"delete_{project.id}", type="secondary"):
        st.session_state[f'confirm_delete_{project.id}'] = True
    
    if st.session_state.get(f'confirm_delete_{project.id}'):
        st.warning("Êtes-vous sûr ? Cette action est irréversible.")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Confirmer", key=f"confirm_del_{project.id}", type="primary"):
                if delete_project_and_related(project.id):
                    st.success("Projet supprimé.")
                    st.session_state.show_project_detail = False
                    st.rerun()
        with col2:
            if st.button("❌ Annuler", key=f"cancel_del_{project.id}"):
                st.session_state[f'confirm_delete_{project.id}'] = False
                st.rerun()


def render_milestones_section(project_id: int):
    """Affiche la section des milestones."""
    milestones = get_project_milestones_list(project_id)
    
    st.markdown("**Milestones existants**")
    
    if milestones:
        for ms in milestones:
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.markdown(f"🎯 **{ms.name}** - {ms.due_date or 'Pas de date'}")
                if ms.description:
                    st.caption(ms.description)
            with col2:
                st.markdown(f"📊 {ms.progress:.0f}%")
            with col3:
                if st.button("🗑️", key=f"del_ms_{ms.id}"):
                    delete_milestone(ms.id)
                    st.rerun()
            st.markdown("---")
    else:
        st.info("Aucun milestone créé.")
    
    # Formulaire d'ajout
    st.markdown("**Ajouter un milestone**")
    data, submitted = render_milestone_form(project_id=project_id, key_prefix=f"ms_{project_id}")
    
    if submitted:
        if not data['name']:
            st.error("Le nom est requis.")
        else:
            ms_id = create_project_milestone(
                project_id=project_id,
                name=data['name'],
                description=data['description'],
                due_date=data['due_date']
            )
            if ms_id:
                st.success("Milestone créé!")
                st.rerun()


def render_project_members_section(project_id: int):
    """Affiche la section des membres du projet."""
    members = get_project_members_list(project_id)
    available_members = get_members_not_in_project(project_id)
    
    st.markdown("**Membres actuels**")
    
    if members:
        for member in members:
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"👤 **{member.user_name}** - {member.user_email}")
            with col2:
                if st.button("❌", key=f"remove_member_{member.id}"):
                    remove_member_from_project(project_id, member.user_id)
                    st.rerun()
    else:
        st.info("Aucun membre assigné.")
    
    # Ajouter un membre
    if available_members:
        st.markdown("**Ajouter un membre**")
        selected_member = st.selectbox(
            "Sélectionner un membre",
            options=[m.id for m in available_members],
            format_func=lambda x: next(m.full_name or m.username for m in available_members if m.id == x),
            key=f"add_member_{project_id}"
        )
        
        if st.button("➕ Ajouter", key=f"btn_add_member_{project_id}"):
            if assign_member_to_project(project_id, selected_member):
                st.success("Membre ajouté!")
                st.rerun()
    else:
        st.info("Tous les membres sont déjà assignés à ce projet.")
