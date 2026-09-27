"""
Fonctions de calcul pour le simulateur de transactions (frais, conversion).
Logique pure (aucun accès base de données), pour rester testable isolément.
"""

from typing import Optional


def calculer_frais(
    montant: float,
    frais_fixe: float = 0.0,
    taux_pourcentage: float = 0.0,
    frais_min: Optional[float] = None,
    frais_max: Optional[float] = None,
) -> dict:
    """Calcule le frais total d'une transaction, avec plancher/plafond éventuels."""
    frais_pct = montant * taux_pourcentage / 100
    frais_total = frais_fixe + frais_pct

    if frais_min is not None:
        frais_total = max(frais_total, frais_min)
    if frais_max is not None:
        frais_total = min(frais_total, frais_max)

    frais_total = round(frais_total, 2)

    return {
        "montant_initial": round(montant, 2),
        "frais_fixe": round(frais_fixe, 2),
        "frais_pourcentage": round(frais_pct, 2),
        "frais_total": frais_total,
        "montant_final": round(montant - frais_total, 2),
    }


def convertir_devise(
    montant: float,
    taux_change: float,
    frais_conversion_pct: float = 0.0,
) -> dict:
    """Convertit un montant selon un taux de change, avec frais de conversion en %."""
    montant_converti_brut = montant * taux_change
    frais = montant_converti_brut * frais_conversion_pct / 100
    montant_final = montant_converti_brut - frais

    return {
        "montant_initial": round(montant, 2),
        "taux_change": taux_change,
        "montant_converti_brut": round(montant_converti_brut, 2),
        "frais_conversion": round(frais, 2),
        "montant_final": round(montant_final, 2),
    }
