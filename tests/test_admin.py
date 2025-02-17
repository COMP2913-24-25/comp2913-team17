def test_admin_page(client):
    response = client.get('/admin/')
    assert response.status_code == 200
    assert b'Admin page' in response.data

# Add any additional tests below similar to the one above
