from datetime import datetime, timezone
from app.database.connection import db

class BaseModelMixin(object):
    """
    Enterprise Base Model Mixin providing standard audit timestamps, soft deletion,
    and generic CRUD helper methods across all database tables.
    """

    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    is_deleted = db.Column(db.Boolean, default=False, nullable=False, index=True)
    deleted_at = db.Column(db.DateTime(timezone=True), nullable=True)

    def save(self):
        """Saves current instance to session and commits transaction."""
        db.session.add(self)
        db.session.commit()
        return self

    def delete(self, soft=True):
        """Performs soft deletion by setting is_deleted=True or hard deletion."""
        if soft:
            self.is_deleted = True
            self.deleted_at = datetime.now(timezone.utc)
            db.session.commit()
        else:
            db.session.delete(self)
            db.session.commit()

    @classmethod
    def find_by_id(cls, entity_id: int):
        """Finds non-deleted record by primary key id."""
        return cls.query.filter_by(id=entity_id, is_deleted=False).first()

    @classmethod
    def get_all(cls):
        """Returns all non-deleted records."""
        return cls.query.filter_by(is_deleted=False).all()
