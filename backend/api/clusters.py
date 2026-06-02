from fastapi import APIRouter, Depends

from core.auth import get_current_user
from kubernetes.cluster_manager import list_cluster_contexts

router = APIRouter()


@router.get("/clusters")
def get_clusters(_user: dict = Depends(get_current_user)) -> list[str]:
    """Return available kubectl contexts from kubeconfig."""
    result = list_cluster_contexts()
    return result.get("contexts", [])
