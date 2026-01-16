"""
Mise à jour de l'avancement - Interface membre.
"""

import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from services.auth_service import require_auth, get_current_user_id
from services.task_service import (
    get_user_assigned_tasks, update_task_progress_value,
    get_task_details, add_comment_to_task
)
from config import TASK_STATUS, TASK_PRIORITY


def render_update_progress():
    """Page de mise à jour de l'avancement."""
    require_auth()
    user_id = get_current_user_id()
    
    st.markdown("<h1>🔄 Mise à jour de l'avancement</h1>", unsafe_allow_html=True)
    
    # Récupérer les tâches non terminées
    tasks = get_user_assigned_tasks(user_id)
    tasks = [t for t in tasks if t.status != 'COMPLETED']
    
    if not tasks:
        st.success("🎉 Toutes vos tâches sont terminées!")
        return
    
    st.markdown(f"**{len(tasks)} tâche(s) à mettre à jour**")
    
    # Sélection de la tâche
    selected_task_id = st.selectbox(
        "Sélectionner une tâche",
        options=[t.id for t in tasks],
        format_func=lambda x: next(
            f"{t.title} ({t.progress}%)" for t in tasks if t.id == x
        )
    )
    
    if selected_task_id:
        task = get_task_details(selected_task_id)
        if task:
            render_progress_form(task, user_id)


def render_progress_form(task, user_id):
    """Formulaire de mise à jour de progression."""
    st.markdown("---")
    
    # Informations de la tâche
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"### 📋 {task.title}")
        if task.description:
            st.markdown(f"*{task.description}*")
    with col2:
        st.markdown(f"**Projet:** {task.project_name}")
        st.markdown(f"**Priorité:** {TASK_PRIORITY[task.priority]}")
        st.markdown(f"**Deadline:** {task.deadline or 'Non définie'}")
    
    if task.is_overdue:
        st.error("⚠️ Cette tâche est en retard!")
    
    st.markdown("---")
    
    # Formulaire
    with st.form("update_progress"):
        new_progress = st.slider(
            "Nouvelle progression",
            min_value=0,
            max_value=100,
            value=task.progress,
            step=5
        )
        
        # Statut automatique
        if new_progress == 0:
            new_status = "À faire"
        elif new_progress == 100:
            new_status = "Terminé"
        else:
            new_status = "En cours"
        
        st.info(f"Nouveau statut: **{new_status}**")
        
        comment = st.text_area(
            "Ajouter un commentaire (optionnel)",
            placeholder="Décrivez ce qui a été fait..."
        )
        
        submitted = st.form_submit_button("🔄 Mettre à jour", use_container_width=True)
        
        if submitted:
            success = update_task_progress_value(
                task.id, new_progress, user_id, comment if comment else None
            )
            
            if success:
                if new_progress == 100:
                    st.success("🎉 Tâche terminée! Excellent travail!")
                    st.balloons()
                else:
                    st.success("✅ Progression mise à jour!")
                st.rerun()
            else:
                st.error("Erreur lors de la mise à jour.")
