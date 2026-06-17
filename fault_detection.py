import numpy as np
from constants import (MOTS_CLES_ERREUR, CANAL_VITESSE, CANAL_VITESSE_ALT,
                       SEUIL_VITESSE, SEUIL_COINCIDENCE, FENETRE_DECLENCHEUR)


def detecter_flags_erreur(mdf, canaux_disponibles):
    """Détecte automatiquement les canaux d'erreur binaires/petits entiers."""
    candidats = [c for c in canaux_disponibles
                 if any(mot in c.upper() for mot in MOTS_CLES_ERREUR)]
    flags = []
    for canal in candidats:
        try:
            sig = mdf.get(canal)
            s = sig.samples.astype(float)
            v = set(s)
            if v <= {0.0, 1.0} or (len(v) <= 8 and max(v) <= 255):
                flags.append(canal)
        except Exception:
            continue
    return flags


def _canal_vitesse(mdf):
    """Retourne le vecteur vitesse disponible (Speed ou RCP_GPS_Speed)."""
    for nom in [CANAL_VITESSE, CANAL_VITESSE_ALT]:
        try:
            sig = mdf.get(nom)
            return sig.timestamps, sig.samples.astype(float)
        except Exception:
            continue
    return None, None


def calculer_zones_faute(mdf, flags_erreur):
    """
    Détecte les zones de faute réelles via logique latch + coïncidence.
    - Déclenche si >= SEUIL_COINCIDENCE flags actifs ET voiture roule
    - Reste actif (latch) jusqu'à ce que tous les flags retombent à 0
    - Fusionne les zones proches (< 5s)
    """
    if not flags_erreur:
        return []
    try:
        sig0 = mdf.get(flags_erreur[0])
        t_deb, t_fin = float(sig0.timestamps[0]), float(sig0.timestamps[-1])
    except Exception:
        return []

    grille = np.arange(t_deb, t_fin, 1.0)
    if len(grille) < 2:
        return []

    mat = []
    for f in flags_erreur:
        try:
            sig = mdf.get(f)
            vals = np.interp(grille, sig.timestamps, sig.samples.astype(float))
            mat.append((vals > 0.5).astype(int))
        except Exception:
            continue
    if not mat:
        return []

    nb_simul = np.array(mat).sum(axis=0)

    t_vit, s_vit = _canal_vitesse(mdf)
    if t_vit is not None:
        vit = np.interp(grille, t_vit, s_vit)
    else:
        vit = np.full(len(grille), SEUIL_VITESSE + 1.0)

    # Latch
    zones, en_faute, debut = [], False, 0
    for i in range(len(grille)):
        if not en_faute and nb_simul[i] >= SEUIL_COINCIDENCE and vit[i] > SEUIL_VITESSE:
            debut = grille[i]; en_faute = True
        elif en_faute and nb_simul[i] == 0:
            zones.append((float(debut), float(grille[i]))); en_faute = False
    if en_faute:
        zones.append((float(debut), float(grille[-1])))

    # Fusionner < 5s
    if not zones:
        return []
    fus = [zones[0]]
    for d, f in zones[1:]:
        if d - fus[-1][1] <= 5.0:
            fus[-1] = (fus[-1][0], f)
        else:
            fus.append((d, f))
    return fus


def identifier_declencheurs(mdf, flags_erreur, zones_faute, fault_codes):
    """
    Pour chaque zone de faute, trouve les flags qui ont transitionné
    dans les FENETRE_DECLENCHEUR secondes précédant le déclenchement.
    Retourne: {debut_zone: [(dt, flag, v_avant, v_apres, description), ...]}
    """
    resultat = {}
    for debut, fin in zones_faute:
        transitions = []
        for flag in flags_erreur:
            try:
                sig = mdf.get(flag)
                t, s = sig.timestamps, sig.samples.astype(float)
                mask = (t >= debut - FENETRE_DECLENCHEUR) & (t <= debut + 2.0)
                t_f, s_f = t[mask], s[mask]
                if len(s_f) < 2:
                    continue
                diffs = np.diff(s_f.astype(int))
                for idx in np.where(diffs != 0)[0]:
                    v_av, v_ap = int(s_f[idx]), int(s_f[idx + 1])
                    if v_av == 0 and v_ap != 0:
                        dt = float(t_f[idx + 1]) - debut
                        desc = fault_codes.get(flag, {}).get(v_ap, None)
                        transitions.append((dt, flag, v_av, v_ap, desc))
            except Exception:
                continue
        resultat[debut] = sorted(transitions, key=lambda x: x[0])
    return resultat