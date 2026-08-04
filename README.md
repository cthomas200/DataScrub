# DataScrub
An AI-powered data cleaning and validation web app built with Python and Streamlit. 

## Features 

* **Multi-format Support** - Accepts CSV, Excel (.xlsx), and JSON files.
* **Automated Issue Detection** - Scans for missing values, duplicates, data type mismatches, outliers, and formatting inconsistencies 
* **AI-Suggested Fixes** - Uses Claude API to generate fix recommendations with risk analysis (low/medium/high)
* **Human Approval** - Users review and approve each fix before anything is applied.
* **Before & After Comparison** - Side-by-side view of the original vs. cleaned dataset
* **Cleaned File Export** - Users can export their cleaned dataset in JSON, CSV, and XLSX format
* **Multi-Export Support** - Download cleaned data as CSV, JSON, or Excel 

## Tech Stack 

- Python, Streamlit, Pandas, Numpy
- Anthropic Claude API
- openpyxl, xlsxwriter

## Getting Started

1. Clone the repo
2. Create a '.env' file in the project root and add your Anthropic API key: ANTHROPIC_API_KEY = sk-ant-XXXXXXXXXXX
3. Install dependencies: Run pip install -r requirements.txt in the terminal 
4. Run the app: streamlit run app.py.

## Structure 

dataScrub/
|---app.py
|---core/
| |--loader.py
| |--ai_advisor.py
| |--cleaner.py
| |--analyzer.py
|---requirements.py
|---.env

## Notes
Anthropic API Key is required: get one at console.anthropic.com (lowest tier is $5)
Outlier detection uses IQR method - may produce wide bounds (ex: scores out of 100)
