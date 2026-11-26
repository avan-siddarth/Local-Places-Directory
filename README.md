# Local Places Directory — Streamlit

## Run
1. Install Python 3.10+.
2. Open a terminal in this folder.
3. Run `pip install -r requirements.txt`.
4. Run `streamlit run app.py`.

## Demo login
- Username: `admin`
- Password: `admin123`

Change the demo credentials in `app.py` before deployment. This is demonstration authentication, not production-grade security.

## Features
- Login and logout
- Dashboard metrics
- Add places with input validation
- Search by keyword, category and status
- Analytics and category chart
- CSV and JSON export
- Local persistence using `places.json` and `places.csv`

The app initializes sample directory data automatically if the JSON file is missing or invalid.
