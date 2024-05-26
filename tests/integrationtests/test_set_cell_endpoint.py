from tests.utils import get_cell_from_database


def test_set_cell_endpoint_success(client):
    # setting up sheet
    new_sheet_json = {
        "columns": [
            {"name": "col1", "type": "string"},
            {"name": "col2", "type": "int"},
            {"name": "col3", "type": "double"},
            {"name": "col4", "type": "boolean"},
        ]
    }

    # Send a POST request to the createSheet endpoint
    response = client.post(
        "/sheet/createSheet", json=new_sheet_json, content_type="application/json"
    )
    sheet_id = response.get_json()["sheetId"]

    request = {
        "sheet_id": sheet_id,
        "column_name": "col2",
        "row_number": 1,
        "value": 10,
    }

    response = client.post(
        "/sheet/setCell", json=request, content_type="application/json"
    )

    # verify response
    assert response.status_code == 201
    assert response.data.decode("utf-8") == ""
    result = get_cell_from_database(sheet_id, "col2", 1)
    assert result == 10

    # LOOKUP request
    request = {
        "sheet_id": sheet_id,
        "column_name": "col2",
        "row_number": 2,
        "value": "LOOKUP(col2,1)",
    }

    response = client.post(
        "/sheet/setCell", json=request, content_type="application/json"
    )

    assert response.status_code == 201
    assert response.data.decode("utf-8") == ""
    result_row_2 = get_cell_from_database(sheet_id, "col2", 2)
    result_row_1 = get_cell_from_database(sheet_id, "col2", 1)
    assert result_row_2 == result_row_1 == 10


def test_set_cell_endpoint_invalid(client):
    # setting up sheet
    new_sheet_json = {
        "columns": [
            {"name": "col1", "type": "string"},
            {"name": "col2", "type": "int"},
            {"name": "col3", "type": "double"},
            {"name": "col4", "type": "boolean"},
        ]
    }

    response = client.post(
        "/sheet/createSheet", json=new_sheet_json, content_type="application/json"
    )
    sheet_id = response.get_json()["sheetId"]

    request_wrong_type = {
        "sheet_id": sheet_id,
        "column_name": "col2",
        "row_number": 1,
        "value": "invalid_value",
    }

    # wrong type to cell
    response = client.post(
        "/sheet/setCell", json=request_wrong_type, content_type="application/json"
    )

    # verify response
    assert response.status_code == 400
    assert "Invalid value" in response.data.decode("utf-8")

    # wrong pattern to lookup
    request_wrong_lookup = {
        "sheet_id": sheet_id,
        "column_name": "col2",
        "row_number": 1,
        "value": "LOOKUP(col2)",
    }

    response = client.post(
        "/sheet/setCell", json=request_wrong_lookup, content_type="application/json"
    )

    assert response.status_code == 400
    assert (
        "string starts with 'LOOKUP' but does not match the pattern"
        in response.data.decode("utf-8")
    )
