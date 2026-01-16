"""
Gestion des membres - Interface administrateur.
"""

import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from services.auth_service import require_admin
from services.member_service import (
    create_new_member, get_all_members_list, get_member_details,
    update_member_info, deactivate_member, get_member_workload
)
from services.progress_service import get_member_individual_performance
from database.crud import get_user_projects, get_user_tasks, get_recent_activities
from components.forms import render_member_form
from components.charts import create_progress_gauge
from config import ROLE_ADMIN, ROLE_MEMBER


def render_members_page():
    """Affiche la page de gestion des membres."""
    require_admin()
    
    st.markdown("<h1>👥 Gestion des membres</h1>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📋 Liste des membres", "➕ Nouveau membre"])
    
    with tab1:
        render_members_list()
    with tab2:
        render_create_member_form()


def render_members_list():
    """Affiche la liste des membres."""
    col1, col2 = st.columns([3, 1])
    with col1:
        search = st.text_input("🔍 Rechercher", placeholder="Nom ou email...")
    with col2:
        include_admins = st.checkbox("Inclure les admins", value=True)
    
    members = get_all_members_list(include_admins=include_admins)
    if search:
        members = [m for m in members if search.lower() in (m.full_name or '').lower() or search.lower() in m.email.lower()]
    
    st.markdown(f"**{len(members)} membre(s)**")
    
    for member in members:
        render_member_card(member)


def render_member_card(member):
    """Affiche une carte de membre."""
    role_badge = "👑" if member.role == ROLE_ADMIN else "👤"
    
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.markdown(f"**{role_badge} {member.full_name or member.username}**")
        st.caption(f"@{member.username} | {member.email}")
    with col2:
        st.markdown("✅ Actif" if member.is_active else "❌ Inactif")
    with col3:
        if st.button("👁️", key=f"view_{member.id}"):
            st.session_state.selected_member_id = member.id
            st.rerun()
    st.markdown("---")
    
    if st.session_state.get('selected_member_id') == member.id:
        render_member_detail(member.id)


def render_member_detail(member_id: int):
    """Affiche le détail d'un membre."""
    member = get_member_details(member_id)
    if not member:
        return
    
    performance = get_member_individual_performance(member_id)
    
    with st.expander(f"Détails de {member.full_name}", expanded=True):
        if st.button("❌ Fermer"):
            st.session_state.selected_member_id = None
            st.rerun()
        
        if performance:
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Tâches totales", performance.total_tasks)
                st.metric("Complétées", performance.completed_tasks)
            with col2:
                st.metric("Taux complétion", f"{performance.completion_rate:.1f}%")
        
        render_edit_member_form(member)


def render_edit_member_form(member):
    """Formulaire de modification."""
    with st.form(f"edit_{member.id}"):
        full_name = st.text_input("Nom", value=member.full_name or "")
        email = st.text_input("Email", value=member.email)
        role = st.selectbox("Rôle", [ROLE_MEMBER, ROLE_ADMIN], 
                           index=0 if member.role == ROLE_MEMBER else 1)
        
        if st.form_submit_button("💾 Enregistrer"):
            update_member_info(member.id, full_name=full_name, email=email, role=role)
            st.success("Mis à jour!")
            st.rerun()


def render_create_member_form():
    """Formulaire de création."""
    st.markdown("### ➕ Nouveau membre")
    data, submitted = render_member_form(key_prefix="new")
    
    if submitted and data['username'] and data['email'] and data['password']:
        member_id = create_new_member(
            username=data['username'], email=data['email'],
            password=data['password'], full_name=data['full_name'], role=data['role']
        )
        if member_id:
            st.success("Membre créé!")
            st.rerun()
