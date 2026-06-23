import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# ---------------------------------
# DATABASE
# ---------------------------------

conn = sqlite3.connect('ap_database.db', check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS invoices(
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
comments TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS audit_log(
id INTEGER PRIMARY KEY AUTOINCREMENT,
action TEXT,
action_date TEXT
)
""")

conn.commit()

# ---------------------------------
# FUNCTIONS
# ---------------------------------

def add_invoice(invoice_no,vendor_name,invoice_date,amount,po_number,uploaded_by):

    c.execute("""
    SELECT * FROM invoices
    WHERE invoice_no=?
    """,(invoice_no,))

    duplicate = c.fetchone()

    if duplicate:
        return False

    c.execute("""
    INSERT INTO invoices(
    invoice_no,
    vendor_name,
    invoice_date,
    amount,
    po_number,
    status,
    approval_status,
    uploaded_by,
    upload_date,
    comments
    )
    VALUES(?,?,?,?,?,?,?,?,?,?)
    """,
    (
        invoice_no,
        vendor_name,
        invoice_date,
        amount,
        po_number,
        "Pending Payment",
        "Pending Approval",
        uploaded_by,
        datetime.now().strftime("%Y-%m-%d %H:%M"),
        ""
    ))

    conn.commit()

    add_audit(f"Invoice Uploaded: {invoice_no}")

    return True


def add_audit(action):

    c.execute("""
    INSERT INTO audit_log(action,action_date)
    VALUES(?,?)
    """,
    (
        action,
        datetime.now().strftime("%Y-%m-%d %H:%M")
    ))

    conn.commit()


def get_invoices():

    return pd.read_sql_query(
        "SELECT * FROM invoices",
        conn
    )


def get_audit():

    return pd.read_sql_query(
        "SELECT * FROM audit_log",
        conn
    )


def approve_invoice(invoice_id):

    c.execute("""
    UPDATE invoices
    SET approval_status='Approved'
    WHERE id=?
    """,(invoice_id,))

    conn.commit()

    add_audit(f"Invoice Approved ID {invoice_id}")


def reject_invoice(invoice_id):

    c.execute("""
    UPDATE invoices
    SET approval_status='Rejected'
    WHERE id=?
    """,(invoice_id,))

    conn.commit()

    add_audit(f"Invoice Rejected ID {invoice_id}")


def mark_paid(invoice_id):

    c.execute("""
    UPDATE invoices
    SET status='Paid'
    WHERE id=?
    """,(invoice_id,))

    conn.commit()

    add_audit(f"Invoice Paid ID {invoice_id}")


# ---------------------------------
# UI
# ---------------------------------

st.set_page_config(
    page_title="Accounts Payable Tool",
    layout="wide"
)

st.title("📊 Accounts Payable Management System")

menu = st.sidebar.selectbox(
    "Menu",
    [
        "Dashboard",
        "Upload Invoice",
        "Invoice Repository",
        "Approval Workflow",
        "Payment Processing",
        "Audit Trail"
    ]
)

# ---------------------------------
# DASHBOARD
# ---------------------------------

if menu == "Dashboard":

    df = get_invoices()

    total_invoice = len(df)

    total_amount = (
        df["amount"].sum()
        if not df.empty else 0
    )

    pending_approval = (
        len(df[df["approval_status"]=="Pending Approval"])
        if not df.empty else 0
    )

    pending_payment = (
        len(df[df["status"]=="Pending Payment"])
        if not df.empty else 0
    )

    col1,col2,col3,col4 = st.columns(4)

    col1.metric("Invoices",total_invoice)
    col2.metric("Invoice Amount",f"₹ {total_amount:,.2f}")
    col3.metric("Pending Approval",pending_approval)
    col4.metric("Pending Payment",pending_payment)

    st.subheader("Invoice Summary")

    if not df.empty:
        st.dataframe(df,use_container_width=True)

# ---------------------------------
# UPLOAD INVOICE
# ---------------------------------

elif menu == "Upload Invoice":

    st.subheader("Upload Invoice")

    with st.form("invoice_form"):

        invoice_no = st.text_input("Invoice Number")

        vendor_name = st.text_input("Vendor Name")

        invoice_date = st.date_input("Invoice Date")

        amount = st.number_input(
            "Invoice Amount",
            min_value=0.0
        )

        po_number = st.text_input("PO Number")

        uploaded_by = st.text_input("Uploaded By")

        submit = st.form_submit_button("Submit")

        if submit:

            result = add_invoice(
                invoice_no,
                vendor_name,
                str(invoice_date),
                amount,
                po_number,
                uploaded_by
            )

            if result:
                st.success("Invoice Uploaded Successfully")
            else:
                st.error("Duplicate Invoice Found")

# ---------------------------------
# REPOSITORY
# ---------------------------------

elif menu == "Invoice Repository":

    st.subheader("Invoice Repository")

    df = get_invoices()

    search = st.text_input("Search Invoice/Vendor")

    if search:
        df = df[
            df["invoice_no"].astype(str).str.contains(search,case=False)
            |
            df["vendor_name"].astype(str).str.contains(search,case=False)
        ]

    st.dataframe(df,use_container_width=True)

# ---------------------------------
# APPROVAL WORKFLOW
# ---------------------------------

elif menu == "Approval Workflow":

    st.subheader("Approval Workflow")

    df = get_invoices()

    pending = df[
        df["approval_status"]=="Pending Approval"
    ]

    st.dataframe(
        pending,
        use_container_width=True
    )

    invoice_id = st.number_input(
        "Invoice ID",
        step=1
    )

    col1,col2 = st.columns(2)

    if col1.button("Approve"):
        approve_invoice(invoice_id)
        st.success("Approved")

    if col2.button("Reject"):
        reject_invoice(invoice_id)
        st.error("Rejected")

# ---------------------------------
# PAYMENT PROCESSING
# ---------------------------------

elif menu == "Payment Processing":

    st.subheader("Payment Processing")

    df = get_invoices()

    approved = df[
        df["approval_status"]=="Approved"
    ]

    st.dataframe(
        approved,
        use_container_width=True
    )

    invoice_id = st.number_input(
        "Approved Invoice ID",
        step=1
    )

    if st.button("Mark as Paid"):

        mark_paid(invoice_id)

        st.success("Payment Updated")

# ---------------------------------
# AUDIT TRAIL
# ---------------------------------

elif menu == "Audit Trail":

    st.subheader("Audit Trail")

    audit_df = get_audit()

    st.dataframe(
        audit_df,
        use_container_width=True
    )
