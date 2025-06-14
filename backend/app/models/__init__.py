import pkgutil
import importlib
import inspect

__all__ = []

# 动态地发现并导入此包中的所有模块
# `__path__` 和 `__name__` 是在 `__init__.py` 中可用的特殊变量
for module_info in pkgutil.walk_packages(path=__path__, prefix=__name__ + '.'):
    # 导入模块
    module = importlib.import_module(module_info.name)
    # 遍历模块中的所有类
    for class_name, _class in inspect.getmembers(module, inspect.isclass):
        # 确保该类是在当前模块中定义的，而不是从其他地方导入的
        if _class.__module__ == module_info.name:
            # 将类名添加到 __all__ 列表中, 这样 `from app.models import *` 才能工作
            __all__.append(class_name)
            # 将类添加到包的全局命名空间中,
            # 这样 `from app.models import User` 这样的导入才能工作
            globals()[class_name] = _class
