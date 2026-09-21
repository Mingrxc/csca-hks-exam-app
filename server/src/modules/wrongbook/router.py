"""Wrong-book API routes."""

from datetime import datetime
from io import BytesIO

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from src.common.deps import get_current_user_id
from src.common.response import ApiResponse, success
from src.config.database import get_db
from src.modules.question.schemas import PaperResponse
from src.modules.wrongbook.schemas import (
    MasteredStatusResponse,
    RelatedQuestion,
    WrongBookDetail,
    WrongBookItem,
)
from src.modules.wrongbook.service import generate_redo_paper as generate_redo_paper_service
from src.modules.wrongbook.service import export_wrongbook_pdf as export_wrongbook_pdf_service
from src.modules.wrongbook.service import get_related as get_related_service
from src.modules.wrongbook.service import get_wrong_detail as get_wrong_detail_service
from src.modules.wrongbook.service import get_wrong_detail_by_question as get_wrong_detail_by_question_service
from src.modules.wrongbook.service import list_wrong_questions as list_wrong_questions_service
from src.modules.wrongbook.service import mark_mastered as mark_mastered_service

router = APIRouter()


@router.get("/list")
def list_wrong_questions(
    exam_type: str = Query("all", alias="examType"),
    knowledge: str = "all",
    wrong_count: str = Query("all", alias="wrongCount"),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
) -> ApiResponse[list[WrongBookItem]]:
    """Return wrong questions with optional filters."""
    return success(list_wrong_questions_service(db, user_id, exam_type, knowledge, wrong_count))


@router.get("/related/{question_id}")
def get_related(
    question_id: int,
    db: Session = Depends(get_db),
) -> ApiResponse[list[RelatedQuestion]]:
    """Return questions from the same exam, subject, and knowledge point."""
    return success(get_related_service(db, question_id))


@router.get("/export-pdf")
def export_pdf(
    exam_type: str = Query("all", alias="examType"),
    knowledge: str = "all",
    wrong_count: str = Query("all", alias="wrongCount"),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Export the filtered wrong book as a PDF."""
    content = export_wrongbook_pdf_service(db, user_id, exam_type, knowledge, wrong_count)
    filename = f"wrongbook-{datetime.now().strftime('%Y%m%d')}.pdf"
    return StreamingResponse(
        BytesIO(content),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/redo-paper")
def generate_redo_paper(
    exam_type: str = Query(..., alias="examType", pattern="^(CSCA|HKS)$"),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
) -> ApiResponse[PaperResponse]:
    """Generate a practice paper from unmastered wrong questions."""
    return success(generate_redo_paper_service(db, user_id, exam_type, limit))


@router.get("/question/{question_id}")
def get_wrong_detail_by_question(
    question_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
) -> ApiResponse[WrongBookDetail]:
    """Return the current user's wrong-book detail by question ID."""
    return success(get_wrong_detail_by_question_service(db, user_id, question_id))


@router.get("/{wrongbook_id}")
def get_wrong_detail(
    wrongbook_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
) -> ApiResponse[WrongBookDetail]:
    """Return an owned wrong-book entry."""
    return success(get_wrong_detail_service(db, user_id, wrongbook_id))


@router.put("/{wrongbook_id}/master")
def mark_mastered(
    wrongbook_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
) -> ApiResponse[MasteredStatusResponse]:
    """Toggle the mastered state for an owned wrong-book entry."""
    return success(mark_mastered_service(db, user_id, wrongbook_id))
