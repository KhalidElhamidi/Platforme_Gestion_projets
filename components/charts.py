"""
Composants de visualisation graphique avec Plotly.
"""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import List, Dict, Any
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import THEME_COLORS, PROJECT_STATUS, TASK_STATUS, TASK_PRIORITY


# Palette de couleurs
COLORS = {
    'primary': '#667eea',
    'secondary': '#764ba2',
    'success': '#48bb78',
    'warning': '#ed8936',
    'danger': '#f56565',
    'info': '#4299e1',
    'purple': '#9f7aea',
    'pink': '#ed64a6',
    'gray': '#718096'
}

STATUS_COLORS = {
    'TODO': COLORS['gray'],
    'IN_PROGRESS': COLORS['info'],
    'REVIEW': COLORS['purple'],
    'COMPLETED': COLORS['success'],
    'BLOCKED': COLORS['danger']
}

PRIORITY_COLORS = {
    'LOW': COLORS['success'],
    'MEDIUM': COLORS['info'],
    'HIGH': COLORS['warning'],
    'CRITICAL': COLORS['danger']
}


def create_progress_gauge(value: float, title: str = "Progression") -> go.Figure:
    """
    Crée une jauge de progression circulaire.
    """
    # Déterminer la couleur selon la valeur
    if value >= 75:
        color = COLORS['success']
    elif value >= 50:
        color = COLORS['info']
    elif value >= 25:
        color = COLORS['warning']
    else:
        color = COLORS['danger']
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 16}},
        number={'suffix': '%', 'font': {'size': 36, 'color': color}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': COLORS['gray']},
            'bar': {'color': color},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': COLORS['gray'],
            'steps': [
                {'range': [0, 25], 'color': '#fed7d7'},
                {'range': [25, 50], 'color': '#feebc8'},
                {'range': [50, 75], 'color': '#bee3f8'},
                {'range': [75, 100], 'color': '#c6f6d5'}
            ],
            'threshold': {
                'line': {'color': COLORS['danger'], 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    
    fig.update_layout(
        height=250,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig


def create_tasks_by_status_chart(data: Dict[str, int], title: str = "Tâches par statut") -> go.Figure:
    """
    Crée un graphique en barres des tâches par statut.
    """
    statuses = list(data.keys())
    values = list(data.values())
    colors = [STATUS_COLORS.get(s, COLORS['gray']) for s in statuses]
    labels = [TASK_STATUS.get(s, s) for s in statuses]
    
    fig = go.Figure(data=[
        go.Bar(
            x=labels,
            y=values,
            marker_color=colors,
            text=values,
            textposition='auto',
            hovertemplate='%{x}: %{y} tâches<extra></extra>'
        )
    ])
    
    fig.update_layout(
        title=title,
        xaxis_title="",
        yaxis_title="Nombre de tâches",
        height=350,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False
    )
    
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor='rgba(0,0,0,0.1)')
    
    return fig


def create_tasks_pie_chart(data: Dict[str, int], title: str = "Répartition des tâches") -> go.Figure:
    """
    Crée un graphique circulaire des tâches.
    """
    labels = [TASK_STATUS.get(k, k) for k in data.keys()]
    values = list(data.values())
    colors = [STATUS_COLORS.get(k, COLORS['gray']) for k in data.keys()]
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.4,
        marker_colors=colors,
        textinfo='percent+value',
        textposition='outside',
        hovertemplate='%{label}: %{value} tâches (%{percent})<extra></extra>'
    )])
    
    fig.update_layout(
        title=title,
        height=350,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        showlegend=True,
        legend=dict(orientation='h', yanchor='bottom', y=-0.2)
    )
    
    return fig


def create_priority_distribution_chart(data: Dict[str, int]) -> go.Figure:
    """
    Crée un graphique de la distribution des priorités.
    """
    labels = [TASK_PRIORITY.get(k, k) for k in data.keys()]
    values = list(data.values())
    colors = [PRIORITY_COLORS.get(k, COLORS['gray']) for k in data.keys()]
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.5,
        marker_colors=colors,
        textinfo='percent+label',
        hovertemplate='%{label}: %{value} tâches<extra></extra>'
    )])
    
    fig.update_layout(
        title="Répartition par priorité",
        height=300,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        showlegend=False
    )
    
    return fig


def create_member_performance_chart(data: List[Dict[str, Any]]) -> go.Figure:
    """
    Crée un graphique de performance des membres.
    """
    if not data:
        return go.Figure()
    
    df = pd.DataFrame(data)
    
    fig = go.Figure()
    
    # Barres pour les tâches complétées
    fig.add_trace(go.Bar(
        name='Complétées',
        x=df['name'],
        y=df['completed'],
        marker_color=COLORS['success'],
        text=df['completed'],
        textposition='auto'
    ))
    
    # Barres pour les tâches restantes
    remaining = df['tasks'] - df['completed']
    fig.add_trace(go.Bar(
        name='Restantes',
        x=df['name'],
        y=remaining,
        marker_color=COLORS['info'],
        text=remaining,
        textposition='auto'
    ))
    
    fig.update_layout(
        title="Performance des membres",
        xaxis_title="",
        yaxis_title="Nombre de tâches",
        barmode='stack',
        height=400,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
    )
    
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor='rgba(0,0,0,0.1)')
    
    return fig


def create_progress_timeline(data: List[Dict[str, Any]], title: str = "Évolution de la progression") -> go.Figure:
    """
    Crée un graphique de l'évolution de la progression dans le temps.
    """
    if not data:
        return go.Figure()
    
    df = pd.DataFrame(data)
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['progress'],
        mode='lines+markers',
        name='Progression',
        line=dict(color=COLORS['primary'], width=3),
        marker=dict(size=8),
        fill='tozeroy',
        fillcolor='rgba(102, 126, 234, 0.2)',
        hovertemplate='%{x}<br>Progression: %{y}%<extra></extra>'
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title="Progression (%)",
        yaxis=dict(range=[0, 100]),
        height=350,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False
    )
    
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor='rgba(0,0,0,0.1)')
    
    return fig


def create_velocity_chart(data: List[Dict[str, Any]]) -> go.Figure:
    """
    Crée un graphique de la vélocité de l'équipe.
    """
    if not data:
        return go.Figure()
    
    df = pd.DataFrame(data)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df['week'],
        y=df['tasks_completed'],
        marker_color=COLORS['primary'],
        text=df['tasks_completed'],
        textposition='outside',
        hovertemplate='%{x}<br>Tâches: %{y}<extra></extra>'
    ))
    
    # Ligne de tendance (moyenne)
    avg = df['tasks_completed'].mean()
    fig.add_hline(
        y=avg, 
        line_dash="dash", 
        line_color=COLORS['warning'],
        annotation_text=f"Moyenne: {avg:.1f}",
        annotation_position="right"
    )
    
    fig.update_layout(
        title="Vélocité de l'équipe (tâches/semaine)",
        xaxis_title="",
        yaxis_title="Tâches complétées",
        height=300,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False
    )
    
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor='rgba(0,0,0,0.1)')
    
    return fig


def create_projects_overview_chart(projects: List[Any]) -> go.Figure:
    """
    Crée un graphique d'aperçu de tous les projets.
    """
    if not projects:
        return go.Figure()
    
    names = [p.name[:20] + "..." if len(p.name) > 20 else p.name for p in projects]
    progress = [p.progress for p in projects]
    
    # Couleurs selon la progression
    colors = []
    for p in progress:
        if p >= 75:
            colors.append(COLORS['success'])
        elif p >= 50:
            colors.append(COLORS['info'])
        elif p >= 25:
            colors.append(COLORS['warning'])
        else:
            colors.append(COLORS['danger'])
    
    fig = go.Figure(data=[
        go.Bar(
            x=progress,
            y=names,
            orientation='h',
            marker_color=colors,
            text=[f"{p}%" for p in progress],
            textposition='outside',
            hovertemplate='%{y}<br>Progression: %{x}%<extra></extra>'
        )
    ])
    
    fig.update_layout(
        title="Avancement des projets",
        xaxis_title="Progression (%)",
        yaxis_title="",
        xaxis=dict(range=[0, 110]),
        height=max(300, len(projects) * 50),
        margin=dict(l=150, r=50, t=50, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False
    )
    
    fig.update_xaxes(showgrid=True, gridcolor='rgba(0,0,0,0.1)')
    fig.update_yaxes(showgrid=False)
    
    return fig


def create_workload_distribution_chart(data: List[Dict[str, Any]]) -> go.Figure:
    """
    Crée un graphique de distribution de la charge de travail.
    """
    if not data:
        return go.Figure()
    
    df = pd.DataFrame(data)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df['name'],
        y=df['tasks'],
        marker_color=COLORS['primary'],
        text=df['tasks'],
        textposition='outside',
        name='Total tâches'
    ))
    
    fig.update_layout(
        title="Distribution de la charge de travail",
        xaxis_title="",
        yaxis_title="Nombre de tâches",
        height=350,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False
    )
    
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor='rgba(0,0,0,0.1)')
    
    return fig


def create_completion_rate_chart(data: List[Dict[str, Any]]) -> go.Figure:
    """
    Crée un graphique des taux de complétion.
    """
    if not data:
        return go.Figure()
    
    df = pd.DataFrame(data)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df['name'],
        y=df['completion_rate'],
        marker_color=[
            COLORS['success'] if r >= 70 else 
            COLORS['warning'] if r >= 40 else 
            COLORS['danger'] 
            for r in df['completion_rate']
        ],
        text=[f"{r:.0f}%" for r in df['completion_rate']],
        textposition='outside',
        hovertemplate='%{x}<br>Taux: %{y:.1f}%<extra></extra>'
    ))
    
    fig.update_layout(
        title="Taux de complétion par membre",
        xaxis_title="",
        yaxis_title="Taux de complétion (%)",
        yaxis=dict(range=[0, 110]),
        height=350,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False
    )
    
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor='rgba(0,0,0,0.1)')
    
    return fig


def create_dashboard_metrics() -> Dict[str, go.Figure]:
    """
    Crée un ensemble de graphiques pour le tableau de bord.
    Retourne un dictionnaire de figures Plotly.
    """
    from services.progress_service import (
        get_dashboard_statistics,
        get_all_members_performance,
        get_team_velocity
    )
    from database.crud import get_all_projects
    
    stats = get_dashboard_statistics()
    performances = get_all_members_performance()
    velocity = get_team_velocity()
    projects = get_all_projects()
    
    metrics = {}
    
    # Jauge de progression globale
    metrics['progress_gauge'] = create_progress_gauge(
        stats.overall_progress, 
        "Progression globale"
    )
    
    # Tâches par statut
    tasks_by_status = {
        'TODO': stats.total_tasks - stats.completed_tasks - stats.in_progress_tasks,
        'IN_PROGRESS': stats.in_progress_tasks,
        'COMPLETED': stats.completed_tasks
    }
    metrics['tasks_status'] = create_tasks_by_status_chart(tasks_by_status)
    
    # Performance des membres
    if performances:
        perf_data = [
            {'name': p.user_name, 'tasks': p.total_tasks, 
             'completed': p.completed_tasks, 'completion_rate': p.completion_rate}
            for p in performances
        ]
        metrics['member_performance'] = create_member_performance_chart(perf_data)
        metrics['completion_rate'] = create_completion_rate_chart(perf_data)
    
    # Vélocité
    if velocity['weekly_data']:
        metrics['velocity'] = create_velocity_chart(velocity['weekly_data'])
    
    # Projets
    if projects:
        metrics['projects_overview'] = create_projects_overview_chart(projects)
    
    return metrics
