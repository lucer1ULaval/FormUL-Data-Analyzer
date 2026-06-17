import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import html, dcc
from constants import BG, BG3, BG4, BG5, BORDER, BORDER2, TEXT, MONO, SANS, DIM, COULEURS, ROUGE, ORANGE


def _timeline_erreurs(zones_faute, declencheurs, t_max):
    if not zones_faute:
        return None
    fig = go.Figure()
    fig.add_shape(type='rect', xref='x', yref='paper',
                  x0=0, x1=t_max, y0=0, y1=1,
                  fillcolor='#111', line_width=0, layer='below')
    for debut, fin in zones_faute:
        fig.add_shape(type='rect', xref='x', yref='paper',
                      x0=debut, x1=fin, y0=0, y1=1,
                      fillcolor='rgba(160,40,40,0.5)',
                      line=dict(color='rgba(160,40,40,0.8)', width=1),
                      layer='below')
        causes = declencheurs.get(debut, []) if declencheurs else []
        if causes:
            _, flag, _, v_ap, desc = causes[0]
            label = desc if desc else f"{flag}={v_ap}"
            fig.add_annotation(
                x=debut, y=0.5, xref='x', yref='paper',
                text=f"  {label}", showarrow=False,
                font=dict(family=SANS, size=9, color=ORANGE),
                xanchor='left',
            )
    fig.update_layout(
        paper_bgcolor=BG5, plot_bgcolor=BG5,
        margin=dict(l=56, r=12, t=4, b=4), height=28,
        xaxis=dict(range=[0, t_max], showgrid=False,
                   showticklabels=False, zeroline=False, color='#444'),
        yaxis=dict(showgrid=False, showticklabels=False,
                   zeroline=False, fixedrange=True),
        showlegend=False,
    )
    return dcc.Graph(figure=fig,
                     config={'displayModeBar': False, 'staticPlot': True},
                     style={'height': '28px', 'marginBottom': '1px'})


def construire_math_view(resultats, zones_faute=None, declencheurs=None, t_max=313):
    from ui import msg
    blocs = []

    # ── Fault timeline ───────────────────────────────────────────────────────
    blocs.append(html.Div("fault timeline", style={
        'fontFamily': SANS, 'fontSize': '10px', 'color': DIM,
        'padding': '4px 8px', 'background': BG5,
        'borderBottom': f'1px solid {BORDER}',
    }))
    if zones_faute:
        tl = _timeline_erreurs(zones_faute, declencheurs or {}, t_max)
        if tl: blocs.append(tl)
        for debut, fin in zones_faute:
            causes = declencheurs.get(debut, []) if declencheurs else []
            cause_txt = ''
            if causes:
                _, flag, _, v_ap, desc = causes[0]
                cause_txt = f"  —  {desc if desc else flag+' = '+str(v_ap)}"
            blocs.append(html.Div([
                html.Span(f"t = {debut:.1f} → {fin:.1f} s  (Δ {fin-debut:.1f} s)",
                          style={'fontFamily': MONO, 'fontSize': '10px', 'color': TEXT}),
                html.Span(cause_txt,
                          style={'fontFamily': SANS, 'fontSize': '10px', 'color': ORANGE}),
            ], style={
                'padding': '3px 8px', 'borderBottom': f'1px solid {BORDER2}',
                'borderLeft': f'2px solid {ROUGE}', 'background': BG3,
            }))
    else:
        blocs.append(html.Div("no fault detected during driving", style={
            'fontFamily': SANS, 'fontSize': '10px', 'color': DIM,
            'padding': '5px 8px', 'borderBottom': f'1px solid {BORDER}',
        }))

    # ── Computed channels ────────────────────────────────────────────────────
    blocs.append(html.Div("computed channels", style={
        'fontFamily': SANS, 'fontSize': '10px', 'color': DIM,
        'padding': '4px 8px', 'background': BG5,
        'borderBottom': f'1px solid {BORDER}', 'marginTop': '1px',
    }))

    if not resultats:
        blocs.append(html.Div("no math channel computable — check available channels", style={
            'fontFamily': SANS, 'fontSize': '10px', 'color': DIM, 'padding': '5px 8px',
        }))
        return html.Div(blocs)

    n = len(resultats)
    fig = make_subplots(
        rows=n, cols=1, shared_xaxes=True, vertical_spacing=0.006,
        subplot_titles=[
            f"<span style='font-family:Arial,sans-serif;font-size:10px;color:#555'>"
            f"{r['label']}  ({r['unite']})</span>"
            for r in resultats
        ]
    )
    for i, r in enumerate(resultats):
        couleur = COULEURS[i % len(COULEURS)]
        t, s = r['t'], r['s']
        s_plot = np.where(np.isfinite(s), s, None)
        if zones_faute:
            hauteur = 1.0 / n
            y0 = 1.0 - (i + 1) * hauteur
            y1 = 1.0 - i * hauteur
            for debut, fin in zones_faute:
                fig.add_shape(type='rect', xref='x', yref='paper',
                              x0=debut, x1=fin, y0=y0, y1=y1,
                              fillcolor='rgba(160,40,40,0.12)',
                              line=dict(color='rgba(160,40,40,0.3)', width=0.5),
                              layer='below')
        fig.add_trace(
            go.Scatter(x=t, y=s_plot, mode='lines', name=r['label'],
                       line=dict(color=couleur, width=1.0), connectgaps=False,
                       hovertemplate=(
                           f'<span style="font-family:Consolas">'
                           f'<b>{r["label"]}</b><br>t = %{{x:.3f}} s<br>'
                           f'%{{y:.4g}} {r["unite"]}</span><extra></extra>'
                       )),
            row=i+1, col=1
        )
        fig.update_yaxes(
            title_text=r['unite'], title_standoff=3, row=i+1, col=1,
            gridcolor='#1e1e1e', color='#444',
            zeroline=True, zerolinecolor='#282828', zerolinewidth=1,
            tickfont=dict(family='Consolas, monospace', size=10, color='#555'),
            title_font=dict(family='Arial, sans-serif', size=10, color='#444'),
            fixedrange=True,   # Y fixé — molette zoome X seulement
        )

    h = max(200, 160 * n)
    fig.update_layout(
        paper_bgcolor=BG, plot_bgcolor='#131313',
        font=dict(color=TEXT, family='Arial, sans-serif', size=10),
        margin=dict(l=56, r=12, t=14, b=28),
        hovermode='x unified',
        hoverlabel=dict(bgcolor='#1e1e1e', bordercolor='#333',
                        font=dict(family='Consolas, monospace', size=10, color='#aaa')),
        showlegend=False, height=h, dragmode='pan',
    )
    fig.update_xaxes(
        gridcolor='#1e1e1e', color='#444', zeroline=False,
        tickfont=dict(family='Consolas, monospace', size=10, color='#555'),
        showline=True, linecolor='#2a2a2a', linewidth=1, fixedrange=False,
    )
    fig.update_xaxes(title_text='t (s)', row=n, col=1,
                     title_font=dict(family='Arial, sans-serif', size=10, color='#444'),
                     title_standoff=3)
    for j in range(1, n):
        fig.add_shape(type='line', xref='paper', yref='paper',
                      x0=0, x1=1, y0=1.0-j/n, y1=1.0-j/n,
                      line=dict(color='#252525', width=1))

    lignes_f = [html.Div([
        html.Span(r['label'], style={
            'fontFamily': SANS, 'fontSize': '11px', 'color': '#555',
            'width': '180px', 'minWidth': '180px', 'display': 'inline-block'
        }),
        html.Span(r['desc'], style={'fontFamily': MONO, 'fontSize': '10px', 'color': '#333'}),
    ], style={'padding': '3px 8px', 'borderBottom': f'1px solid {BORDER2}'})
    for r in resultats]

    blocs += [
        dcc.Graph(id='graphe-math', figure=fig,
                  config={
                      'displayModeBar': True,
                      'modeBarButtonsToRemove': ['select2d', 'lasso2d', 'toggleSpikelines',
                                                 'drawopenpath', 'drawclosedpath', 'drawcircle',
                                                 'drawrect', 'eraseshape'],
                      'displaylogo': False,
                      'scrollZoom': False,   # molette = scroll page
                  },
                  style={'height': f'{h}px'}),
        html.Div([
            html.Div("formulas", style={
                'fontFamily': SANS, 'fontSize': '10px', 'color': DIM,
                'padding': '4px 8px', 'background': BG5,
                'borderBottom': f'1px solid {BORDER}'
            }),
            *lignes_f
        ], style={'background': BG3, 'border': f'1px solid {BORDER}', 'marginTop': '1px'}),
    ]
    return html.Div(blocs)