"""
Module de base de données pour la gestion de projets.
"""

from .db_setup import init_database, get_connection
from .crud import *
