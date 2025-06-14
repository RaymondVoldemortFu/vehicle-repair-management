from app.crud.base import CRUDBase
from app.models.service import Service
from app.schemas.service import ServiceCreate, ServiceUpdate

class CRUDService(CRUDBase[Service, ServiceCreate, ServiceUpdate]):
    pass

service_crud = CRUDService(Service) 