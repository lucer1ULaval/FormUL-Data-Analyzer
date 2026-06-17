import asammdf
import pandas as pd
import yaml


def charger_config(chemin_config="config.yaml"):
    with open(chemin_config, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def charger_mdf(chemin_mdf, config):
    mdf = asammdf.MDF(chemin_mdf)
    canaux_disponibles = set(mdf.channels_db.keys())

    domaines = {}
    for nom_domaine, infos in config["domaines"].items():
        canaux_cles = infos.get("canaux_cles", [])
        canaux_trouves = [c for c in canaux_cles if c in canaux_disponibles]

        prefixes = infos.get("prefixes", [])
        tous_canaux_domaine = [
            c for c in canaux_disponibles
            if any(c.startswith(p) for p in prefixes)
        ]

        domaines[nom_domaine] = {
            "canaux_cles": canaux_trouves,
            "tous_canaux": sorted(tous_canaux_domaine),
        }

    flags_erreur = [
        c for c in canaux_disponibles
        if any(c.startswith(p) for p in config["erreurs"]["prefixes"])
    ]

    return mdf, domaines, flags_erreur, canaux_disponibles


def signal_vers_dataframe(mdf, nom_canal):
    try:
        sig = mdf.get(nom_canal)
        samples = sig.samples
        if hasattr(samples, 'dtype') and samples.dtype.byteorder == '>':
            samples = samples.byteswap().view(samples.dtype.newbyteorder('<'))
        df = pd.DataFrame({
            "timestamp": sig.timestamps,
            nom_canal: samples,
        })
        return df, sig.unit
    except Exception:
        return None, ""


def stats_session(mdf, canaux_cles):
    stats = {}
    for canal in canaux_cles:
        try:
            sig = mdf.get(canal)
            stats[canal] = {
                "min": float(sig.samples.min()),
                "max": float(sig.samples.max()),
                "mean": float(sig.samples.mean()),
                "unit": sig.unit,
            }
        except Exception:
            continue
    return stats