# src/services/budget_parser.py
import csv, io, re
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from ..models import BudgetItem, StoredFile
from ..core.file_storage import save_file

CHINESE_NUM_MAP = {
    "壹":1,"貳":2,"參":3,"叁":3,"肆":4,"伍":5,"陸":6,"柒":7,"捌":8,"玖":9,"拾":10
}

INSTALL_KEYWORDS = ["安裝","安裝測試","測試","拆收","運交","搬遷","整合","改接","移設","調整","修改","擴充"]
EQUIP_KEYWORDS = [
    "控制器","伺服器","交換器","攝影機","分電箱","配電櫃","UPS","機櫃","標誌","讀卡機","記錄主機",
    "轉換器","終端","分析器","工作站","閥","閘閥","逆止閥","蝶型閥","過濾器","接頭","感測器",
    "智慧影像","探測器","變標誌","支架","構造物","PDU","UPS"
]
MATERIAL_KEYWORDS = [
    "光纜","電纜","電線","導線","管","鋼管","保溫","盒","配線","托架","鋁皮","配線機櫃","鋁製","電纜托架"
]
IGNORE_KEYWORDS = ["小計","合計","計   ","計 ","總計"]

def _is_install(name: str) -> bool:
    return any(k in name for k in INSTALL_KEYWORDS)

def _is_equipment(name: str) -> bool:
    return any(k in name for k in EQUIP_KEYWORDS)

def _is_material(name: str) -> bool:
    return any(k in name for k in MATERIAL_KEYWORDS)

def classify_type(name: str) -> str:
    if _is_install(name):
        return "work"
    if _is_equipment(name):
        return "equipment"
    if _is_material(name):
        return "material"
    return "material"  # default fallback

def parse_hierarchy(code: str):
    code = code.strip()
    if not code:
        return None, None
    parts = code.split(".")
    numeric = []
    for p in parts:
        p = p.strip()
        if not p:
            continue
        if p in CHINESE_NUM_MAP:
            numeric.append(CHINESE_NUM_MAP[p])
        else:
            # 純數字
            if re.fullmatch(r"\d+", p):
                numeric.append(int(p))
            else:
                # 混合：嘗試移除非數字
                digits = re.findall(r"\d+", p)
                if digits:
                    numeric.append(int(digits[-1]))
                else:
                    # 無法解析仍保留（不加入 numeric）
                    pass
    return code, numeric if numeric else None

def import_complex_budget(db: Session, file_bytes: bytes, filename: str, budget_id: str):
     # 1) 儲存原始檔案
    file_save = save_file(file_bytes, filename, "budget/raw", db=db)
    # 明確轉型，確保為 int（防守性作法）
    source_file_id: int = int(file_save["file_id"])

    text = file_bytes.decode("utf-8", errors="ignore")
    rows = list(csv.reader(io.StringIO(text)))
    rows = [r for r in rows if any(c.strip() for c in r)]
   
    # 尋找標頭
    header_idx = None
    for i, r in enumerate(rows):
        line_join = ",".join(r)
        if "項 次" in line_join and "項" in line_join and "說" in line_join:
            header_idx = i
            break
    if header_idx is None:
        return {"status": False, "message": "header_not_found"}

    data_rows = rows[header_idx+1:]
    inserted = 0
    warnings: List[str] = []
    items_buffer: List[Dict[str, Any]] = []
    last_item = None
    
    for raw in data_rows:
        # 正規化欄位長度
        while len(raw) < 7:
            raw.append("")
        code_col = raw[0].strip()
        name_col = raw[1].strip()
        unit = raw[2].strip()
        qty = raw[3].strip()
        unit_price = raw[4].strip()
        total_price = raw[5].strip()
        code_field = raw[6].strip()

        # 續行判斷：無 code_col 且 (name_col 不是分類關鍵詞) 且 last_item 存在
        if (not code_col) and name_col and last_item and not any(k in name_col for k in IGNORE_KEYWORDS):
            # 合併續行
            last_item["merged_segments"].append(name_col)
            last_item["name"] = last_item["name"] + name_col
            continue

        # 忽略小計 / 合計等
        if any(k in name_col for k in IGNORE_KEYWORDS):
            continue

        # 分類行判斷：有階層碼但無數量、無單位、無編碼或明顯為章節
        is_pure_section = False
        if code_col and (not qty) and (not unit) and (not code_field) and len(name_col) <= 20:
            is_pure_section = True
        if code_col and re.fullmatch(r"[壹貳參叁肆伍陸柒捌玖拾]{1,3}(\.[壹貳參叁肆伍陸柒捌玖拾\d]+)*", code_col) and not qty and not unit:
            if not code_field:
                is_pure_section = True

        if is_pure_section:
            last_item = None
            continue

        # 真正的可匯入項
        if not name_col:
            continue

        # 數量解析
        try:
            quantity = float(qty) if qty else None
        except:
            quantity = None
            warnings.append(f"quantity_parse_fail:{code_col}:{name_col}")

        # 單價/複價（MVP 可忽略空值）
        try:
            up = float(unit_price) if unit_price else None
        except:
            up = None
        try:
            tp = float(total_price) if total_price else None
        except:
            tp = None

        hierarchy_code, hierarchy_numeric = parse_hierarchy(code_col) if code_col else (None, None)

        item_type = classify_type(name_col)

        record = {
            "budget_id": budget_id,
            "name": name_col,
            "type": item_type,
            "unit": unit or None,
            "quantity": quantity,
            "unit_price": up,
            "total_price": tp,
            "description": None,
            "metadata_json": {
                "raw_name": name_col,
                "merged_segments": [name_col],
                "code_raw": code_field,
                "code_clean": code_field.replace("#","") if code_field else None,
                "hierarchy_code": hierarchy_code,
                "hierarchy_numeric": hierarchy_numeric,
                "source_file_id": source_file_id, # int 主鍵
                # 可選附加，利於前端展示與除錯（不必每次 join StoredFile）
                "source_file_original_name": filename,
                "source_file_type": "budget/raw",
                "is_work": item_type == "work",
                "is_equipment": item_type == "equipment"
            }
        }
        
        items_buffer.append(record)
        last_item = record

    # 寫入 DB
    for rec in items_buffer:
        bi = BudgetItem(
            budget_id=rec["budget_id"],
            name=rec["name"],
            type=rec["type"],
            unit=rec["unit"],
            quantity=rec["quantity"],
            unit_price=rec["unit_price"],
            total_price=rec["total_price"],
            description=rec["description"],
            metadata_json=rec["metadata_json"]
        )
        db.add(bi)
        inserted += 1
    db.commit()

    return {
        "status": True,
        "message": f"imported {inserted} items",
        "budget_id": budget_id,
        "inserted": inserted,
        "warnings": warnings[:30],
        "stats": _summarize(items_buffer),
        # 可選：將來源檔 id 回傳給前端，方便後續提供「下載原檔」功能
        "source_file_id": source_file_id
    }
    
def _summarize(items: List[Dict[str, Any]]):
    from collections import Counter
    c = Counter([it["type"] for it in items])
    return {
        "by_type": dict(c),
        "work_ratio": round(c.get("work",0)/len(items), 4) if items else 0
    }
