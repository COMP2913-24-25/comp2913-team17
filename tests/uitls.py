from main.models import User, Item

def register_user(client, email, password, name="Test User"):
    """Helper function to register a user"""
    return client.post('/auth/register', data={
        'email': email,
        'name': name,
        'password': password,
        'password2': password
    }, follow_redirects=True)

def login_user(client, email, password):
    """Helper function to login a user"""
    return client.post('/auth/login', data={
        'email': email,
        'password': password
    }, follow_redirects=True)

def logout_user(client):
    """Helper function to logout a user"""
    return client.get('/auth/logout', follow_redirects=True)

def create_item(title, description, starting_price, auction_end, seller_id):
    """Helper function to create an auction item"""
    item = Item(
        title=title,
        description=description,
        starting_price=starting_price,
        auction_end=auction_end,
        seller_id=seller_id
    )
    from main import db
    db.session.add(item)
    db.session.commit()
    return item