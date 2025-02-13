def test_bidding_page(client):
    response = client.get('/bidding/')
    assert response.status_code == 200
    assert b'Bidding page' in response.data

# Add any additional tests below similar to the one above