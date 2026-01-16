"""
Configuration de l'application de gestion de projets.
"""

import os

# Chemin de base de l'application
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Configuration de la base de données
DATABASE_PATH = os.path.join(BASE_DIR, "database", "gestion_projets.db")

# Rôles utilisateurs
ROLE_ADMIN = "admin"
ROLE_PROJECT_MANAGER = "project_manager"
ROLE_MEMBER = "member"

# Descriptions des rôles
ROLE_LABELS = {
    ROLE_ADMIN: "👑 Administrateur",
    ROLE_PROJECT_MANAGER: "👨‍💻 Chef de Projet",
    ROLE_MEMBER: "👤 Membre"
}

# Statuts des projets
PROJECT_STATUS = {
    "NOT_STARTED": "Non démarré",
    "IN_PROGRESS": "En cours",
    "ON_HOLD": "En pause",
    "COMPLETED": "Terminé",
    "CANCELLED": "Annulé"
}

# Statuts des tâches
TASK_STATUS = {
    "TODO": "À faire",
    "IN_PROGRESS": "En cours",
    "REVIEW": "En révision",
    "COMPLETED": "Terminé",
    "BLOCKED": "Bloqué"
}

# Priorités des tâches
TASK_PRIORITY = {
    "LOW": "Basse",
    "MEDIUM": "Moyenne",
    "HIGH": "Haute",
    "CRITICAL": "Critique"
}

# Statuts des milestones
MILESTONE_STATUS = {
    "PENDING": "En attente",
    "IN_PROGRESS": "En cours",
    "COMPLETED": "Terminé"
}

# Configuration de l'interface
APP_TITLE = "Gestion de Projets"
APP_ICON = "🎯"
APP_LAYOUT = "wide"

# Couleurs du thème
THEME_COLORS = {
    "primary": "#667eea",
    "secondary": "#764ba2",
    "success": "#48bb78",
    "warning": "#ed8936",
    "danger": "#f56565",
    "info": "#4299e1"
}
