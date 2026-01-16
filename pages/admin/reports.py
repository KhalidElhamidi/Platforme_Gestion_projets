"""
Rapports et statistiques - Interface administrateur.
"""

import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from services.auth_service import require_admin
from services.report_service import (
    generate_project_report, generate_team_performance_report,
    export_project_to_csv, export_all_projects_to_csv,
    export_team_performance_to_csv, generate_pdf_report
)
from services.progress_service import (
    get_dashboard_statistics, get_all_members_performance,
    get_progress_over_time, get_workload_distribution
)
from database.crud import get_all_projects
from components.charts import (
    create_progress_timeline, create_member_performance_chart,
    create_workload_distribution_chart, create_completion_rate_chart
)


def render_reports_page():
    """Affiche la page des rapports."""
    require_admin()
    
    st.markdown("<h1>📋 Rapports & Statistiques</h1>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📊 Rapports", "📈 Analyses", "📥 Exports"])
    
    with tab1:
        render_reports_section()
    with tab2:
        render_analysis_section()
    with tab3:
        render_export_section()


def render_reports_section():
    """Section des rapports."""
    st.markdown("### 📁 Rapport par projet")
    
    projects = get_all_projects()
    if not projects:
        st.info("Aucun projet disponible.")
        return
    
    selected = st.selectbox(
        "Sélectionner un projet",
        options=[p.id for p in projects],
        format_func=lambda x: next(p.name for p in projects if p.id == x)
    )
    
    if st.button("📊 Générer le rapport"):
        report = generate_project_report(selected)
        if report:
            st.markdown(f"## 📁 {report['project'].name}")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total tâches", report['stats']['total_tasks'])
            with col2:
                st.metric("Complétées", report['stats']['completed_tasks'])
            with col3:
                st.metric("En cours", report['stats']['in_progress_tasks'])
            with col4:
                st.metric("En retard", report['stats']['overdue_tasks'])
            
            st.markdown("### 🎯 Milestones")
            for ms in report['milestones']:
                st.markdown(f"- **{ms.name}**: {ms.progress:.0f}%")
            
            for m in report['members']:
                st.markdown(f"- {m.user_name}")
            
            # Bouton de téléchargement du rapport PDF complet
            st.markdown("---")
            pdf_data = generate_pdf_report(selected)
            if pdf_data:
                st.download_button(
                    label=f"📥 Télécharger le rapport complet pour {report['project'].name}",
                    data=pdf_data,
                    file_name=f"rapport_projet_{report['project'].id}.pdf",
                    mime="application/pdf"
                )
            else:
                st.error("Impossible de générer le PDF. Vérifiez l'installation de ReportLab.")


def render_analysis_section():
    """Section d'analyse."""
    st.markdown("### 📈 Évolution de la progression")
    
    progress_data = get_progress_over_time(days=30)
    if progress_data:
        fig = create_progress_timeline(progress_data)
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("### 👥 Performance de l'équipe")
    
    performances = get_all_members_performance()
    if performances:
        perf_data = [
            {'name': p.user_name, 'tasks': p.total_tasks, 
             'completed': p.completed_tasks, 'completion_rate': p.completion_rate}
            for p in performances
        ]
        
        col1, col2 = st.columns(2)
        with col1:
            fig = create_member_performance_chart(perf_data)
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig = create_completion_rate_chart(perf_data)
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("### ⚖️ Distribution de la charge")
    
    workload = get_workload_distribution()
    if workload['distribution']:
        fig = create_workload_distribution_chart(workload['distribution'])
        st.plotly_chart(fig, use_container_width=True)
        
        if workload['balanced']:
            st.success("✅ La charge de travail est équilibrée")
        else:
            st.warning("⚠️ La charge de travail est déséquilibrée")


def render_export_section():
    """Section d'export."""
    st.markdown("### 📥 Exporter les données")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Projets**")
        csv_data = export_all_projects_to_csv()
        st.download_button(
            "📥 Télécharger CSV",
            data=csv_data,
            file_name="projets.csv",
            mime="text/csv"
        )
    
    with col2:
        st.markdown("**Performance équipe**")
        csv_perf = export_team_performance_to_csv()
        st.download_button(
            "📥 Télécharger CSV",
            data=csv_perf,
            file_name="performance.csv",
            mime="text/csv"
        )
    
    st.markdown("---")
    st.markdown("**Rapport PDF**")
    
    if st.button("📄 Générer PDF Global"):
        pdf_data = generate_pdf_report()
        if pdf_data:
            st.download_button(
                "📥 Télécharger PDF",
                data=pdf_data,
                file_name="rapport_global.pdf",
                mime="application/pdf"
            )
        else:
            st.warning("ReportLab non installé pour la génération PDF")
