from dash import html, dcc
from constants import *


# ─────────────────────────────────────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────────────────────────────────────

def msg(t):
    """Empty-state message centered in content area."""
    return html.Div([
        html.Div("⊘", style={
            'fontSize': '48px', 'color': DIM2, 'lineHeight': '1',
            'marginBottom': '12px',
        }),
        html.Div(t, style={
            'fontFamily': SANS, 'fontSize': '13px', 'color': DIM,
        }),
    ], style={
        'display': 'flex', 'flexDirection': 'column',
        'alignItems': 'center', 'justifyContent': 'center',
        'height': '60vh', 'gap': '0',
    })


# ─────────────────────────────────────────────────────────────────────────────
#  Topbar
# ─────────────────────────────────────────────────────────────────────────────

def _tab_btn(v, detache):
    return html.Button(
        [
            html.Span(v.get('icon', ''), style={
                'marginRight': '5px',
                'fontSize': '10px',
                'opacity': '0.7',
            }),
            v['label'],
        ],
        id={'type': 'btn-vue-det' if detache else 'btn-vue', 'index': v['value']},
        n_clicks=0,
        style={
            'fontFamily': SANS, 'fontSize': '11px', 'fontWeight': '500',
            'color': DIM,
            'background': 'none', 'border': 'none',
            'borderBottom': '2px solid transparent',
            'padding': '0 12px',
            'height': '36px',
            'cursor': 'pointer',
            'letterSpacing': '0.01em',
            'transition': 'color 0.15s',
            'display': 'flex', 'alignItems': 'center',
        }
    )


def topbar(detache=False):
    upload_id  = 'upload-mdf-det' if detache else 'upload-mdf'
    label_id   = 'label-session-det' if detache else 'label-session'
    vue_btn_id = 'btn-nouvelle-vue-det' if detache else 'btn-nouvelle-vue'

    tabs = [_tab_btn(v, detache) for v in VUES]

    # Logo / brand area
    logo = html.Div([
        html.Span("F", style={'color': ACCENT, 'fontWeight': '700'}),
        html.Span("ORM", style={'color': BRIGHT, 'fontWeight': '700'}),
        html.Span("UL", style={'color': ACCENT, 'fontWeight': '700'}),
        html.Span(" ANALYZER", style={
            'color': DIM, 'fontWeight': '400', 'fontSize': '9px',
            'letterSpacing': '0.2em', 'marginLeft': '4px',
        }),
    ], style={
        'fontFamily': SANS, 'fontSize': '13px',
        'letterSpacing': '0.05em',
        'padding': '0 16px',
        'borderRight': f'1px solid {BORDER}',
        'height': '36px', 'display': 'flex', 'alignItems': 'center',
        'flexShrink': '0', 'userSelect': 'none',
    })

    # Session label
    session_label = html.Div([
        html.Span("▶ ", style={'color': ACCENT, 'fontSize': '8px'}),
        html.Span(id=label_id, children='no file loaded', style={
            'fontFamily': MONO, 'fontSize': '10px', 'color': DIM,
        }),
    ], style={
        'padding': '0 14px',
        'borderRight': f'1px solid {BORDER}',
        'height': '36px', 'display': 'flex', 'alignItems': 'center',
        'maxWidth': '240px', 'overflow': 'hidden',
        'textOverflow': 'ellipsis', 'whiteSpace': 'nowrap',
        'flexShrink': '0',
    })

    # Tab strip
    tab_strip = html.Div(tabs, style={
        'display': 'flex', 'alignItems': 'stretch',
        'flex': '1', 'overflow': 'hidden',
    })

    # Right actions
    def _action(label, btn_id=None, upload_id_=None, download=False):
        style = {
            'fontFamily': SANS, 'fontSize': '11px', 'color': DIM,
            'cursor': 'pointer', 'padding': '0 12px',
            'height': '36px', 'display': 'flex', 'alignItems': 'center',
            'borderLeft': f'1px solid {BORDER}',
            'whiteSpace': 'nowrap',
            'transition': 'color 0.15s',
        }
        if upload_id_:
            return dcc.Upload(
                id=upload_id_,
                children=html.Span(label, style=style),
                accept='.mdf,.MDF,.mf4,.MF4',
            )
        return html.Span(label, id=btn_id, n_clicks=0, style=style)

    right = html.Div([
        _action("Open MDF", upload_id_=upload_id),
        _action("+ View", btn_id=vue_btn_id) if not detache else html.Span(),
        _action("↓ CSV", btn_id='btn-export-csv'),
        dcc.Download(id='download-csv'),
    ], style={'display': 'flex', 'alignItems': 'center', 'flexShrink': '0'})

    if detache:
        det_badge = html.Span("DETACHED", style={
            'fontFamily': MONO, 'fontSize': '9px', 'color': ACCENT,
            'background': f'{ACCENT}22',
            'border': f'1px solid {ACCENT}44',
            'borderRadius': '2px',
            'padding': '1px 6px',
            'marginLeft': '10px',
            'letterSpacing': '0.1em',
        })
    else:
        det_badge = html.Span()

    return html.Div([
        logo,
        det_badge,
        session_label,
        tab_strip,
        right,
    ], style={
        'background': BG5,
        'borderBottom': f'1px solid {BORDER}',
        'height': '36px',
        'display': 'flex',
        'alignItems': 'center',
        'flexShrink': '0',
        'userSelect': 'none',
    })


# ─────────────────────────────────────────────────────────────────────────────
#  Sidebar
# ─────────────────────────────────────────────────────────────────────────────

def sidebar(detache=False):
    suffix = '-det' if detache else ''

    search = dcc.Input(
        id=f'input-recherche{suffix}',
        placeholder='  Search channels...',
        style={
            'width': '100%',
            'background': BG3,
            'border': 'none',
            'borderBottom': f'1px solid {BORDER}',
            'color': TEXT,
            'fontFamily': SANS,
            'fontSize': '11px',
            'padding': '7px 10px',
            'outline': 'none',
            'boxSizing': 'border-box',
        }
    )

    toolbar = html.Div([
        html.Span("Deselect all",
                  id=f'btn-deselectionner{suffix}',
                  n_clicks=0,
                  style={
                      'fontFamily': SANS, 'fontSize': '10px', 'color': DIM,
                      'cursor': 'pointer', 'padding': '4px 10px',
                  }),
        # channel type filter
        dcc.Checklist(
            id=f'filtre-type{suffix}',
            options=[
                {'label': 'raw', 'value': 'raw'},
                {'label': 'math', 'value': 'math'},
            ],
            value=['raw', 'math'],
            inline=True,
            style={'display': 'flex', 'gap': '8px', 'padding': '4px 10px'},
            inputStyle={
                'accentColor': ACCENT,
                'marginRight': '3px',
            },
            labelStyle={
                'fontFamily': SANS, 'fontSize': '10px', 'color': DIM,
                'cursor': 'pointer',
            },
        ),
    ], style={
        'borderBottom': f'1px solid {BORDER}',
        'display': 'flex', 'alignItems': 'center',
        'justifyContent': 'space-between',
        'flexWrap': 'wrap',
    })

    channel_list = html.Div(
        id=f'liste-canaux{suffix}',
        style={'overflowY': 'auto', 'flex': '1'},
    )

    return html.Div([
        search,
        toolbar,
        channel_list,
    ], style={
        'width': '190px',
        'minWidth': '190px',
        'background': BG3,
        'borderRight': f'1px solid {BORDER}',
        'display': 'flex',
        'flexDirection': 'column',
        'height': f'calc(100vh - 36px - 20px)',
        'flexShrink': '0',
        'overflow': 'hidden',
    })


# ─────────────────────────────────────────────────────────────────────────────
#  Channel list items (called from callbacks)
# ─────────────────────────────────────────────────────────────────────────────

def _domaine_header(nom, couleur, count):
    """Domain group header with colored left bar."""
    return html.Div([
        html.Div(style={
            'width': '3px', 'height': '100%',
            'background': couleur,
            'position': 'absolute', 'left': '0', 'top': '0',
        }),
        html.Span(nom.upper(), style={
            'fontFamily': SANS, 'fontSize': '9px', 'fontWeight': '700',
            'color': couleur, 'letterSpacing': '0.12em',
            'marginLeft': '8px',
        }),
        html.Span(f' {count}', style={
            'fontFamily': MONO, 'fontSize': '9px', 'color': DIM,
            'marginLeft': '4px',
        }),
    ], style={
        'padding': '6px 8px 4px 6px',
        'position': 'relative',
        'marginTop': '6px',
        'borderTop': f'1px solid {BORDER}',
        'display': 'flex', 'alignItems': 'center',
    })


def _canal_item(canal, selectionne, couleur='#888'):
    return html.Div([
        html.Div(style={
            'width': '2px', 'height': '10px',
            'background': couleur if selectionne else DIM2,
            'borderRadius': '1px',
            'flexShrink': '0',
        }),
        html.Span(canal, style={
            'fontFamily': MONO, 'fontSize': '10px',
            'color': BRIGHT if selectionne else DIM,
            'overflow': 'hidden', 'textOverflow': 'ellipsis',
            'whiteSpace': 'nowrap', 'flex': '1',
        }),
    ], id={'type': 'canal-item', 'index': canal},
    n_clicks=0,
    style={
        'display': 'flex', 'alignItems': 'center', 'gap': '7px',
        'padding': '3px 8px 3px 10px',
        'cursor': 'pointer',
        'background': f'{couleur}18' if selectionne else 'transparent',
        'borderLeft': f'2px solid {couleur}' if selectionne else f'2px solid transparent',
    })


def construire_liste_canaux(canaux_filtres, canaux_sel, domaines_data):
    """Build the sidebar channel list with domain group headers."""
    if not canaux_filtres:
        return html.Div("No channels", style={
            'fontFamily': SANS, 'fontSize': '11px', 'color': DIM,
            'padding': '16px 10px', 'textAlign': 'center',
        })

    # Group by domain
    canal_domaine = {}
    for domaine, info in (domaines_data or {}).items():
        for c in info.get('canaux', []):
            canal_domaine[c] = domaine

    sel_set = set(canaux_sel or [])
    groups = {}
    ungrouped = []

    for c in canaux_filtres:
        dom = canal_domaine.get(c)
        if dom:
            groups.setdefault(dom, []).append(c)
        else:
            ungrouped.append(c)

    children = []

    for domaine, canaux in groups.items():
        couleur = COULEURS_DOMAINES.get(domaine, '#888')
        children.append(_domaine_header(domaine, couleur, len(canaux)))
        for c in canaux:
            children.append(_canal_item(c, c in sel_set, couleur))

    if ungrouped:
        children.append(html.Div([
            html.Span("OTHER", style={
                'fontFamily': SANS, 'fontSize': '9px', 'fontWeight': '700',
                'color': DIM, 'letterSpacing': '0.12em',
            }),
        ], style={
            'padding': '6px 8px 4px 10px',
            'marginTop': '6px',
            'borderTop': f'1px solid {BORDER}',
        }))
        for c in ungrouped:
            children.append(_canal_item(c, c in sel_set))

    return html.Div(children)


# ─────────────────────────────────────────────────────────────────────────────
#  Main layouts
# ─────────────────────────────────────────────────────────────────────────────

def _statusbar():
    return html.Div(id='statusbar-content', style={
        'background': BG5,
        'borderTop': f'1px solid {BORDER}',
        'height': '20px',
        'display': 'flex', 'alignItems': 'center',
        'padding': '0 12px', 'flexShrink': '0', 'gap': '20px',
    })


def _statusbar_det():
    return html.Div(id='statusbar-content-det', style={
        'background': BG5,
        'borderTop': f'1px solid {BORDER}',
        'height': '20px',
        'display': 'flex', 'alignItems': 'center',
        'padding': '0 12px', 'flexShrink': '0', 'gap': '20px',
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
        _statusbar(),
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
        _statusbar_det(),
    ], style={
        'background': BG, 'color': TEXT,
        'height': '100vh', 'overflow': 'hidden',
        'display': 'flex', 'flexDirection': 'column',
    })
