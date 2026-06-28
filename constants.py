MONO  = "'Consolas', 'Courier New', monospace"
SANS  = "'Segoe UI', 'Arial', sans-serif"

# ── Backgrounds ──────────────────────────────────────────────────────────────
BG    = '#0d0d0d'
BG2   = '#111111'
BG3   = '#161616'
BG4   = '#1c1c1c'
BG5   = '#0a0a0a'

# ── Borders ───────────────────────────────────────────────────────────────────
BORDER  = '#222222'
BORDER2 = '#2a2a2a'

# ── Text ──────────────────────────────────────────────────────────────────────
TEXT    = '#d0d0d0'
DIM     = '#5a5a5a'
DIM2    = '#333333'
BRIGHT  = '#efefef'

# ── Accent / semantic ─────────────────────────────────────────────────────────
ACCENT  = '#E31837'   # FormUL red (Université Laval)
ACCENT2 = '#ff4455'   # lighter hover
ROUGE   = '#c03030'
ORANGE  = '#c07828'
VERT    = '#4a9a4a'
JAUNE   = '#c8a820'
BLEU    = '#4488cc'

# ── Couleurs traces session 1 ─────────────────────────────────────────────────
COULEURS = [
    '#4f8fd4',
    '#65b03f',
    '#e07020',
    '#f0b800',
    '#9050c0',
    '#00a8c8',
    '#d05060',
]

# ── Couleurs traces session 2 (désaturées) ────────────────────────────────────
COULEURS_S2 = [
    '#2a5e9a',
    '#3d7025',
    '#9a4c10',
    '#a07800',
    '#5a2880',
    '#006888',
    '#803040',
]

# ── Couleurs par domaine ──────────────────────────────────────────────────────
COULEURS_DOMAINES = {
    'Batterie':  '#4f8fd4',
    'Moteurs':   '#65b03f',
    'Thermique': '#e07020',
    'Pedales':   '#f0b800',
    'Systeme':   '#9050c0',
}

# ── Vues disponibles ──────────────────────────────────────────────────────────
VUES = [
    {'label': 'Channels',  'value': 'graphes',      'icon': '▤'},
    {'label': 'Summary',   'value': 'resume',        'icon': '≡'},
    {'label': 'Faults',    'value': 'erreurs',       'icon': '⚡'},
    {'label': 'Analysis',  'value': 'math',          'icon': '∫'},
    {'label': 'Heatmap',   'value': 'heatmap',       'icon': '▦'},
    {'label': 'Energy',    'value': 'energie',       'icon': '⚡'},
    {'label': 'Motors',    'value': 'motors',        'icon': '◎'},
    {'label': 'Compare',   'value': 'comparaison',   'icon': '⇄'},
]

# ── Détection de fautes ───────────────────────────────────────────────────────
MOTS_CLES_ERREUR    = ['ERROR', 'ERR', 'FAULT', 'FAIL', 'BSPD', 'ALARM', 'WARN']
CANAL_VITESSE       = 'Speed'
CANAL_VITESSE_ALT   = 'RCP_GPS_Speed'
SEUIL_VITESSE       = 3.0
SEUIL_COINCIDENCE   = 3
FENETRE_DECLENCHEUR = 5.0

# ── Conversion ────────────────────────────────────────────────────────────────
RPM_TO_KMH   = 107.76
POLES_PAIRES = 10
