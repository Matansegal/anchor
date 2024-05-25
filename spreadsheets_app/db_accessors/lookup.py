import re
from typing import Any
from sqlalchemy import Table, select
from sqlalchemy.exc import IntegrityError
from spreadsheets_app import DATABASE
from spreadsheets_app.models import Dependancy, ReverseDependent
from spreadsheets_app.db_accessors.cell import update_cell

LOOKUP_PATTERN = r"LOOKUP\(([^,]+),\s*([^)]+)\)"


def lookup(
    *,
    table: Table,
    sheet_id: int,
    dest_row_number: int,
    dest_col: str,
    lookup_string: str,
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

    if cyclic_path := CyclicDependents(sheet_id, dest_row_number, dest_col).is_cyclic(
        source_row_number, source_column
    ):
        cyclic_path_str = " -> ".join(cyclic_path)
        origin_cell = f"({dest_row_number},{dest_col})(given) -> "
        raise ValueError(f"the given LOOKUP call creates a cyclic path\n{origin_cell}{cyclic_path_str}")

    # get the value from the source
    value = get_lookup_value(table, source_row_number, source_column)

    # TODO make sure it is same type before insert

    add_dependency(
        sheet_id, dest_row_number, dest_col, source_row_number, source_column
    )

    return value


def get_lookup_value(table: Table, source_row_number: int, source_column: str):
    with DATABASE.engine.connect() as conn:
        # TODO handle if value do not exsits
        select_statement = select(table.c[source_column]).where(
            table.c.row_number == source_row_number
        )
        result = conn.execute(select_statement)
        [value] = result.fetchone()
        return value


def reverse_dependent(sheet_id: int, dest_row: int, dest_col: str) -> Dependancy:
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
    dependency = reverse_dependent(sheet_id, dest_row, dest_col)

    # breakpoint()

    if dependency:
        if dependency.source_row == source_row and dependency.source_col == source_col:
            # stay the same
            return

        # remove from reverse depenpent table
        old_source_row = dependency.source_row
        old_source_col = dependency.source_col
        remove_from_reverse_dependency(
            sheet_id, dest_row, dest_col, old_source_row, old_source_col
        )

        # update row
        dependency.source_row = source_row
        dependency.source_col = source_col

    else:
        new_dependency = Dependancy(
            sheet_id, dest_row, dest_col, source_row, source_col
        )
        DATABASE.session.add(new_dependency)

    # in both cases, commit
    DATABASE.session.commit()

    # in both cases add to reverse dependancy
    add_reverse_dependency(sheet_id, dest_row, dest_col, source_row, source_col)


def remove_dependency(sheet_id: int, dest_row: int, dest_col: str):
    dependency = reverse_dependent(sheet_id, dest_row, dest_col)
    if dependency:
        remove_from_reverse_dependency(
            sheet_id, dest_row, dest_col, dependency.source_row, dependency.source_col
        )
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


def remove_from_reverse_dependency(
    sheet_id: int,
    dest_row: int,
    dest_col: str,
    old_source_row: int,
    old_source_col: str,
):
    reverse_dependent_row = get_reverse_dependency_row(
        sheet_id, old_source_row, old_source_col
    )
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


def add_reverse_dependency(
    sheet_id: int, dest_row: int, dest_col: str, source_row: int, source_col: str
):

    reverse_dependent = get_reverse_dependency_row(sheet_id, source_row, source_col)

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
        dependents = {dest_row: [dest_col]}
        rerverse_dependent = ReverseDependent(
            sheet_id, source_row, source_col, dependents
        )
        DATABASE.session.add(rerverse_dependent)

    # commit in both cases
    DATABASE.session.commit()


def backtracking(
    sheet: Table, sheet_id: int, source_row: int, source_col: str, value: Any
):
    """
    When we udpate a value of a cell which multiple cell depends on we would go over all
    the dependents and their dependents to update them
    """

    reverse_dependent_row = get_reverse_dependency_row(sheet_id, source_row, source_col)
    # loop over all dependents
    if reverse_dependent_row:
        for (
            dependent_row,
            dependent_col_list,
        ) in reverse_dependent_row.dependents.items():
            # json in the database save all as string
            dependent_row = int(dependent_row)
            for dependent_col in dependent_col_list:
                # update current cell value
                update_cell(sheet, dependent_row, dependent_col, value)
                # go to this cell dependents
                backtracking(sheet, sheet_id, dependent_row, dependent_col, value)


class CyclicDependents:
    def __init__(self, sheet_id: int, dest_row: int, dest_col: str):
        self.sheet_id = sheet_id
        self.new_dest = (dest_row, dest_col)
        self.cyclic_path = []

    def is_cyclic(self, source_row, source_col):
        
        self.cyclic_path.append(f"({source_row}, {source_col})")
        
        if self.new_dest == (source_row, source_col):
            # find cyclic, return the path
            return self.cyclic_path
        
        # get source depenency
        source_dependancy = reverse_dependent(
            self.sheet_id, source_row, source_col
        )
        
        if source_dependancy:            
            return self.is_cyclic(source_dependancy.source_row, source_dependancy.source_col)
    
