def test_home_page(client):
    response = client.get('/home/')
    assert response.status_code == 200
    assert b'Home Page' in response.data

# Add any additional tests below similar to the one above