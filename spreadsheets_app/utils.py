from sqlalchemy import Table

# type decorator for strict type checking
# I need it since I dont have sqlite>=3.37 where they have the STRICT operator,
# and it looks like sqlalchemy dont support it yet.
# more info https://github.com/sqlalchemy/sqlalchemy/issues/7398
def strict_types(row : dict, table : Table):
    for col_name, value in row.items():
        col_type = table.c[col_name].type.python_type
        if not isinstance(value, col_type):
            raise ValueError(
                f"Invalid value '{value}' for column '{col_name}'. Must be of type {col_type}."
            )