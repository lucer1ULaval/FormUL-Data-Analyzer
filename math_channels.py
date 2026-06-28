import numpy as np
from constants import RPM_TO_KMH

# Chaque entrée : (nom, label, unite, desc, requis, requis_alt)
MATH_CHANNELS = [
    {
        'nom':        'MATH_Puissance_kW',
        'label':      'Puissance totale',
        'unite':      'kW',
        'desc':       'BMS_TotVolt × BMS_AvgCur / 1000',
        'requis':     ['BMS_TotVolt', 'BMS_AvgCur'],
        'requis_alt': [['BMS_totalVoltage', 'BMS_avgCurrent']],
    },
    {
        'nom':        'MATH_Speed_FL',
        'label':      'Vitesse roue FL',
        'unite':      'km/h',
        'desc':       'DI_Inv1_speed_rpm / 107.76',
        'requis':     ['DI_Inv1_speed_rpm'],
        'requis_alt': [['DI1_RPM']],
    },
    {
        'nom':        'MATH_Speed_FR',
        'label':      'Vitesse roue FR',
        'unite':      'km/h',
        'desc':       'DI_Inv2_speed_rpm / 107.76',
        'requis':     ['DI_Inv2_speed_rpm'],
        'requis_alt': [['DI2_RPM']],
    },
    {
        'nom':        'MATH_Speed_RL',
        'label':      'Vitesse roue RL',
        'unite':      'km/h',
        'desc':       'DI_Inv3_speed_rpm / 107.76',
        'requis':     ['DI_Inv3_speed_rpm'],
        'requis_alt': [['DI3_RPM']],
    },
    {
        'nom':        'MATH_Speed_RR',
        'label':      'Vitesse roue RR',
        'unite':      'km/h',
        'desc':       'DI_Inv4_speed_rpm / 107.76',
        'requis':     ['DI_Inv4_speed_rpm'],
        'requis_alt': [['DI4_RPM']],
    },
    {
        'nom':        'MATH_Deseq_AV_AR',
        'label':      'Déséquilibre AV/AR',
        'unite':      'rpm',
        'desc':       '(Inv1+Inv2)/2 − (Inv3+Inv4)/2  →  positif = avant tourne plus vite',
        'requis':     ['DI_Inv1_speed_rpm', 'DI_Inv2_speed_rpm',
                       'DI_Inv3_speed_rpm', 'DI_Inv4_speed_rpm'],
        'requis_alt': [['DI1_RPM', 'DI2_RPM', 'DI3_RPM', 'DI4_RPM']],
    },
    {
        'nom':        'MATH_Deseq_G_D',
        'label':      'Déséquilibre G/D',
        'unite':      'rpm',
        'desc':       '(Inv1+Inv3)/2 − (Inv2+Inv4)/2  →  positif = gauche tourne plus vite',
        'requis':     ['DI_Inv1_speed_rpm', 'DI_Inv3_speed_rpm',
                       'DI_Inv2_speed_rpm', 'DI_Inv4_speed_rpm'],
        'requis_alt': [['DI1_RPM', 'DI3_RPM', 'DI2_RPM', 'DI4_RPM']],
    },
    {
        'nom':        'MATH_Glissement_FL',
        'label':      'Glissement FL',
        'unite':      '%',
        'desc':       '(vitesse_FL − vitesse_ref) / vitesse_ref × 100',
        'requis':     ['DI_Inv1_speed_rpm', 'Speed'],
        'requis_alt': [['DI1_RPM', 'Speed'], ['DI_Inv1_speed_rpm', 'RCP_GPS_Speed']],
    },
    {
        'nom':        'MATH_Glissement_FR',
        'label':      'Glissement FR',
        'unite':      '%',
        'desc':       '(vitesse_FR − vitesse_ref) / vitesse_ref × 100',
        'requis':     ['DI_Inv2_speed_rpm', 'Speed'],
        'requis_alt': [['DI2_RPM', 'Speed'], ['DI_Inv2_speed_rpm', 'RCP_GPS_Speed']],
    },
    {
        'nom':        'MATH_Roulis_Susp',
        'label':      'Roulis suspension',
        'unite':      'mm',
        'desc':       '(Pot_FL + Pot_RL)/2 − (Pot_FR + Pot_RR)/2',
        'requis':     ['Pot_FL', 'Pot_FR', 'Pot_RL', 'Pot_RR'],
        'requis_alt': [],
    },
    {
        'nom':        'MATH_Tangage_Susp',
        'label':      'Tangage suspension',
        'unite':      'mm',
        'desc':       '(Pot_FL + Pot_FR)/2 − (Pot_RL + Pot_RR)/2',
        'requis':     ['Pot_FL', 'Pot_FR', 'Pot_RL', 'Pot_RR'],
        'requis_alt': [],
    },
    {
        'nom':        'MATH_Cell_Imbalance',
        'label':      'Déséquilibre cellules',
        'unite':      'mV',
        'desc':       '(max(BMS_CV*) − min(BMS_CV*)) × 1000 par pas de temps',
        'requis':     [],  # calculé dynamiquement
        'requis_alt': [],
        '_special':   'cell_imbalance',
    },
    {
        'nom':        'MATH_Temp_Max',
        'label':      'Température max onduleurs',
        'unite':      '°C',
        'desc':       'max(DI1CTL_Temp, DI2CTL_Temp, DI3CTL_Temp, DI4CTL_Temp)',
        'requis':     ['DI1CTL_Temp', 'DI2CTL_Temp', 'DI3CTL_Temp', 'DI4CTL_Temp'],
        'requis_alt': [['DI1_Controller_Temperature', 'DI2_Controller_Temperature',
                        'DI3_Controller_Temperature', 'DI4_Controller_Temperature']],
    },
    {
        'nom':        'MATH_APPS_Plausibility',
        'label':      'Plausibilité APPS',
        'unite':      '%',
        'desc':       'Écart entre APPS1 et APPS2 (doit rester < 10%)',
        'requis':     ['ACQ_apps'],
        'requis_alt': [['VCU_APPS']],
        '_special':   'apps_plausibility',
    },
    {
        'nom':        'MATH_Puissance_FL',
        'label':      'Puissance roue FL',
        'unite':      'kW',
        'desc':       'DI1_AC × DI1_RPM / 9549 × 1000',
        'requis':     ['DI1_AC', 'DI_Inv1_speed_rpm'],
        'requis_alt': [['DI1_AC', 'DI1_RPM']],
    },
    {
        'nom':        'MATH_Puissance_FR',
        'label':      'Puissance roue FR',
        'unite':      'kW',
        'desc':       'DI2_AC × DI2_RPM / 9549 × 1000',
        'requis':     ['DI2_AC', 'DI_Inv2_speed_rpm'],
        'requis_alt': [['DI2_AC', 'DI2_RPM']],
    },
]


def _get_signal(mdf, canaux_disponibles, noms):
    for nom in noms:
        if nom in canaux_disponibles:
            try:
                sig = mdf.get(nom)
                return sig.timestamps, sig.samples.astype(float)
            except Exception:
                continue
    return None, None


def _resample(t_ref, t_src, s_src):
    if len(t_src) == 0 or len(s_src) == 0 or len(t_ref) == 0:
        return np.full(len(t_ref), np.nan)
    return np.interp(t_ref, t_src, s_src)


def _essayer_combo(mdf, canaux_disponibles, combo):
    sigs, t_ref = {}, None
    for c in combo:
        t, s = _get_signal(mdf, canaux_disponibles, [c])
        if t is None or len(t) == 0 or len(s) == 0:
            return None, None
        if t_ref is None:
            t_ref = t
        if len(t_ref) == 0:
            return None, None
        sigs[c] = _resample(t_ref, t, s)
    return t_ref, sigs


def calculer_math_channel(mdf, canaux_disponibles, mc):
    nom = mc['nom']

    # Cas spéciaux (multi-canaux dynamiques)
    if mc.get('_special') == 'cell_imbalance':
        return _calc_cell_imbalance(mdf, canaux_disponibles)

    if mc.get('_special') == 'apps_plausibility':
        return _calc_apps_plausibility(mdf, canaux_disponibles, mc)

    for combo in [mc['requis']] + mc.get('requis_alt', []):
        if not combo:
            continue
        t_ref, sigs = _essayer_combo(mdf, canaux_disponibles, combo)
        if t_ref is None:
            continue
        try:
            result = _appliquer_formule(nom, sigs, combo, t_ref)
            if result is not None:
                return t_ref, result, combo
        except Exception:
            continue

    return None, None, None


def _appliquer_formule(nom, sigs, combo, t_ref):
    if nom == 'MATH_Puissance_kW':
        return np.abs(sigs[combo[0]] * sigs[combo[1]]) / 1000.0

    if nom in ('MATH_Speed_FL', 'MATH_Speed_FR', 'MATH_Speed_RL', 'MATH_Speed_RR'):
        return np.abs(sigs[combo[0]]) / RPM_TO_KMH

    if nom == 'MATH_Deseq_AV_AR':
        av = (np.abs(sigs[combo[0]]) + np.abs(sigs[combo[1]])) / 2
        ar = (np.abs(sigs[combo[2]]) + np.abs(sigs[combo[3]])) / 2
        return av - ar

    if nom == 'MATH_Deseq_G_D':
        g = (np.abs(sigs[combo[0]]) + np.abs(sigs[combo[1]])) / 2
        d = (np.abs(sigs[combo[2]]) + np.abs(sigs[combo[3]])) / 2
        return g - d

    if nom in ('MATH_Glissement_FL', 'MATH_Glissement_FR'):
        rpm  = np.abs(sigs[combo[0]])
        vref = np.where(sigs[combo[1]] > 1.0, sigs[combo[1]], np.nan)
        vroue = rpm / RPM_TO_KMH
        return (vroue - vref) / vref * 100.0

    if nom == 'MATH_Roulis_Susp':
        fl, fr, rl, rr = sigs[combo[0]], sigs[combo[1]], sigs[combo[2]], sigs[combo[3]]
        return (fl + rl) / 2 - (fr + rr) / 2

    if nom == 'MATH_Tangage_Susp':
        fl, fr, rl, rr = sigs[combo[0]], sigs[combo[1]], sigs[combo[2]], sigs[combo[3]]
        return (fl + fr) / 2 - (rl + rr) / 2

    if nom == 'MATH_Temp_Max':
        vals = np.stack([sigs[c] for c in combo])
        return np.max(vals, axis=0)

    if nom in ('MATH_Puissance_FL', 'MATH_Puissance_FR'):
        # Approximation: I_AC × ω / 1000  (sans couple direct)
        i_ac = np.abs(sigs[combo[0]])
        rpm  = np.abs(sigs[combo[1]])
        omega = rpm * 2 * np.pi / 60  # rad/s
        # Tension nominale par onduleur ≈ pack/2
        return i_ac * omega / 1000.0  # approximation

    return None


def _calc_cell_imbalance(mdf, canaux_disponibles):
    """Déséquilibre entre cellules BMS: max(CV) - min(CV) en mV."""
    cv_canaux = [c for c in canaux_disponibles if c.startswith('BMS_CV')]
    if len(cv_canaux) < 2:
        return None, None, None
    t_ref = None
    all_s = []
    for c in sorted(cv_canaux):
        try:
            sig = mdf.get(c)
            t_c = sig.timestamps.astype(float)
            s_c = sig.samples.astype(float)
            if t_ref is None:
                t_ref = t_c
            all_s.append(np.interp(t_ref, t_c, s_c))
        except Exception:
            continue
    if len(all_s) < 2 or t_ref is None:
        return None, None, None
    mat = np.array(all_s)
    imbalance_v  = np.max(mat, axis=0) - np.min(mat, axis=0)
    imbalance_mv = imbalance_v * 1000.0
    return t_ref, imbalance_mv, cv_canaux


def _calc_apps_plausibility(mdf, canaux_disponibles, mc):
    """Si deux canaux APPS disponibles, calcule l'écart. Sinon, retourne None."""
    t1, s1 = _get_signal(mdf, canaux_disponibles, mc['requis'])
    if t1 is None:
        for combo in mc.get('requis_alt', []):
            t1, s1 = _get_signal(mdf, canaux_disponibles, combo)
            if t1 is not None:
                break
    if t1 is None:
        return None, None, None
    # Chercher APPS2
    for nom2 in ['ACQ_apps2', 'VCU_APPS2', 'ACQ_apps_2']:
        t2, s2 = _get_signal(mdf, canaux_disponibles, [nom2])
        if t2 is not None:
            s2_r = np.interp(t1, t2, s2)
            return t1, np.abs(s1 - s2_r), [mc['requis'][0], nom2]
    return None, None, None


def calculer_tous(mdf, canaux_disponibles):
    resultats = []
    for mc in MATH_CHANNELS:
        t, s, combo = calculer_math_channel(mdf, canaux_disponibles, mc)
        if t is not None:
            resultats.append({**mc, 't': t, 's': s, 'canaux_utilises': combo})
    return resultats
