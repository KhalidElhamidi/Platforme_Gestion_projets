"""
Plateforme de Gestion de Projets avec Suivi Automatisé et Reporting
Application Streamlit principale.
"""

import streamlit as st
import sys
import os

# Configuration du chemin
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import APP_TITLE, APP_ICON, APP_LAYOUT
from database.db_setup import init_database
from services.auth_service import init_session, is_authenticated, is_admin, is_project_manager, is_member
from components.sidebar import render_sidebar

# Pages Admin
from pages.login import render_login_page
from pages.admin.dashboard import render_dashboard
from pages.admin.projects import render_projects_page
from pages.admin.tasks import render_tasks_page
from pages.admin.users import render_users_page
from pages.admin.teams import render_teams_page
from pages.admin.reports import render_reports_page

# Pages Chef de Projet
from pages.project_manager.pm_dashboard import render_pm_dashboard
from pages.project_manager.pm_projects import render_pm_projects
from pages.project_manager.pm_tasks import render_pm_tasks
from pages.project_manager.pm_team import render_pm_team
from pages.project_manager.pm_tracking import render_pm_tracking
from pages.project_manager.pm_reports import render_pm_reports

# Pages Membre
from pages.member.my_projects import render_my_projects
from pages.member.my_tasks import render_my_tasks
from pages.member.update_progress import render_update_progress
from pages.member.my_progress import render_my_progress


def main():
    """Point d'entrée principal de l'application."""
    
    # Configuration de la page
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon=APP_ICON,
        layout=APP_LAYOUT,
        initial_sidebar_state="expanded"
    )
    
    # CSS global personnalisé
    st.markdown("""
        <style>
        /* Style global */
        .main {
            padding: 1rem 2rem;
        }
        
        /* Masquer le footer Streamlit */
        footer {visibility: hidden;}
        
        /* Style des boutons */
        .stButton > button {
            border-radius: 8px;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }
        
        /* Style des métriques */
        [data-testid="stMetricValue"] {
            font-size: 2rem;
            font-weight: 700;
        }
        
        /* Style de la sidebar - Thème noir */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
        }
        
        [data-testid="stSidebar"] * {
            color: #ffffff !important;
        }
        
        [data-testid="stSidebar"] .stButton > button {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: white !important;
        }
        
        [data-testid="stSidebar"] .stButton > button:hover {
            background: rgba(255, 255, 255, 0.2);
            border-color: rgba(255, 255, 255, 0.3);
        }
        
        [data-testid="stSidebar"] .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
        }
        
        [data-testid="stSidebar"] hr {
            border-color: rgba(255, 255, 255, 0.2);
        }
        
        /* Style des expanders */
        .streamlit-expanderHeader {
            font-weight: 600;
            font-size: 1.1rem;
        }
        
        /* Animation fade-in */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .main .block-container {
            animation: fadeIn 0.5s ease-out;
        }
        
        /* Style des tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        
        .stTabs [data-baseweb="tab"] {
            border-radius: 8px;
            padding: 8px 16px;
        }
        
        /* Style des inputs */
        .stTextInput > div > div > input {
            border-radius: 8px;
        }
        
        .stSelectbox > div > div {
            border-radius: 8px;
        }
        
        /* Progress bar style */
        .stProgress > div > div > div > div {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Initialiser la base de données
    init_database()
    
    # Initialiser la session
    init_session()
    
    # Afficher la page appropriée
    if not is_authenticated():
        render_login_page()
    else:
        # Navigation avec sidebar
        selected_page = render_sidebar()
        
        # Router vers la page sélectionnée selon le rôle
        if is_admin():
            render_admin_page(selected_page)
        elif is_project_manager():
            render_project_manager_page(selected_page)
        else:
            render_member_page(selected_page)


def render_admin_page(page: str):
    """Affiche la page admin appropriée."""
    pages = {
        'dashboard': render_dashboard,
        'projects': render_projects_page,
        'tasks': render_tasks_page,
        'users': render_users_page,
        'teams': render_teams_page,
        'reports': render_reports_page
    }
    
    render_func = pages.get(page, render_dashboard)
    render_func()


def render_project_manager_page(page: str):
    """Affiche la page chef de projet appropriée."""
    pages = {
        'pm_dashboard': render_pm_dashboard,
        'pm_projects': render_pm_projects,
        'pm_tasks': render_pm_tasks,
        'pm_team': render_pm_team,
        'pm_tracking': render_pm_tracking,
        'pm_reports': render_pm_reports
    }
    
    render_func = pages.get(page, render_pm_dashboard)
    render_func()


def render_member_page(page: str):
    """Affiche la page membre appropriée."""
    pages = {
        'my_projects': render_my_projects,
        'my_tasks': render_my_tasks,
        'update_progress': render_update_progress,
        'my_progress': render_my_progress
    }
    
    render_func = pages.get(page, render_my_projects)
    render_func()


if __name__ == "__main__":
    main()

