from typing import Any

import inflect
from sqlalchemy.ext.declarative import as_declarative, declared_attr

p = inflect.engine()


@as_declarative()
class Base:
    id: Any
    __name__: str

    # Генерируйте __tablename__ автоматически в форме множественного числа.
    # т.е. модель 'Post' будет генерировать имя таблицы 'posts'
    @declared_attr
    def __tablename__(cls) -> str:
        return p.plural(cls.__name__.lower())