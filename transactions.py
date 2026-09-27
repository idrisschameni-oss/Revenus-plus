from fastapi import APIRouter

from .. import schemas
from ..simulators import transaction_calc

router = APIRouter(prefix="/api/transactions", tags=["transactions"])

# Ces deux routes sont volontairement publiques (pas de Depends(get_current_user)) :
# ce sont de purs calculs, sans lecture ni écriture des données d'un utilisateur.


@router.post("/fee", response_model=schemas.FeeResult)
def compute_fee(payload: schemas.FeeRequest):
    resultat = transaction_calc.calculer_frais(
        montant=payload.montant,
        frais_fixe=payload.frais_fixe,
        taux_pourcentage=payload.taux_pourcentage,
        frais_min=payload.frais_min,
        frais_max=payload.frais_max,
    )
    return schemas.FeeResult(**resultat)


@router.post("/convert", response_model=schemas.ConversionResult)
def compute_conversion(payload: schemas.ConversionRequest):
    resultat = transaction_calc.convertir_devise(
        montant=payload.montant,
        taux_change=payload.taux_change,
        frais_conversion_pct=payload.frais_conversion_pct,
    )
    return schemas.ConversionResult(**resultat)
