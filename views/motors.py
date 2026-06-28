"""
Vue 4 moteurs — comparaison FL/FR/RL/RR
Torque, RPM, température, courant AC par inverseur
"""
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import html, dcc
from constants import (BG, BG3, BG4, BG5, BORDER, BORDER2,
                       MONO, SANS, DIM, TEXT, ROUGE, ORANGE, VERT, COULEURS)


MOTEURS = [
    {'id': 'DI1', 'label': 'FL', 'couleur': '#5b9bd5'},
    {'id': 'DI2', 'label': 'FR', 'couleur': '#70ad47'},
    {'id': 'DI3', 'label': 'RL', 'couleur': '#ed7d31'},
    {'id': 'DI4', 'label': 'RR', 'couleur': '#ffc000'},
]

# Variantes de noms par signal
SIGNAL_VARIANTS = {
    'RPM':         ['{id}_RPM', 'DI_Inv{n}_speed_rpm'],
    'AC_current':  ['{id}_AC', '{id}_AC_current', 'DI_Inv{n}_iq'],
    'CTL_Temp':    ['{id}CTL_Temp', '{id}_Controller_Temperature'],
    'MOT_Temp':    ['{id}MOT_Temp', '{id}_Motor_Temperature'],
    'Fault':       ['{id}_Fault_Code', '{id}_FaultCode'],
}


def _section(titre):
    return html.Div(titre, style={
        'fontFamily': SANS, 'fontSize': '10px', 'color': DIM,
        'padding': '4px 8px', 'background': BG5,
        'borderBottom': f'1px solid {BORDER}',
    })


def _get(mdf, canaux, templates, di_id, n):
    for tmpl in templates:
        nom = tmpl.replace('{id}', di_id).replace('{n}', str(n))
        if nom in canaux:
            try:
                sig = mdf.get(nom)
                return sig.timestamps.astype(float), sig.samples.astype(float), nom
            except Exception:
                continue
    return None, None, None


def _kpi_mini(label, val, unite, couleur=TEXT):
    return html.Div([
        html.Div(label, style={'fontFamily': SANS, 'fontSize': '8px', 'color': '#333',
                               'letterSpacing': '0.08em'}),
        html.Span(val, style={'fontFamily': MONO, 'fontSize': '15px', 'color': couleur}),
        html.Span(f' {unite}', style={'fontFamily': SANS, 'fontSize': '9px', 'color': '#444'}),
    ], style={'padding': '4px 8px', 'flex': '1', 'textAlign': 'center',
              'borderRight': f'1px solid {BORDER}'})


def construire_motors(mdf, canaux_disponibles):
    from ui import msg
    blocs = [_section("motors — 4-inverter comparison")]

    # ── KPI par moteur ─────────────────────────────────────────────────────
    kpi_row = []
    motor_data = {}

    for i, m in enumerate(MOTEURS):
        di   = m['id']
        n    = i + 1
        col  = m['couleur']
        lbl  = m['label']

        t_rpm, s_rpm, _ = _get(mdf, canaux_disponibles, SIGNAL_VARIANTS['RPM'], di, n)
        t_iac, s_iac, _ = _get(mdf, canaux_disponibles, SIGNAL_VARIANTS['AC_current'], di, n)
        t_ctl, s_ctl, _ = _get(mdf, canaux_disponibles, SIGNAL_VARIANTS['CTL_Temp'], di, n)
        t_mot, s_mot, _ = _get(mdf, canaux_disponibles, SIGNAL_VARIANTS['MOT_Temp'], di, n)

        motor_data[di] = {
            'rpm': (t_rpm, s_rpm), 'iac': (t_iac, s_iac),
            'ctl': (t_ctl, s_ctl), 'mot': (t_mot, s_mot),
            'label': lbl, 'couleur': col,
        }

        rpm_avg  = f"{np.nanmean(np.abs(s_rpm)):.0f}"  if s_rpm is not None else '—'
        rpm_max  = f"{np.nanmax(np.abs(s_rpm)):.0f}"   if s_rpm is not None else '—'
        ctl_max  = f"{np.nanmax(s_ctl):.1f}"            if s_ctl is not None else '—'
        mot_max  = f"{np.nanmax(s_mot):.1f}"            if s_mot is not None else '—'
        iac_max  = f"{np.nanmax(np.abs(s_iac)):.1f}"   if s_iac is not None else '—'

        c_ctl = ROUGE if s_ctl is not None and np.nanmax(s_ctl) > 80 else \
                ORANGE if s_ctl is not None and np.nanmax(s_ctl) > 70 else TEXT
        c_mot = ROUGE if s_mot is not None and np.nanmax(s_mot) > 75 else \
                ORANGE if s_mot is not None and np.nanmax(s_mot) > 65 else TEXT

        kpi_row.append(html.Div([
            html.Div([
                html.Div(style={'width': '4px', 'background': col,
                                'alignSelf': 'stretch', 'flexShrink': '0'}),
                html.Div(lbl, style={'fontFamily': MONO, 'fontSize': '18px', 'color': col,
                                     'padding': '0 8px', 'fontWeight': '600'}),
            ], style={'display': 'flex', 'alignItems': 'center',
                      'borderBottom': f'1px solid {BORDER}', 'padding': '4px 0'}),
            html.Div([
                _kpi_mini('RPM avg', rpm_avg, ''),
                _kpi_mini('RPM max', rpm_max, ''),
                _kpi_mini('I_AC max', iac_max, 'A'),
                _kpi_mini('CTL max', ctl_max, '°C', c_ctl),
                _kpi_mini('MOT max', mot_max, '°C', c_mot),
            ], style={'display': 'flex', 'flexWrap': 'wrap'}),
        ], style={
            'flex': '1', 'minWidth': '220px',
            'background': BG3, 'border': f'1px solid {BORDER}',
        }))

    blocs.append(html.Div(kpi_row, style={
        'display': 'flex', 'flexWrap': 'wrap', 'gap': '1px',
        'padding': '8px', 'background': BG4,
        'borderBottom': f'1px solid {BORDER}',
    }))

    # ── Graphe RPM comparatif ─────────────────────────────────────────────
    blocs.append(_section("motor speed — all 4 wheels"))

    fig_rpm = go.Figure()
    for m in MOTEURS:
        di = m['id']
        t_rpm, s_rpm = motor_data[di]['rpm']
        if t_rpm is not None:
            fig_rpm.add_trace(go.Scatter(
                x=t_rpm, y=np.abs(s_rpm),
                mode='lines', name=m['label'],
                line=dict(color=m['couleur'], width=1.0),
                hovertemplate=f'<b>{m["label"]}</b><br>t=%{{x:.1f}}s  %{{y:.0f}} rpm<extra></extra>',
            ))

    _update_fig(fig_rpm, 'RPM', 160)
    blocs.append(dcc.Graph(figure=fig_rpm,
                           config=_cfg('formul_rpm'), style={'height': '160px'}))

    # ── Graphe courant AC ─────────────────────────────────────────────────
    blocs.append(_section("AC current — all 4 inverters"))

    fig_iac = go.Figure()
    for m in MOTEURS:
        di = m['id']
        t_iac, s_iac = motor_data[di]['iac']
        if t_iac is not None:
            fig_iac.add_trace(go.Scatter(
                x=t_iac, y=np.abs(s_iac),
                mode='lines', name=m['label'],
                line=dict(color=m['couleur'], width=1.0),
                hovertemplate=f'<b>{m["label"]}</b><br>t=%{{x:.1f}}s  %{{y:.1f}} A<extra></extra>',
            ))

    _update_fig(fig_iac, 'A (AC)', 140)
    blocs.append(dcc.Graph(figure=fig_iac,
                           config=_cfg('formul_iac'), style={'height': '140px'}))

    # ── Graphe températures ───────────────────────────────────────────────
    blocs.append(_section("temperatures — controller & motor"))

    fig_temp = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.04,
                             subplot_titles=[
                                 "<span style='font-family:Arial;font-size:10px;color:#555'>Controller (°C)</span>",
                                 "<span style='font-family:Arial;font-size:10px;color:#555'>Motor (°C)</span>",
                             ])

    for m in MOTEURS:
        di = m['id']
        t_ctl, s_ctl = motor_data[di]['ctl']
        t_mot, s_mot = motor_data[di]['mot']
        if t_ctl is not None:
            fig_temp.add_trace(go.Scatter(
                x=t_ctl, y=s_ctl, mode='lines', name=f'{m["label"]} CTL',
                line=dict(color=m['couleur'], width=1.0),
                hovertemplate=f'<b>{m["label"]} CTL</b><br>t=%{{x:.1f}}s  %{{y:.1f}}°C<extra></extra>',
            ), row=1, col=1)
        if t_mot is not None:
            fig_temp.add_trace(go.Scatter(
                x=t_mot, y=s_mot, mode='lines', name=f'{m["label"]} MOT',
                line=dict(color=m['couleur'], width=1.0, dash='dash'),
                hovertemplate=f'<b>{m["label"]} MOT</b><br>t=%{{x:.1f}}s  %{{y:.1f}}°C<extra></extra>',
            ), row=2, col=1)

    # Seuils températures
    for row, seuil in [(1, 85), (2, 80)]:
        fig_temp.add_hline(y=seuil, line_dash='dot',
                           line_color='rgba(192,64,64,0.4)', line_width=1,
                           row=row, col=1)

    for row in [1, 2]:
        fig_temp.update_yaxes(
            title_text='°C', title_standoff=3, row=row, col=1,
            gridcolor='#1e1e1e', color='#444',
            tickfont=dict(family='Consolas, monospace', size=10, color='#555'),
            title_font=dict(family='Arial, sans-serif', size=10, color='#444'),
            fixedrange=True,
        )

    fig_temp.update_layout(
        paper_bgcolor=BG, plot_bgcolor='#131313',
        font=dict(color=TEXT, family='Arial, sans-serif', size=10),
        margin=dict(l=56, r=12, t=14, b=28),
        hovermode='x unified',
        hoverlabel=dict(bgcolor='#1e1e1e', bordercolor='#333',
                        font=dict(family='Consolas, monospace', size=10, color='#aaa')),
        showlegend=True,
        legend=dict(bgcolor='rgba(15,15,15,0.9)', bordercolor=BORDER, borderwidth=1,
                    font=dict(family=SANS, size=10, color=DIM),
                    orientation='h', x=0, y=1.04, xanchor='left'),
        height=280, dragmode='pan',
    )
    fig_temp.update_xaxes(
        gridcolor='#1e1e1e', color='#444', zeroline=False,
        tickfont=dict(family='Consolas, monospace', size=10, color='#555'),
        showline=True, linecolor='#2a2a2a', fixedrange=False,
    )
    fig_temp.update_xaxes(title_text='t (s)', row=2, col=1,
                          title_font=dict(family='Arial, sans-serif', size=10, color='#444'),
                          title_standoff=3)
    fig_temp.add_shape(type='line', xref='paper', yref='paper',
                       x0=0, x1=1, y0=0.5, y1=0.5,
                       line=dict(color='#252525', width=1))

    blocs.append(dcc.Graph(figure=fig_temp,
                           config=_cfg('formul_temps'), style={'height': '280px'}))

    # ── Déséquilibre thermique ────────────────────────────────────────────
    blocs.append(_section("thermal imbalance — max spread between motors"))

    temps_ctl = {}
    t_ref = None
    for m in MOTEURS:
        t_ctl, s_ctl = motor_data[m['id']]['ctl']
        if t_ctl is not None:
            if t_ref is None:
                t_ref = t_ctl
            temps_ctl[m['id']] = np.interp(t_ref, t_ctl, s_ctl)

    if len(temps_ctl) >= 2 and t_ref is not None:
        mat = np.array(list(temps_ctl.values()))
        spread = np.max(mat, axis=0) - np.min(mat, axis=0)
        fig_sp = go.Figure()
        couleur_sp = ROUGE if np.nanmax(spread) > 10 else ORANGE if np.nanmax(spread) > 5 else VERT
        fig_sp.add_trace(go.Scatter(
            x=t_ref, y=spread, mode='lines',
            line=dict(color=couleur_sp, width=1.2),
            fill='tozeroy', fillcolor='rgba(192,64,64,0.06)',
            hovertemplate='Spread: %{y:.1f}°C<extra></extra>',
        ))
        _update_fig(fig_sp, '°C', 120)
        fig_sp.add_hline(y=10, line_dash='dot', line_color='rgba(192,64,64,0.4)', line_width=1)
        blocs.append(dcc.Graph(figure=fig_sp,
                               config=_cfg('formul_spread'), style={'height': '120px'}))
    else:
        blocs.append(html.Div("Not enough temperature channels for spread analysis.",
                              style={'fontFamily': SANS, 'fontSize': '10px',
                                     'color': DIM, 'padding': '6px 8px'}))

    return html.Div(blocs)


def _update_fig(fig, yunit, h):
    fig.update_layout(
        paper_bgcolor=BG, plot_bgcolor='#131313',
        font=dict(color=TEXT, family='Arial, sans-serif', size=10),
        margin=dict(l=56, r=12, t=8, b=28),
        hovermode='x unified',
        hoverlabel=dict(bgcolor='#1e1e1e', bordercolor='#333',
                        font=dict(family='Consolas, monospace', size=10, color='#aaa')),
        showlegend=True,
        legend=dict(bgcolor='rgba(15,15,15,0.9)', bordercolor=BORDER, borderwidth=1,
                    font=dict(family=SANS, size=10, color=DIM),
                    orientation='h', x=0, y=1.02, xanchor='left'),
        height=h, dragmode='pan',
    )
    fig.update_xaxes(
        gridcolor='#1e1e1e', color='#444', zeroline=False,
        tickfont=dict(family='Consolas, monospace', size=10, color='#555'),
        showline=True, linecolor='#2a2a2a', fixedrange=False,
        title_text='t (s)',
        title_font=dict(family='Arial, sans-serif', size=10, color='#444'),
        title_standoff=3,
    )
    fig.update_yaxes(
        title_text=yunit, gridcolor='#1e1e1e', color='#444',
        tickfont=dict(family='Consolas, monospace', size=10, color='#555'),
        title_font=dict(family='Arial, sans-serif', size=10, color='#444'),
        title_standoff=3, fixedrange=True,
    )


def _cfg(filename):
    return {
        'displayModeBar': True,
        'displaylogo': False,
        'modeBarButtonsToRemove': ['select2d', 'lasso2d', 'toggleSpikelines',
                                   'drawopenpath', 'drawclosedpath', 'drawcircle',
                                   'drawrect', 'eraseshape'],
        'scrollZoom': True,
        'toImageButtonOptions': {'format': 'png', 'filename': filename,
                                 'scale': 2},
    }
