from io import BytesIO
from pathlib import Path
import re
import uuid
import warnings

from PIL import Image, ImageOps, UnidentifiedImageError

from src.common.exceptions import AppException
from src.config.settings import settings
from src.modules.user.models import User
from src.modules.user.service import count_user_favorites, get_target_dates, serialize_user

MAX_AVATAR_BYTES = 2 * 1024 * 1024


def avatar_file(filename: str) -> Path:
    if not re.fullmatch(r"[a-f0-9]{32}\.jpg", filename):
        raise AppException(40402, "头像不存在", status_code=404)
    path = Path(settings.USER_AVATAR_ROOT).resolve() / filename
    if not path.is_file():
        raise AppException(40402, "头像不存在", status_code=404)
    return path


def save_avatar(db, user_id: int, content: bytes) -> dict:
    if not content or len(content) > MAX_AVATAR_BYTES:
        raise AppException(41301, "请选择不超过2MB的头像", status_code=413)
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(BytesIO(content)) as source:
                if source.format not in {"JPEG", "PNG", "WEBP"} or source.width * source.height > 16_000_000:
                    raise ValueError("Unsupported image")
                image = ImageOps.exif_transpose(source)
                image.thumbnail((512, 512))
                rgba = image.convert("RGBA")
                safe = Image.new("RGB", rgba.size, "white")
                safe.paste(rgba, mask=rgba.getchannel("A"))
                output = BytesIO()
                safe.save(output, format="JPEG", quality=88)
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError, Image.DecompressionBombWarning) as exc:
        raise AppException(42203, "请选择有效的PNG、JPEG或WebP头像", status_code=422) from exc
    user = db.query(User).filter(User.id == user_id).first()
    root = Path(settings.USER_AVATAR_ROOT).resolve()
    root.mkdir(parents=True, exist_ok=True)
    path = root / f"{uuid.uuid4().hex}.jpg"
    path.write_bytes(output.getvalue())
    try:
        user.avatar_url = f"/api/v1/user/avatar/{path.name}"
        db.commit()
        db.refresh(user)
    except Exception:
        db.rollback()
        path.unlink(missing_ok=True)
        raise
    return serialize_user(user, count_user_favorites(db, user.id), get_target_dates(db, user))
