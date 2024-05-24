import re
from sqlalchemy import Table, insert, select 
from spreadsheets_app import DATABASE, METADATA
from spreadsheets_app.models import Dependancy, ReverseDependent

LOOKUP_PATTERN = r'LOOKUP\(([^,]+),\s*([^)]+)\)'


def lookup(*, table : Table, sheet_id : int, dest_row_number : int, dest_col: str, lookup_string: str):
    match_pattern = re.match(LOOKUP_PATTERN, lookup_string)
    if not match_pattern:
        raise ValueError(
            "string start with 'LOOKUP' but does not match the pattern 'LOOKUP(col,value)'"
        )
    source_column = match_pattern.group(1).strip()
    row_number_str = match_pattern.group(2).strip()

    try:
        source_row_number = int(row_number_str)
    except ValueError:
        raise ValueError(
            "Given row number in LOOKUP(col,row_number) is not an int."
        )
    
    with DATABASE.engine.connect() as conn:
        # check if row_numer exsits
        select_statement = select(table.c[source_column]).where(table.c.row_number == source_row_number)
        result = conn.execute(select_statement)
        [value] = result.fetchone()
        
    # add to depandency
    save_depandancy(sheet_id,dest_row_number,dest_col,source_row_number,source_column)
    
    # TODO add to reverse depandancy
    
    # TODO remove from depandancy if new set for the cell
    # I can do it with check in depandancy
    
    
    return value
    
    
def save_depandancy(
    sheet_id: int,
    dest_row: int,
    dest_col: str,
    source_row: int,
    source_col: str
):
    depandancy = Dependancy(sheet_id,
        dest_row,
        dest_col,
        source_row,
        source_col)
    
    DATABASE.session.add(depandancy)
    DATABASE.session.commit()
    
    
def check_if_in_depandancy():
    pass
    
    
    
