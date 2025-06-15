import json
import os
from sqlalchemy.orm import Session
from app.crud.material import material_crud
from app.schemas.material import MaterialCreate
from app.config.logging import get_logger

logger = get_logger()

def init_materials(db: Session) -> None:
    """
    初始化默认材料。
    如果数据库中没有材料，则从JSON文件中加载并创建它们。
    """
    logger.info("正在检查并初始化材料数据...")
    
    # 检查数据库中是否已有材料
    material_count = material_crud.count(db)
    if material_count > 0:
        logger.info(f"数据库中已存在 {material_count} 种材料，跳过初始化。")
        return

    logger.info("数据库中没有材料，开始从文件加载默认材料...")
    
    # 构建JSON文件路径
    # __file__ 是当前文件路径 (backend/app/db/init_data.py)
    # os.path.dirname(__file__) 是 backend/app/db
    # os.path.join(..., '..', 'core', 'default_materials.json') 找到目标文件
    file_path = os.path.join(
        os.path.dirname(__file__), '..', 'core', 'default_materials.json'
    )

    if not os.path.exists(file_path):
        logger.error(f"默认材料文件未找到: {file_path}")
        return

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            default_materials = json.load(f)

        created_count = 0
        for material_data in default_materials:
            material_in = MaterialCreate(**material_data)
            existing_material = material_crud.get_by_name(db, name=material_in.name)
            if not existing_material:
                material_crud.create(db, obj_in=material_in)
                created_count += 1
        
        logger.info(f"成功创建了 {created_count} 种新材料。")

    except json.JSONDecodeError:
        logger.error(f"解析默认材料文件失败: {file_path}")
    except Exception as e:
        logger.error(f"初始化材料时发生未知错误: {str(e)}") 