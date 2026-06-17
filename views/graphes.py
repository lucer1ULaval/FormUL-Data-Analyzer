import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import dcc
from constants import BG, TEXT, SANS, COULEURS
from utils.mdf_loader import signal_vers_dataframe


def _zones(fig, zones_faute, declencheurs, i, y0, y1, t_min, t_max):
    for debut, fin in zones_faute:
        fig.add_shape(
            type='rect', xref='x', yref='paper',
            x0=debut, x1=fin, y0=y0, y1=y1,
            fillcolor='rgba(160,40,40,0.15)',
            line=dict(color='rgba(160,40,40,0.35)', width=0.5),
            layer='below'
        )
        fig.add_shape(
            type='line', xref='x', yref='paper',
            x0=debut, x1=debut, y0=y0, y1=y1,
            line=dict(color='rgba(176,120,40,0.7)', width=1, dash='dot'),
            layer='above'
        )
        if i == 0:
            causes = declencheurs.get(debut, [])
            if causes:
                _, flag, _, v_ap, desc = causes[0]
                label = f"{flag} = {v_ap}" + (f"  ({desc})" if desc else "")
                duree = t_max - t_min if t_max > t_min else 1
                vers_gauche = (debut - t_min) / duree > 0.5
                offset = duree * 0.002
                fig.add_annotation(
                    x=debut - offset if vers_gauche else debut + offset,
                    y=y1, xref='x', yref='paper',
                    text=label, showarrow=False,
                    font=dict(family=SANS, size=10, color='#a07830'),
                    bgcolor='rgba(20,20,20,0.92)',
                    bordercolor='rgba(176,120,40,0.35)', borderwidth=1,
                    xanchor='right' if vers_gauche else 'left',
                    align='right' if vers_gauche else 'left',
                )


def construire_graphes(mdf, canaux_sel, zones_faute, declencheurs):
    n = len(canaux_sel)
    t_min, t_max = 0, 0
    for canal in canaux_sel:
        try:
            sig = mdf.get(canal)
            t_min = float(sig.timestamps[0])
            t_max = float(sig.timestamps[-1])
            break
        except Exception:
            continue

    fig = make_subplots(
        rows=n, cols=1, shared_xaxes=True, vertical_spacing=0.006,
        subplot_titles=[
            f"<span style='font-family:Arial,sans-serif;font-size:10px;color:#555'>{c}</span>"
            for c in canaux_sel
        ]
    )

    for i, canal in enumerate(canaux_sel):
        df, unit = signal_vers_dataframe(mdf, canal)
        if df is None:
            continue
        couleur = COULEURS[i % len(COULEURS)]
        hauteur = 1.0 / n
        y0 = 1.0 - (i + 1) * hauteur
        y1 = 1.0 - i * hauteur

        _zones(fig, zones_faute, declencheurs, i, y0, y1, t_min, t_max)

        fig.add_trace(
            go.Scatter(
                x=df['timestamp'].values,
                y=df[canal].values.astype(float),
                mode='lines', name=canal,
                line=dict(color=couleur, width=1.0),
                hovertemplate=(
                    f'<span style="font-family:Consolas">'
                    f'<b>{canal}</b><br>t = %{{x:.3f}} s<br>'
                    f'%{{y:.4g}} {unit}</span><extra></extra>'
                )
            ),
            row=i+1, col=1
        )
        fig.update_yaxes(
            title_text=unit or '', title_standoff=3,
            row=i+1, col=1,
            gridcolor='#1e1e1e', gridwidth=1, color='#444',
            zeroline=True, zerolinecolor='#282828', zerolinewidth=1,
            tickfont=dict(family='Consolas, monospace', size=10, color='#555'),
            title_font=dict(family='Arial, sans-serif', size=10, color='#444'),
            fixedrange=True,
        )

    h = max(200, 160 * n)
    fig.update_layout(
        paper_bgcolor=BG, plot_bgcolor='#131313',
        font=dict(color=TEXT, family='Arial, sans-serif', size=10),
        margin=dict(l=56, r=12, t=14, b=28),
        hovermode='x unified',
        hoverlabel=dict(bgcolor='#1e1e1e', bordercolor='#333',
                        font=dict(family='Consolas, monospace', size=10, color='#aaa')),
        showlegend=False, height=h,
        dragmode='pan',
    )
    fig.update_xaxes(
        gridcolor='#1e1e1e', gridwidth=1, color='#444', zeroline=False,
        tickfont=dict(family='Consolas, monospace', size=10, color='#555'),
        showline=True, linecolor='#2a2a2a', linewidth=1,
        fixedrange=False,
    )
    fig.update_xaxes(title_text='t (s)', row=n, col=1,
                     title_font=dict(family='Arial, sans-serif', size=10, color='#444'),
                     title_standoff=3)
    for j in range(1, n):
        fig.add_shape(type='line', xref='paper', yref='paper',
                      x0=0, x1=1, y0=1.0-j/n, y1=1.0-j/n,
                      line=dict(color='#252525', width=1))

    return dcc.Graph(
        id='graphe-principal', figure=fig,
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
    )