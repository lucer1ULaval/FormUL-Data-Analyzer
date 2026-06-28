from dash import html, dcc
from constants import *


def msg(t):
    return html.Div(t, style={
        'fontFamily': SANS, 'fontSize': '12px', 'color': DIM,
        'marginTop': '80px', 'textAlign': 'center',
    })


def _btn_vue(v, detache):
    return html.Button(
        v['label'],
        id={'type': 'btn-vue-det' if detache else 'btn-vue', 'index': v['value']},
        n_clicks=0,
        style={
            'fontFamily': SANS, 'fontSize': '11px', 'color': DIM,
            'background': 'none', 'border': 'none',
            'padding': '0 8px', 'height': '26px',
            'cursor': 'pointer',
        }
    )


def topbar(detache=False):
    sep = html.Span('|', style={'color': '#222', 'fontSize': '10px', 'padding': '0 1px'})
    onglets = []
    for i, v in enumerate(VUES):
        if i > 0:
            onglets.append(sep)
        onglets.append(_btn_vue(v, detache))

    upload_id  = 'upload-mdf-det' if detache else 'upload-mdf'
    label_id   = 'label-session-det' if detache else 'label-session'
    vue_btn_id = 'btn-nouvelle-vue-det' if detache else 'btn-nouvelle-vue'

    return html.Div([
        html.Span("FORMUL", style={
            'fontFamily': SANS, 'fontSize': '11px', 'fontWeight': '600',
            'color': '#888', 'letterSpacing': '0.15em',
            'padding': '0 12px', 'borderRight': f'1px solid {BORDER}',
            'height': '26px', 'display': 'flex', 'alignItems': 'center',
        }),
        html.Span(
            "detached",
            style={
                'fontFamily': SANS, 'fontSize': '10px', 'color': '#333',
                'padding': '0 8px', 'borderRight': f'1px solid {BORDER}',
                'height': '26px', 'display': 'flex', 'alignItems': 'center',
            }
        ) if detache else html.Span(),
        html.Span(id=label_id, children='no file', style={
            'fontFamily': SANS, 'fontSize': '11px', 'color': DIM,
            'padding': '0 12px', 'borderRight': f'1px solid {BORDER}',
            'height': '26px', 'display': 'flex', 'alignItems': 'center',
            'maxWidth': '260px', 'overflow': 'hidden', 'textOverflow': 'ellipsis',
            'whiteSpace': 'nowrap',
        }),
        html.Div(onglets, style={
            'display': 'flex', 'alignItems': 'center', 'padding': '0 4px',
        }),
        html.Div([
            dcc.Upload(id=upload_id,
                children=html.Span("Open MDF", style={
                    'fontFamily': SANS, 'fontSize': '11px', 'color': DIM,
                    'cursor': 'pointer', 'padding': '0 10px',
                    'height': '26px', 'display': 'flex', 'alignItems': 'center',
                    'borderLeft': f'1px solid {BORDER}',
                }),
                accept='.mdf,.MDF,.mf4,.MF4',
            ),
            html.Span("+ View", id=vue_btn_id, n_clicks=0, style={
                'fontFamily': SANS, 'fontSize': '11px', 'color': DIM,
                'cursor': 'pointer', 'padding': '0 10px',
                'height': '26px', 'display': 'flex', 'alignItems': 'center',
                'borderLeft': f'1px solid {BORDER}',
            }) if not detache else html.Span(),
            html.Span("↓ CSV", id='btn-export-csv', n_clicks=0, style={
                'fontFamily': SANS, 'fontSize': '11px', 'color': DIM,
                'cursor': 'pointer', 'padding': '0 10px',
                'height': '26px', 'display': 'flex', 'alignItems': 'center',
                'borderLeft': f'1px solid {BORDER}',
            }),
            dcc.Download(id='download-csv'),
        ], style={'marginLeft': 'auto', 'display': 'flex'}),
    ], style={
        'background': BG5, 'borderBottom': f'1px solid {BORDER}',
        'height': '26px', 'display': 'flex', 'alignItems': 'center',
        'flexShrink': '0',
    })


def sidebar(detache=False):
    suffix = '-det' if detache else ''
    return html.Div([
        dcc.Input(
            id=f'input-recherche{suffix}',
            placeholder='Filter channels...',
            style={
                'width': '100%', 'background': BG3,
                'border': 'none', 'borderBottom': f'1px solid {BORDER}',
                'color': TEXT, 'fontFamily': SANS, 'fontSize': '11px',
                'padding': '5px 8px', 'outline': 'none',
                'boxSizing': 'border-box',
            }
        ),
        html.Div("Deselect all", id=f'btn-deselectionner{suffix}', n_clicks=0, style={
            'fontFamily': SANS, 'fontSize': '10px', 'color': DIM,
            'padding': '3px 8px', 'cursor': 'pointer',
            'borderBottom': f'1px solid {BORDER}',
        }),
        html.Div(id=f'liste-canaux{suffix}',
                 style={'overflowY': 'auto', 'flex': '1'}),
    ], style={
        'width': '170px', 'minWidth': '170px', 'background': BG3,
        'borderRight': f'1px solid {BORDER}',
        'display': 'flex', 'flexDirection': 'column',
        'height': 'calc(100vh - 26px - 18px)',
        'flexShrink': '0', 'overflow': 'hidden',
    })


def layout_principal():
    return html.Div([
        topbar(detache=False),
        html.Div([
            sidebar(detache=False),
            html.Div(id='contenu-vue', style={
                'flex': '1', 'overflowY': 'auto',
                'background': BG, 'minWidth': '0',
            }),
        ], style={'display': 'flex', 'flex': '1', 'overflow': 'hidden'}),
        html.Div(id='statusbar-content', style={
            'background': BG5, 'borderTop': f'1px solid {BORDER}',
            'height': '18px', 'display': 'flex', 'alignItems': 'center',
            'padding': '0 8px', 'flexShrink': '0', 'gap': '16px',
        }),
    ], style={
        'background': BG, 'color': TEXT,
        'height': '100vh', 'overflow': 'hidden',
        'display': 'flex', 'flexDirection': 'column',
    })


def layout_vue_libre():
    return html.Div([
        topbar(detache=True),
        html.Div([
            sidebar(detache=True),
            html.Div(id='contenu-vue-det', style={
                'flex': '1', 'overflowY': 'auto',
                'background': BG, 'minWidth': '0',
            }),
        ], style={'display': 'flex', 'flex': '1', 'overflow': 'hidden'}),
        html.Div(id='statusbar-content-det', style={
            'background': BG5, 'borderTop': f'1px solid {BORDER}',
            'height': '18px', 'display': 'flex', 'alignItems': 'center',
            'padding': '0 8px', 'flexShrink': '0', 'gap': '16px',
        }),
    ], style={
        'background': BG, 'color': TEXT,
        'height': '100vh', 'overflow': 'hidden',
        'display': 'flex', 'flexDirection': 'column',
    })
