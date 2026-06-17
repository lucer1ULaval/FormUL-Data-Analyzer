import numpy as np
from constants import RPM_TO_KMH

# Définition des math channels
# Chaque entrée : (nom, unité, description, fonction(canaux_dict) -> np.array, canaux_requis)

MATH_CHANNELS = [
    {
        'nom':         'MATH_Puissance_kW',
        'label':       'Puissance totale',
        'unite':       'kW',
        'desc':        'BMS_TotVolt × BMS_AvgCur / 1000',
        'requis':      ['BMS_TotVolt', 'BMS_AvgCur'],
        'requis_alt':  [['BMS_totalVoltage', 'BMS_avgCurrent']],
    },
    {
        'nom':         'MATH_Speed_FL',
        'label':       'Vitesse roue FL',
        'unite':       'km/h',
        'desc':        'DI_Inv1_speed_rpm / 107.76  (ou DI1_RPM)',
        'requis':      ['DI_Inv1_speed_rpm'],
        'requis_alt':  [['DI1_RPM']],
    },
    {
        'nom':         'MATH_Speed_FR',
        'label':       'Vitesse roue FR',
        'unite':       'km/h',
        'desc':        'DI_Inv2_speed_rpm / 107.76',
        'requis':      ['DI_Inv2_speed_rpm'],
        'requis_alt':  [['DI2_RPM']],
    },
    {
        'nom':         'MATH_Speed_RL',
        'label':       'Vitesse roue RL',
        'unite':       'km/h',
        'desc':        'DI_Inv3_speed_rpm / 107.76',
        'requis':      ['DI_Inv3_speed_rpm'],
        'requis_alt':  [['DI3_RPM']],
    },
    {
        'nom':         'MATH_Speed_RR',
        'label':       'Vitesse roue RR',
        'unite':       'km/h',
        'desc':        'DI_Inv4_speed_rpm / 107.76',
        'requis':      ['DI_Inv4_speed_rpm'],
        'requis_alt':  [['DI4_RPM']],
    },
    {
        'nom':         'MATH_Deseq_AV_AR',
        'label':       'Déséquilibre AV/AR',
        'unite':       'rpm',
        'desc':        '(Inv1+Inv2)/2 − (Inv3+Inv4)/2  →  positif = AV tourne plus vite',
        'requis':      ['DI_Inv1_speed_rpm', 'DI_Inv2_speed_rpm',
                        'DI_Inv3_speed_rpm', 'DI_Inv4_speed_rpm'],
        'requis_alt':  [['DI1_RPM', 'DI2_RPM', 'DI3_RPM', 'DI4_RPM']],
    },
    {
        'nom':         'MATH_Deseq_G_D',
        'label':       'Déséquilibre G/D',
        'unite':       'rpm',
        'desc':        '(Inv1+Inv3)/2 − (Inv2+Inv4)/2  →  positif = gauche tourne plus vite',
        'requis':      ['DI_Inv1_speed_rpm', 'DI_Inv3_speed_rpm',
                        'DI_Inv2_speed_rpm', 'DI_Inv4_speed_rpm'],
        'requis_alt':  [['DI1_RPM', 'DI3_RPM', 'DI2_RPM', 'DI4_RPM']],
    },
    {
        'nom':         'MATH_Glissement_FL',
        'label':       'Glissement FL',
        'unite':       '%',
        'desc':        '(vitesse_FL − vitesse_ref) / vitesse_ref × 100',
        'requis':      ['DI_Inv1_speed_rpm', 'Speed'],
        'requis_alt':  [['DI1_RPM', 'Speed'], ['DI_Inv1_speed_rpm', 'RCP_GPS_Speed']],
    },
    {
        'nom':         'MATH_Glissement_FR',
        'label':       'Glissement FR',
        'unite':       '%',
        'desc':        '(vitesse_FR − vitesse_ref) / vitesse_ref × 100',
        'requis':      ['DI_Inv2_speed_rpm', 'Speed'],
        'requis_alt':  [['DI2_RPM', 'Speed'], ['DI_Inv2_speed_rpm', 'RCP_GPS_Speed']],
    },
    {
        'nom':         'MATH_Roulis_Susp',
        'label':       'Roulis suspension',
        'unite':       'mm',
        'desc':        '(Pot_FL + Pot_RL)/2 − (Pot_FR + Pot_RR)/2',
        'requis':      ['Pot_FL', 'Pot_FR', 'Pot_RL', 'Pot_RR'],
        'requis_alt':  [],
    },
    {
        'nom':         'MATH_Tangage_Susp',
        'label':       'Tangage suspension',
        'unite':       'mm',
        'desc':        '(Pot_FL + Pot_FR)/2 − (Pot_RL + Pot_RR)/2',
        'requis':      ['Pot_FL', 'Pot_FR', 'Pot_RL', 'Pot_RR'],
        'requis_alt':  [],
    },
]


def _get_signal(mdf, canaux_disponibles, noms):
    """Essaie chaque nom dans la liste, retourne (timestamps, samples) du premier trouvé."""
    for nom in noms:
        if nom in canaux_disponibles:
            try:
                sig = mdf.get(nom)
                return sig.timestamps, sig.samples.astype(float)
            except Exception:
                continue
    return None, None


def _resample(t_ref, t_src, s_src):
    """Interpole s_src sur t_ref."""
    return np.interp(t_ref, t_src, s_src)


def calculer_math_channel(mdf, canaux_disponibles, mc):
    """
    Calcule un math channel. Retourne (t, s, canal_utilise) ou (None, None, None).
    Essaie d'abord `requis`, puis les alternatives dans `requis_alt`.
    """
    nom = mc['nom']

    def _essayer(liste_canaux):
        sigs = {}
        t_ref = None
        for c in liste_canaux:
            t, s = _get_signal(mdf, canaux_disponibles, [c])
            if t is None:
                return None, None
            if t_ref is None:
                t_ref = t
            sigs[c] = _resample(t_ref, t, s)
        return t_ref, sigs

    # Construire toutes les combinaisons à essayer
    combinaisons = [mc['requis']] + mc.get('requis_alt', [])

    for combo in combinaisons:
        t_ref, sigs = _essayer(combo)
        if t_ref is None:
            continue

        try:
            # --- Puissance ---
            if nom == 'MATH_Puissance_kW':
                volt = sigs[combo[0]]
                cur  = sigs[combo[1]]
                s = np.abs(volt * cur) / 1000.0
                return t_ref, s, combo

            # --- Vitesse par roue ---
            if nom in ('MATH_Speed_FL', 'MATH_Speed_FR',
                       'MATH_Speed_RL', 'MATH_Speed_RR'):
                rpm = sigs[combo[0]]
                return t_ref, np.abs(rpm) / RPM_TO_KMH, combo

            # --- Déséquilibre AV/AR ---
            if nom == 'MATH_Deseq_AV_AR':
                av = (np.abs(sigs[combo[0]]) + np.abs(sigs[combo[1]])) / 2
                ar = (np.abs(sigs[combo[2]]) + np.abs(sigs[combo[3]])) / 2
                return t_ref, av - ar, combo

            # --- Déséquilibre G/D ---
            if nom == 'MATH_Deseq_G_D':
                g = (np.abs(sigs[combo[0]]) + np.abs(sigs[combo[1]])) / 2
                d = (np.abs(sigs[combo[2]]) + np.abs(sigs[combo[3]])) / 2
                return t_ref, g - d, combo

            # --- Glissement ---
            if nom in ('MATH_Glissement_FL', 'MATH_Glissement_FR'):
                rpm  = np.abs(sigs[combo[0]])
                vref = sigs[combo[1]]
                vref = np.where(vref > 1.0, vref, np.nan)
                vroue = rpm / RPM_TO_KMH
                return t_ref, (vroue - vref) / vref * 100.0, combo

            # --- Roulis suspension ---
            if nom == 'MATH_Roulis_Susp':
                fl = sigs[combo[0]]; fr = sigs[combo[1]]
                rl = sigs[combo[2]]; rr = sigs[combo[3]]
                return t_ref, (fl + rl) / 2 - (fr + rr) / 2, combo

            # --- Tangage suspension ---
            if nom == 'MATH_Tangage_Susp':
                fl = sigs[combo[0]]; fr = sigs[combo[1]]
                rl = sigs[combo[2]]; rr = sigs[combo[3]]
                return t_ref, (fl + fr) / 2 - (rl + rr) / 2, combo

        except Exception:
            continue

    return None, None, None


def calculer_tous(mdf, canaux_disponibles):
    """
    Retourne la liste des math channels calculables avec leurs données.
    [{...mc, 't': array, 's': array, 'canaux_utilises': list}]
    """
    resultats = []
    for mc in MATH_CHANNELS:
        t, s, combo = calculer_math_channel(mdf, canaux_disponibles, mc)
        if t is not None:
            resultats.append({**mc, 't': t, 's': s, 'canaux_utilises': combo})
    return resultats