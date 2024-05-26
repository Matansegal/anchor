# Anchor

### Build
`docker build -t spreadsheet-app .`
- this will run all the tests

### Run
`docker run -p 5000:5000 spreadsheet-app`

### Requests

- setting something up: `./requests/setting_up` -> this will create two tables, which sheet_1 looks like:
| row_number | A | B | C | D |
| --- | --- | --- | --- | --- |
| 1 | None | 1 | None | None |
| 2 | None | 2 | None | None |
| 3 | None | 3 | None | None |
| 4 | None | 1 | None | None |
| 5 | None | 1 | None | None |
| 6 | None | 1 | None | None |
| 7 | None | 1 | None | None |
| 8 | None | 1 | None | None |

- we have the cyclic depenendent of: 
    - (B,7) -> (B,6) -> (B,5) -> (B,4) -> (B,1) 
    - (B,8) -> (B,1)

You can use the following commands to play arround with it:

1. create sheet: `./requests/create_sheet`
2. set cell: `./requests/set_cell <sheet_id> <column_name> <row_number> <value>`
3. get_sheet: `./requests/get_sheet <sheet_id>`
4. set cell with look up: `./requests/set_cell_with_lookup <sheet_id> <column_name> <row_number> LOOKUP(<column>,<row_number>)`