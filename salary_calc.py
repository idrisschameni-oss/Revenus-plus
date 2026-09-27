"""
Fonctions de calcul pour le simulateur de salaire hebdomadaire.
Logique pure (aucun accès base de données), pour rester testable isolément.
"""

from typing import Optional


def calculer_brut(
    salaire_brut: Optional[float] = None,
    heures: Optional[float] = None,
    taux_horaire: Optional[float] = None,
) -> float:
    """Retourne le salaire brut, saisi directement ou via heures x taux horaire."""
    if salaire_brut is not None:
        return round(salaire_brut, 2)
    if heures is not None and taux_horaire is not None:
        return round(heures * taux_horaire, 2)
    raise ValueError("Fournir 'salaire_brut', ou 'heures' et 'taux_horaire'.")


def calculer_semaine(
    brut: float,
    taux_cotisations: float = 0.0,
    taux_impot: float = 0.0,
    autres_retenues: float = 0.0,
) -> dict:
    """Calcule cotisations, impôt, charges totales et net à partir du brut."""
    cotisations = round(brut * taux_cotisations / 100, 2)
    impot = round(brut * taux_impot / 100, 2)
    charges = round(cotisations + impot + autres_retenues, 2)
    net = round(brut - charges, 2)
    return {
        "cotisations": cotisations,
        "impot": impot,
        "charges": charges,
        "net": net,
    }
