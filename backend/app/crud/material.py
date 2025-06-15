from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.material import Material
from app.schemas.material import MaterialCreate, MaterialUpdate
from fastapi.encoders import jsonable_encoder

class CRUDMaterial(CRUDBase[Material, MaterialCreate, MaterialUpdate]):
    def create(self, db: Session, *, obj_in: MaterialCreate, **kwargs) -> Material:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data, **kwargs)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_code(self, db: Session, *, code: str) -> Material | None:
        return db.query(self.model).filter(self.model.material_code == code).first()

    def get_by_name(self, db: Session, *, name: str) -> Material | None:
        return db.query(self.model).filter(self.model.name == name).first()

material_crud = CRUDMaterial(Material) 