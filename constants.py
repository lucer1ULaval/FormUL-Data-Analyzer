MONO  = "'Consolas', 'Courier New', monospace"
SANS  = "'Segoe UI', 'Arial', sans-serif"

BG    = '#141414'
BG2   = '#111111'
BG3   = '#1a1a1a'
BG4   = '#202020'
BG5   = '#0f0f0f'

BORDER  = '#2a2a2a'
BORDER2 = '#222222'

TEXT    = '#c8c8c8'
DIM     = '#666666'
DIM2    = '#3a3a3a'
BRIGHT  = '#e8e8e8'

ACCENT  = '#5a9fd4'
ROUGE   = '#c04040'
ORANGE  = '#b07828'
VERT    = '#4a8a4a'

COULEURS = [
    '#5b9bd5',
    '#70ad47',
    '#ed7d31',
    '#ffc000',
    '#9b59b6',
    '#00b0d8',
    '#e06070',
]

# Couleurs session 2 pour comparaison (versions desaturées/tiretées)
COULEURS_S2 = [
    '#2d6fa8',
    '#4a7a30',
    '#a85520',
    '#b08800',
    '#6a3a86',
    '#0080a8',
    '#a04050',
]

VUES = [
    {'label': 'channels',   'value': 'graphes',     'icon': 'ti-chart-line'},
    {'label': 'summary',    'value': 'resume',      'icon': 'ti-layout-grid'},
    {'label': 'faults',     'value': 'erreurs',     'icon': 'ti-alert-triangle'},
    {'label': 'analysis',   'value': 'math',        'icon': 'ti-math-function'},
    {'label': 'heatmap',    'value': 'heatmap',     'icon': 'ti-battery'},
    {'label': 'compare',    'value': 'comparaison', 'icon': 'ti-arrows-diff'},
]

MOTS_CLES_ERREUR    = ['ERROR', 'ERR', 'FAULT', 'FAIL', 'BSPD', 'ALARM', 'WARN']
CANAL_VITESSE       = 'Speed'
CANAL_VITESSE_ALT   = 'RCP_GPS_Speed'
SEUIL_VITESSE       = 3.0
SEUIL_COINCIDENCE   = 3
FENETRE_DECLENCHEUR = 5.0

RPM_TO_KMH   = 107.76
POLES_PAIRES = 10