import numpy as np
from dash import html
from constants import BG, BG3, BG4, BG5, BORDER, BORDER2, MONO, SANS, DIM, TEXT, ROUGE


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
                'min': float(s.min()), 'max': float(s.max()),
                'mean': float(s.mean()), 'unit': sig.unit or ''
            }
        except Exception:
            continue
    return stats


def construire_resume(stats, label):
    from ui import msg
    if not stats:
        return msg("No key channels found for this file")

    # En-tête
    header = html.Div([
        html.Span(label, style={
            'fontFamily': SANS, 'fontSize': '11px', 'color': DIM,
        }),
    ], style={
        'padding': '4px 10px', 'background': BG5,
        'borderBottom': f'1px solid {BORDER}',
    })

    # En-tête colonnes
    col_hdr = html.Div([
        html.Div("Channel", style={
            'fontFamily': SANS, 'fontSize': '10px', 'color': '#3a3a3a',
            'flex': '2', 'paddingLeft': '8px',
        }),
        html.Div("Avg", style={
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
            'width': '80px', 'paddingRight': '8px',
        }),
    ], style={
        'display': 'flex', 'alignItems': 'center',
        'padding': '3px 0', 'background': BG4,
        'borderBottom': f'1px solid {BORDER}',
    })

    lignes = []
    for i, (canal, v) in enumerate(stats.items()):
        bg = BG3 if i % 2 == 0 else '#1d1d1d'
        vmin, vmax, vmoy = v['min'], v['max'], v['mean']
        plage_val = vmax - vmin
        pct = (vmoy - vmin) / plage_val * 100 if plage_val > 0 else 50

        # Couleur de la valeur moyenne selon position dans la plage
        if pct > 85:   c_val = '#c06060'
        elif pct < 15: c_val = '#6090c0'
        else:           c_val = TEXT

        # Barre miniature inline
        barre = html.Div([
            html.Div(style={
                'width': f'{pct:.0f}%', 'height': '100%',
                'background': '#3a6a3a' if pct < 70 else ('#8a6030' if pct < 85 else '#8a3a3a'),
            })
        ], style={
            'width': '70px', 'height': '6px', 'background': '#1a1a1a',
            'display': 'inline-block', 'verticalAlign': 'middle',
        })

        lignes.append(html.Div([
            html.Div(canal, title=canal, style={
                'fontFamily': SANS, 'fontSize': '11px', 'color': TEXT,
                'flex': '2', 'paddingLeft': '8px',
                'overflow': 'hidden', 'textOverflow': 'ellipsis', 'whiteSpace': 'nowrap',
            }),
            html.Div(fmt(vmoy), style={
                'fontFamily': MONO, 'fontSize': '12px', 'color': c_val,
                'flex': '1', 'textAlign': 'right', 'fontWeight': '500',
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
                'width': '80px', 'display': 'flex', 'alignItems': 'center',
                'paddingRight': '8px',
            }),
        ], style={
            'display': 'flex', 'alignItems': 'center',
            'padding': '5px 0', 'background': bg,
            'borderBottom': f'1px solid {BORDER2}',
        }))

    return html.Div([header, col_hdr, *lignes])