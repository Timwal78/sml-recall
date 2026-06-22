from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()

class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(255), unique=True, nullable=False, index=True)
    tier = db.Column(db.String(50), nullable=False)
    generated_key = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(50), default='pending') # pending, paid, fulfilled
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    fulfilled_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f"<Payment {self.session_id} - {self.status}>"
