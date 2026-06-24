import streamlit as st
import json
import os
from datetime import datetime, date

DATA_FILE = "data.json"


# -----------------------------
# Data Handling
# -----------------------------
def default_data():
    return {
        "vendors": [],
        "invoices": [],
        "payments": []
    }


def load_data():
    if not os.path.exists(DATA_FILE):
        save_data(default_data())
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def next_id(items, prefix):
    if not items:
        return f"{prefix}001"
    nums = []
    for item in items:
        raw_id = item.get("id", "")
        digits = "".join(ch for ch in raw_id if ch.isdigit())
        if digits:
            nums.append(int(digits))
    next_num = max(nums) + 1 if nums else 1
    return f"{prefix}{str(next_num).zfill(3)}"


def parse_date(value):
    return datetime.strptime(value, "%Y-%m-%d").date()


def days_overdue(due_date_str, status):
    if status == "Paid":
        return 0
    due_dt = parse_date(due_date_str)
    today = date.today()
    delta = (today - due_dt).days
    return max(delta, 0)


def aging_bucket(days):
    if days <= 0:
        return "Current"
    if 1 <= days <= 30:
        return "1-30 Days"
    if 31 <= days <= 60:
        return "31-60 Days"
    if 61 <= days <= 90:
        return "61-90 Days"
    return "90+ Days"


def currency(amount):
    return f"${amount:,.2f}"


# -----------------------------
# App Config
# -----------------------------
st.set_page_config(
    page_title="Accounts Payable Module",
    page_icon="💼",
    layout="wide"
)

# -----------------------------
# Styling
# -----------------------------
st.markdown(
    """
    <style>
        .stApp {
            background-color: #edf2ee;
        }

        .main-title {
            font-size: 32px;
            font-weight: 700;
            color: #2f4f3f;
            margin-bottom: 5px;
        }

        .sub-title {
            font-size: 15px;
            color: #5f6f65;
            margin-bottom: 20px;
        }

        .card {
            background-color: #f7faf8;
            border: 1px solid #c9d8cc;
            border-radius: 12px;
            padding: 18px;
            margin-bottom: 15px;
            box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
        }

        .metric-card {
            background-color: #dcebdd;
            border: 1px solid #bdd3c0;
            border-radius: 12px;
            padding: 16px;
            text-align: center;
        }

        .metric-label {
            font-size: 14px;
            color: #52645a;
        }

        .metric-value {
            font-size: 28px;
            font-weight: 700;
            color: #22352a;
        }

        .section-header {
            font-size: 22px;
            font-weight: 600;
            color: #30483a;
            margin-top: 10px;
            margin-bottom: 10px;
        }

        .small-note {
            color: #6a7a70;
            font-size: 13px;
        }

        div[data-testid="stSidebar"] {
            background-color: #dfe6e1;
        }

        .stButton > button {
            background-color: #90b79c;
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: 600;
        }

        .stButton > button:hover {
            background-color: #7ea88a;
            color: white;
        }

        .stDownloadButton > button {
            background-color: #90b79c;
            color: white;
            border-radius: 8px;
            border: none;
            font-weight: 600;
        }

        .stTextInput > div > div > input,
        .stNumberInput input,
        .stDateInput input,
        .stSelectbox div[data-baseweb="select"] > div {
            background-color: #f7faf8;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# Load Data
# -----------------------------
data = load_data()

# -----------------------------
# Sidebar Navigation
# -----------------------------
st.sidebar.title("Finance Menu")
page = st.sidebar.radio(
    "Go to",
    [
        "Dashboard",
        "Vendor Management",
        "Invoice Entry",
        "Payment Processing",
        "Invoice Register",
        "Aging Report"
    ]
)

st.markdown('<div class="main-title">Accounts Payable Module</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">Professional finance workflow for vendor, invoice, and payment management.</div>',
    unsafe_allow_html=True
)

# -----------------------------
# Dashboard
# -----------------------------
if page == "Dashboard":
    total_vendors = len(data["vendors"])
    total_invoices = len(data["invoices"])
    unpaid_invoices = [inv for inv in data["invoices"] if inv["status"] != "Paid"]
    paid_invoices = [inv for inv in data["invoices"] if inv["status"] == "Paid"]

    total_outstanding = sum(inv["amount"] - inv.get("paid_amount", 0) for inv in unpaid_invoices)
    total_paid = sum(inv.get("paid_amount", 0) for inv in paid_invoices)

    overdue_count = 0
    for inv in unpaid_invoices:
        if days_overdue(inv["due_date"], inv["status"]) > 0:
            overdue_count += 1

    st.markdown('<div class="section-header">Dashboard Overview</div>', unsafe_allow_html=True)

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">Vendors</div><div class="metric-value">{total_vendors}</div></div>',
            unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">Invoices</div><div class="metric-value">{total_invoices}</div></div>',
            unsafe_allow_html=True
        )
    with col3:
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">Outstanding</div><div class="metric-value">{currency(total_outstanding)}</div></div>',
            unsafe_allow_html=True
        )
    with col4:
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">Paid</div><div class="metric-value">{currency(total_paid)}</div></div>',
            unsafe_allow_html=True
        )
    with col5:
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">Overdue</div><div class="metric-value">{overdue_count}</div></div>',
            unsafe_allow_html=True
        )

    st.write("")
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Recent Invoices")

    if data["invoices"]:
        recent = sorted(data["invoices"], key=lambda x: x["invoice_date"], reverse=True)[:10]
        rows = []
        for inv in recent:
            outstanding = inv["amount"] - inv.get("paid_amount", 0)
            rows.append({
                "Invoice ID": inv["id"],
                "Vendor": inv["vendor_name"],
                "Invoice No": inv["invoice_number"],
                "Invoice Date": inv["invoice_date"],
                "Due Date": inv["due_date"],
                "Amount": currency(inv["amount"]),
                "Paid": currency(inv.get("paid_amount", 0)),
                "Outstanding": currency(outstanding),
                "Status": inv["status"]
            })
        st.dataframe(rows, use_container_width=True)
    else:
        st.info("No invoices available.")

    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# Vendor Management
# -----------------------------
elif page == "Vendor Management":
    st.markdown('<div class="section-header">Vendor Management</div>', unsafe_allow_html=True)

    with st.form("vendor_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            vendor_name = st.text_input("Vendor Name")
            vendor_email = st.text_input("Vendor Email")
            tax_id = st.text_input("Tax ID")
        with col2:
            vendor_phone = st.text_input("Phone")
            payment_terms = st.selectbox("Payment Terms", ["Net 15", "Net 30", "Net 45", "Net 60"])
            vendor_status = st.selectbox("Status", ["Active", "Inactive"])

        submitted = st.form_submit_button("Add Vendor")

        if submitted:
            if not vendor_name.strip():
                st.error("Vendor name is required.")
            else:
                vendor_id = next_id(data["vendors"], "VEN")
                data["vendors"].append({
                    "id": vendor_id,
                    "vendor_name": vendor_name.strip(),
                    "vendor_email": vendor_email.strip(),
                    "tax_id": tax_id.strip(),
                    "vendor_phone": vendor_phone.strip(),
                    "payment_terms": payment_terms,
                    "vendor_status": vendor_status
                })
                save_data(data)
                st.success(f"Vendor {vendor_id} added successfully.")

    st.subheader("Vendor Register")
    if data["vendors"]:
        st.dataframe(data["vendors"], use_container_width=True)
    else:
        st.info("No vendors found.")

# -----------------------------
# Invoice Entry
# -----------------------------
elif page == "Invoice Entry":
    st.markdown('<div class="section-header">Invoice Entry</div>', unsafe_allow_html=True)

    vendor_names = [v["vendor_name"] for v in data["vendors"] if v["vendor_status"] == "Active"]

    if not vendor_names:
        st.warning("Please add at least one active vendor before entering invoices.")
    else:
        with st.form("invoice_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                selected_vendor = st.selectbox("Vendor", vendor_names)
                invoice_number = st.text_input("Invoice Number")
                invoice_date = st.date_input("Invoice Date", value=date.today())
                amount = st.number_input("Invoice Amount", min_value=0.0, format="%.2f")
            with col2:
                due_date = st.date_input("Due Date", value=date.today())
                department = st.selectbox("Department", ["Operations", "Finance", "HR", "IT", "Procurement", "Admin"])
                cost_center = st.text_input("Cost Center")
                description = st.text_area("Description")

            submitted = st.form_submit_button("Save Invoice")

            if submitted:
                if not invoice_number.strip():
                    st.error("Invoice number is required.")
                elif amount <= 0:
                    st.error("Invoice amount must be greater than zero.")
                else:
                    invoice_id = next_id(data["invoices"], "INV")
                    data["invoices"].append({
                        "id": invoice_id,
                        "vendor_name": selected_vendor,
                        "invoice_number": invoice_number.strip(),
                        "invoice_date": str(invoice_date),
                        "due_date": str(due_date),
                        "amount": float(amount),
                        "paid_amount": 0.0,
                        "department": department,
                        "cost_center": cost_center.strip(),
                        "description": description.strip(),
                        "status": "Open"
                    })
                    save_data(data)
                    st.success(f"Invoice {invoice_id} created successfully.")

    st.subheader("Invoice Register")
    if data["invoices"]:
        invoice_rows = []
        for inv in data["invoices"]:
            outstanding = inv["amount"] - inv.get("paid_amount", 0)
            invoice_rows.append({
                "Invoice ID": inv["id"],
                "Vendor": inv["vendor_name"],
                "Invoice No": inv["invoice_number"],
                "Invoice Date": inv["invoice_date"],
                "Due Date": inv["due_date"],
                "Amount": currency(inv["amount"]),
                "Paid": currency(inv.get("paid_amount", 0)),
                "Outstanding": currency(outstanding),
                "Status": inv["status"]
            })
        st.dataframe(invoice_rows, use_container_width=True)
    else:
        st.info("No invoices entered yet.")

# -----------------------------
# Payment Processing
# -----------------------------
elif page == "Payment Processing":
    st.markdown('<div class="section-header">Payment Processing</div>', unsafe_allow_html=True)

    open_invoices = [
        inv for inv in data["invoices"]
        if inv.get("paid_amount", 0) < inv["amount"]
    ]

    if not open_invoices:
        st.info("No open invoices available for payment.")
    else:
        invoice_options = {
            f'{inv["id"]} | {inv["vendor_name"]} | {inv["invoice_number"]} | Outstanding: {currency(inv["amount"] - inv.get("paid_amount", 0))}': inv
            for inv in open_invoices
        }

        with st.form("payment_form", clear_on_submit=True):
            selected_label = st.selectbox("Select Invoice", list(invoice_options.keys()))
            selected_invoice = invoice_options[selected_label]

            outstanding_amt = selected_invoice["amount"] - selected_invoice.get("paid_amount", 0)

            col1, col2 = st.columns(2)
            with col1:
                payment_date = st.date_input("Payment Date", value=date.today())
                payment_method = st.selectbox("Payment Method", ["Bank Transfer", "Cheque", "Cash", "Wire"])
            with col2:
                payment_amount = st.number_input(
                    "Payment Amount",
                    min_value=0.0,
                    max_value=float(outstanding_amt),
                    value=float(outstanding_amt),
                    format="%.2f"
                )
                reference_no = st.text_input("Reference Number")

            submitted = st.form_submit_button("Record Payment")

            if submitted:
                if payment_amount <= 0:
                    st.error("Payment amount must be greater than zero.")
                else:
                    payment_id = next_id(data["payments"], "PAY")
                    data["payments"].append({
                        "id": payment_id,
                        "invoice_id": selected_invoice["id"],
                        "vendor_name": selected_invoice["vendor_name"],
                        "payment_date": str(payment_date),
                        "payment_method": payment_method,
                        "payment_amount": float(payment_amount),
                        "reference_no": reference_no.strip()
                    })

                    for inv in data["invoices"]:
                        if inv["id"] == selected_invoice["id"]:
                            inv["paid_amount"] = float(inv.get("paid_amount", 0) + payment_amount)
                            if inv["paid_amount"] >= inv["amount"]:
                                inv["status"] = "Paid"
                                inv["paid_amount"] = inv["amount"]
                            elif inv["paid_amount"] > 0:
                                inv["status"] = "Partially Paid"

                    save_data(data)
                    st.success(f"Payment {payment_id} recorded successfully.")

    st.subheader("Payment History")
    if data["payments"]:
        payment_rows = []
        for pmt in sorted(data["payments"], key=lambda x: x["payment_date"], reverse=True):
            payment_rows.append({
                "Payment ID": pmt["id"],
                "Invoice ID": pmt["invoice_id"],
                "Vendor": pmt["vendor_name"],
                "Payment Date": pmt["payment_date"],
                "Method": pmt["payment_method"],
                "Amount": currency(pmt["payment_amount"]),
                "Reference": pmt["reference_no"]
            })
        st.dataframe(payment_rows, use_container_width=True)
    else:
        st.info("No payments recorded yet.")

# -----------------------------
# Invoice Register
# -----------------------------
elif page == "Invoice Register":
    st.markdown('<div class="section-header">Invoice Register</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        vendor_filter = st.selectbox("Filter by Vendor", ["All"] + sorted(list(set(inv["vendor_name"] for inv in data["invoices"]))))
    with col2:
        status_filter = st.selectbox("Filter by Status", ["All", "Open", "Partially Paid", "Paid"])
    with col3:
        search_text = st.text_input("Search Invoice Number")

    filtered = data["invoices"]

    if vendor_filter != "All":
        filtered = [inv for inv in filtered if inv["vendor_name"] == vendor_filter]

    if status_filter != "All":
        filtered = [inv for inv in filtered if inv["status"] == status_filter]

    if search_text.strip():
        filtered = [
            inv for inv in filtered
            if search_text.lower().strip() in inv["invoice_number"].lower()
        ]

    if filtered:
        rows = []
        for inv in filtered:
            paid_amt = inv.get("paid_amount", 0)
            outstanding = inv["amount"] - paid_amt
            overdue_days = days_overdue(inv["due_date"], inv["status"])
            rows.append({
                "Invoice ID": inv["id"],
                "Vendor": inv["vendor_name"],
                "Invoice No": inv["invoice_number"],
                "Invoice Date": inv["invoice_date"],
                "Due Date": inv["due_date"],
                "Department": inv["department"],
                "Amount": currency(inv["amount"]),
                "Paid": currency(paid_amt),
                "Outstanding": currency(outstanding),
                "Overdue Days": overdue_days,
                "Status": inv["status"]
            })
        st.dataframe(rows, use_container_width=True)

        export_data = json.dumps(rows, indent=4)
        st.download_button(
            label="Download Register as JSON",
            data=export_data,
            file_name="invoice_register.json",
            mime="application/json"
        )
    else:
        st.info("No invoices match the selected filters.")

# -----------------------------
# Aging Report
# -----------------------------
elif page == "Aging Report":
    st.markdown('<div class="section-header">Aging Report</div>', unsafe_allow_html=True)

    aging_summary = {
        "Current": 0.0,
        "1-30 Days": 0.0,
        "31-60 Days": 0.0,
        "61-90 Days": 0.0,
        "90+ Days": 0.0
    }

    detailed_rows = []

    for inv in data["invoices"]:
        outstanding = inv["amount"] - inv.get("paid_amount", 0)
        if outstanding > 0:
            overdue = days_overdue(inv["due_date"], inv["status"])
            bucket = aging_bucket(overdue)
            aging_summary[bucket] += outstanding

            detailed_rows.append({
                "Invoice ID": inv["id"],
                "Vendor": inv["vendor_name"],
                "Invoice No": inv["invoice_number"],
                "Due Date": inv["due_date"],
                "Outstanding": currency(outstanding),
                "Overdue Days": overdue,
                "Bucket": bucket
            })

    col1, col2, col3, col4, col5 = st.columns(5)
    buckets = list(aging_summary.items())

    for i, col in enumerate([col1, col2, col3, col4, col5]):
        with col:
            st.markdown(
                f'<div class="metric-card"><div class="metric-label">{buckets[i][0]}</div><div class="metric-value">{currency(buckets[i][1])}</div></div>',
                unsafe_allow_html=True
            )

    st.write("")
    st.subheader("Aging Details")
    if detailed_rows:
        st.dataframe(detailed_rows, use_container_width=True)
    else:
        st.info("No outstanding invoices for aging analysis.")
