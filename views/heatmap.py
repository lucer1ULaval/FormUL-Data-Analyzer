import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import html, dcc
from constants import BG, BG3, BG4, BG5, BORDER, BORDER2, MONO, SANS, DIM, TEXT, ROUGE, ORANGE


def fmt(val):
    if val == 0: return '0'
    a = abs(val)
    if a >= 100: return f"{val:.1f}"
    elif a >= 1: return f"{val:.3f}"
    else:        return f"{val:.4f}"


def _couleur_cellule(v, vmin, vmax, vmoy):
    ecart = v - vmoy
    plage = vmax - vmin if vmax != vmin else 0.001
    if abs(ecart) > plage * 0.3:    return ROUGE
    elif abs(ecart) > plage * 0.15: return ORANGE
    else:                            return '#4a7a4a'


def _section_titre(texte):
    return html.Div(texte, style={
        'fontFamily': SANS, 'fontSize': '10px', 'color': DIM,
        'padding': '4px 8px', 'background': BG5,
        'borderBottom': f'1px solid {BORDER}',
    })


def construire_heatmap(mdf, canaux_disponibles):
    from ui import msg
    blocs = []

    # ── Canaux cellules ───────────────────────────────────────────────────
    canaux_cv = sorted([c for c in canaux_disponibles if c.startswith('BMS_CV')])

    modules = {}
    for c in canaux_cv:
        parts = c.split('_')
        mod = parts[1] if len(parts) >= 2 else 'CV?'
        modules.setdefault(mod, []).append(c)

    # ── Snapshot ──────────────────────────────────────────────────────────
    blocs.append(_section_titre("cell voltages — snapshot (session avg)"))

    if modules:
        toutes_vals = {}
        for c in canaux_cv:
            try:
                sig = mdf.get(c)
                toutes_vals[c] = float(np.mean(sig.samples.astype(float)))
            except Exception:
                continue

        if toutes_vals:
            vmin_g = min(toutes_vals.values())
            vmax_g = max(toutes_vals.values())
            vmoy_g = float(np.mean(list(toutes_vals.values())))
            plage_g = vmax_g - vmin_g
            alerte = plage_g > 0.05

            blocs.append(html.Div([
                html.Span(f"avg  {vmoy_g:.3f} V", style={
                    'fontFamily': MONO, 'fontSize': '11px', 'color': TEXT, 'marginRight': '20px'
                }),
                html.Span(f"min  {vmin_g:.3f} V", style={
                    'fontFamily': MONO, 'fontSize': '11px', 'color': '#4a7a4a', 'marginRight': '20px'
                }),
                html.Span(f"max  {vmax_g:.3f} V", style={
                    'fontFamily': MONO, 'fontSize': '11px', 'color': '#7a4a4a', 'marginRight': '20px'
                }),
                html.Span(f"Δ  {plage_g:.3f} V", style={
                    'fontFamily': MONO, 'fontSize': '11px',
                    'color': ROUGE if alerte else DIM
                }),
            ], style={
                'padding': '5px 8px', 'background': BG4,
                'borderBottom': f'1px solid {BORDER}',
                'display': 'flex', 'flexWrap': 'wrap',
            }))

            for mod, cellules in sorted(modules.items()):
                mod_vals = {c: toutes_vals[c] for c in cellules if c in toutes_vals}
                if not mod_vals: continue
                vmoy_mod = float(np.mean(list(mod_vals.values())))

                blocs.append(html.Div(mod, style={
                    'fontFamily': SANS, 'fontSize': '9px', 'color': '#333',
                    'padding': '2px 8px', 'background': BG4,
                    'borderBottom': f'1px solid {BORDER2}',
                }))
                cartes = []
                for c in sorted(cellules):
                    if c not in mod_vals: continue
                    v = mod_vals[c]
                    pct = (v - vmin_g) / plage_g * 100 if plage_g > 0.001 else 50
                    couleur = _couleur_cellule(v, vmin_g, vmax_g, vmoy_mod)
                    nom = c.replace(f'BMS_{mod}_', '')
                    cartes.append(html.Div([
                        html.Div(nom, style={
                            'fontFamily': SANS, 'fontSize': '8px', 'color': '#444',
                            'marginBottom': '2px',
                        }),
                        html.Div(fmt(v), style={
                            'fontFamily': MONO, 'fontSize': '11px', 'color': couleur,
                        }),
                        html.Div(style={
                            'width': f'{pct:.0f}%', 'height': '2px',
                            'background': couleur, 'marginTop': '3px',
                        }),
                    ], style={
                        'background': BG3, 'border': f'1px solid {BORDER2}',
                        'padding': '4px 6px', 'minWidth': '60px', 'flex': '1',
                    }))
                blocs.append(html.Div(cartes, style={
                    'display': 'flex', 'flexWrap': 'wrap', 'gap': '1px',
                    'padding': '1px', 'background': BORDER,
                    'borderBottom': f'1px solid {BORDER}',
                }))
    else:
        blocs.append(html.Div("No cell voltage channels found (BMS_CV*)", style={
            'fontFamily': SANS, 'fontSize': '10px', 'color': DIM, 'padding': '5px 8px'
        }))

    # ── Graphe temporel ───────────────────────────────────────────────────
    blocs.append(_section_titre("cell voltages — over time"))

    if modules:
        n_mod = len(modules)
        CELL_COLORS = [
            '#5b9bd5', '#70ad47', '#ed7d31', '#ffc000', '#9b59b6',
            '#00b0d8', '#e06070', '#4ecdc4', '#a8e6cf', '#ff8b94',
            '#45b7d1', '#96ceb4', '#88d8b0',
        ]

        fig = make_subplots(
            rows=n_mod, cols=1, shared_xaxes=True, vertical_spacing=0.04,
            subplot_titles=[
                f"<span style='font-family:Arial,sans-serif;font-size:10px;color:#555'>{mod}</span>"
                for mod in sorted(modules.keys())
            ]
        )

        for row, mod in enumerate(sorted(modules.keys()), 1):
            cellules = sorted(modules[mod])
            all_t, all_s = [], []

            for j, c in enumerate(cellules):
                try:
                    sig = mdf.get(c)
                    t = sig.timestamps.astype(float)
                    s = sig.samples.astype(float)
                    couleur = CELL_COLORS[j % len(CELL_COLORS)]
                    nom = c.replace(f'BMS_{mod}_', '')
                    fig.add_trace(go.Scatter(
                        x=t, y=s,
                        mode='lines', name=nom,
                        legendgroup=mod,
                        showlegend=(row == 1),
                        line=dict(color=couleur, width=0.8),
                        hovertemplate=(
                            f'<b>{c}</b><br>t=%{{x:.1f}}s<br>%{{y:.4f}} V<extra></extra>'
                        )
                    ), row=row, col=1)
                    all_t.append(t)
                    all_s.append(s)
                except Exception:
                    continue

            if all_t and all_s:
                t_ref = all_t[0]
                try:
                    mat = np.array([np.interp(t_ref, t, s) for t, s in zip(all_t, all_s)])
                    avg = mat.mean(axis=0)
                    fig.add_trace(go.Scatter(
                        x=t_ref, y=avg,
                        mode='lines', name=f'{mod} avg',
                        legendgroup=f'{mod}_avg',
                        showlegend=False,
                        line=dict(color='#ffffff', width=1.2, dash='dot'),
                        opacity=0.3,
                        hovertemplate=f'<b>{mod} avg</b><br>t=%{{x:.1f}}s<br>%{{y:.4f}} V<extra></extra>'
                    ), row=row, col=1)
                except Exception:
                    pass

            fig.update_yaxes(
                title_text='V', title_standoff=3, row=row, col=1,
                gridcolor='#1e1e1e', color='#444',
                tickfont=dict(family='Consolas, monospace', size=9, color='#555'),
                title_font=dict(family='Arial, sans-serif', size=9, color='#444'),
                fixedrange=True,
            )

        h = max(300, 160 * n_mod)
        fig.update_layout(
            paper_bgcolor=BG, plot_bgcolor='#131313',
            font=dict(color=TEXT, family='Arial, sans-serif', size=10),
            margin=dict(l=50, r=12, t=14, b=28),
            hovermode='x unified',
            hoverlabel=dict(bgcolor='#1e1e1e', bordercolor='#333',
                            font=dict(family='Consolas, monospace', size=9, color='#aaa')),
            showlegend=False, height=h, dragmode='pan',
        )
        fig.update_xaxes(
            gridcolor='#1e1e1e', color='#444', zeroline=False,
            tickfont=dict(family='Consolas, monospace', size=9, color='#555'),
            showline=True, linecolor='#2a2a2a', linewidth=1,
            fixedrange=False,   # X zoomable — Y fixe
        )
        fig.update_xaxes(
            title_text='t (s)', row=n_mod, col=1,
            title_font=dict(family='Arial, sans-serif', size=10, color='#444'),
            title_standoff=3
        )
        for j in range(1, n_mod):
            fig.add_shape(type='line', xref='paper', yref='paper',
                          x0=0, x1=1, y0=1.0-j/n_mod, y1=1.0-j/n_mod,
                          line=dict(color='#252525', width=1))

        blocs.append(dcc.Graph(
            id='graphe-heatmap-temps',
            figure=fig,
            config={
                'displayModeBar': True,
                'modeBarButtonsToRemove': [
                    'select2d', 'lasso2d', 'toggleSpikelines',
                    'drawopenpath', 'drawclosedpath', 'drawcircle',
                    'drawrect', 'eraseshape',
                ],
                'displaylogo': False,
                'scrollZoom': False,
            },
            style={'height': f'{h}px'}
        ))
    else:
        blocs.append(html.Div("No cell voltage channels found", style={
            'fontFamily': SANS, 'fontSize': '10px', 'color': DIM, 'padding': '5px 8px'
        }))

    # ── Températures onduleurs ────────────────────────────────────────────
    blocs.append(_section_titre("inverter temperatures"))

    inv_data = {}
    for inv in ['DI1', 'DI2', 'DI3', 'DI4']:
        inv_data[inv] = {}
        for type_temp, label in [('Controller_Temperature', 'CTL'), ('Motor_Temperature', 'MOT')]:
            c = f"{inv}_{type_temp}"
            if c in canaux_disponibles:
                try:
                    sig = mdf.get(c)
                    inv_data[inv][label] = float(np.mean(sig.samples.astype(float)))
                except Exception:
                    pass

    toutes_temps = [v for inv in inv_data.values() for v in inv.values()]
    if toutes_temps:
        tmin_v, tmax_v = min(toutes_temps), max(toutes_temps)
        rangee = []
        for inv, temps in sorted(inv_data.items()):
            if not temps: continue
            cellules_inv = []
            for label, v in sorted(temps.items()):
                pct = (v - tmin_v) / (tmax_v - tmin_v) if tmax_v != tmin_v else 0.5
                r = int(50 + pct * 150)
                g = int(130 - pct * 90)
                b = int(80 - pct * 60)
                couleur = f'rgb({r},{g},{b})'
                cellules_inv.append(html.Div([
                    html.Div(label, style={
                        'fontFamily': SANS, 'fontSize': '9px', 'color': DIM,
                        'marginBottom': '3px'
                    }),
                    html.Div(f"{v:.1f} °C", style={
                        'fontFamily': MONO, 'fontSize': '13px', 'color': couleur,
                    }),
                ], style={
                    'background': BG3, 'border': f'1px solid {BORDER}',
                    'padding': '8px 10px', 'flex': '1', 'textAlign': 'center',
                }))
            rangee.append(html.Div([
                html.Div(inv, style={
                    'fontFamily': SANS, 'fontSize': '9px', 'color': '#333',
                    'padding': '2px 0', 'textAlign': 'center',
                }),
                html.Div(cellules_inv, style={'display': 'flex', 'gap': '1px'}),
            ], style={'flex': '1'}))
        blocs.append(html.Div(rangee, style={
            'display': 'flex', 'gap': '1px', 'padding': '8px'
        }))
    else:
        blocs.append(html.Div("No inverter temperature channels found", style={
            'fontFamily': SANS, 'fontSize': '10px', 'color': DIM, 'padding': '5px 8px'
        }))

    return html.Div(blocs)