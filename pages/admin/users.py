"""
Gestion des utilisateurs - Administrateur uniquement.
"""

import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from services.auth_service import require_admin
from services.member_service import (
    create_new_member, get_all_members_list, get_member_details,
    update_member_info, deactivate_member
)
from database.crud import get_recent_activities
from components.forms import render_member_form
from config import ROLE_ADMIN, ROLE_PROJECT_MANAGER, ROLE_MEMBER, ROLE_LABELS


def render_users_page():
    """Gestion des utilisateurs (admin uniquement)."""
    require_admin()
    
    st.markdown("<h1>👤 Gestion des utilisateurs</h1>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📋 Utilisateurs", "➕ Nouvel utilisateur", "📜 Activité récente"])
    
    with tab1:
        render_users_list()
    
    with tab2:
        render_create_user()
    
    with tab3:
        render_recent_activities()


def render_users_list():
    """Liste des utilisateurs."""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search = st.text_input("🔍 Rechercher", placeholder="Nom, email...")
    
    with col2:
        role_filter = st.selectbox(
            "Rôle",
            options=[None, ROLE_ADMIN, ROLE_PROJECT_MANAGER, ROLE_MEMBER],
            format_func=lambda x: "Tous" if x is None else ROLE_LABELS.get(x, x)
        )
    
    users = get_all_members_list(include_admins=True)
    
    # Filtrer
    if search:
        users = [u for u in users if 
                 search.lower() in (u.full_name or '').lower() or
                 search.lower() in u.email.lower()]
    if role_filter:
        users = [u for u in users if u.role == role_filter]
    
    st.markdown(f"**{len(users)} utilisateur(s)**")
    st.markdown("---")
    
    for user in users:
        render_user_row(user)


def render_user_row(user):
    """Affiche une ligne utilisateur."""
    role_icons = {
        ROLE_ADMIN: "👑",
        ROLE_PROJECT_MANAGER: "🧑‍✈️",
        ROLE_MEMBER: "👤"
    }
    
    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
    
    with col1:
        icon = role_icons.get(user.role, "👤")
        st.markdown(f"**{icon} {user.full_name or user.username}**")
        st.caption(f"@{user.username} | {user.email}")
    
    with col2:
        st.markdown(ROLE_LABELS.get(user.role, user.role))
    
    with col3:
        if user.is_active:
            st.markdown("✅ Actif")
        else:
            st.markdown("❌ Inactif")
    
    with col4:
        if st.button("✏️", key=f"edit_user_{user.id}"):
            st.session_state.editing_user = user.id
            st.rerun()
    
    st.markdown("---")
    
    # Formulaire d'édition
    if st.session_state.get('editing_user') == user.id:
        render_edit_user(user)


def render_edit_user(user):
    """Formulaire d'édition utilisateur."""
    with st.expander(f"✏️ Modifier {user.full_name}", expanded=True):
        if st.button("❌ Fermer", key=f"close_edit_{user.id}"):
            st.session_state.editing_user = None
            st.rerun()
        
        with st.form(f"edit_user_form_{user.id}"):
            col1, col2 = st.columns(2)
            
            with col1:
                full_name = st.text_input("Nom complet", value=user.full_name or "")
                email = st.text_input("Email", value=user.email)
            
            with col2:
                role = st.selectbox(
                    "Rôle",
                    options=[ROLE_MEMBER, ROLE_PROJECT_MANAGER, ROLE_ADMIN],
                    format_func=lambda x: ROLE_LABELS.get(x, x),
                    index=[ROLE_MEMBER, ROLE_PROJECT_MANAGER, ROLE_ADMIN].index(user.role)
                )
                new_password = st.text_input("Nouveau mot de passe", type="password",
                                            help="Laisser vide pour ne pas modifier")
            
            submitted = st.form_submit_button("💾 Enregistrer")
            
            if submitted:
                update_data = {'full_name': full_name, 'email': email, 'role': role}
                if new_password:
                    update_data['password'] = new_password
                
                update_member_info(user.id, **update_data)
                st.success("Utilisateur mis à jour!")
                st.session_state.editing_user = None
                st.rerun()
        
        # Actions
        st.markdown("---")
        if user.is_active:
            if st.button("🔒 Désactiver", key=f"deact_{user.id}"):
                deactivate_member(user.id)
                st.rerun()
        else:
            if st.button("🔓 Réactiver", key=f"react_{user.id}"):
                update_member_info(user.id, is_active=True)
                st.rerun()


def render_create_user():
    """Création d'utilisateur."""
    st.markdown("### ➕ Nouvel utilisateur")
    
    with st.form("create_user_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            full_name = st.text_input("Nom complet *")
            username = st.text_input("Nom d'utilisateur *")
            email = st.text_input("Email *")
        
        with col2:
            password = st.text_input("Mot de passe *", type="password")
            role = st.selectbox(
                "Rôle *",
                options=[ROLE_MEMBER, ROLE_PROJECT_MANAGER, ROLE_ADMIN],
                format_func=lambda x: ROLE_LABELS.get(x, x)
            )
        
        submitted = st.form_submit_button("➕ Créer", use_container_width=True)
        
        if submitted:
            if not all([username, email, password]):
                st.error("Tous les champs obligatoires doivent être remplis.")
            else:
                user_id = create_new_member(
                    username=username,
                    email=email,
                    password=password,
                    full_name=full_name,
                    role=role
                )
                if user_id:
                    st.success(f"Utilisateur '{full_name or username}' créé!")
                    st.rerun()
                else:
                    st.error("Erreur: l'utilisateur existe peut-être déjà.")

def render_recent_activities():
    # Activité récente 
    st.markdown("### 📜 Activité récente")
    
    activities = get_recent_activities(limit=10)
    if activities:
        for activity in activities:
            action_icons = {
                'LOGIN': '🔑',
                'LOGOUT': '🚪',
                'PROJECT_CREATED': '📁',
                'TASK_CREATED': '✅',
                'TASK_UPDATED': '✏️',
                'MEMBER_ADDED': '👤'
            }
            icon = action_icons.get(activity.action, '📝')
            
            st.markdown(f"""
                <div style="
                    display: flex;
                    align-items: center;
                    padding: 0.5rem;
                    background: #f7fafc;
                    border-radius: 8px;
                    margin-bottom: 0.5rem;
                ">
                    <span style="font-size: 1.2rem; margin-right: 0.5rem;">{icon}</span>
                    <div>
                        <strong>{activity.user_name or 'Système'}</strong>
                        <span style="color: #718096;"> - {activity.details or activity.action}</span>
                        <div style="font-size: 0.8rem; color: #a0aec0;">{activity.timestamp}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Aucune activité récente.")
