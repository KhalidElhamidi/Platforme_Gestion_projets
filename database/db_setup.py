"""
Configuration et initialisation de la base de données SQLite.
"""

import sqlite3
import os
import bcrypt
from datetime import datetime

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DATABASE_PATH, ROLE_ADMIN, ROLE_PROJECT_MANAGER, ROLE_MEMBER


def get_connection():
    """Crée et retourne une connexion à la base de données."""
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Initialise la base de données avec toutes les tables nécessaires."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Table des utilisateurs
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'member',
            full_name TEXT,
            avatar_url TEXT,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Table des projets
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            start_date DATE,
            end_date DATE,
            status TEXT DEFAULT 'NOT_STARTED',
            budget REAL,
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (created_by) REFERENCES users(id)
        )
    ''')
    
    # Table des milestones (jalons)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS milestones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            due_date DATE,
            status TEXT DEFAULT 'PENDING',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        )
    ''')
    
    # Table des tâches
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            milestone_id INTEGER,
            title TEXT NOT NULL,
            description TEXT,
            priority TEXT DEFAULT 'MEDIUM',
            status TEXT DEFAULT 'TODO',
            progress INTEGER DEFAULT 0,
            assigned_to INTEGER,
            deadline DATE,
            estimated_hours REAL,
            actual_hours REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
            FOREIGN KEY (milestone_id) REFERENCES milestones(id) ON DELETE SET NULL,
            FOREIGN KEY (assigned_to) REFERENCES users(id) ON DELETE SET NULL
        )
    ''')
    
    # Table d'association projets-membres
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS project_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            role_in_project TEXT DEFAULT 'member',
            assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            UNIQUE(project_id, user_id)
        )
    ''')
    
    # Table des commentaires sur les tâches
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS task_comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            comment TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    # Table du journal d'activité
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS activity_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT NOT NULL,
            entity_type TEXT,
            entity_id INTEGER,
            details TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
        )
    ''')
    
    conn.commit()
    
    # Créer les utilisateurs par défaut si la table est vide
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        create_default_users(cursor)
        conn.commit()
    
    conn.close()
    return True


def create_default_users(cursor):
    """Crée les utilisateurs par défaut pour les tests."""
    # Mots de passe hashés
    admin_password = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    chef_password = bcrypt.hashpw("chef123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    member_password = bcrypt.hashpw("membre123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    default_users = [
        # Administrateur
        ("admin", "admin@test.com", admin_password, ROLE_ADMIN, "Administrateur Système"),
        # Chefs de projet
        ("chef.projet", "chef@test.com", chef_password, ROLE_PROJECT_MANAGER, "Chef de Projet"),
        ("sophie.manager", "sophie@test.com", chef_password, ROLE_PROJECT_MANAGER, "Sophie Manager"),
        # Membres d'équipe
        ("jean.dupont", "jean@test.com", member_password, ROLE_MEMBER, "Jean Dupont"),
        ("marie.martin", "marie@test.com", member_password, ROLE_MEMBER, "Marie Martin"),
        ("pierre.durand", "pierre@test.com", member_password, ROLE_MEMBER, "Pierre Durand"),
    ]
    
    cursor.executemany('''
        INSERT INTO users (username, email, password_hash, role, full_name)
        VALUES (?, ?, ?, ?, ?)
    ''', default_users)


def reset_database():
    """Supprime et recrée la base de données (pour les tests)."""
    if os.path.exists(DATABASE_PATH):
        os.remove(DATABASE_PATH)
    init_database()


if __name__ == "__main__":
    init_database()
    print(f"Base de données initialisée: {DATABASE_PATH}")
