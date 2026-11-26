import streamlit as st
import json, csv, os
from collections import Counter
from io import StringIO

APP_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_FILE = os.path.join(APP_DIR, "places.json")
CSV_FILE = os.path.join(APP_DIR, "places.csv")
DEMO_USERNAME = "admin"
DEMO_PASSWORD = "admin123"
CATEGORIES = ["Restaurant", "Hospital", "School", "College", "Hotel", "Park", "Shopping", "Transport", "Bank", "Other"]

SAMPLE_PLACES = [
    {"id": 1, "name": "City Central Hospital", "category": "Hospital", "area": "Hyderabad", "address": "Main Road, Hyderabad", "phone": "040-24567890", "status": "Open"},
    {"id": 2, "name": "Green Leaf Restaurant", "category": "Restaurant", "area": "Medchal", "address": "Market Street, Medchal", "phone": "9876500001", "status": "Open"},
    {"id": 3, "name": "Knowledge High School", "category": "School", "area": "Kompally", "address": "Lake View Road, Kompally", "phone": "9876500002", "status": "Open"},
    {"id": 4, "name": "Metro City College", "category": "College", "area": "Miyapur", "address": "College Road, Miyapur", "phone": "9876500003", "status": "Open"},
    {"id": 5, "name": "Sunrise Hotel", "category": "Hotel", "area": "Secunderabad", "address": "Station Road, Secunderabad", "phone": "9876500004", "status": "Open"},
    {"id": 6, "name": "People's Park", "category": "Park", "area": "Alwal", "address": "Green Avenue, Alwal", "phone": "Not available", "status": "Open"},
    {"id": 7, "name": "City Mall", "category": "Shopping", "area": "Kukatpally", "address": "Forum Road, Kukatpally", "phone": "9876500005", "status": "Open"},
    {"id": 8, "name": "RTC Bus Station", "category": "Transport", "area": "Uppal", "address": "Bus Station Road, Uppal", "phone": "040-23456789", "status": "Open"},
    {"id": 9, "name": "State Bank Branch", "category": "Bank", "area": "Bowenpally", "address": "Market Road, Bowenpally", "phone": "040-22334455", "status": "Open"},
    {"id": 10, "name": "Family Care Clinic", "category": "Hospital", "area": "Bachupally", "address": "Doctors Lane, Bachupally", "phone": "9876500006", "status": "Open"}
]

def save_places(places):
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(places, f, indent=4, ensure_ascii=False)
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        fields = ["id", "name", "category", "area", "address", "phone", "status"]
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(places)

def load_places():
    try:
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        pass
    save_places(SAMPLE_PLACES)
    return SAMPLE_PLACES.copy()

def login_page():
    st.markdown("<h1 style='text-align:center;'>📍 Local Places Directory</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'>Please sign in to continue</p>", unsafe_allow_html=True)
    _, center, _ = st.columns([1, 1.3, 1])
    with center:
        with st.container(border=True):
            st.subheader("🔐 Login")
            with st.form("login_form"):
                username = st.text_input("Username", placeholder="Enter username")
                password = st.text_input("Password", type="password", placeholder="Enter password")
                submitted = st.form_submit_button("Login", use_container_width=True)
            if submitted:
                if username == DEMO_USERNAME and password == DEMO_PASSWORD:
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error("Invalid username or password.")
        st.caption("Demo username: admin  |  Password: admin123")

def dashboard(places):
    st.title("📊 Dashboard")
    a, b, c = st.columns(3)
    a.metric("Total Places", len(places))
    b.metric("Categories", len(set(p.get("category") for p in places)))
    c.metric("Open Places", sum(p.get("status") == "Open" for p in places))
    st.subheader("Recently added places")
    st.dataframe(places[-5:][::-1], use_container_width=True, hide_index=True)

def add_place(places):
    st.title("➕ Add a Place")
    with st.form("add_place_form", clear_on_submit=True):
        name = st.text_input("Place name *")
        category = st.selectbox("Category *", CATEGORIES)
        area = st.text_input("Area / locality *")
        address = st.text_area("Full address *")
        phone = st.text_input("Phone number (optional)")
        status = st.selectbox("Status", ["Open", "Closed", "Temporarily Closed"])
        submitted = st.form_submit_button("Save Place", use_container_width=True)
    if submitted:
        errors = []
        for label, value in [("Place name", name), ("Area", area), ("Address", address)]:
            if not value.strip():
                errors.append(f"{label} cannot be blank.")
        if len(name) > 100 or len(area) > 100 or len(address) > 250:
            errors.append("Name and area must be under 100 characters; address under 250.")
        if len(phone) > 20:
            errors.append("Phone number must be under 20 characters.")
        if errors:
            for error in errors: st.error(error)
        else:
            new_id = max((p.get("id", 0) for p in places), default=0) + 1
            places.append({"id": new_id, "name": name.strip(), "category": category,
                           "area": area.strip(), "address": address.strip(),
                           "phone": phone.strip() or "Not available", "status": status})
            save_places(places)
            st.success("Place added successfully.")
            st.rerun()

def search_places(places):
    st.title("🔎 Search Places")
    c1, c2 = st.columns(2)
    keyword = c1.text_input("Search name, area or address")
    category = c2.selectbox("Category", ["All"] + CATEGORIES)
    status = st.selectbox("Status", ["All", "Open", "Closed", "Temporarily Closed"])
    results = []
    for p in places:
        haystack = " ".join(str(p.get(k, "")) for k in ["name", "area", "address", "category"]).lower()
        if keyword.strip().lower() not in haystack: continue
        if category != "All" and p.get("category") != category: continue
        if status != "All" and p.get("status") != status: continue
        results.append(p)
    st.caption(f"{len(results)} result(s) found")
    if results: st.dataframe(results, use_container_width=True, hide_index=True)
    else: st.info("No matching places found.")

def analytics(places):
    st.title("📈 Analytics & Summary")
    if not places:
        st.info("No records available.")
        return
    counts = Counter(p.get("category", "Other") for p in places)
    a, b = st.columns(2)
    a.metric("Total records", len(places))
    b.metric("Open places", sum(p.get("status") == "Open" for p in places))
    st.subheader("Places by category")
    st.bar_chart(counts)
    status_counts = Counter(p.get("status", "Unknown") for p in places)
    st.subheader("Status summary")
    st.dataframe([{"Status": k, "Count": v} for k, v in status_counts.items()],
                 use_container_width=True, hide_index=True)
    top = counts.most_common(1)[0]
    st.success(f"Most represented category: {top[0]} ({top[1]} place(s)).")

def export_data(places):
    st.title("⬇️ Export Data")
    if not places:
        st.info("No records to export.")
        return
    output = StringIO()
    fields = ["id", "name", "category", "area", "address", "phone", "status"]
    writer = csv.DictWriter(output, fieldnames=fields)
    writer.writeheader()
    writer.writerows(places)
    st.download_button("Download CSV report", output.getvalue(),
                       "local_places_directory.csv", "text/csv", use_container_width=True)
    st.download_button("Download JSON backup", json.dumps(places, indent=4),
                       "local_places_directory.json", "application/json", use_container_width=True)

def main():
    st.set_page_config(page_title="Local Places Directory", page_icon="📍", layout="wide")
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if not st.session_state.authenticated:
        login_page()
        return
    places = load_places()
    with st.sidebar:
        st.title("📍 Places Directory")
        st.caption("Signed in as " + st.session_state.get("username", "admin"))
        page = st.radio("Navigation", ["Dashboard", "Add Place", "Search Places", "Analytics", "Export Data"])
        st.divider()
        if st.button("Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.pop("username", None)
            st.rerun()
    if page == "Dashboard": dashboard(places)
    elif page == "Add Place": add_place(places)
    elif page == "Search Places": search_places(places)
    elif page == "Analytics": analytics(places)
    elif page == "Export Data": export_data(places)
    st.divider()
    st.caption("Local Places Directory • Built with Python and Streamlit • Local JSON/CSV storage")

if __name__ == "__main__":
    main()
