# Импортируйте все модели, чтобы Base имел
# их перед импортом в Alembic.
from .. import models  # noqa
from .base import Base  # noqa
