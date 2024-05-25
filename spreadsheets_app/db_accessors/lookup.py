import re
from sqlalchemy import Table, select
from sqlalchemy.exc import IntegrityError
from spreadsheets_app import DATABASE
from spreadsheets_app.models import Dependancy, ReverseDependent

LOOKUP_PATTERN = r"LOOKUP\(([^,]+),\s*([^)]+)\)"


def lookup(
    *,
    table: Table,
    sheet_id: int,
    dest_row_number: int,
    dest_col: str,
    lookup_string: str
):
    match_pattern = re.match(LOOKUP_PATTERN, lookup_string)
    if not match_pattern:
        raise ValueError(
            "string start with 'LOOKUP' but does not match the pattern 'LOOKUP(col,value)'."
        )
    source_column = match_pattern.group(1).strip()
    row_number_str = match_pattern.group(2).strip()

    try:
        source_row_number = int(row_number_str)
    except ValueError:
        raise ValueError("Given row number in LOOKUP(col,row_number) is not an int.")

    # get the value from the source
    value = get_lookup_value(table, source_row_number, source_column)
    
    breakpoint()
    # add to dependency
    try:
        add_dependency(
            sheet_id, dest_row_number, dest_col, source_row_number, source_column
        )
    except IntegrityError as err:
        raise ValueError("Dependency already exist")
    

    # TODO change all dependents if source is changed
    # do that recursively for dependants of depandants

    
    return value

def get_lookup_value(table: Table, source_row_number : int, source_column : str):
    with DATABASE.engine.connect() as conn:
        # TODO handle if value do not exsits
        select_statement = select(table.c[source_column]).where(
            table.c.row_number == source_row_number
        )
        result = conn.execute(select_statement)
        [value] = result.fetchone()
        return value


def get_dependency_row(sheet_id: int, dest_row: int, dest_col: str) -> Dependancy:
    return (
        DATABASE.session.query(Dependancy)
        .filter(
            Dependancy.sheet_id == sheet_id,
            Dependancy.dest_row == dest_row,
            Dependancy.dest_col == dest_col,
        )
        .first()
    )


def add_dependency(
    sheet_id: int, dest_row: int, dest_col: str, source_row: int, source_col: str
):
    # check if exsits
    dependency = get_dependency_row(sheet_id, dest_row, dest_col)
    
    if dependency:
        if dependency.source_row == source_row and dependency.source_col == source_col:
            # stay the same
            return
        
        # remove from reverse depenpent table
        old_source_row = dependency.source_row
        old_source_col = dependency.source_col
        remove_from_reverse_dependency(sheet_id,dest_row,dest_col,old_source_row,old_source_col)
        
        # update row
        dependency.source_row = source_row
        dependency.source_col = source_col
        
    
    else:
        new_dependency = Dependancy(sheet_id, dest_row, dest_col, source_row, source_col)
        DATABASE.session.add(new_dependency)
    
    # in both cases, commit
    DATABASE.session.commit()
    
    # in both cases add to reverse dependancy
    add_reverse_dependency(sheet_id, dest_row, dest_col, source_row, source_col)
  
    
def remove_dependency(sheet_id: int, dest_row: int, dest_col: str):
    dependency = get_dependency_row(sheet_id, dest_row, dest_col)
    if dependency:
        remove_from_reverse_dependency(sheet_id, dest_row, dest_col, dependency.source_row, dependency.source_col)
        DATABASE.session.delete(dependency)
        DATABASE.session.commit()


def get_reverse_dependency_row(sheet_id: int, source_row: int, source_col: str):
    return (
        DATABASE.session.query(ReverseDependent)
        .filter(
            ReverseDependent.sheet_id == sheet_id,
            ReverseDependent.source_row == source_row,
            ReverseDependent.source_col == source_col,
        )
        .first()
    )
    

def remove_from_reverse_dependency(sheet_id: int, dest_row: int, dest_col: str, old_source_row: int, old_source_col: str):
    reverse_dependent_row = get_reverse_dependency_row(sheet_id,old_source_row,old_source_col)
    # shouls always get into this if
    if reverse_dependent_row:
        # json in the database save all as string
        dest_row = str(dest_row)
        # update the dependent json
        if dest_row in reverse_dependent_row.dependents:
            cols_list = reverse_dependent_row.dependents[dest_row]
            try:
                cols_list.remove(dest_col)
            except ValueError:
                # dest col not in the list, which should not happen
                return
            
            # if list empty, remove this key
            if len(cols_list) == 0:
                del reverse_dependent_row.dependents[dest_row]
                # if dict empty remove row
                if len(reverse_dependent_row.dependents) == 0:
                    DATABASE.session.delete(reverse_dependent_row)
    
            DATABASE.session.commit()


def add_reverse_dependency(sheet_id: int, dest_row: int, dest_col: str, source_row: int, source_col: str):

    reverse_dependent = get_reverse_dependency_row(sheet_id,source_row,source_col)
    
    if reverse_dependent:
        # json in the database save all as string
        dest_row = str(dest_row)
        # update the dependent json
        if dest_row in reverse_dependent.dependents:
            # prevent duplicity
            if dest_col not in reverse_dependent.dependents[dest_row]:
                reverse_dependent.dependents[dest_row].append(dest_col)
        else:
            reverse_dependent.dependents[dest_row] = [dest_col]
    
    else:
        # if not exsits, add new row
        dependents = {dest_row : [dest_col]}
        rerverse_dependent = ReverseDependent(
            sheet_id,
            source_row,
            source_col,
            dependents
        )
        DATABASE.session.add(rerverse_dependent)
        
    # commit in both cases
    DATABASE.session.commit()


def check_if_in_dependency():
    pass
