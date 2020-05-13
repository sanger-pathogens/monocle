from juno.database import Column, Model, db

class UserModel(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(256), unique=True, nullable=False)
    first_name = db.Column(db.String(256), nullable=False)
    last_name = db.Column(db.String(256), nullable=False)

    def __repr__(self):
        return '<User %r>' % self.email

class SampleModel(db.Model):
    __tablename__ = 'sample'
    id = db.Column(db.Integer, primary_key=True)
    lane_id = db.Column(db.String(256), unique=True, nullable=False)
    sample_id = db.Column(db.String(256), unique=True, nullable=False)
    public_name = db.Column(db.String(256), nullable=True)
    submitting_institution = db.Column(db.String(256), nullable=False)

    def __repr__(self):
        return '<Sample %r>' % self.lane_id
