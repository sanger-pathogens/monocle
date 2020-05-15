from juno.database import db


class AffiliationModel(db.Model):
    __tablename__ = "affiliation"
    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(256), db.ForeignKey("user.email"))
    institution_name = db.Column(
        db.String(256), db.ForeignKey("institution.name")
    )

    user = db.relationship(
        "UserModel",
        backref=db.backref("affiliation", cascade="all, delete-orphan"),
    )
    institution = db.relationship(
        "InstitutionModel",
        backref=db.backref("affiliation", cascade="all, delete-orphan"),
    )

    def __repr__(self):
        return "<Affiliation %r>" % self.id


class UserModel(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(256), unique=True, nullable=False)
    first_name = db.Column(db.String(256), nullable=False)
    last_name = db.Column(db.String(256), nullable=False)

    affiliated_institutions = db.relationship(
        "InstitutionModel", secondary="affiliation"
    )

    def __repr__(self):
        return "<User %r>" % self.email


class InstitutionModel(db.Model):
    __tablename__ = "institution"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), unique=True, nullable=False)
    country = db.Column(db.String(256), unique=True, nullable=False)
    submitted_samples = db.relationship("SampleModel")

    affiliated_members = db.relationship("UserModel", secondary="affiliation")

    def __repr__(self):
        return "<Institution %r>" % self.name


class SampleModel(db.Model):
    __tablename__ = "sample"
    id = db.Column(db.Integer, primary_key=True)
    lane_id = db.Column(db.String(256), unique=True, nullable=False)
    sample_id = db.Column(db.String(256), unique=True, nullable=False)
    public_name = db.Column(db.String(256), nullable=True)
    submitting_institution_name = db.Column(
        db.String(256), db.ForeignKey("institution.name")
    )
    submitting_institution = db.relationship(
        "InstitutionModel", back_populates="submitted_samples"
    )

    def __repr__(self):
        return "<Sample %r>" % self.lane_id
