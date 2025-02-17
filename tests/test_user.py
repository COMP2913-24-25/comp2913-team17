def test_user_page(client):
    response = client.get('/user/')
    assert response.status_code == 200
    assert b'User Page' in response.data

# Add any additional tests below similar to the one above
