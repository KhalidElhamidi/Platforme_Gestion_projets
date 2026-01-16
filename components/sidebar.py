"""
Composant de navigation latérale (sidebar).
"""

import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.auth_service import (
    is_authenticated, is_admin, is_project_manager, is_member, 
    get_current_user, logout, get_role_display
)
from config import APP_TITLE


def render_sidebar():
    """
    Affiche la barre de navigation latérale selon le rôle de l'utilisateur.
    
    Returns:
        str: La page sélectionnée
    """
    with st.sidebar:
        # Logo et titre
        st.markdown(f"""
            <div style="text-align: center; padding: 1rem 0;">
                <h1 style="color: #667eea; margin: 0;">{APP_TITLE}</h1>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        if not is_authenticated():
            st.info("👋 Veuillez vous connecter")
            return "login"
        
        # Informations utilisateur
        user = get_current_user()
        if user:
            st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 1rem;
                    border-radius: 10px;
                    margin-bottom: 1rem;
                    color: white;
                ">
                    <div style="font-size: 0.9rem; opacity: 0.9;">Connecté en tant que</div>
                    <div style="font-weight: bold; font-size: 1.1rem;">{user.full_name or user.username}</div>
                    <div style="font-size: 0.8rem; opacity: 0.8;">{get_role_display(user.role)}</div>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Navigation selon le rôle
        if is_admin():
            selected = _render_admin_menu()
        elif is_project_manager():
            selected = _render_project_manager_menu()
        else:
            selected = _render_member_menu()
        
        st.markdown("---")
        
        # Bouton de déconnexion
        if st.button("🚪 Déconnexion", use_container_width=True, type="secondary"):
            logout()
            st.rerun()
        
        # Footer
        st.markdown("""
            <div style="
                position: fixed;
                bottom: 1rem;
                left: 1rem;
                font-size: 0.75rem;
                color: #888;
            ">
                <p>© 2024 Gestion de Projets</p>
            </div>
        """, unsafe_allow_html=True)
        
        return selected


def _render_admin_menu() -> str:
    """Affiche le menu pour les administrateurs."""
    
    menu_items = {
        "dashboard": ("📊", "Tableau de bord global"),
        "projects": ("📁", "Gestion des projets"),
        "tasks": ("✅", "Gestion des tâches"),
        "users": ("👤", "Gestion des utilisateurs"),
        "teams": ("👥", "Gestion des équipes"),
        "reports": ("📋", "Rapports & statistiques"),
    }
    
    return _render_menu(menu_items, 'dashboard')


def _render_project_manager_menu() -> str:
    """Affiche le menu pour les chefs de projet."""
    
    menu_items = {
        "pm_dashboard": ("📊", "Tableau de bord"),
        "pm_projects": ("📁", "Mes projets"),
        "pm_tasks": ("✅", "Gestion des tâches"),
        "pm_team": ("👥", "Gestion de l'équipe"),
        "pm_tracking": ("📈", "Suivi de l'avancement"),
        "pm_reports": ("📋", "Rapports du projet"),
    }
    
    return _render_menu(menu_items, 'pm_dashboard')


def _render_member_menu() -> str:
    """Affiche le menu pour les membres de l'équipe."""
    
    menu_items = {
        "my_projects": ("📁", "Mes projets"),
        "my_tasks": ("✅", "Mes tâches"),
        "update_progress": ("🔄", "Mise à jour avancement"),
        "my_progress": ("📈", "Mon progrès"),
    }
    
    return _render_menu(menu_items, 'my_projects')


def _render_menu(menu_items: dict, default_page: str) -> str:
    """Affiche un menu générique."""
    # Initialiser la page si nécessaire
    if 'current_page' not in st.session_state:
        st.session_state.current_page = default_page
    
    selected = st.session_state.current_page
    
    # Vérifier que la page sélectionnée est valide pour ce menu
    if selected not in menu_items:
        selected = default_page
        st.session_state.current_page = default_page
    
    for key, (icon, label) in menu_items.items():
        button_type = "primary" if selected == key else "secondary"
        if st.button(
            f"{icon} {label}", 
            key=f"menu_{key}",
            use_container_width=True,
            type=button_type
        ):
            st.session_state.current_page = key
            selected = key
            st.rerun()
    
    return selected


def set_page(page: str):
    """Change la page courante."""
    st.session_state.current_page = page

