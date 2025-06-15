from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.material import Material
from app.schemas.material import MaterialCreate, MaterialUpdate

class CRUDMaterial(CRUDBase[Material, MaterialCreate, MaterialUpdate]):
    def get_by_name(self, db: Session, *, name: str) -> Material | None:
        return db.query(self.model).filter(self.model.name == name).first()

material_crud = CRUDMaterial(Material) 