from app.crud.base import CRUDBase
from app.models.material import Material
from app.schemas.material import MaterialCreate, MaterialUpdate

class CRUDMaterial(CRUDBase[Material, MaterialCreate, MaterialUpdate]):
    pass

material_crud = CRUDMaterial(Material) 