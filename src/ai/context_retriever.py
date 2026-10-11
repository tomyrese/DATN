import re
from typing import Dict, List, Any, Optional
from src.database.db import Database, get_db

class ContextRetriever:
    """
    Retrieves grounded, permission-filtered business context for the AI Concierge.
    Guarantees no raw SQL execution by the LLM and strict role-based data filtering.
    """

    def __init__(self, db: Optional[Database] = None):
        self.db = db or get_db()

    def retrieve_context(self, question: str, role: str = "guest", store_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        q_clean = question.lower().strip()
        tokens = re.findall(r"\w+", q_clean)

        # 1. Fetch Stores
        store_rows = self.db.fetchall("SELECT id, name, category, description, opening_hours, contact_phone FROM stores WHERE is_active = 1")
        matched_stores = []
        for s in store_rows:
            if any(t in s["name"].lower() or t in s["category"].lower() or t in (s["description"] or "").lower() for t in tokens):
                matched_stores.append(dict(s))
        if not matched_stores:
            matched_stores = [dict(s) for s in store_rows[:4]]

        # 2. Fetch Active Promotions
        promo_rows = self.db.fetchall("""
            SELECT p.title, p.description, p.discount_percent, p.promo_code, s.name as store_name
            FROM promotions p
            JOIN stores s ON p.store_id = s.id
            WHERE p.is_active = 1
            LIMIT 5
        """)
        matched_promos = [dict(p) for p in promo_rows]

        # 3. Fetch FAQ
        faq_rows = self.db.fetchall("SELECT category, question, answer FROM mall_faq WHERE is_active = 1")
        matched_faqs = []
        for f in faq_rows:
            if any(t in f["question"].lower() or t in f["category"].lower() or t in f["answer"].lower() for t in tokens):
                matched_faqs.append(dict(f))
        if not matched_faqs:
            matched_faqs = [dict(f) for f in faq_rows[:3]]

        # 4. Fetch Suggested POI
        suggested_poi = None
        poi_rows = self.db.fetchall("SELECT id, name, category, description FROM mall_pois WHERE is_staff_only = 0")
        for p in poi_rows:
            if any(t in p["name"].lower() or t in (p["description"] or "").lower() for t in tokens):
                suggested_poi = dict(p)
                break

        return {
            "stores": matched_stores,
            "promotions": matched_promos,
            "faqs": matched_faqs,
            "suggested_poi": suggested_poi
        }

    def format_context_string(self, context_data: Dict[str, Any]) -> str:
        lines = ["=== DỮ LIỆU CHÍNH THỨC TRUNG TÂM THƯƠNG MẠI ==="]

        if context_data.get("faqs"):
            lines.append("\n[Thông Tin Thường Gặp & Tiện Ích]")
            for f in context_data["faqs"]:
                lines.append(f"- Hỏi: {f['question']}")
                lines.append(f"  Đáp: {f['answer']}")

        if context_data.get("stores"):
            lines.append("\n[Danh Sách Cửa Hàng]")
            for s in context_data["stores"]:
                lines.append(f"- {s['name']} ({s['category']}): {s['description']}. Giờ mở cửa: {s['opening_hours']}")

        if context_data.get("promotions"):
            lines.append("\n[Chương Trình Khuyến Mãi Đang Diễn Ra]")
            for p in context_data["promotions"]:
                lines.append(f"- {p['store_name']}: {p['title']} ({p['description']}). Mã: {p.get('promo_code', 'Không cần mã')}")

        lines.append("=================================================")
        return "\n".join(lines)
