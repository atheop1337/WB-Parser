# WildBerries Parser

This Python script is a fork of another repository, where bugs have been fixed and the code made fully functional. It scrapes item information from Wildberries.ru and stores it in an Excel file. It supports parsing by directory or search keyword and gathers data such as link, ID, name, brand, pricing, rating, reviews, and sales. Ideal for market research and analysis.



## Original Repository

This project is a fork of [kirillignatyev/wildberries-parser-in-python](https://github.com/kirillignatyev/wildberries-parser-in-python), which served as the foundation for this improved version. Thanks :)

## Usage

1. Clone the repository.
2. Install the required dependencies using `pip install -r requirements.txt`.
3. Run the script `wildberries_parser.py`.
4. Follow the instructions to choose the parsing mode:
   - Enter `1` to parse a category.
   - Enter `2` to parse by keyword search.
5. Follow the prompts and input the required information.
6. The script will generate an Excel file with the scraped data.

## Examples
To parse a specific category:
- Choose the parsing mode for a category.
- Enter the category name or URL.
- The script will retrieve all products in the category, collect sales data, and save the parsed data to an xlsx file.

To parse by keywords:
- Choose the parsing mode for keywords.
- Enter the search query.
- The script will retrieve all products in the search results, collect sales data, and save the parsed data to an xlsx file.

## Dependencies

- `pandas`: For data manipulation and storage.
- `requests`: For making HTTP requests to Wildberries API.
- `openpyxl`: For reading/writing .xlsx

## License
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

This project is licensed under the MIT License. Contributions are welcome.

## Disclaimer

This script is for educational purposes only. Use responsibly and ensure compliance with Wildberries' terms of service.
