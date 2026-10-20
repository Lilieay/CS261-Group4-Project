from app.models.user import User


def format_publisher_name(publisher: User) -> str:
    thai_name = (publisher.displayname_th or "").strip()
    english_name = (publisher.displayname_en or "").strip()
    if thai_name and english_name:
        return f"{thai_name} ({english_name})"
    return thai_name or english_name or "ไม่ระบุชื่อ"
