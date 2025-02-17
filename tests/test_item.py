def test_item_page(client):
    response = client.get('/item/')
    assert response.status_code == 200
    assert b'Item page' in response.data

# Add any additional tests below similar to the one above
