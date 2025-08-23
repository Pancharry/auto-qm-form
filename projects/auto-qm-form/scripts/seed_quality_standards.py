# scripts/seed_quality_standards.py
from src.db import SessionLocal
from src.models import QualityStandard

data = [
    {
        "item_name": "鋼筋",
        "item_type": "material",
        "source": "ref_manual_A",
        "inspection_items": ["材質", "尺寸"],
        "inspection_methods": ["材質證明文件", "游標卡尺量測"],
        "acceptance_criteria": ["符號標記完整", "尺寸公差±2%"],
        "frequency": "每批",
        "responsible_party": "監造"
    },
    {
        "item_name": "水泥",
        "item_type": "material",
        "source": "ref_manual_B",
        "inspection_items": ["出廠證明", "批號"],
        "inspection_methods": ["文件審查", "目視"],
        "acceptance_criteria": ["規格符合 CNS", "批號可追蹤"],
        "frequency": "每批",
        "responsible_party": "廠商"
    }
]

def run():
    db = SessionLocal()
    for d in data:
        if not db.query(QualityStandard).filter_by(item_name=d["item_name"], item_type=d["item_type"]).first():
            db.add(QualityStandard(**d))
    db.commit()
    db.close()

if __name__ == "__main__":
    run()
