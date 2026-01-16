"""
Constantes de l'application.
"""

# Messages d'erreur
ERROR_MESSAGES = {
    'INVALID_CREDENTIALS': "Email ou mot de passe incorrect.",
    'USER_INACTIVE': "Ce compte a été désactivé.",
    'REQUIRED_FIELD': "Ce champ est obligatoire.",
    'INVALID_EMAIL': "L'adresse email n'est pas valide.",
    'PASSWORD_TOO_SHORT': "Le mot de passe doit contenir au moins 6 caractères.",
    'USERNAME_TAKEN': "Ce nom d'utilisateur est déjà pris.",
    'EMAIL_TAKEN': "Cet email est déjà utilisé.",
    'PROJECT_NOT_FOUND': "Projet non trouvé.",
    'TASK_NOT_FOUND': "Tâche non trouvée.",
    'USER_NOT_FOUND': "Utilisateur non trouvé.",
    'PERMISSION_DENIED': "Vous n'avez pas la permission d'effectuer cette action."
}

# Messages de succès
SUCCESS_MESSAGES = {
    'LOGIN': "Connexion réussie!",
    'LOGOUT': "Déconnexion réussie.",
    'PROJECT_CREATED': "Projet créé avec succès!",
    'PROJECT_UPDATED': "Projet mis à jour.",
    'PROJECT_DELETED': "Projet supprimé.",
    'TASK_CREATED': "Tâche créée avec succès!",
    'TASK_UPDATED': "Tâche mise à jour.",
    'TASK_DELETED': "Tâche supprimée.",
    'USER_CREATED': "Utilisateur créé avec succès!",
    'USER_UPDATED': "Utilisateur mis à jour.",
    'PROGRESS_UPDATED': "Progression mise à jour!"
}

# Icônes pour les actions
ACTION_ICONS = {
    'LOGIN': '🔑',
    'LOGOUT': '🚪',
    'PROJECT_CREATED': '📁',
    'PROJECT_UPDATED': '✏️',
    'PROJECT_DELETED': '🗑️',
    'TASK_CREATED': '✅',
    'TASK_UPDATED': '✏️',
    'TASK_DELETED': '🗑️',
    'USER_CREATED': '👤',
    'MEMBER_ADDED': '➕',
    'MEMBER_REMOVED': '➖',
    'MILESTONE_CREATED': '🎯',
    'COMMENT_ADDED': '💬'
}
