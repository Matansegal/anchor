def test_create_sheet_endpoint_success(client):
    request_data = {
        "columns": [
            {"name": "col1", "type": "string"},
            {"name": "col2", "type": "int"},
            {"name": "col3", "type": "double"},
            {"name": "col4", "type": "boolean"},
        ]
    }

    # Send a POST request to the createSheet endpoint
    response = client.post(
        "/sheet/createSheet", json=request_data, content_type="application/json"
    )

    # verify response
    assert response.status_code == 201
    assert response.get_json() == {"sheetId": 1}

    # send again
    response = client.post(
        "/sheet/createSheet", json=request_data, content_type="application/json"
    )

    # verify response
    assert response.status_code == 201
    assert response.get_json() == {"sheetId": 2}


def test_create_sheet_endpoint_invalid_schema(client):

    # empty schema
    response = client.post(
        "/sheet/createSheet", json={}, content_type="application/json"
    )

    # verify response
    assert response.status_code == 400
    assert response.data.decode("utf-8") == "Invalid schema"

    # no type schema

    request = {"columns": [{"name": "int"}]}
    response = client.post(
        "/sheet/createSheet", json=request, content_type="application/json"
    )

    assert response.status_code == 400
    assert "Column should have `name` and `type`." in response.data.decode("utf-8")
