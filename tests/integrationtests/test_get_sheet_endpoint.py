def test_get_sheet_endpoint_success(client):
    reqiest_create_sheet = {
        "columns": [
            {"name": "col1", "type": "string"},
            {"name": "col2", "type": "int"},
            {"name": "col3", "type": "double"},
            {"name": "col4", "type": "boolean"},
        ]
    }

    # Send a POST request to the createSheet endpoint
    create_sheet_response = client.post(
        "/sheet/createSheet", json=reqiest_create_sheet, content_type="application/json"
    )

    assert create_sheet_response.status_code == 201
    sheet_id = create_sheet_response.get_json()["sheetId"]

    request_set_cell = {
        "sheet_id": sheet_id,
        "column_name": "col2",
        "row_number": 1,
        "value": 10,
    }

    response_set_cell1 = client.post(
        "/sheet/setCell", json=request_set_cell, content_type="application/json"
    )

    assert response_set_cell1.status_code == 201

    request_set_cell = {
        "sheet_id": sheet_id,
        "column_name": "col1",
        "row_number": 2,
        "value": "matan",
    }

    response_set_cell2 = client.post(
        "/sheet/setCell", json=request_set_cell, content_type="application/json"
    )

    assert response_set_cell2.status_code == 201

    response_get_sheet = client.get(
        f"/sheet/{sheet_id}", content_type="application/json"
    )

    expected_result = {
        "sheet_1": [
            {"col1": None, "col2": 10, "col3": None, "col4": None, "row_number": 1},
            {
                "col1": "matan",
                "col2": None,
                "col3": None,
                "col4": None,
                "row_number": 2,
            },
        ]
    }

    assert response_get_sheet.status_code == 201
    assert response_get_sheet.get_json() == expected_result



