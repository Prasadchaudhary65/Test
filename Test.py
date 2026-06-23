import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

st.set_page_config(page_title="FinFlow AP Suite", page_icon="💰", layout="wide")

st.markdown("""
<style>
.main {background-color:#f4f7fb;}
div[data-testid="metric-container"]{
background:white;padding:10px;border-radius:10px;border-left:5px solid #0d6efd;
}
h1,h2,h3 {color:#12395b;}
</style>
""", unsafe_allow_html=True)

USERS = {
    "admin":{"password":"Admin@123","role":"Admin"},
    "ap_exec":{"password":"AP@123","role":"AP Executive"},
    "ap_mgr":{"password":"MGR@123","role":"AP Manager"},
    "finance_head":{"password":"FIN@123","role":"Finance Head"}
}

conn = sqlite3.connect("ap_database.db",check_same_thread=False)
c = conn.cursor()

c.execute("""CREATE TABLE IF NOT EXISTS invoices(
id INTEGER PRIMARY KEY AUTOINCREMENT,
invoice_no TEXT,
vendor_name TEXT,
invoice_date TEXT,
amount REAL,
po_number TEXT,
status TEXT,
approval_status TEXT,
uploaded_by TEXT,
upload_date TEXT,
comments TEXT)""")

c.execute("""CREATE TABLE IF NOT EXISTS audit_log(
id INTEGER PRIMARY KEY AUTOINCREMENT,
action TEXT,
user_name TEXT,
action_date TEXT)""")

conn.commit()

def audit(action,user):
    c.execute("INSERT INTO audit_log(action,user_name,action_date) VALUES(?,?,?)",
              (action,user,datetime.now().strftime("%Y-%m-%d %H:%M")))
    conn.commit()

def invoices():
    return pd.read_sql_query("select * from invoices",conn)

def logs():
    return pd.read_sql_query("select * from audit_log",conn)

if "login" not in st.session_state:
    st.session_state.login=False

if not st.session_state.login:
    st.title("💰 FinFlow AP Suite")
    st.subheader("Enterprise Accounts Payable Platform")

    u=st.text_input("Username")
    p=st.text_input("Password",type="password")

    if st.button("Login"):
        if u in USERS and USERS[u]["password"]==p:
            st.session_state.login=True
            st.session_state.user=u
            st.session_state.role=USERS[u]["role"]
            st.rerun()
        else:
            st.error("Invalid Credentials")
    st.stop()

st.sidebar.success(f"{st.session_state.user}")
st.sidebar.info(st.session_state.role)

menu=st.sidebar.radio("Navigation",[
"Dashboard",
"Upload Invoice",
"Invoice Repository",
"Approval Workflow",
"Payment Processing",
"Risk Dashboard",
"Analytics",
"Audit Trail"
])

df=invoices()

if menu=="Dashboard":
    st.title("Dashboard")

    total=len(df)
    amount=df["amount"].sum() if not df.empty else 0

    pending=len(df[df["approval_status"]=="Pending Approval"]) if not df.empty else 0
    paid=len(df[df["status"]=="Paid"]) if not df.empty else 0

    c1,c2,c3,c4=st.columns(4)
    c1.metric("Invoices",total)
    c2.metric("Amount",f"₹ {amount:,.0f}")
    c3.metric("Pending Approval",pending)
    c4.metric("Paid",paid)

    if not df.empty:
        st.subheader("Vendor Spend")
        st.bar_chart(df.groupby("vendor_name")["amount"].sum())

        st.subheader("Invoice Data")
        st.dataframe(df,use_container_width=True)

elif menu=="Upload Invoice":

    st.title("Upload Invoice")

    with st.form("inv"):

        invoice_no=st.text_input("Invoice Number")
        vendor=st.text_input("Vendor Name")
        invoice_date=st.date_input("Invoice Date")
        amount=st.number_input("Amount",min_value=0.0)
        po=st.text_input("PO Number")
        comments=st.text_area("Comments")
        pdf=st.file_uploader("Invoice PDF",type=["pdf"])

        submit=st.form_submit_button("Submit")

        if submit:

            dup=c.execute("select * from invoices where invoice_no=?",(invoice_no,)).fetchone()

            if dup:
                st.error("Duplicate Invoice")
            else:
                c.execute("""insert into invoices
                (invoice_no,vendor_name,invoice_date,amount,po_number,status,
                approval_status,uploaded_by,upload_date,comments)
                values(?,?,?,?,?,?,?,?,?,?)""",
                (
                    invoice_no,vendor,str(invoice_date),amount,po,
                    "Pending Payment","Pending Approval",
                    st.session_state.user,
                    datetime.now().strftime("%Y-%m-%d %H:%M"),
                    comments
                ))
                conn.commit()

                audit(f"Uploaded {invoice_no}",st.session_state.user)
                st.success("Invoice Uploaded")

elif menu=="Invoice Repository":

    st.title("Invoice Repository")

    search=st.text_input("Search")

    temp=df.copy()

    if search and not temp.empty:
        temp=temp[
            temp["invoice_no"].astype(str).str.contains(search,case=False)
            |
            temp["vendor_name"].astype(str).str.contains(search,case=False)
        ]

    st.dataframe(temp,use_container_width=True)

    csv=temp.to_csv(index=False)

    st.download_button(
        "Export CSV",
        csv,
        "invoice_repository.csv"
    )

elif menu=="Approval Workflow":

    st.title("Approval Workflow")

    pending=df[df["approval_status"]=="Pending Approval"] if not df.empty else pd.DataFrame()

    st.dataframe(pending,use_container_width=True)

    if st.session_state.role not in ["Admin","AP Manager"]:
        st.warning("Only AP Manager/Admin can approve.")
    else:
        inv=st.number_input("Invoice ID",step=1)

        c1,c2=st.columns(2)

        if c1.button("Approve"):
            c.execute("update invoices set approval_status='Approved' where id=?",(int(inv),))
            conn.commit()
            audit(f"Approved invoice {inv}",st.session_state.user)
            st.success("Approved")

        if c2.button("Reject"):
            c.execute("update invoices set approval_status='Rejected' where id=?",(int(inv),))
            conn.commit()
            audit(f"Rejected invoice {inv}",st.session_state.user)
            st.error("Rejected")

elif menu=="Payment Processing":

    st.title("Payment Processing")

    approved=df[df["approval_status"]=="Approved"] if not df.empty else pd.DataFrame()

    st.dataframe(approved,use_container_width=True)

    if st.session_state.role not in ["Admin","Finance Head"]:
        st.warning("Only Finance Head/Admin can release payment.")
    else:
        inv=st.number_input("Approved Invoice ID",step=1)

        if st.button("Mark Paid"):
            c.execute("update invoices set status='Paid' where id=?",(int(inv),))
            conn.commit()
            audit(f"Paid invoice {inv}",st.session_state.user)
            st.success("Payment Released")

elif menu=="Risk Dashboard":

    st.title("Risk Dashboard")

    duplicate_count=0

    if not df.empty:
        duplicate_count=df.duplicated(subset=["invoice_no"]).sum()

    high_value=len(df[df["amount"]>500000]) if not df.empty else 0

    missing_po=len(df[df["po_number"].isna()]) if not df.empty else 0

    c1,c2,c3=st.columns(3)

    c1.metric("Duplicate Invoices",duplicate_count)
    c2.metric("High Value Invoices",high_value)
    c3.metric("Missing PO",missing_po)

elif menu=="Analytics":

    st.title("Analytics")

    if not df.empty:

        st.subheader("Top Vendors")

        vendor=df.groupby("vendor_name")["amount"].sum().sort_values(ascending=False)

        st.bar_chart(vendor)

        st.subheader("Approval Status")

        st.dataframe(
            df.groupby("approval_status")["amount"].sum().reset_index()
        )

    else:
        st.info("No data available")

elif menu=="Audit Trail":

    st.title("Audit Trail")

    st.dataframe(logs(),use_container_width=True)
