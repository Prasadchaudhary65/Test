import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Accounts Payable Management System",
    page_icon="💰",
    layout="wide"
)

# ---------------- STYLING ----------------
st.markdown("""
<style>
.main {
    background-color: #f4f7f5;
}
.stApp {
    background-color: #f4f7f5;
}
h1,h2,h3 {
    color: #2f4f4f;
}
.metric-container {
    background-color: white;
    padding: 15px;
    border-radius: 10px;
}
div[data-testid="stSidebar"] {
    background-color: #d8e8d8;
}
.stButton>button {
    background-color: #90c695;
    color: black;
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- SAMPLE DATA ----------------
if 'ap_data' not in st.session_state:
    st.session_state.ap_data = pd.DataFrame({
        "Vendor": ["ABC Ltd", "XYZ Pvt Ltd", "PQR Services"],
        "Invoice No": ["INV001", "INV002", "INV003"],
        "Invoice Date": ["2026-06-01", "2026-05-20", "2026-06-10"],
        "Due Date": ["2026-07-01", "2026-06-20", "2026-07-10"],
        "Amount": [150000, 80000, 120000],
        "Status": ["Pending", "Paid", "Pending"]
    })

df = st.session_state.ap_data

# ---------------- SIDEBAR ----------------
st.sidebar.title("Accounts Payable")
menu = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Invoice Entry", "Vendor Master", "Aging Analysis", "Reports"]
)

# ---------------- DASHBOARD ----------------
if menu == "Dashboard":

    st.title("💰 Accounts Payable Dashboard")

    total_invoice = df["Amount"].sum()
    total_pending = df[df["Status"] == "Pending"]["Amount"].sum()
    total_paid = df[df["Status"] == "Paid"]["Amount"].sum()
    vendor_count = df["Vendor"].nunique()

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total AP", f"₹{total_invoice:,.0f}")
    c2.metric("Pending", f"₹{total_pending:,.0f}")
    c3.metric("Paid", f"₹{total_paid:,.0f}")
    c4.metric("Vendors", vendor_count)

    st.markdown("---")

    status_chart = px.pie(
        df,
        names="Status",
        values="Amount",
        title="Invoice Status Distribution"
    )

    vendor_chart = px.bar(
        df.groupby("Vendor")["Amount"].sum().reset_index(),
        x="Vendor",
        y="Amount",
        title="Spend by Vendor"
    )

    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(status_chart, use_container_width=True)

    with col2:
        st.plotly_chart(vendor_chart, use_container_width=True)

    st.subheader("Recent Invoices")
    st.dataframe(df, use_container_width=True)

# ---------------- INVOICE ENTRY ----------------
elif menu == "Invoice Entry":

    st.title("🧾 Invoice Entry")

    with st.form("invoice_form"):
        vendor = st.text_input("Vendor Name")
        invoice_no = st.text_input("Invoice Number")
        invoice_date = st.date_input("Invoice Date")
        due_date = st.date_input("Due Date")
        amount = st.number_input("Amount", min_value=0.0)
        status = st.selectbox("Status", ["Pending", "Paid"])

        submit = st.form_submit_button("Add Invoice")

        if submit:
            new_row = pd.DataFrame({
                "Vendor": [vendor],
                "Invoice No": [invoice_no],
                "Invoice Date": [invoice_date],
                "Due Date": [due_date],
                "Amount": [amount],
                "Status": [status]
            })

            st.session_state.ap_data = pd.concat(
                [st.session_state.ap_data, new_row],
                ignore_index=True
            )

            st.success("Invoice added successfully.")

# ---------------- VENDOR MASTER ----------------
elif menu == "Vendor Master":

    st.title("🏢 Vendor Master")

    vendor_list = pd.DataFrame({
        "Vendor Name": df["Vendor"].unique()
    })

    st.dataframe(vendor_list, use_container_width=True)

    new_vendor = st.text_input("Add New Vendor")

    if st.button("Add Vendor"):
        st.success(f"{new_vendor} added to vendor list.")

# ---------------- AGING ANALYSIS ----------------
elif menu == "Aging Analysis":

    st.title("⏳ AP Aging Analysis")

    aging_df = df.copy()

    today = pd.Timestamp.today()

    aging_df["Due Date"] = pd.to_datetime(aging_df["Due Date"])

    aging_df["Days Outstanding"] = (
        today - aging_df["Due Date"]
    ).dt.days

    st.dataframe(aging_df, use_container_width=True)

    aging_chart = px.histogram(
        aging_df,
        x="Days Outstanding",
        title="Outstanding Aging Distribution"
    )

    st.plotly_chart(aging_chart, use_container_width=True)

# ---------------- REPORTS ----------------
elif menu == "Reports":

    st.title("📊 Reports")

    uploaded_file = st.file_uploader(
        "Upload AP Data",
        type=["csv"]
    )

    if uploaded_file:
        upload_df = pd.read_csv(uploaded_file)

        st.subheader("Uploaded Data")

        st.dataframe(upload_df)

        csv = upload_df.to_csv(index=False)

        st.download_button(
            "Download Report",
            csv,
            "accounts_payable_report.csv",
            "text/csv"
        )

    st.subheader("Current AP Data")

    st.dataframe(df)

    report_csv = df.to_csv(index=False)

    st.download_button(
        "Download Current AP Report",
        report_csv,
        "ap_report.csv",
        "text/csv")
