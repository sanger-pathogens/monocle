"""Model unit tests."""

import pytest

from juno.graphql.models import UserModel, InstitutionModel


@pytest.mark.usefixtures('db')
class TestUserModel:
    """UserModel tests."""

    def test_can_get_by_email(self, db):
        """Get user by email."""
        user = UserModel(email='gollum@misty-mountains.com', first_name='Smeagol', last_name='Deagol')
        
        db.session.add(user)
        db.session.commit()

        retrieved = UserModel.query.filter_by(email=user.email).first()
        assert retrieved == user


@pytest.mark.usefixtures('db')
class TestInstitutionModel:
    """InstitutionModel tests."""

    def test_can_get_by_name(self, db):
        """Get institution by name."""
        institution = InstitutionModel(name='Fellowship of the Ring', country='Middle Earth')
        
        db.session.add(institution)
        db.session.commit()

        retrieved = InstitutionModel.query.filter_by(name=institution.name).first()
        assert retrieved == institution
        