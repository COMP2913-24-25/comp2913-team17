import pytest
from app import app, db
from models import Expert, ItemAssignment

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

def test_assign_expert(client):
    """Test assigning an expert to an item"""
    with app.app_context():
        expert = Expert(name='John Doe', expertise_category='Antiques')
        db.session.add(expert)
        db.session.commit()

    response = client.post('/allocate_expert/assign-expert', json={'item_id': 1, 'category': 'Antiques'})

    assert response.status_code == 200
    assert b'Item 1 assigned to expert John Doe' in response.data
