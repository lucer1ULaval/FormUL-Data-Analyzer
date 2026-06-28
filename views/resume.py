import numpy as np
from dash import html
from constants import BG, BG3, BG4, BG5, BORDER, BORDER2, MONO, SANS, DIM, TEXT, ROUGE, ORANGE


def fmt(val):
    if val == 0: return '0'
    a = abs(val)
    if a >= 10000: return f"{val:,.0f}"
    elif a >= 100: return f"{val:.1f}"
    elif a >= 1:   return f"{val:.2f}"
    elif a >= 0.01: return f"{val:.4f}"
    else:           return f"{val:.6f}"


def calculer_stats(mdf, canaux_cles, plage=None):
    stats = {}
    for canal in canaux_cles:
        try:
            sig = mdf.get(canal)
            ts, s = sig.timestamps, sig.samples.astype(float)
            if plage:
                mask = (ts >= plage['debut']) & (ts <= plage['fin'])
                s = s[mask]
            if len(s) == 0: continue
            stats[canal] = {
                'min':  float(s.min()),
                'max':  float(s.max()),
                'mean': float(s.mean()),
                'std':  float(s.std()),
                'unit': sig.unit or '',
            }
        except Exception:
            continue
    return stats


def _verifier_seuil(canal, stats, seuils):
    """Retourne (couleur_alerte, texte_alerte) si une limite est dépassée."""
    s = seuils.get(canal, {})
    if not s:
        return None, ''
    v = stats['mean']
    vmax = stats['max']
    vmin = stats['min']
    alertes = []
    if 'max' in s and vmax > s['max']:
        alertes.append(f"MAX {s['max']} exceeded ({fmt(vmax)})")
    if 'min' in s and vmin < s['min']:
        alertes.append(f"MIN {s['min']} not met ({fmt(vmin)})")
    if alertes:
        return ROUGE, ' | '.join(alertes)
    return None, ''


def construire_resume(stats, label, seuils=None):
    from ui import msg
    if not stats:
        return msg("No key channels found for this file")

    seuils = seuils or {}

    # Compter les alertes
    nb_alertes = sum(
        1 for c, v in stats.items()
        if _verifier_seuil(c, v, seuils)[0] is not None
    )

    # En-tête
    alerte_hdr = []
    if nb_alertes > 0:
        alerte_hdr.append(html.Span(
            f"  ⚠ {nb_alertes} threshold{'s' if nb_alertes > 1 else ''} exceeded",
            style={'fontFamily': SANS, 'fontSize': '10px', 'color': ROUGE,
                   'marginLeft': '12px'}
        ))

    header = html.Div([
        html.Span(label, style={'fontFamily': SANS, 'fontSize': '11px', 'color': DIM}),
        *alerte_hdr,
    ], style={
        'padding': '4px 10px', 'background': BG5,
        'borderBottom': f'1px solid {BORDER}',
        'display': 'flex', 'alignItems': 'center',
    })

    col_hdr = html.Div([
        html.Div("Channel", style={
            'fontFamily': SANS, 'fontSize': '10px', 'color': '#3a3a3a',
            'flex': '2', 'paddingLeft': '8px',
        }),
        html.Div("Avg", style={
            'fontFamily': SANS, 'fontSize': '10px', 'color': '#3a3a3a',
            'flex': '1', 'textAlign': 'right',
        }),
        html.Div("Std", style={
            'fontFamily': SANS, 'fontSize': '10px', 'color': '#3a3a3a',
            'flex': '1', 'textAlign': 'right',
        }),
        html.Div("Min", style={
            'fontFamily': SANS, 'fontSize': '10px', 'color': '#3a3a3a',
            'flex': '1', 'textAlign': 'right',
        }),
        html.Div("Max", style={
            'fontFamily': SANS, 'fontSize': '10px', 'color': '#3a3a3a',
            'flex': '1', 'textAlign': 'right',
        }),
        html.Div("Unit", style={
            'fontFamily': SANS, 'fontSize': '10px', 'color': '#3a3a3a',
            'width': '40px', 'textAlign': 'right', 'paddingRight': '8px',
        }),
        html.Div("Range", style={
            'fontFamily': SANS, 'fontSize': '10px', 'color': '#3a3a3a',
            'width': '90px', 'paddingRight': '8px',
        }),
    ], style={
        'display': 'flex', 'alignItems': 'center',
        'padding': '3px 0', 'background': BG4,
        'borderBottom': f'1px solid {BORDER}',
    })

    lignes = []
    for i, (canal, v) in enumerate(stats.items()):
        bg_base = BG3 if i % 2 == 0 else '#1d1d1d'
        vmin, vmax, vmoy, vstd = v['min'], v['max'], v['mean'], v.get('std', 0)
        plage_val = vmax - vmin
        pct = (vmoy - vmin) / plage_val * 100 if plage_val > 0 else 50

        # Vérifier les seuils
        couleur_alerte, texte_alerte = _verifier_seuil(canal, v, seuils)
        bg = '#1a0a0a' if couleur_alerte else bg_base

        # Couleur valeur moyenne selon position
        if couleur_alerte:
            c_val = ROUGE
        elif pct > 85:
            c_val = '#c06060'
        elif pct < 15:
            c_val = '#6090c0'
        else:
            c_val = TEXT

        barre = html.Div([
            html.Div(style={
                'width': f'{pct:.0f}%', 'height': '100%',
                'background': '#8a3a3a' if couleur_alerte else
                              ('#8a6030' if pct >= 85 else '#3a6a3a'),
            })
        ], style={
            'width': '78px', 'height': '6px', 'background': '#1a1a1a',
            'display': 'inline-block', 'verticalAlign': 'middle',
        })

        alerte_badge = []
        if couleur_alerte:
            alerte_badge.append(html.Span("⚠", title=texte_alerte, style={
                'color': ROUGE, 'fontSize': '10px', 'marginLeft': '4px',
                'cursor': 'help',
            }))

        lignes.append(html.Div([
            html.Div([
                html.Span(canal, title=texte_alerte or canal, style={
                    'fontFamily': SANS, 'fontSize': '11px', 'color': TEXT,
                    'overflow': 'hidden', 'textOverflow': 'ellipsis', 'whiteSpace': 'nowrap',
                }),
                *alerte_badge,
            ], style={
                'flex': '2', 'paddingLeft': '8px', 'display': 'flex',
                'alignItems': 'center', 'overflow': 'hidden',
            }),
            html.Div(fmt(vmoy), style={
                'fontFamily': MONO, 'fontSize': '12px', 'color': c_val,
                'flex': '1', 'textAlign': 'right', 'fontWeight': '500',
            }),
            html.Div(fmt(vstd), style={
                'fontFamily': MONO, 'fontSize': '10px', 'color': '#3a4a5a',
                'flex': '1', 'textAlign': 'right',
            }),
            html.Div(fmt(vmin), style={
                'fontFamily': MONO, 'fontSize': '11px', 'color': '#4a7a4a',
                'flex': '1', 'textAlign': 'right',
            }),
            html.Div(fmt(vmax), style={
                'fontFamily': MONO, 'fontSize': '11px', 'color': '#7a4a4a',
                'flex': '1', 'textAlign': 'right',
            }),
            html.Div(v['unit'] or '—', style={
                'fontFamily': SANS, 'fontSize': '10px', 'color': '#444',
                'width': '40px', 'textAlign': 'right', 'paddingRight': '8px',
            }),
            html.Div(barre, style={
                'width': '90px', 'display': 'flex', 'alignItems': 'center',
                'paddingRight': '8px',
            }),
        ], style={
            'display': 'flex', 'alignItems': 'center',
            'padding': '5px 0', 'background': bg,
            'borderBottom': f'1px solid {BORDER2}',
            'borderLeft': f'2px solid {ROUGE}' if couleur_alerte else '2px solid transparent',
        }))

    return html.Div([header, col_hdr, *lignes])
