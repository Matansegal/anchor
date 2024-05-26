from typing import List, Any
from sqlalchemy import Table, Column, Integer, Boolean, Float, String, select
from spreadsheets_app import DATABASE, METADATA
from spreadsheets_app.models import SheetsMetaData

TYPE_MAPPING = {
    "boolean": Boolean,
    "int": Integer,
    "double": Float,
    "string": String,
}


def create_table(sheet_id: int, columns: List[Column]):
    # dynamically create the table
    table_name = f"sheet_{sheet_id}"
    table = Table(table_name, METADATA, *columns)
    METADATA.create_all(DATABASE.engine, tables=[table])


def set_columns_list(schema_columns: List[dict]) -> List[Column]:
    columns = [Column("row_number", Integer, primary_key=True)]
    for col in schema_columns:
        columns.append(Column(col["name"], get_column_type(col["type"]), nullable=True))
    return columns


def get_column_type(column_type: str) -> Any:
    try:
        return TYPE_MAPPING[column_type]
    except KeyError as err:
        raise RuntimeError(f"column type is unrecognized: {err}")


def save_metadata(columns: List[Column]) -> int:
    sheet = SheetsMetaData(columns)
    DATABASE.session.add(sheet)
    DATABASE.session.commit()
    return sheet.id


def get_sheet(sheet_id: int) -> Table:
    table_name = f"sheet_{sheet_id}"
    return Table(table_name, METADATA, autoload_with=DATABASE.engine)


def select_all_from_sheet(table: Table) -> List:
    with DATABASE.engine.connect() as conn:
        # get the whole sheet order by row number
        select_statement = select(table).order_by("row_number")
        return conn.execute(select_statement).fetchall()
