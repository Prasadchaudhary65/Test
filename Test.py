import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

st.set_page_config(
    page_title="Accounts Payable Dashboard",
    page_icon="💰",
    layout="wide"
)

# ---------------- Styling ----------------
st.markdown("""
<style>
.stApp {
    background-color: #f5f7f5;
}

section[data-testid="stSidebar"] {
    background-color: #d9ead3;
}

h1,h2,h3 {
    color: #4f4f4f;
}

div[data-testid="metric-container"] {
    background-color: white;
    border: 1px solid #d3d3d3;
    padding: 10px;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- Sample Data ----------------
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame({
        "Vendor":["ABC Ltd","XYZ Pvt Ltd","PQR Services"],
        "Invoice No":["INV001","INV002","INV003"],
        "Invoice Date":["2026-06-01","2026-06-10","2026-06-15"],
        "Due Date":["2026-07-01","2026-07-10","2026-07-15"],
        "Amount":[150000,80000,120000],
        "Status":["Pending","Paid","Pending"]
    })

df = st.session_state.data

# ---------------- Sidebar ----------------
st.sidebar.title("Accounts Payable")
page = st.sidebar.radio(
    "Menu",
    ["Dashboard","Add Invoice","Vendor Analysis","Aging Report","Data Upload"]
)

# ---------------- Dashboard ----------------
if page == "Dashboard":

    st.title("💰 Accounts Payable Dashboard")

    total_ap = df["Amount"].sum()
    total_pending = df[df["Status"]=="Pending"]["Amount"].sum()
    total_paid = df[df["Status"]=="Paid"]["Amount"].sum()
    vendors = df["Vendor"].nunique()

    c1,c2,c3,c4 = st.columns(4)

    c1.metric("Total AP",f"₹{total_ap:,.0f}")
    c2.metric("Pending",f"₹{total_pending:,.0f}")
    c3.metric("Paid",f"₹{total_paid:,.0f}")
    c4.metric("Vendors",vendors)

    st.markdown("---")

    col1,col2 = st.columns(2)

    with col1:
        st.subheader("Invoice Status")

        fig, ax = plt.subplots()
        df.groupby("Status")["Amount"].sum().plot(
            kind="pie",
            autopct="%1.1f%%",
            ax=ax
        )
        ax.set_ylabel("")
        st.pyplot(fig)

    with col2:
        st.subheader("Vendor Spend")

        vendor_data = df.groupby("Vendor")["Amount"].sum()

        fig, ax = plt.subplots()
        vendor_data.plot(kind="bar", ax=ax)
        st.pyplot(fig)

    st.subheader("Invoice Register")
    st.dataframe(df, use_container_width=True)

# ---------------- Add Invoice ----------------
elif page == "Add Invoice":

    st.title("Add Invoice")

    with st.form("invoice_form"):

        vendor = st.text_input("Vendor Name")
        invoice_no = st.text_input("Invoice Number")
        invoice_date = st.date_input("Invoice Date")
        due_date = st.date_input("Due Date")
        amount = st.number_input("Amount", min_value=0.0)
        status = st.selectbox(
            "Status",
            ["Pending","Paid"]
        )

        submit = st.form_submit_button("Save Invoice")

        if submit:

            new_row = pd.DataFrame({
                "Vendor":[vendor],
                "Invoice No":[invoice_no],
                "Invoice Date":[invoice_date],
                "Due Date":[due_date],
                "Amount":[amount],
                "Status":[status]
            })

            st.session_state.data = pd.concat(
                [st.session_state.data,new_row],
                ignore_index=True
            )

            st.success("Invoice Saved Successfully")

# ---------------- Vendor Analysis ----------------
elif page == "Vendor Analysis":

    st.title("Vendor Analysis")

    summary = (
        df.groupby("Vendor")["Amount"]
        .sum()
        .reset_index()
        .sort_values("Amount", ascending=False)
    )

    st.dataframe(summary, use_container_width=True)

# ---------------- Aging Report ----------------
elif page == "Aging Report":

    st.title("Aging Report")

    aging_df = df.copy()

    aging_df["Due Date"] = pd.to_datetime(
        aging_df["Due Date"]
    )

    today = pd.Timestamp.today()

    aging_df["Days Outstanding"] = (
        today - aging_df["Due Date"]
    ).dt.days

    st.dataframe(
        aging_df,
        use_container_width=True
    )

# ---------------- Upload Data ----------------
elif page == "Data Upload":

    st.title("Upload AP Data")

    file = st.file_uploader(
        "Upload CSV",
        type=["csv"]
    )

    if file:

        uploaded_df = pd.read_csv(file)

        st.dataframe(
            uploaded_df,
            use_container_width=True
        )

        st.download_button(
            "Download Uploaded Data",
            uploaded_df.to_csv(index=False),
            "AP_Report.csv",
            "text/csv"
        )
