from sqlalchemy import MetaData

from app.settings.db import database_settings
from app.storage.db.connection_manager import ConnectionManager

db_manager = ConnectionManager(database_settings)
metadata = MetaData()
