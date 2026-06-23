import streamlit as st
import pandas as pd
import datetime

# --- Set Page Configuration & Professional Styling ---
st.set_page_config(page_title="AP Module", page_icon="🧾", layout="wide")

# Custom CSS for Light Green, Grey, and Professional Layout
st.markdown(
    """
    <style>
        /* Main background and text */
        .stApp { background-color: #F8F9FA; color: #343A40; }
        
        /* Headers */
        h1, h2, h3 { color: #2D3748; }
        
        /* Sidebar styling */
        [data-testid="stSidebar"] { background-color: #E2E8F0; }
        
        /* Light green success & highlight elements */
        .stButton>button {
            background-color: #48BB78; 
            color: white;
            font-weight: bold;
            border: none;
            border-radius: 4px;
        }
        .stButton>button:hover { background-color: #38A169; }
        
        /* Metric cards */
        div[data-testid="stMetricValue"] { color: #2F855A; }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Dummy Data Initialization ---
if "ap_data" not in st.session_state:
    st.session_state["ap_data"] = pd.DataFrame(
        {
            "Invoice ID": ["INV-10245", "INV-10246", "INV-10247", "INV-10248"],
            "Vendor": ["Vendor Alpha", "Vendor Beta", "Vendor Gamma", "Vendor Alpha"],
            "Amount ($)": [4500.00, 12500.50, 800.00, 3100.00],
            "Due Date": ["2026-07-15", "2026-06-18", "2026-07-01", "2026-07-20"],
            "Status": ["Pending", "Overdue", "Approved", "Pending"],
        }
    )
    st.session_state["ap_data"]["Due Date"] = pd.to_datetime(
        st.session_state["ap_data"]["Due Date"]
    ).dt.date

# --- App Header ---
st.title("🧾 Accounts Payable Dashboard")
st.write("Manage vendor invoices, track aging, and process approvals seamlessly.")

# --- Sidebar Filters ---
st.sidebar.header("Navigation")
app_mode = st.sidebar.radio(
    "Go to", ["Dashboard", "Invoice Entry", "Aging Report", "Payment Approvals"]
)

# --- App Logic ---
if app_mode == "Dashboard":
    st.subheader("Executive Overview")

    # Metrics
    col1, col2, col3 = st.columns(3)
    total_ap = st.session_state["ap_data"]["Amount ($)"].sum()
    pending_count = (st.session_state["ap_data"]["Status"] == "Pending").sum()
    overdue_amount = st.session_state["ap_data"].loc[
        st.session_state["ap_data"]["Status"] == "Overdue", "Amount ($)"
    ].sum()

    col1.metric("Total AP Outstanding", f"${total_ap:,.2f}")
    col2.metric("Pending Invoices", pending_count)
    col3.metric("Overdue Amount", f"${overdue_amount:,.2f}")

    st.markdown("### Recent Activity")
    st.dataframe(st.session_state["ap_data"], use_container_width=True)

elif app_mode == "Invoice Entry":
    st.subheader("Enter New Invoice")

    with st.form("invoice_form"):
        col1, col2 = st.columns(2)
        vendor = col1.text_input("Vendor Name")
        invoice_id = col1.text_input("Invoice ID")
        amount = col2.number_input("Amount ($)", min_value=0.0, format="%.2f")
        due_date = col2.date_input("Due Date")

        submitted = st.form_submit_button("Submit Invoice")

        if submitted and vendor and invoice_id:
            new_invoice = pd.DataFrame(
                {
                    "Invoice ID": [invoice_id],
                    "Vendor": [vendor],
                    "Amount ($)": [amount],
                    "Due Date": [due_date],
                    "Status": ["Pending"],
                }
            )
            st.session_state["ap_data"] = pd.concat(
                [st.session_state["ap_data"], new_invoice], ignore_index=True
            )
            st.success(f"Invoice {invoice_id} successfully logged!")
        elif submitted:
            st.warning("Please fill out all required fields.")

elif app_mode == "Aging Report":
    st.subheader("Accounts Payable Aging Schedule")

    # Adding fake Aging buckets
    df = st.session_state["ap_data"].copy()
    df["Current (0-30)"] = df.apply(
        lambda x: x["Amount ($)"] if x["Status"] != "Overdue" else 0, axis=1
    )
    df["31-60 Days"] = 0.0
    df["61-90 Days"] = 0.0
    df["90+ Days"] = df.apply(
        lambda x: x["Amount ($)"] if x["Status"] == "Overdue" else 0, axis=1
    )

    display_cols = [
        "Vendor",
        "Invoice ID",
        "Amount ($)",
        "Current (0-30)",
        "31-60 Days",
        "61-90 Days",
        "90+ Days",
    ]
    st.dataframe(df[display_cols], use_container_width=True)

elif app_mode == "Payment Approvals":
    st.subheader("Payment Approval Queue")

    # Filter for pending
    pending_df = st.session_state["ap_data"][
        st.session_state["ap_data"]["Status"] == "Pending"
    ]

    if pending_df.empty:
        st.info("No pending invoices require approval.")
    else:
        st.markdown("Select invoices to approve:")
        for idx, row in pending_df.iterrows():
            col1, col2, col3 = st.columns([3, 2, 2])
            col1.write(
                f"**{row['Vendor']}** - {row['Invoice ID']} (${row['Amount ($)']:,.2f})"
            )

            # Update status logic
            if col2.button("Approve", key=f"app_{row['Invoice ID']}"):
                st.session_state["ap_data"].loc[idx, "Status"] = "Approved"
                st.rerun()

            if col3.button("Reject", key=f"rej_{row['Invoice ID']}"):
                st.session_state["ap_data"].loc[idx, "Status"] = "Rejected"
                st.rerun()
