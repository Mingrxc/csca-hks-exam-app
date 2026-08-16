"""错题本业务逻辑."""

from datetime import datetime
from html import escape
from io import BytesIO

from sqlalchemy.orm import Session

from src.common.exceptions import AppException
from src.common.time import utc_now_naive
from src.modules.exam.models import AnswerRecord
from src.modules.question.models import Paper, Question
from src.modules.question.service import serialize_paper, serialize_question
from src.modules.wrongbook.models import WrongBook


def list_wrong_questions(
    db: Session,
    user_id: int,
    exam_type: str = "all",
    knowledge: str = "all",
    wrong_count: str = "all",
) -> list[dict]:
    query = build_wrong_query(db, user_id, exam_type, knowledge, wrong_count)
    return [serialize_wrong_item(item, question) for item, question in query.all()]


def build_wrong_query(
    db: Session,
    user_id: int,
    exam_type: str = "all",
    knowledge: str = "all",
    wrong_count: str = "all",
):
    query = (
        db.query(WrongBook, Question)
        .join(Question, Question.id == WrongBook.question_id)
        .filter(WrongBook.user_id == user_id)
        .order_by(WrongBook.last_wrong_at.desc())
    )

    if exam_type != "all":
        query = query.filter(Question.exam_type == exam_type)
    if knowledge != "all":
        query = query.filter(Question.knowledge_point == knowledge)
    if wrong_count == "1":
        query = query.filter(WrongBook.wrong_count == 1)
    elif wrong_count == "2+":
        query = query.filter(WrongBook.wrong_count >= 2)

    return query


def export_wrongbook_pdf(
    db: Session,
    user_id: int,
    exam_type: str = "all",
    knowledge: str = "all",
    wrong_count: str = "all",
) -> bytes:
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.cidfonts import UnicodeCIDFont
    from reportlab.platypus import KeepTogether, Paragraph, SimpleDocTemplate, Spacer

    rows = build_wrong_query(db, user_id, exam_type, knowledge, wrong_count).all()
    if not rows:
        raise AppException(40423, "没有符合条件的错题可导出", status_code=404)

    question_ids = [question.id for _, question in rows]
    records = (
        db.query(AnswerRecord)
        .filter(
            AnswerRecord.user_id == user_id,
            AnswerRecord.question_id.in_(question_ids),
            AnswerRecord.is_correct == 0,
        )
        .order_by(AnswerRecord.created_at.desc(), AnswerRecord.id.desc())
        .all()
    )
    latest_answers: dict[int, str] = {}
    for record in records:
        latest_answers.setdefault(record.question_id, record.user_answer or "未作答")

    font_name = "STSong-Light"
    if font_name not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(UnicodeCIDFont(font_name))

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ChineseTitle",
        parent=styles["Title"],
        fontName=font_name,
        fontSize=18,
        leading=26,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#1F2937"),
        spaceAfter=8 * mm,
    )
    heading_style = ParagraphStyle(
        "QuestionHeading",
        parent=styles["Heading3"],
        fontName=font_name,
        fontSize=11,
        leading=17,
        textColor=colors.HexColor("#3730A3"),
        spaceAfter=3 * mm,
    )
    body_style = ParagraphStyle(
        "ChineseBody",
        parent=styles["BodyText"],
        fontName=font_name,
        fontSize=10,
        leading=17,
        textColor=colors.HexColor("#1F2937"),
        spaceAfter=2 * mm,
    )
    answer_style = ParagraphStyle(
        "AnswerBody",
        parent=body_style,
        backColor=colors.HexColor("#F3F4F6"),
        borderPadding=8,
        spaceBefore=2 * mm,
        spaceAfter=4 * mm,
    )

    output = BytesIO()
    document = SimpleDocTemplate(
        output,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
        title="留学考霸错题本",
        author="留学考霸",
    )
    story = [
        Paragraph("留学考霸错题本", title_style),
        Paragraph(
            f"导出时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}　共 {len(rows)} 道错题",
            body_style,
        ),
        Spacer(1, 3 * mm),
    ]

    for index, (item, question) in enumerate(rows, start=1):
        meta = (
            f"第 {index} 题　{escape(question.exam_type)} / {escape(question.knowledge_point)}"
            f"　难度：{escape(question.difficulty)}　累计错误：{item.wrong_count or 0} 次"
        )
        block = [
            Paragraph(meta, heading_style),
            Paragraph(escape(question.stem_text).replace("\n", "<br/>"), body_style),
        ]
        for option in question.options or []:
            option_key = escape(str(option.get("key", "")))
            option_text = escape(str(option.get("text", ""))).replace("\n", "<br/>")
            block.append(Paragraph(f"{option_key}. {option_text}", body_style))
        block.append(Paragraph(
            f"最近答案：{escape(latest_answers.get(question.id, '未作答'))}<br/>"
            f"正确答案：{escape(question.answer)}<br/>"
            f"解析：{escape(question.analysis or '暂无解析').replace(chr(10), '<br/>')}",
            answer_style,
        ))
        story.extend([KeepTogether(block), Spacer(1, 3 * mm)])

    def add_page_number(canvas, doc):
        canvas.saveState()
        canvas.setFont(font_name, 9)
        canvas.setFillColor(colors.HexColor("#6B7280"))
        canvas.drawCentredString(A4[0] / 2, 8 * mm, f"第 {doc.page} 页")
        canvas.restoreState()

    document.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
    return output.getvalue()


def get_wrong_detail(db: Session, user_id: int, wrongbook_id: int) -> dict:
    row = (
        db.query(WrongBook, Question)
        .join(Question, Question.id == WrongBook.question_id)
        .filter(WrongBook.id == wrongbook_id, WrongBook.user_id == user_id)
        .first()
    )
    if not row:
        raise AppException(40421, "错题记录不存在", status_code=404)

    item, question = row
    return serialize_wrong_detail(db, user_id, item, question)


def get_wrong_detail_by_question(db: Session, user_id: int, question_id: int) -> dict:
    row = (
        db.query(WrongBook, Question)
        .join(Question, Question.id == WrongBook.question_id)
        .filter(WrongBook.user_id == user_id, WrongBook.question_id == question_id)
        .first()
    )
    if not row:
        raise AppException(40421, "错题记录不存在", status_code=404)

    item, question = row
    return serialize_wrong_detail(db, user_id, item, question)


def serialize_wrong_detail(db: Session, user_id: int, item: WrongBook, question: Question) -> dict:
    latest_record = (
        db.query(AnswerRecord)
        .filter(
            AnswerRecord.user_id == user_id,
            AnswerRecord.question_id == question.id,
            AnswerRecord.is_correct == 0,
        )
        .order_by(AnswerRecord.created_at.desc(), AnswerRecord.id.desc())
        .first()
    )
    return {
        **serialize_wrong_item(item, question),
        "question": serialize_question(question),
        "last_user_answer": latest_record.user_answer if latest_record else "",
        "wrong_options_analysis": question.wrong_options_analysis or {},
    }


def mark_mastered(db: Session, user_id: int, wrongbook_id: int) -> dict:
    item = (
        db.query(WrongBook)
        .filter(WrongBook.id == wrongbook_id, WrongBook.user_id == user_id)
        .first()
    )
    if not item:
        raise AppException(40421, "错题记录不存在", status_code=404)

    item.is_mastered = 0 if item.is_mastered else 1
    item.last_review_at = utc_now_naive()
    db.commit()
    db.refresh(item)
    return {
        "id": item.id,
        "question_id": item.question_id,
        "is_mastered": bool(item.is_mastered),
    }


def generate_redo_paper(db: Session, user_id: int, exam_type: str, limit: int = 20) -> dict:
    rows = (
        db.query(WrongBook, Question)
        .join(Question, Question.id == WrongBook.question_id)
        .filter(
            WrongBook.user_id == user_id,
            WrongBook.is_mastered == 0,
            Question.is_active == 1,
            Question.exam_type == exam_type,
        )
        .order_by(WrongBook.last_wrong_at.desc(), WrongBook.id.desc())
        .limit(limit)
        .all()
    )
    if not rows:
        raise AppException(40422, "No unmastered wrong questions found", status_code=404)

    questions = [question for _, question in rows]
    paper = Paper(
        user_id=user_id,
        title=f"{exam_type} 错题重做",
        exam_type=exam_type,
        strategy="knowledge",
        question_ids=[question.id for question in questions],
        total_score=len(questions),
        time_limit=0,
        mode="practice",
        difficulty="all",
    )
    db.add(paper)
    db.commit()
    db.refresh(paper)
    return serialize_paper(paper, questions, include_solution=True)


def get_related(db: Session, question_id: int, limit: int = 3) -> list[dict]:
    question = db.query(Question).filter(Question.id == question_id, Question.is_active == 1).first()
    if not question:
        raise AppException(40401, "题目不存在", status_code=404)

    related = (
        db.query(Question)
        .filter(
            Question.id != question.id,
            Question.is_active == 1,
            Question.exam_type == question.exam_type,
            Question.knowledge_point == question.knowledge_point,
        )
        .limit(limit)
        .all()
    )
    return [
        {
            **serialize_question(item, include_solution=False),
            "similarity_score": 1.0,
        }
        for item in related
    ]


def serialize_wrong_item(item: WrongBook, question: Question) -> dict:
    return {
        "id": item.id,
        "question_id": question.id,
        "exam_type": question.exam_type,
        "stem": question.stem_text,
        "type": question.question_type,
        "difficulty": question.difficulty,
        "knowledge_point": question.knowledge_point,
        "wrong_count": item.wrong_count or 0,
        "correct_count": item.correct_count or 0,
        "is_mastered": bool(item.is_mastered),
        "first_wrong_at": item.first_wrong_at,
        "last_wrong_at": item.last_wrong_at,
        "last_review_at": item.last_review_at,
    }
