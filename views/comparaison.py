import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import html, dcc
from constants import (BG, BG3, BG4, BG5, BORDER, BORDER2, TEXT, MONO, SANS, DIM,
                       COULEURS, COULEURS_S2)


def _nom_court(filename, max_len=25):
    n = (filename or '').replace('.mdf', '').replace('.MDF', '').replace('.mf4', '').replace('.MF4', '')
    return n[-max_len:] if len(n) > max_len else n


def construire_comparaison_upload():
    return html.Div([
        html.Div("compare sessions", style={
            'fontFamily': SANS, 'fontSize': '10px', 'color': DIM,
            'padding': '4px 8px', 'background': BG5,
            'borderBottom': f'1px solid {BORDER}',
        }),
        html.Div([
            html.Div("Session 1  (current)", style={
                'fontFamily': SANS, 'fontSize': '10px', 'color': DIM, 'marginBottom': '4px'
            }),
            html.Div(id='label-s1-display', style={
                'fontFamily': MONO, 'fontSize': '11px', 'color': TEXT,
                'padding': '6px 8px', 'background': BG3, 'border': f'1px solid {BORDER}',
                'marginBottom': '12px',
            }),
            html.Div("Session 2", style={
                'fontFamily': SANS, 'fontSize': '10px', 'color': DIM, 'marginBottom': '4px'
            }),
            dcc.Upload(
                id='upload-mdf-s2',
                children=html.Div([
                    html.Span("Drop MDF file here  or  ", style={
                        'fontFamily': SANS, 'fontSize': '11px', 'color': DIM
                    }),
                    html.Span("browse", style={
                        'fontFamily': SANS, 'fontSize': '11px', 'color': '#5b9bd5',
                        'cursor': 'pointer', 'textDecoration': 'underline',
                    }),
                ]),
                style={
                    'border': f'1px dashed {BORDER}', 'padding': '14px',
                    'textAlign': 'center', 'background': BG3, 'cursor': 'pointer',
                },
                accept='.mdf,.MDF,.mf4,.MF4',
            ),
            html.Div(id='label-s2', children='', style={
                'fontFamily': MONO, 'fontSize': '11px', 'color': TEXT, 'marginTop': '6px'
            }),
            html.Div([
                html.Div([
                    html.Div(style={'width': '20px', 'height': '2px',
                                    'background': COULEURS[0], 'marginRight': '6px',
                                    'flexShrink': '0'}),
                    html.Span("Session 1 — solid", style={
                        'fontFamily': SANS, 'fontSize': '10px', 'color': DIM
                    }),
                ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '3px'}),
                html.Div([
                    html.Div(style={'width': '20px', 'height': '2px',
                                    'borderTop': f'2px dashed {COULEURS_S2[0]}',
                                    'marginRight': '6px', 'flexShrink': '0'}),
                    html.Span("Session 2 — dashed", style={
                        'fontFamily': SANS, 'fontSize': '10px', 'color': DIM
                    }),
                ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '3px'}),
                html.Div([
                    html.Div(style={'width': '20px', 'height': '2px',
                                    'borderTop': '2px dotted #888',
                                    'marginRight': '6px', 'flexShrink': '0'}),
                    html.Span("Δ (S1 − S2) — dotted", style={
                        'fontFamily': SANS, 'fontSize': '10px', 'color': DIM
                    }),
                ], style={'display': 'flex', 'alignItems': 'center'}),
            ], style={
                'marginTop': '10px', 'padding': '8px',
                'background': BG3, 'border': f'1px solid {BORDER}',
            }),
        ], style={'padding': '10px', 'maxWidth': '480px'}),
        html.Div(id='contenu-comparaison'),
    ])


def construire_overlay(mdf1, mdf2, canaux_sel, label1='Session 1', label2='Session 2'):
    from ui import msg
    from utils.mdf_loader import signal_vers_dataframe

    if not canaux_sel:
        return msg("Select channels in the sidebar")

    nom1 = _nom_court(label1)
    nom2 = _nom_court(label2)

    n = len(canaux_sel)
    # 3 subplots par canal: S1, S2, Δ — mais on les intègre dans un seul subplot par canal
    fig = make_subplots(
        rows=n, cols=1, shared_xaxes=True, vertical_spacing=0.006,
        subplot_titles=[
            f"<span style='font-family:Arial,sans-serif;font-size:10px;color:#555'>{c}</span>"
            for c in canaux_sel
        ]
    )

    def t0(mdf, canal):
        try: return float(mdf.get(canal).timestamps[0])
        except: return 0.0

    stats_rows = []

    for i, canal in enumerate(canaux_sel):
        c1 = COULEURS[i % len(COULEURS)]
        c2 = COULEURS_S2[i % len(COULEURS_S2)]

        df1, unit = signal_vers_dataframe(mdf1, canal)
        df2, unit2 = signal_vers_dataframe(mdf2, canal)

        t1_arr = t2_arr = s1_arr = s2_arr = None

        if df1 is not None:
            off1 = t0(mdf1, canal)
            t1_arr = df1['timestamp'].values - off1
            s1_arr = df1[canal].values.astype(float)
            fig.add_trace(go.Scatter(
                x=t1_arr, y=s1_arr, mode='lines',
                name=nom1, legendgroup='s1', showlegend=(i == 0),
                line=dict(color=c1, width=1.0),
                hovertemplate=f'<b>{nom1}</b><br>{canal}<br>t=%{{x:.3f}}s  %{{y:.4g}} {unit}<extra></extra>',
            ), row=i+1, col=1)

        if df2 is not None:
            off2 = t0(mdf2, canal)
            t2_arr = df2['timestamp'].values - off2
            s2_arr = df2[canal].values.astype(float)
            fig.add_trace(go.Scatter(
                x=t2_arr, y=s2_arr, mode='lines',
                name=nom2, legendgroup='s2', showlegend=(i == 0),
                line=dict(color=c2, width=1.0, dash='dash'),
                hovertemplate=f'<b>{nom2}</b><br>{canal}<br>t=%{{x:.3f}}s  %{{y:.4g}} {unit2}<extra></extra>',
            ), row=i+1, col=1)

        # Delta trace (S1 - S2)
        if t1_arr is not None and t2_arr is not None and s1_arr is not None and s2_arr is not None:
            t_ref = t1_arr
            t_min = min(t1_arr[0], t2_arr[0])
            t_max = max(t1_arr[-1], t2_arr[-1])
            s2_i = np.interp(t_ref, t2_arr, s2_arr,
                             left=np.nan, right=np.nan)
            delta = s1_arr - s2_i
            fig.add_trace(go.Scatter(
                x=t_ref, y=delta, mode='lines',
                name='Δ (S1−S2)', legendgroup='delta', showlegend=(i == 0),
                line=dict(color='#888888', width=0.8, dash='dot'),
                hovertemplate=f'<b>Δ</b><br>{canal}<br>t=%{{x:.3f}}s  %{{y:.4g}}<extra></extra>',
            ), row=i+1, col=1)

            # Stats comparatives
            d_avg = float(np.nanmean(delta))
            d_rms = float(np.sqrt(np.nanmean(delta ** 2)))
            stats_rows.append((canal, unit, d_avg, d_rms))

        fig.update_yaxes(
            title_text=unit or '', title_standoff=3, row=i+1, col=1,
            gridcolor='#1e1e1e', color='#444',
            zeroline=True, zerolinecolor='#282828', zerolinewidth=1,
            tickfont=dict(family='Consolas, monospace', size=10, color='#555'),
            title_font=dict(family='Arial, sans-serif', size=10, color='#444'),
            fixedrange=False,
        )

    h = max(200, 160 * n)
    fig.update_layout(
        paper_bgcolor=BG, plot_bgcolor='#131313',
        font=dict(color=TEXT, family='Arial, sans-serif', size=10),
        margin=dict(l=56, r=12, t=40, b=28),
        hovermode='x unified',
        hoverlabel=dict(bgcolor='#1e1e1e', bordercolor='#333',
                        font=dict(family='Consolas, monospace', size=10, color='#aaa')),
        showlegend=True,
        legend=dict(
            bgcolor='rgba(15,15,15,0.9)', bordercolor=BORDER, borderwidth=1,
            font=dict(family=SANS, size=10, color=DIM),
            orientation='h', x=0, y=1.02, xanchor='left', yanchor='bottom',
        ),
        height=h, dragmode='pan',
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

    graphe = dcc.Graph(
        id='graphe-comparaison', figure=fig,
        config={
            'displayModeBar': True,
            'modeBarButtonsToRemove': ['select2d', 'lasso2d', 'toggleSpikelines',
                                       'drawopenpath', 'drawclosedpath', 'drawcircle',
                                       'drawrect', 'eraseshape'],
            'displaylogo': False, 'scrollZoom': True,
            'toImageButtonOptions': {
                'format': 'png', 'filename': 'formul_compare',
                'height': h, 'width': 1400, 'scale': 2,
            },
        },
        style={'height': f'{h}px'}
    )

    # Tableau delta stats
    if stats_rows:
        delta_hdr = html.Div([
            html.Div("delta statistics  (S1 − S2)", style={
                'fontFamily': SANS, 'fontSize': '10px', 'color': DIM,
                'padding': '4px 8px', 'background': BG5,
                'borderBottom': f'1px solid {BORDER}',
            }),
            html.Div([
                html.Div("Channel", style={'fontFamily': SANS, 'fontSize': '10px', 'color': '#3a3a3a', 'flex': '2', 'paddingLeft': '8px'}),
                html.Div("Mean Δ", style={'fontFamily': SANS, 'fontSize': '10px', 'color': '#3a3a3a', 'flex': '1', 'textAlign': 'right'}),
                html.Div("RMS Δ", style={'fontFamily': SANS, 'fontSize': '10px', 'color': '#3a3a3a', 'flex': '1', 'textAlign': 'right', 'paddingRight': '8px'}),
            ], style={'display': 'flex', 'padding': '3px 0', 'background': BG4, 'borderBottom': f'1px solid {BORDER}'}),
            *[html.Div([
                html.Div(c, style={'fontFamily': SANS, 'fontSize': '11px', 'color': TEXT, 'flex': '2', 'paddingLeft': '8px', 'overflow': 'hidden', 'textOverflow': 'ellipsis'}),
                html.Div(f"{d_avg:+.4g} {u}", style={'fontFamily': MONO, 'fontSize': '11px', 'color': '#5b9bd5', 'flex': '1', 'textAlign': 'right'}),
                html.Div(f"{d_rms:.4g} {u}", style={'fontFamily': MONO, 'fontSize': '11px', 'color': '#888', 'flex': '1', 'textAlign': 'right', 'paddingRight': '8px'}),
            ], style={'display': 'flex', 'padding': '4px 0', 'borderBottom': f'1px solid {BORDER2}',
                       'background': BG3 if k % 2 == 0 else '#1d1d1d'})
             for k, (c, u, d_avg, d_rms) in enumerate(stats_rows)],
        ])
        return html.Div([graphe, delta_hdr])

    return graphe
