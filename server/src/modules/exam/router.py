"""Exam and answer API routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.common.deps import get_current_user_id
from src.common.response import ApiResponse, success
from src.config.database import get_db
from src.modules.exam.schemas import ExamResultResponse, SubmitAnswerRequest, SubmitAnswerResponse
from src.modules.exam.service import get_result as get_result_service
from src.modules.exam.service import submit_answer as submit_answer_service

router = APIRouter()


@router.post("/submit")
def submit_answer(
    payload: SubmitAnswerRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
) -> ApiResponse[SubmitAnswerResponse]:
    """Submit or revise one answer."""
    return success(submit_answer_service(db, user_id, payload))


@router.get("/result/{paper_id}")
def get_result(
    paper_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
) -> ApiResponse[ExamResultResponse]:
    """Return the full result for an owned paper."""
    return success(get_result_service(db, user_id, paper_id))
