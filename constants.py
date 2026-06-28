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
JAUNE   = '#c8a020'

# Couleurs traces session principale
COULEURS = [
    '#5b9bd5',
    '#70ad47',
    '#ed7d31',
    '#ffc000',
    '#9b59b6',
    '#00b0d8',
    '#e06070',
]

# Couleurs traces session 2 (desaturées)
COULEURS_S2 = [
    '#2d6fa8',
    '#4a7a30',
    '#a85520',
    '#b08800',
    '#6a3a86',
    '#0080a8',
    '#a04050',
]

# Couleurs par domaine (sidebar groups)
COULEURS_DOMAINES = {
    'Batterie':  '#5b9bd5',
    'Moteurs':   '#70ad47',
    'Thermique': '#ed7d31',
    'Pedales':   '#ffc000',
    'Systeme':   '#9b59b6',
}

VUES = [
    {'label': 'channels',  'value': 'graphes'},
    {'label': 'summary',   'value': 'resume'},
    {'label': 'faults',    'value': 'erreurs'},
    {'label': 'analysis',  'value': 'math'},
    {'label': 'heatmap',   'value': 'heatmap'},
    {'label': 'energy',    'value': 'energie'},
    {'label': 'motors',    'value': 'motors'},
    {'label': 'compare',   'value': 'comparaison'},
]

MOTS_CLES_ERREUR    = ['ERROR', 'ERR', 'FAULT', 'FAIL', 'BSPD', 'ALARM', 'WARN']
CANAL_VITESSE       = 'Speed'
CANAL_VITESSE_ALT   = 'RCP_GPS_Speed'
SEUIL_VITESSE       = 3.0
SEUIL_COINCIDENCE   = 3
FENETRE_DECLENCHEUR = 5.0

RPM_TO_KMH   = 107.76
POLES_PAIRES = 10
