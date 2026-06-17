from dash import html
from constants import BG, BG3, BG4, BG5, BORDER, BORDER2, MONO, SANS, DIM, TEXT, ROUGE, ORANGE


def construire_erreurs(zones_faute, declencheurs, flags_erreur):
    from ui import msg
    if not zones_faute:
        return html.Div([
            html.Div("faults", style={
                'fontFamily': SANS, 'fontSize': '10px', 'color': DIM,
                'padding': '4px 8px', 'background': BG5,
                'borderBottom': f'1px solid {BORDER}',
            }),
            html.Div("No fault detected during driving.", style={
                'fontFamily': SANS, 'fontSize': '12px', 'color': '#3a6a3a',
                'padding': '16px', 'borderLeft': '2px solid #3a6a3a',
                'margin': '12px', 'background': '#111a11',
            }),
            _systemes_bloc(flags_erreur),
        ])

    systemes = {}
    for flag in flags_erreur:
        pfx = flag.split('_')[0] if '_' in flag else 'OTHER'
        systemes.setdefault(pfx, []).append(flag)

    blocs = [
        html.Div("faults", style={
            'fontFamily': SANS, 'fontSize': '10px', 'color': DIM,
            'padding': '4px 8px', 'background': BG5,
            'borderBottom': f'1px solid {BORDER}',
        }),
    ]

    for debut, fin in zones_faute:
        causes = declencheurs.get(debut, [])
        cp = causes[0] if causes else None
        if cp:
            _, flag, _, v_ap, desc = cp
            label_cause = desc if desc else f"{flag} = {v_ap}"
            sous_label = flag if desc else ''
        else:
            label_cause = 'Undetermined'
            sous_label = ''

        blocs.append(html.Div([

            # ── Header ──────────────────────────────────────────────────
            html.Div([
                html.Span("● FAULT", style={
                    'fontFamily': SANS, 'fontSize': '11px', 'fontWeight': '700',
                    'color': ROUGE, 'letterSpacing': '0.05em', 'marginRight': '20px',
                }),
                html.Span(f"t = {debut:.1f} s", style={
                    'fontFamily': MONO, 'fontSize': '12px', 'color': TEXT,
                    'marginRight': '8px',
                }),
                html.Span("→", style={
                    'fontFamily': SANS, 'fontSize': '11px', 'color': '#444',
                    'marginRight': '8px',
                }),
                html.Span(f"{fin:.1f} s", style={
                    'fontFamily': MONO, 'fontSize': '12px', 'color': TEXT,
                    'marginRight': '20px',
                }),
                html.Span(f"duration  {fin-debut:.1f} s", style={
                    'fontFamily': MONO, 'fontSize': '11px', 'color': '#555',
                }),
            ], style={
                'padding': '8px 12px', 'background': '#1a0808',
                'borderBottom': f'1px solid #3a1515',
                'display': 'flex', 'alignItems': 'center',
            }),

            # ── Cause principale ─────────────────────────────────────────
            html.Div([
                html.Div([
                    html.Div("PROBABLE CAUSE", style={
                        'fontFamily': SANS, 'fontSize': '9px', 'color': '#444',
                        'letterSpacing': '0.12em', 'marginBottom': '6px',
                    }),
                    html.Div(label_cause, style={
                        'fontFamily': SANS, 'fontSize': '14px', 'color': ORANGE,
                        'fontWeight': '500',
                    }),
                    html.Div(sous_label, style={
                        'fontFamily': MONO, 'fontSize': '10px', 'color': '#555',
                        'marginTop': '3px',
                    }) if sous_label else html.Div(),
                ], style={
                    'padding': '10px 12px', 'flex': '1',
                    'borderLeft': f'3px solid {ORANGE}',
                }),

                # Stats rapides
                html.Div([
                    html.Div([
                        html.Div("flags", style={'fontFamily': SANS, 'fontSize': '9px', 'color': '#333'}),
                        html.Div(str(len(causes)), style={
                            'fontFamily': MONO, 'fontSize': '20px', 'color': ROUGE,
                        }),
                    ], style={'textAlign': 'center', 'padding': '0 16px'}),
                    html.Div([
                        html.Div("systems", style={'fontFamily': SANS, 'fontSize': '9px', 'color': '#333'}),
                        html.Div(str(len(set(f for _, f, *_ in causes))), style={
                            'fontFamily': MONO, 'fontSize': '20px', 'color': TEXT,
                        }),
                    ], style={'textAlign': 'center', 'padding': '0 16px',
                               'borderLeft': f'1px solid {BORDER}'}),
                ], style={
                    'display': 'flex', 'alignItems': 'center',
                    'borderLeft': f'1px solid {BORDER}', 'padding': '8px 0',
                }),
            ], style={
                'display': 'flex', 'alignItems': 'stretch',
                'background': '#151010',
                'borderBottom': f'1px solid #2a1515',
            }),

            # ── Séquence ─────────────────────────────────────────────────
            html.Div([
                html.Div("TRIGGER SEQUENCE", style={
                    'fontFamily': SANS, 'fontSize': '9px', 'color': '#333',
                    'letterSpacing': '0.12em', 'marginBottom': '6px',
                }),
                *[html.Div([
                    html.Span(f"{dt:+.2f} s", style={
                        'fontFamily': MONO, 'fontSize': '11px', 'color': '#555',
                        'minWidth': '60px', 'display': 'inline-block',
                    }),
                    html.Span("  "),
                    html.Span(flag, style={
                        'fontFamily': MONO, 'fontSize': '11px', 'color': '#777',
                        'marginRight': '12px',
                    }),
                    html.Span(f"= {v_ap}", style={
                        'fontFamily': MONO, 'fontSize': '11px', 'color': ROUGE,
                        'marginRight': '10px',
                    }),
                    html.Span(desc if desc else '', style={
                        'fontFamily': SANS, 'fontSize': '11px', 'color': ORANGE,
                    }),
                ], style={
                    'padding': '4px 0',
                    'borderBottom': f'1px solid {BORDER2}',
                })
                for dt, flag, v_av, v_ap, desc in causes],
            ], style={'padding': '10px 12px', 'background': BG3}),

        ], style={
            'border': f'1px solid #2a1515',
            'borderLeft': f'3px solid {ROUGE}',
            'marginBottom': '8px',
            'overflow': 'hidden',
        }))

    blocs.append(_systemes_bloc(flags_erreur))
    return html.Div(blocs, style={'padding': '8px', 'maxWidth': '900px'})


def _systemes_bloc(flags_erreur):
    systemes = {}
    for flag in flags_erreur:
        pfx = flag.split('_')[0] if '_' in flag else 'OTHER'
        systemes.setdefault(pfx, []).append(flag)

    return html.Div([
        html.Div("MONITORED SYSTEMS", style={
            'fontFamily': SANS, 'fontSize': '9px', 'color': '#333',
            'letterSpacing': '0.12em', 'marginBottom': '8px',
        }),
        html.Div([
            html.Div([
                html.Div(sys, style={
                    'fontFamily': MONO, 'fontSize': '10px', 'color': DIM,
                }),
                html.Div(str(len(f)), style={
                    'fontFamily': MONO, 'fontSize': '14px', 'color': TEXT,
                }),
                html.Div("flags", style={
                    'fontFamily': SANS, 'fontSize': '9px', 'color': '#333',
                }),
            ], style={
                'background': BG3, 'border': f'1px solid {BORDER}',
                'padding': '8px 12px', 'textAlign': 'center',
                'minWidth': '70px',
            })
            for sys, f in sorted(systemes.items())
        ], style={'display': 'flex', 'gap': '1px', 'flexWrap': 'wrap'}),
    ], style={
        'padding': '10px 12px', 'background': BG5,
        'borderTop': f'1px solid {BORDER}', 'marginTop': '4px',
    })