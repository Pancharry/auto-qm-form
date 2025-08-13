 
from src.db import SessionLocal
from src.models import MaterialEquipment

def main():
    with SessionLocal() as db:
        obj = MaterialEquipment(name="測試A", type="material", category="CAT1")
        db.add(obj)
        db.commit()
        db.refresh(obj)
        print("Inserted ID:", obj.id)

if __name__ == "__main__":
    main()
