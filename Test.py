import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

st.set_page_config(page_title="FinFlow AP Suite", page_icon="💰", layout="wide")

USERS = {
    "admin": {"password": "Admin@123", "role": "Admin"},
    "ap_exec": {"password": "AP@123", "role": "AP Executive"},
    "ap_mgr": {"password": "MGR@123", "role": "AP Manager"},
    "finance_head": {"password": "FIN@123", "role": "Finance Head"}
}

conn = sqlite3.connect("ap_database.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS invoices(
id INTEGER PRIMARY KEY AUTOINCREMENT,
invoice_no TEXT,
vendor_name TEXT,
invoice_date TEXT,
amount REAL,
status TEXT,
approval_status TEXT,
uploaded_by TEXT,
upload_date TEXT
)
""")
conn.commit()

def get_df():
    return pd.read_sql_query("SELECT * FROM invoices", conn)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("💰 FinFlow AP Suite")
    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")
    if st.button("Login"):
        if user in USERS and USERS[user]["password"] == pwd:
            st.session_state.logged_in = True
            st.session_state.user = user
            st.session_state.role = USERS[user]["role"]
            st.rerun()
        else:
            st.error("Invalid credentials")
    st.stop()

st.sidebar.success(f"{st.session_state.user} ({st.session_state.role})")

menu = st.sidebar.radio("Menu",
["Dashboard","Upload Invoice","Repository"])

if menu == "Dashboard":
    st.title("Dashboard")
    df = get_df()
    c1,c2 = st.columns(2)
    c1.metric("Invoices", len(df))
    c2.metric("Amount", f"₹ {df['amount'].sum() if not df.empty else 0:,.0f}")
    if not df.empty:
        st.bar_chart(df.groupby("vendor_name")["amount"].sum())

elif menu == "Upload Invoice":
    st.title("Upload Invoice")
    with st.form("f"):
        inv = st.text_input("Invoice No")
        vendor = st.text_input("Vendor")
        dt = st.date_input("Date")
        amt = st.number_input("Amount", min_value=0.0)
        if st.form_submit_button("Save"):
            c.execute("""INSERT INTO invoices
            (invoice_no,vendor_name,invoice_date,amount,status,approval_status,uploaded_by,upload_date)
            VALUES (?,?,?,?,?,?,?,?)""",
            (inv,vendor,str(dt),amt,"Pending Payment","Pending Approval",
             st.session_state.user,datetime.now().strftime("%Y-%m-%d %H:%M")))
            conn.commit()
            st.success("Saved")

else:
    st.title("Repository")
    st.dataframe(get_df(), use_container_width=True)
