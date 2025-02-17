def test_home_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Home page' in response.data

# Add any additional tests below similar to the one above
