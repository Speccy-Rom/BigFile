from .base import Base  # noqa

# Импортируйте все модели, чтобы Base имел
# их перед импортом в Alembic.
from .. import models  # noqa