import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import html, dcc
from constants import (BG, BG3, BG4, BG5, BORDER, BORDER2,
                       MONO, SANS, DIM, TEXT, ROUGE, ORANGE, VERT, ACCENT)


def _section(titre):
    return html.Div(titre, style={
        'fontFamily': SANS, 'fontSize': '10px', 'color': DIM,
        'padding': '4px 8px', 'background': BG5,
        'borderBottom': f'1px solid {BORDER}',
    })


def _kpi(label, valeur, unite, couleur=TEXT, sous_texte=''):
    return html.Div([
        html.Div(label, style={
            'fontFamily': SANS, 'fontSize': '9px', 'color': '#444',
            'letterSpacing': '0.1em', 'marginBottom': '4px',
        }),
        html.Div([
            html.Span(valeur, style={
                'fontFamily': MONO, 'fontSize': '22px', 'color': couleur,
                'fontWeight': '500',
            }),
            html.Span(f"  {unite}", style={
                'fontFamily': SANS, 'fontSize': '11px', 'color': '#444',
            }),
        ]),
        html.Div(sous_texte, style={
            'fontFamily': SANS, 'fontSize': '10px', 'color': '#3a3a3a',
            'marginTop': '2px',
        }) if sous_texte else html.Div(),
    ], style={
        'background': BG3, 'border': f'1px solid {BORDER}',
        'padding': '10px 14px', 'flex': '1', 'minWidth': '120px',
    })


def _get(mdf, *noms):
    for nom in noms:
        try:
            sig = mdf.get(nom)
            return sig.timestamps.astype(float), sig.samples.astype(float)
        except Exception:
            continue
    return None, None


def construire_energie(mdf, canaux_disponibles, plage=None):
    from ui import msg
    blocs = [_section("energy — session overview")]

    # ── Données de base ───────────────────────────────────────────────────
    t_v, s_v = _get(mdf, 'BMS_TotVolt', 'BMS_totalVoltage')
    t_i, s_i = _get(mdf, 'BMS_AvgCur',  'BMS_avgCurrent')
    t_soc, s_soc = _get(mdf, 'BMS_SOC')
    t_spd, s_spd = _get(mdf, 'Speed', 'RCP_GPS_Speed')

    if t_v is None or t_i is None:
        return html.Div([
            _section("energy — session overview"),
            html.Div(
                "BMS voltage and current channels not found (BMS_TotVolt / BMS_AvgCur)",
                style={'fontFamily': SANS, 'fontSize': '11px', 'color': DIM,
                       'padding': '16px'}
            )
        ])

    # Appliquer la plage si définie
    def filtrer(t, s):
        if plage and t is not None:
            mask = (t >= plage['debut']) & (t <= plage['fin'])
            return t[mask], s[mask]
        return t, s

    t_v, s_v = filtrer(t_v, s_v)
    t_i, s_i = filtrer(t_i, s_i)

    # Calcul puissance sur grille commune
    if len(t_v) > 1 and len(t_i) > 1:
        t_ref = t_v
        s_i_r = np.interp(t_ref, t_i, s_i)
        s_p   = s_v * s_i_r / 1000.0  # kW

        # Énergie consommée (intégration trapèze)
        dt   = np.diff(t_ref)
        p_av = (s_p[:-1] + s_p[1:]) / 2
        e_kws = p_av * dt  # kW·s par segment
        e_wh  = np.cumsum(e_kws) / 3600.0  # Wh cumulatif
        e_total_wh = float(e_wh[-1]) if len(e_wh) > 0 else 0.0

        # Stats puissance
        p_moy   = float(np.nanmean(s_p))
        p_max   = float(np.nanmax(s_p))
        p_regen = float(np.nanmin(s_p))  # valeur négative = régénération

        # Durée session
        duree_s = float(t_ref[-1] - t_ref[0]) if len(t_ref) > 1 else 0
        duree_min = duree_s / 60.0
    else:
        e_total_wh = 0.0
        p_moy = p_max = p_regen = 0.0
        duree_s = duree_min = 0.0
        s_p = np.array([0.0])
        e_wh = np.array([0.0])
        t_ref = t_v

    # Vitesse moyenne
    if t_spd is not None and len(t_spd) > 1:
        t_spd, s_spd = filtrer(t_spd, s_spd)
        v_moy = float(np.nanmean(s_spd))
        v_max = float(np.nanmax(s_spd))
        dist_km = float(np.trapz(s_spd / 3600.0, t_spd))
        consommation = (e_total_wh / dist_km) if dist_km > 0.1 else 0.0
    else:
        v_moy = v_max = dist_km = consommation = 0.0

    # SOC
    if t_soc is not None and len(t_soc) > 1:
        t_soc, s_soc = filtrer(t_soc, s_soc)
        soc_debut = float(s_soc[0])
        soc_fin   = float(s_soc[-1])
        delta_soc = soc_debut - soc_fin
    else:
        soc_debut = soc_fin = delta_soc = 0.0

    # ── KPIs ─────────────────────────────────────────────────────────────
    couleur_e = ROUGE if e_total_wh > 1500 else (ORANGE if e_total_wh > 800 else TEXT)
    blocs.append(html.Div([
        _kpi("ENERGY CONSUMED", f"{e_total_wh:.0f}", "Wh", couleur_e),
        _kpi("AVG POWER",  f"{p_moy:.1f}", "kW",
             ROUGE if p_moy > 60 else TEXT),
        _kpi("PEAK POWER", f"{p_max:.1f}", "kW",
             ROUGE if p_max > 80 else ORANGE if p_max > 60 else TEXT),
        _kpi("REGEN POWER", f"{abs(p_regen):.1f}", "kW", VERT,
             "max recovered" if p_regen < 0 else "no regen"),
        _kpi("SOC DROP", f"{delta_soc:.1f}", "%",
             ROUGE if delta_soc > 30 else TEXT,
             f"{soc_debut:.0f}% → {soc_fin:.0f}%") if delta_soc != 0 else _kpi("SOC", "—", "%"),
    ], style={
        'display': 'flex', 'flexWrap': 'wrap', 'gap': '1px',
        'padding': '8px', 'background': BG4,
        'borderBottom': f'1px solid {BORDER}',
    }))

    # Ligne 2 : distance et efficacité
    blocs.append(html.Div([
        _kpi("DISTANCE",     f"{dist_km:.2f}",     "km"),
        _kpi("AVG SPEED",    f"{v_moy:.1f}",        "km/h"),
        _kpi("TOP SPEED",    f"{v_max:.1f}",         "km/h"),
        _kpi("CONSUMPTION",  f"{consommation:.0f}",  "Wh/km",
             ROUGE if consommation > 120 else TEXT) if consommation > 0 else _kpi("CONSUMPTION", "—", "Wh/km"),
        _kpi("SESSION",      f"{duree_min:.1f}",     "min"),
    ], style={
        'display': 'flex', 'flexWrap': 'wrap', 'gap': '1px',
        'padding': '8px', 'background': BG4,
        'borderBottom': f'1px solid {BORDER}',
    }))

    # ── Graphes temporels ─────────────────────────────────────────────────
    blocs.append(_section("power & energy over time"))

    if len(t_ref) > 1:
        fig = make_subplots(
            rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.03,
            subplot_titles=[
                "<span style='font-family:Arial,sans-serif;font-size:10px;color:#555'>Power (kW)</span>",
                "<span style='font-family:Arial,sans-serif;font-size:10px;color:#555'>Energy consumed (Wh)</span>",
                "<span style='font-family:Arial,sans-serif;font-size:10px;color:#555'>Pack voltage (V)</span>",
            ]
        )

        # Puissance
        couleurs_p = np.where(s_p >= 0, ACCENT, VERT)
        fig.add_trace(go.Scatter(
            x=t_ref, y=np.where(s_p >= 0, s_p, 0),
            mode='lines', name='Power (draw)',
            line=dict(color=ACCENT, width=1.0),
            fill='tozeroy', fillcolor='rgba(91,155,213,0.08)',
            hovertemplate='<b>Power</b><br>t=%{x:.1f}s  %{y:.2f} kW<extra></extra>',
        ), row=1, col=1)
        if np.any(s_p < 0):
            fig.add_trace(go.Scatter(
                x=t_ref, y=np.where(s_p < 0, s_p, 0),
                mode='lines', name='Regen',
                line=dict(color=VERT, width=1.0),
                fill='tozeroy', fillcolor='rgba(74,138,74,0.12)',
                hovertemplate='<b>Regen</b><br>t=%{x:.1f}s  %{y:.2f} kW<extra></extra>',
            ), row=1, col=1)

        # Énergie cumulée
        fig.add_trace(go.Scatter(
            x=t_ref[1:], y=e_wh,
            mode='lines', name='Energy (Wh)',
            line=dict(color=ORANGE, width=1.2),
            hovertemplate='<b>Energy</b><br>t=%{x:.1f}s  %{y:.1f} Wh<extra></extra>',
        ), row=2, col=1)

        # Tension pack
        fig.add_trace(go.Scatter(
            x=t_v, y=s_v,
            mode='lines', name='Pack voltage',
            line=dict(color='#5b9bd5', width=1.0),
            hovertemplate='<b>Pack voltage</b><br>t=%{x:.1f}s  %{y:.2f} V<extra></extra>',
        ), row=3, col=1)

        # Axe Y commun
        for row, title, unit in [(1, '', 'kW'), (2, '', 'Wh'), (3, '', 'V')]:
            fig.update_yaxes(
                title_text=unit, title_standoff=3, row=row, col=1,
                gridcolor='#1e1e1e', color='#444',
                zeroline=True, zerolinecolor='#282828', zerolinewidth=1,
                tickfont=dict(family='Consolas, monospace', size=10, color='#555'),
                title_font=dict(family='Arial, sans-serif', size=10, color='#444'),
                fixedrange=True,
            )

        fig.update_layout(
            paper_bgcolor=BG, plot_bgcolor='#131313',
            font=dict(color=TEXT, family='Arial, sans-serif', size=10),
            margin=dict(l=56, r=12, t=14, b=28),
            hovermode='x unified',
            hoverlabel=dict(bgcolor='#1e1e1e', bordercolor='#333',
                            font=dict(family='Consolas, monospace', size=10, color='#aaa')),
            showlegend=False, height=480, dragmode='pan',
        )
        fig.update_xaxes(
            gridcolor='#1e1e1e', color='#444', zeroline=False,
            tickfont=dict(family='Consolas, monospace', size=10, color='#555'),
            showline=True, linecolor='#2a2a2a', linewidth=1, fixedrange=False,
        )
        fig.update_xaxes(title_text='t (s)', row=3, col=1,
                         title_font=dict(family='Arial, sans-serif', size=10, color='#444'),
                         title_standoff=3)
        for j in [1, 2]:
            fig.add_shape(type='line', xref='paper', yref='paper',
                          x0=0, x1=1, y0=1.0-j/3, y1=1.0-j/3,
                          line=dict(color='#252525', width=1))

        blocs.append(dcc.Graph(
            figure=fig,
            config={'displayModeBar': True, 'displaylogo': False,
                    'modeBarButtonsToRemove': ['select2d', 'lasso2d', 'toggleSpikelines',
                                               'drawopenpath', 'drawclosedpath',
                                               'drawcircle', 'drawrect', 'eraseshape'],
                    'scrollZoom': False},
            style={'height': '480px'}
        ))

    # ── SOC timeline ──────────────────────────────────────────────────────
    if t_soc is not None and len(t_soc) > 1:
        blocs.append(_section("state of charge"))
        fig_soc = go.Figure()
        couleur_soc = VERT if soc_fin > 50 else (ORANGE if soc_fin > 20 else ROUGE)
        fig_soc.add_trace(go.Scatter(
            x=t_soc, y=s_soc,
            mode='lines', name='SOC',
            line=dict(color=couleur_soc, width=1.5),
            fill='tozeroy', fillcolor=f'rgba(74,138,74,0.08)',
            hovertemplate='<b>SOC</b><br>t=%{x:.1f}s  %{y:.1f}%<extra></extra>',
        ))
        fig_soc.update_layout(
            paper_bgcolor=BG, plot_bgcolor='#131313',
            font=dict(color=TEXT, family='Arial, sans-serif', size=10),
            margin=dict(l=56, r=12, t=8, b=28),
            hovermode='x unified',
            hoverlabel=dict(bgcolor='#1e1e1e', bordercolor='#333',
                            font=dict(family='Consolas, monospace', size=10, color='#aaa')),
            showlegend=False, height=160, dragmode='pan',
            yaxis=dict(title_text='%', gridcolor='#1e1e1e', color='#444',
                       fixedrange=True, range=[0, 105],
                       tickfont=dict(family='Consolas, monospace', size=10, color='#555'),
                       title_font=dict(family='Arial, sans-serif', size=10, color='#444'),
                       title_standoff=3),
            xaxis=dict(gridcolor='#1e1e1e', color='#444', zeroline=False,
                       tickfont=dict(family='Consolas, monospace', size=10, color='#555'),
                       title_text='t (s)',
                       title_font=dict(family='Arial, sans-serif', size=10, color='#444'),
                       title_standoff=3,
                       showline=True, linecolor='#2a2a2a'),
        )
        blocs.append(dcc.Graph(figure=fig_soc,
                               config={'displayModeBar': False, 'staticPlot': False},
                               style={'height': '160px'}))

    # ── Histogramme puissance ─────────────────────────────────────────────
    if len(t_ref) > 1 and len(s_p) > 10:
        blocs.append(_section("power distribution"))
        fig_hist = go.Figure()
        fig_hist.add_trace(go.Histogram(
            x=s_p, nbinsx=40,
            marker_color=ACCENT, opacity=0.75,
            hovertemplate='%{x:.1f} kW — %{y} samples<extra></extra>',
        ))
        fig_hist.update_layout(
            paper_bgcolor=BG, plot_bgcolor='#131313',
            font=dict(color=TEXT, family='Arial, sans-serif', size=10),
            margin=dict(l=56, r=12, t=8, b=28),
            bargap=0.02, showlegend=False, height=160,
            xaxis=dict(title_text='Power (kW)', gridcolor='#1e1e1e', color='#444',
                       tickfont=dict(family='Consolas, monospace', size=10, color='#555'),
                       title_font=dict(family='Arial, sans-serif', size=10, color='#444'),
                       title_standoff=3, showline=True, linecolor='#2a2a2a'),
            yaxis=dict(title_text='samples', gridcolor='#1e1e1e', color='#444',
                       tickfont=dict(family='Consolas, monospace', size=10, color='#555'),
                       title_font=dict(family='Arial, sans-serif', size=10, color='#444'),
                       title_standoff=3),
        )
        blocs.append(dcc.Graph(figure=fig_hist,
                               config={'displayModeBar': False},
                               style={'height': '160px'}))

    return html.Div(blocs)
