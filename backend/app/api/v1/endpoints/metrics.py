from fastapi import APIRouter, Depends
from app.core.auth import get_current_user
from app.models.user import CurrentUser
from app.models.response import StandardResponse
from app.services.metrics.learning_metrics import get_learning_metrics

router = APIRouter(prefix="/metrics")

@router.get("/learning", response_model=StandardResponse[dict])
def learning_metrics(current_user: CurrentUser = Depends(get_current_user)):
    metrics = get_learning_metrics(str(current_user.firm_id))
    return StandardResponse(data=metrics)
