"""Question-bank API routes."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.common.deps import get_current_user_id
from src.common.response import ApiResponse, success
from src.config.database import get_db
from src.modules.question.schemas import (
    ExamType,
    GeneratePaperRequest,
    HistoryPaperResponse,
    PaperResponse,
    QuestionResponse,
    SpecialOptionResponse,
)
from src.modules.question.service import generate_paper as generate_paper_service
from src.modules.question.service import get_question as get_question_service
from src.modules.question.service import list_papers as list_papers_service
from src.modules.question.service import list_special_options as list_special_options_service

router = APIRouter()


@router.post("/generate-paper")
def generate_paper(
    payload: GeneratePaperRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
) -> ApiResponse[PaperResponse]:
    """Generate a paper from the selected strategy."""
    return success(generate_paper_service(db, user_id, payload))


@router.get("/papers")
def list_papers(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
) -> ApiResponse[list[HistoryPaperResponse]]:
    """Return the current user's completed papers."""
    return success(list_papers_service(db, user_id, limit))


@router.get("/special-options")
def list_special_options(
    examType: ExamType = Query(..., alias="examType"),
    limit: int = Query(24, ge=1, le=100),
    db: Session = Depends(get_db),
) -> ApiResponse[list[SpecialOptionResponse]]:
    """Return subject or knowledge-point filters for an exam."""
    return success(list_special_options_service(db, examType.value, limit))


@router.get("/{question_id}")
def get_question(
    question_id: int,
    db: Session = Depends(get_db),
) -> ApiResponse[QuestionResponse]:
    """Return a question without solution fields."""
    return success(get_question_service(db, question_id))
