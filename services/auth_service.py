"""
Service d'authentification et gestion des sessions.
"""

import streamlit as st
from typing import Optional
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.crud import verify_password, get_user_by_id, log_activity
from database.models import User
from config import ROLE_ADMIN, ROLE_PROJECT_MANAGER, ROLE_MEMBER, ROLE_LABELS


def init_session():
    """Initialise les variables de session."""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'role' not in st.session_state:
        st.session_state.role = None


def login(email_or_username: str, password: str) -> tuple[bool, str]:
    """
    Authentifie un utilisateur.
    
    Returns:
        tuple: (succès, message)
    """
    user = verify_password(email_or_username, password)
    
    if user:
        if not user.is_active:
            return False, "Ce compte a été désactivé."
        
        st.session_state.authenticated = True
        st.session_state.user = user
        st.session_state.user_id = user.id
        st.session_state.role = user.role
        
        log_activity(user.id, "LOGIN", "user", user.id, f"Connexion de {user.username}")
        
        return True, f"Bienvenue, {user.full_name or user.username}!"
    
    return False, "Email/nom d'utilisateur ou mot de passe incorrect."


def logout():
    """Déconnecte l'utilisateur actuel."""
    if st.session_state.user:
        log_activity(st.session_state.user_id, "LOGOUT", "user", 
                    st.session_state.user_id, f"Déconnexion")
    
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.user_id = None
    st.session_state.role = None


def is_authenticated() -> bool:
    """Vérifie si l'utilisateur est authentifié."""
    init_session()
    return st.session_state.authenticated


def get_current_user() -> Optional[User]:
    """Retourne l'utilisateur actuellement connecté."""
    if is_authenticated():
        return st.session_state.user
    return None


def get_current_user_id() -> Optional[int]:
    """Retourne l'ID de l'utilisateur actuellement connecté."""
    if is_authenticated():
        return st.session_state.user_id
    return None


def is_admin() -> bool:
    """Vérifie si l'utilisateur actuel est un administrateur."""
    if is_authenticated():
        return st.session_state.role == ROLE_ADMIN
    return False


def is_project_manager() -> bool:
    """Vérifie si l'utilisateur actuel est un chef de projet."""
    if is_authenticated():
        return st.session_state.role == ROLE_PROJECT_MANAGER
    return False


def is_member() -> bool:
    """Vérifie si l'utilisateur actuel est un membre d'équipe."""
    if is_authenticated():
        return st.session_state.role == ROLE_MEMBER
    return False


def has_management_rights() -> bool:
    """Vérifie si l'utilisateur a des droits de gestion (admin ou chef de projet)."""
    return is_admin() or is_project_manager()


def require_auth(redirect_to_login: bool = True):
    """
    Décorateur/fonction pour protéger les pages.
    Redirige vers la page de connexion si non authentifié.
    """
    if not is_authenticated():
        if redirect_to_login:
            st.warning("⚠️ Veuillez vous connecter pour accéder à cette page.")
            st.stop()
        return False
    return True


def require_admin():
    """Vérifie que l'utilisateur est admin, sinon affiche une erreur."""
    require_auth()
    if not is_admin():
        st.error("🚫 Accès refusé. Cette page est réservée aux administrateurs.")
        st.stop()


def require_project_manager():
    """Vérifie que l'utilisateur est chef de projet, sinon affiche une erreur."""
    require_auth()
    if not is_project_manager():
        st.error("🚫 Accès refusé. Cette page est réservée aux chefs de projet.")
        st.stop()


def require_management():
    """Vérifie que l'utilisateur est admin OU chef de projet."""
    require_auth()
    if not has_management_rights():
        st.error("🚫 Accès refusé. Cette page nécessite des droits de gestion.")
        st.stop()


def require_member():
    """Vérifie que l'utilisateur est membre, sinon affiche une erreur."""
    require_auth()
    if not is_member():
        st.error("🚫 Accès refusé. Cette page est réservée aux membres de l'équipe.")
        st.stop()


def get_role_display(role: str) -> str:
    """Retourne le nom d'affichage d'un rôle."""
    return ROLE_LABELS.get(role, role)


def can_manage_users() -> bool:
    """Vérifie si l'utilisateur peut gérer les utilisateurs (admin uniquement)."""
    return is_admin()


def can_manage_all_projects() -> bool:
    """Vérifie si l'utilisateur peut gérer tous les projets (admin uniquement)."""
    return is_admin()


def can_create_projects() -> bool:
    """Vérifie si l'utilisateur peut créer des projets (admin ou chef de projet)."""
    return is_admin() or is_project_manager()

