"""
Page de connexion.
"""

import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.auth_service import login, is_authenticated
from config import APP_TITLE, THEME_COLORS


def render_login_page():
    """Affiche la page de connexion."""
    
    # CSS personnalisé pour la page de connexion
    st.markdown("""
        <style>
        .login-container {
            max-width: 400px;
            margin: 0 auto;
            padding: 2rem;
        }
        .login-header {
            text-align: center;
            margin-bottom: 2rem;
        }
        .login-header h1 {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }
        .login-header p {
            color: #718096;
            font-size: 1rem;
        }
        .login-card {
            background: white;
            border-radius: 16px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
            padding: 2rem;
        }
        .stButton > button {
            width: 100%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }
        .demo-accounts {
            background: #f7fafc;
            border-radius: 8px;
            padding: 1rem;
            margin-top: 1.5rem;
        }
        .demo-accounts h4 {
            color: #4a5568;
            margin-bottom: 0.5rem;
        }
        .demo-accounts code {
            background: #e2e8f0;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 0.85rem;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Conteneur centré
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # En-tête
        st.markdown(f"""
            <div class="login-header">
                <h1>🎯 {APP_TITLE}</h1>
                <p>Plateforme de gestion de projets avec suivi automatisé</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Formulaire de connexion
        st.markdown("### 🔐 Connexion")
        
        with st.form("login_form"):
            email = st.text_input(
                "Email ou nom d'utilisateur",
                placeholder="Entrez votre email ou nom d'utilisateur"
            )
            
            password = st.text_input(
                "Mot de passe",
                type="password",
                placeholder="Entrez votre mot de passe"
            )
            
            submitted = st.form_submit_button("🚀 Se connecter", use_container_width=True)
            
            if submitted:
                if not email or not password:
                    st.error("⚠️ Veuillez remplir tous les champs.")
                else:
                    success, message = login(email, password)
                    if success:
                        st.success(f"✅ {message}")
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
        
    
        
        # Footer
        st.markdown("""
            <div style="text-align: center; margin-top: 2rem; color: #a0aec0; font-size: 0.85rem;">
                <p>© 2024 Gestion de Projets - Projet de fin de module Python</p>
            </div>
        """, unsafe_allow_html=True)
