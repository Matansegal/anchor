# Anchor

### Build
`docker build -t spreadsheet-app .`
- this will run all the tests

### Run
`docker run -p 5000:5000 spreadsheet-app`

1. create sheet: `./requests/create_sheet`
2. set cell: `./requests/set_cell`
3. get_sheet: `./requests/get_sheet`
4. set cell with look up: `./requests/set_cell_with_lookup`