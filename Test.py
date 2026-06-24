"""
Accounts Payable Module — Finance Function
A professional Streamlit application for managing AP workflows.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, date
import random
import io

# ──────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="Accounts Payable | Finance",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────
# DESIGN TOKENS — Light Green & Grey palette
# ──────────────────────────────────────────────
COLORS = {
    "primary":       "#4CAF82",
    "primary_dark":  "#2E7D54",
    "primary_light": "#A8D8B9",
    "accent":        "#81C784",
    "bg_page":       "#F4F6F5",
    "bg_card":       "#FFFFFF",
    "bg_sidebar":    "#2C3E35",
    "text_dark":     "#1C2B24",
    "text_mid":      "#4A6358",
    "text_light":    "#8FA99B",
    "grey_100":      "#F0F2F1",
    "grey_200":      "#E2E6E4",
    "grey_400":      "#9BADA5",
    "danger":        "#E57373",
    "warning":       "#FFB74D",
    "info":          "#64B5F6",
    "success":       "#4CAF82",
}

# ──────────────────────────────────────────────
# GLOBAL CSS
# ──────────────────────────────────────────────
st.markdown(f"""
<style>
  html, body, [data-testid="stAppViewContainer"] {{
      background-color: {COLORS['bg_page']};
      font-family: 'Inter', 'Segoe UI', sans-serif;
  }}
  [data-testid="stAppViewContainer"] > .main {{
      background-color: {COLORS['bg_page']};
  }}
  [data-testid="stSidebar"] {{
      background-color: {COLORS['bg_sidebar']};
  }}
  [data-testid="stSidebar"] * {{
      color: #D6EAE0 !important;
  }}
  [data-testid="stSidebar"] .stRadio label {{
      color: #D6EAE0 !important;
      font-size: 0.93rem;
  }}
  [data-testid="stSidebar"] hr {{
      border-color: #3D5448;
  }}
  .ap-header {{
      background: linear-gradient(135deg, {COLORS['primary_dark']} 0%, {COLORS['primary']} 100%);
      border-radius: 12px;
      padding: 1.4rem 2rem;
      margin-bottom: 1.4rem;
      display: flex;
      align-items: center;
      gap: 1rem;
  }}
  .ap-header h1 {{
      color: #fff;
      margin: 0;
      font-size: 1.6rem;
      font-weight: 700;
      letter-spacing: -0.3px;
  }}
  .ap-header p {{
      color: #C8E6C9;
      margin: 0;
      font-size: 0.85rem;
  }}
  .kpi-card {{
      background: {COLORS['bg_card']};
      border-radius: 10px;
      padding: 1.1rem 1.3rem;
      border-left: 4px solid {COLORS['primary']};
      box-shadow: 0 1px 4px rgba(44,62,53,0.07);
  }}
  .kpi-label {{
      font-size: 0.73rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.8px;
      color: {COLORS['text_light']};
      margin-bottom: 0.3rem;
  }}
  .kpi-value {{
      font-size: 1.8rem;
      font-weight: 700;
      color: {COLORS['text_dark']};
      line-height: 1;
  }}
  .kpi-sub {{
      font-size: 0.78rem;
      color: {COLORS['text_mid']};
      margin-top: 0.25rem;
  }}
  .kpi-up   {{ color: {COLORS['success']}; }}
  .kpi-down {{ color: {COLORS['danger']};  }}
  .section-title {{
      font-size: 1rem;
      font-weight: 700;
      color: {COLORS['text_dark']};
      border-bottom: 2px solid {COLORS['primary_light']};
      padding-bottom: 0.4rem;
      margin-bottom: 1rem;
  }}
  .card {{
      background: {COLORS['bg_card']};
      border-radius: 10px;
      padding: 1.2rem 1.4rem;
      box-shadow: 0 1px 4px rgba(44,62,53,0.07);
      margin-bottom: 1rem;
  }}
  .badge {{
      display: inline-block;
      padding: 2px 10px;
      border-radius: 20px;
      font-size: 0.72rem;
      font-weight: 600;
  }}
  .badge-paid     {{ background:#E8F5E9; color:{COLORS['primary_dark']}; }}
  .badge-pending  {{ background:#FFF3E0; color:#E65100; }}
  .badge-overdue  {{ background:#FFEBEE; color:#C62828; }}
  .badge-approved {{ background:#E3F2FD; color:#1565C0; }}
  .badge-draft    {{ background:{COLORS['grey_100']}; color:{COLORS['text_mid']}; }}
  .styled-table thead th {{
      background: {COLORS['grey_100']};
      color: {COLORS['text_mid']};
      font-size: 0.72rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.5px;
  }}
  div[data-baseweb="select"] > div,
  .stTextInput > div > div > input,
  .stNumberInput input,
  .stDateInput input {{
      border-radius: 6px !important;
      border-color: {COLORS['grey_200']} !important;
  }}
  .stButton > button {{
      background-color: {COLORS['primary']};
      color: #fff;
      border: none;
      border-radius: 7px;
      font-weight: 600;
      padding: 0.45rem 1.2rem;
      transition: background 0.18s;
  }}
  .stButton > button:hover {{
      background-color: {COLORS['primary_dark']};
  }}
  div[data-testid="stMetric"] {{
      background: {COLORS['bg_card']};
      border-radius: 10px;
      padding: 0.9rem 1rem;
      border-left: 3px solid {COLORS['primary']};
  }}
  .stTabs [data-baseweb="tab-list"] {{
      gap: 4px;
      background: {COLORS['grey_100']};
      border-radius: 8px;
      padding: 4px;
  }}
  .stTabs [data-baseweb="tab"] {{
      border-radius: 6px;
      font-weight: 600;
      font-size: 0.85rem;
  }}
  .stTabs [aria-selected="true"] {{
      background: {COLORS['primary']} !important;
      color: #fff !important;
  }}
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# SEED DATA GENERATION
# ──────────────────────────────────────────────
@st.cache_data
def generate_data():
    random.seed(42)
    vendors = [
        "Accenture Ltd", "Dell Technologies", "Microsoft Corp", "AWS Services",
        "Oracle Corp", "SAP SE", "Cisco Systems", "Salesforce Inc",
        "ServiceNow", "Workday Inc", "Zoom Video", "Adobe Systems",
        "Deloitte Advisory", "KPMG Services", "PwC Consulting",
    ]
    categories = ["IT Services", "Software", "Consulting", "Hardware", "Cloud", "Telecom"]
    statuses   = ["Paid", "Pending", "Overdue", "Approved", "Draft"]
    status_weights = [0.40, 0.30, 0.12, 0.12, 0.06]

    today = date.today()
    rows = []
    for i in range(1, 201):
        inv_date = today - timedelta(days=random.randint(1, 180))
        due_date = inv_date + timedelta(days=random.choice([30, 45, 60, 90]))
        amt       = round(random.uniform(1_500, 150_000), 2)
        status    = random.choices(statuses, weights=status_weights)[0]
        vendor    = random.choice(vendors)
        rows.append({
            "Invoice #":    f"INV-{2024000 + i}",
            "Vendor":       vendor,
            "Category":     random.choice(categories),
            "Invoice Date": inv_date,
            "Due Date":     due_date,
            "Amount ($)":   amt,
            "Status":       status,
            "Approver":     random.choice(["J. Martinez", "S. Patel", "L. Chen", "R. Thompson"]),
            "PO #":         f"PO-{random.randint(10000,99999)}",
            "Payment Date": inv_date + timedelta(days=random.randint(5, 60)) if status == "Paid" else None,
        })
    return pd.DataFrame(rows)


@st.cache_data
def generate_vendors():
    vendors = [
        ("Accenture Ltd",    "Technology",   "Net 30", "A+", 4_200_000),
        ("Dell Technologies","Hardware",      "Net 45", "A",  3_100_000),
        ("Microsoft Corp",   "Software",      "Net 30", "A+", 5_800_000),
        ("AWS Services",     "Cloud",         "Net 30", "A+", 2_900_000),
        ("Oracle Corp",      "Software",      "Net 60", "B+", 1_700_000),
        ("SAP SE",           "Software",      "Net 45", "A",  2_400_000),
        ("Cisco Systems",    "Hardware",      "Net 30", "A",  1_200_000),
        ("Salesforce Inc",   "Cloud",         "Net 30", "A+", 980_000),
        ("Deloitte Advisory","Consulting",    "Net 45", "A",  3_600_000),
        ("KPMG Services",    "Consulting",    "Net 30", "A",  2_100_000),
    ]
    return pd.DataFrame(vendors, columns=["Vendor", "Category", "Payment Terms", "Credit Rating", "YTD Spend ($)"])


# ──────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────
def status_badge(status):
    cls = {
        "Paid":     "badge-paid",
        "Pending":  "badge-pending",
        "Overdue":  "badge-overdue",
        "Approved": "badge-approved",
        "Draft":    "badge-draft",
    }.get(status, "badge-draft")
    return f'<span class="badge {cls}">{status}</span>'


def fmt_currency(val):
    return f"${val:,.0f}"


def plotly_defaults(fig, height=320):
    fig.update_layout(
        height=height,
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="Inter, Segoe UI, sans-serif", size=11, color=COLORS["text_dark"]),
        margin=dict(l=12, r=12, t=30, b=12),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    fig.update_xaxes(showgrid=False, linecolor=COLORS["grey_200"])
    fig.update_yaxes(gridcolor=COLORS["grey_100"], linecolor=COLORS["grey_200"])
    return fig


# ──────────────────────────────────────────────
# SIDEBAR NAVIGATION
# ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
        <div style='text-align:center; padding: 1rem 0 0.5rem;'>
            <div style='font-size:2rem;'>💼</div>
            <div style='font-size:1rem; font-weight:700; color:#A8D8B9; letter-spacing:0.5px;'>AP Module</div>
            <div style='font-size:0.72rem; color:#6B8C7D; margin-top:2px;'>Finance · Accounts Payable</div>
        </div>
        <hr/>
    """, unsafe_allow_html=True)

    nav = st.radio(
        "Navigation",
        [
            "📊  Dashboard",
            "🧾  Invoice Management",
            "🏢  Vendor Master",
            "✅  Approval Workflow",
            "💳  Payment Processing",
            "📈  Analytics & Reports",
            "⚙️  Settings",
        ],
        label_visibility="collapsed",
    )

    st.markdown("<hr/>", unsafe_allow_html=True)
    st.markdown(f"""
        <div style='font-size:0.72rem; color:#6B8C7D; padding: 0.5rem 0;'>
            Fiscal Year &nbsp;<strong style='color:#A8D8B9;'>FY 2025</strong><br/>
            Last sync &nbsp;<strong style='color:#A8D8B9;'>{datetime.now().strftime('%d %b %Y %H:%M')}</strong>
        </div>
    """, unsafe_allow_html=True)

page = nav.split("  ")[1]

# Load data
df     = generate_data()
df_vnd = generate_vendors()

# ──────────────────────────────────────────────
# PAGE: DASHBOARD
# ──────────────────────────────────────────────
if page == "Dashboard":
    st.markdown(f"""
        <div class="ap-header">
            <div>
                <h1>Accounts Payable Dashboard</h1>
                <p>Finance Function &nbsp;·&nbsp; {datetime.now().strftime('%A, %d %B %Y')}</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    total_amt   = df["Amount ($)"].sum()
    paid_amt    = df[df["Status"] == "Paid"]["Amount ($)"].sum()
    pending_amt = df[df["Status"] == "Pending"]["Amount ($)"].sum()
    overdue_cnt = len(df[df["Status"] == "Overdue"])
    overdue_amt = df[df["Status"] == "Overdue"]["Amount ($)"].sum()

    k1, k2, k3, k4, k5 = st.columns(5)
    kpis = [
        (k1, "Total Invoices",    f"{len(df)}",             f"{fmt_currency(total_amt)} total value",  ""),
        (k2, "Paid",              fmt_currency(paid_amt),   f"{len(df[df['Status']=='Paid'])} invoices", "kpi-up"),
        (k3, "Pending Approval",  fmt_currency(pending_amt),f"{len(df[df['Status']=='Pending'])} invoices", ""),
        (k4, "Overdue",           str(overdue_cnt),          fmt_currency(overdue_amt),                "kpi-down"),
        (k5, "Avg Days to Pay",   "28 days",                "Target: ≤ 30 days",                       "kpi-up"),
    ]
    for col, label, val, sub, cls in kpis:
        with col:
            st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-label">{label}</div>
                    <div class="kpi-value {cls}">{val}</div>
                    <div class="kpi-sub">{sub}</div>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("<br/>", unsafe_allow_html=True)

    c1, c2 = st.columns([1, 1])

    with c1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Invoice Status Breakdown</div>', unsafe_allow_html=True)
        status_counts = df["Status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]
        color_map = {
            "Paid": COLORS["primary"], "Pending": COLORS["warning"],
            "Overdue": COLORS["danger"], "Approved": COLORS["info"], "Draft": COLORS["grey_400"],
        }
        fig = px.pie(
            status_counts, values="Count", names="Status",
            color="Status", color_discrete_map=color_map, hole=0.55,
        )
        fig = plotly_defaults(fig, 290)
        fig.update_traces(textposition="outside", textinfo="percent+label")
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Monthly AP Spend (Last 6 Months)</div>', unsafe_allow_html=True)
        df["Month"] = pd.to_datetime(df["Invoice Date"]).dt.to_period("M").astype(str)
        monthly = df.groupby("Month")["Amount ($)"].sum().reset_index().sort_values("Month").tail(6)
        fig2 = px.bar(
            monthly, x="Month", y="Amount ($)",
            color_discrete_sequence=[COLORS["primary"]],
        )
        fig2.update_traces(marker_line_width=0)
        fig2 = plotly_defaults(fig2, 290)
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    c3, c4 = st.columns([1, 1])

    with c3:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Spend by Category</div>', unsafe_allow_html=True)
        cat_spend = df.groupby("Category")["Amount ($)"].sum().reset_index().sort_values("Amount ($)", ascending=True)
        fig3 = px.bar(
            cat_spend, x="Amount ($)", y="Category", orientation="h",
            color_discrete_sequence=[COLORS["primary_light"]],
        )
        fig3.update_traces(marker_line_width=0)
        fig3 = plotly_defaults(fig3, 280)
        st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    with c4:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Top 5 Vendors by Spend</div>', unsafe_allow_html=True)
        top_vendors = (
            df.groupby("Vendor")["Amount ($)"].sum()
              .reset_index().sort_values("Amount ($)", ascending=False).head(5)
        )
        fig4 = px.bar(
            top_vendors, x="Vendor", y="Amount ($)",
            color_discrete_sequence=[COLORS["accent"]],
        )
        fig4.update_traces(marker_line_width=0)
        fig4 = plotly_defaults(fig4, 280)
        fig4.update_xaxes(tickangle=-20)
        st.plotly_chart(fig4, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Recent Invoices</div>', unsafe_allow_html=True)
    recent = df.sort_values("Invoice Date", ascending=False).head(8).copy()
    display_cols = ["Invoice #", "Vendor", "Category", "Invoice Date", "Due Date", "Amount ($)", "Status"]
    recent_display = recent[display_cols].copy()
    recent_display["Amount ($)"] = recent_display["Amount ($)"].apply(fmt_currency)
    recent_display["Status"] = recent_display["Status"].apply(status_badge)
    st.write(recent_display.to_html(escape=False, index=False), unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ──────────────────────────────────────────────
# PAGE: INVOICE MANAGEMENT
# ──────────────────────────────────────────────
elif page == "Invoice Management":
    st.markdown('<div class="ap-header"><div><h1>Invoice Management</h1><p>Create, track, and manage all supplier invoices</p></div></div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📋  Invoice List", "➕  New Invoice"])

    with tab1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        f1, f2, f3, f4 = st.columns([2, 1.5, 1.5, 1])
        with f1:
            search = st.text_input("Search vendor or invoice #", placeholder="e.g. Microsoft or INV-2024001")
        with f2:
            status_filter = st.multiselect("Status", df["Status"].unique().tolist(), default=df["Status"].unique().tolist())
        with f3:
            cat_filter = st.multiselect("Category", df["Category"].unique().tolist(), default=df["Category"].unique().tolist())
        with f4:
            sort_by = st.selectbox("Sort by", ["Invoice Date", "Amount ($)", "Due Date"])

        filtered = df.copy()
        if search:
            filtered = filtered[
                filtered["Vendor"].str.contains(search, case=False) |
                filtered["Invoice #"].str.contains(search, case=False)
            ]
        filtered = filtered[filtered["Status"].isin(status_filter)]
        filtered = filtered[filtered["Category"].isin(cat_filter)]
        filtered = filtered.sort_values(sort_by, ascending=False)

        st.markdown(f"<small style='color:{COLORS['text_light']};'>Showing {len(filtered)} of {len(df)} invoices</small>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        display = filtered[["Invoice #", "Vendor", "Category", "Invoice Date", "Due Date", "Amount ($)", "Status", "Approver", "PO #"]].copy()
        display["Amount ($)"] = display["Amount ($)"].apply(fmt_currency)
        display["Status"]     = display["Status"].apply(status_badge)
        st.write(display.head(50).to_html(escape=False, index=False), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        csv_data = filtered.drop(columns=["Status"]).to_csv(index=False).encode()
        st.download_button("⬇ Export to CSV", csv_data, file_name="invoices_export.csv", mime="text/csv")

    with tab2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Create New Invoice</div>', unsafe_allow_html=True)

        r1c1, r1c2, r1c3 = st.columns(3)
        with r1c1:
            new_vendor = st.selectbox("Vendor *", df_vnd["Vendor"].tolist())
        with r1c2:
            new_po = st.text_input("PO Number", placeholder="PO-XXXXX")
        with r1c3:
            new_cat = st.selectbox("Category *", df["Category"].unique().tolist())

        r2c1, r2c2, r2c3 = st.columns(3)
        with r2c1:
            new_inv_date = st.date_input("Invoice Date *", value=date.today())
        with r2c2:
            new_due_date = st.date_input("Due Date *", value=date.today() + timedelta(days=30))
        with r2c3:
            new_amount = st.number_input("Amount ($) *", min_value=0.0, step=100.0, format="%.2f")

        r3c1, r3c2 = st.columns(2)
        with r3c1:
            new_approver = st.selectbox("Approver *", ["J. Martinez", "S. Patel", "L. Chen", "R. Thompson"])
        with r3c2:
            new_desc = st.text_area("Description / Notes", height=90)

        b1, b2 = st.columns([1, 4])
        with b1:
            if st.button("Submit Invoice"):
                if new_amount > 0:
                    st.success(f"✅ Invoice submitted successfully for {new_vendor} — {fmt_currency(new_amount)}")
                else:
                    st.error("Please enter a valid amount.")
        with b2:
            if st.button("Save as Draft"):
                st.info("📝 Invoice saved as draft.")

        st.markdown('</div>', unsafe_allow_html=True)


# ──────────────────────────────────────────────
# PAGE: VENDOR MASTER
# ──────────────────────────────────────────────
elif page == "Vendor Master":
    st.markdown('<div class="ap-header"><div><h1>Vendor Master</h1><p>Manage supplier profiles, terms, and compliance</p></div></div>', unsafe_allow_html=True)

    v1, v2, v3, v4 = st.columns(4)
    for col, label, val in [
        (v1, "Total Vendors",    str(len(df_vnd))),
        (v2, "Active Contracts", "8"),
        (v3, "Avg Credit Rating","A"),
        (v4, "YTD Total Spend",  fmt_currency(df_vnd["YTD Spend ($)"].sum())),
    ]:
        with col:
            st.markdown(f'<div class="kpi-card"><div class="kpi-label">{label}</div><div class="kpi-value">{val}</div></div>', unsafe_allow_html=True)

    st.markdown("<br/>", unsafe_allow_html=True)

    c_left, c_right = st.columns([2, 1])

    with c_left:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Vendor Directory</div>', unsafe_allow_html=True)
        vsearch = st.text_input("Search vendors", placeholder="Vendor name or category")
        vdf = df_vnd.copy()
        if vsearch:
            vdf = vdf[vdf["Vendor"].str.contains(vsearch, case=False) | vdf["Category"].str.contains(vsearch, case=False)]
        vdf["YTD Spend ($)"] = vdf["YTD Spend ($)"].apply(fmt_currency)
        st.dataframe(vdf, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c_right:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Add New Vendor</div>', unsafe_allow_html=True)
        v_name  = st.text_input("Vendor Name *")
        v_cat   = st.selectbox("Category", ["IT Services", "Software", "Consulting", "Hardware", "Cloud", "Telecom"])
        v_terms = st.selectbox("Payment Terms", ["Net 30", "Net 45", "Net 60", "Net 90"])
        v_cr    = st.selectbox("Credit Rating", ["A+", "A", "A-", "B+", "B"])
        v_email = st.text_input("Contact Email")
        v_tax   = st.text_input("Tax / VAT Number")
        if st.button("Add Vendor"):
            if v_name:
                st.success(f"✅ Vendor '{v_name}' added successfully.")
            else:
                st.error("Vendor name is required.")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">YTD Spend by Vendor</div>', unsafe_allow_html=True)
    spend_chart = df_vnd.sort_values("YTD Spend ($)", ascending=False)
    fig5 = px.bar(
        spend_chart, x="Vendor", y="YTD Spend ($)",
        color="Category",
        color_discrete_sequence=[COLORS["primary"], COLORS["accent"], COLORS["primary_light"],
                                   COLORS["grey_400"], COLORS["info"], COLORS["warning"]],
    )
    fig5.update_traces(marker_line_width=0)
    fig5 = plotly_defaults(fig5, 300)
    fig5.update_xaxes(tickangle=-20)
    st.plotly_chart(fig5, use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)


# ──────────────────────────────────────────────
# PAGE: APPROVAL WORKFLOW
# ──────────────────────────────────────────────
elif page == "Approval Workflow":
    st.markdown('<div class="ap-header"><div><h1>Approval Workflow</h1><p>Review and approve pending invoices</p></div></div>', unsafe_allow_html=True)

    pending = df[df["Status"].isin(["Pending", "Draft"])].sort_values("Due Date").copy()

    w1, w2, w3 = st.columns(3)
    for col, label, val, cls in [
        (w1, "Awaiting Approval", str(len(pending)),                                    ""),
        (w2, "Value Pending",     fmt_currency(pending["Amount ($)"].sum()),              ""),
        (w3, "Overdue Items",     str(len(df[df["Status"] == "Overdue"])),               "kpi-down"),
    ]:
        with col:
            st.markdown(f'<div class="kpi-card"><div class="kpi-label">{label}</div><div class="kpi-value {cls}">{val}</div></div>', unsafe_allow_html=True)

    st.markdown("<br/>", unsafe_allow_html=True)

    filter_approver = st.selectbox("Filter by Approver", ["All"] + ["J. Martinez", "S. Patel", "L. Chen", "R. Thompson"])
    if filter_approver != "All":
        pending = pending[pending["Approver"] == filter_approver]

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Pending Items</div>', unsafe_allow_html=True)
    for _, row in pending.head(10).iterrows():
        col_a, col_b, col_c, col_d, col_e, col_f = st.columns([2, 2, 1.2, 1, 1, 1])
        col_a.markdown(f"**{row['Invoice #']}**<br/><small>{row['Vendor']}</small>", unsafe_allow_html=True)
        col_b.markdown(f"{row['Category']}<br/><small>PO: {row['PO #']}</small>", unsafe_allow_html=True)
        col_c.markdown(f"**{fmt_currency(row['Amount ($)'])}**")
        col_d.markdown(f"Due: {row['Due Date']}")
        if col_e.button("✅ Approve", key=f"ap_{row['Invoice #']}"):
            st.success(f"Approved: {row['Invoice #']}")
        if col_f.button("❌ Reject", key=f"rj_{row['Invoice #']}"):
            st.error(f"Rejected: {row['Invoice #']}")
        st.markdown("<hr style='margin:4px 0; border-color:#E2E6E4;'/>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Approvals by Approver</div>', unsafe_allow_html=True)
    app_counts = df[df["Status"] == "Approved"].groupby("Approver").agg(
        Count=("Invoice #", "count"),
        Value=("Amount ($)", "sum")
    ).reset_index()
    fig6 = px.bar(app_counts, x="Approver", y="Value", color="Count",
                  color_continuous_scale=[[0, COLORS["primary_light"]], [1, COLORS["primary_dark"]]])
    fig6 = plotly_defaults(fig6, 260)
    st.plotly_chart(fig6, use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)


# ──────────────────────────────────────────────
# PAGE: PAYMENT PROCESSING
# ──────────────────────────────────────────────
elif page == "Payment Processing":
    st.markdown('<div class="ap-header"><div><h1>Payment Processing</h1><p>Schedule, execute, and track supplier payments</p></div></div>', unsafe_allow_html=True)

    approved = df[df["Status"] == "Approved"].copy()

    p1, p2, p3, p4 = st.columns(4)
    for col, label, val in [
        (p1, "Ready to Pay",      str(len(approved))),
        (p2, "Total to Disburse", fmt_currency(approved["Amount ($)"].sum())),
        (p3, "Paid This Month",   fmt_currency(df[df["Status"] == "Paid"]["Amount ($)"].sum())),
        (p4, "Avg Payment Cycle", "28 days"),
    ]:
        with col:
            st.markdown(f'<div class="kpi-card"><div class="kpi-label">{label}</div><div class="kpi-value">{val}</div></div>', unsafe_allow_html=True)

    st.markdown("<br/>", unsafe_allow_html=True)

    c_pay, c_sched = st.columns([2, 1])

    with c_pay:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Approved — Ready for Payment</div>', unsafe_allow_html=True)
        disp = approved[["Invoice #", "Vendor", "Amount ($)", "Due Date", "Approver"]].copy()
        disp["Amount ($)"] = disp["Amount ($)"].apply(fmt_currency)
        st.dataframe(disp, use_container_width=True, hide_index=True)
        if st.button("🚀 Process All Payments"):
            st.success(f"✅ Payment run initiated for {len(approved)} invoices totalling {fmt_currency(approved['Amount ($)'].sum())}")
        st.markdown('</div>', unsafe_allow_html=True)

    with c_sched:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Schedule Payment</div>', unsafe_allow_html=True)
        pay_inv    = st.text_input("Invoice # to Pay")
        pay_method = st.selectbox("Payment Method", ["Bank Transfer (ACH)", "Wire Transfer", "SWIFT", "Cheque"])
        pay_date   = st.date_input("Payment Date", value=date.today())
        pay_ref    = st.text_input("Bank Reference", placeholder="Optional reference")
        if st.button("Schedule Payment"):
            if pay_inv:
                st.success(f"✅ {pay_inv} scheduled for {pay_date.strftime('%d %b %Y')} via {pay_method}")
            else:
                st.error("Enter an invoice number.")
        st.markdown('</div>', unsafe_allow_html=True)

    paid_df = df[df["Status"] == "Paid"].copy()
    paid_df["Month"] = pd.to_datetime(paid_df["Invoice Date"]).dt.to_period("M").astype(str)
    monthly_paid = paid_df.groupby("Month")["Amount ($)"].sum().reset_index().sort_values("Month").tail(6)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Monthly Payment Trend</div>', unsafe_allow_html=True)
    fig7 = go.Figure()
    fig7.add_trace(go.Scatter(
        x=monthly_paid["Month"], y=monthly_paid["Amount ($)"],
        fill="tozeroy", mode="lines+markers",
        line=dict(color=COLORS["primary"], width=2.5),
        fillcolor="rgba(76,175,130,0.12)",
        marker=dict(size=6, color=COLORS["primary_dark"]),
    ))
    fig7 = plotly_defaults(fig7, 270)
    st.plotly_chart(fig7, use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)


# ──────────────────────────────────────────────
# PAGE: ANALYTICS & REPORTS
# ──────────────────────────────────────────────
elif page == "Analytics & Reports":
    st.markdown('<div class="ap-header"><div><h1>Analytics & Reports</h1><p>Deep-dive insights for finance leadership</p></div></div>', unsafe_allow_html=True)

    tab_a, tab_b, tab_c = st.tabs(["📊  Spend Analytics", "⏱  Aging Report", "📥  Export Reports"])

    with tab_a:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">Spend Trend — All Categories</div>', unsafe_allow_html=True)
            trend = df.copy()
            trend["Month"] = pd.to_datetime(trend["Invoice Date"]).dt.to_period("M").astype(str)
            trend_grp = trend.groupby(["Month", "Category"])["Amount ($)"].sum().reset_index().sort_values("Month")
            fig8 = px.line(
                trend_grp, x="Month", y="Amount ($)", color="Category",
                color_discrete_sequence=[COLORS["primary"], COLORS["accent"], COLORS["primary_light"],
                                          COLORS["grey_400"], COLORS["info"], COLORS["warning"]],
            )
            fig8 = plotly_defaults(fig8, 300)
            st.plotly_chart(fig8, use_container_width=True, config={"displayModeBar": False})
            st.markdown('</div>', unsafe_allow_html=True)

        with c2:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">Invoice Volume vs. Value</div>', unsafe_allow_html=True)
            scatter_df = df.groupby("Vendor").agg(
                Count=("Invoice #", "count"),
                Total=("Amount ($)", "sum")
            ).reset_index()
            fig9 = px.scatter(
                scatter_df, x="Count", y="Total", text="Vendor",
                color="Total",
                color_continuous_scale=[[0, COLORS["primary_light"]], [1, COLORS["primary_dark"]]],
                size="Count",
            )
            fig9.update_traces(textposition="top center", textfont_size=9)
            fig9 = plotly_defaults(fig9, 300)
            st.plotly_chart(fig9, use_container_width=True, config={"displayModeBar": False})
            st.markdown('</div>', unsafe_allow_html=True)

    with tab_b:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Invoice Aging Analysis</div>', unsafe_allow_html=True)
        today_dt = pd.Timestamp(date.today())
        aging = df[df["Status"].isin(["Pending", "Overdue"])].copy()
        aging["Days Outstanding"] = (today_dt - pd.to_datetime(aging["Invoice Date"])).dt.days
        aging["Bucket"] = pd.cut(
            aging["Days Outstanding"],
            bins=[0, 30, 60, 90, 999],
            labels=["0-30 days", "31-60 days", "61-90 days", "90+ days"]
        )
        bucket_df = aging.groupby("Bucket", observed=True).agg(
            Count=("Invoice #", "count"),
            Amount=("Amount ($)", "sum")
        ).reset_index()
        fig10 = px.bar(
            bucket_df, x="Bucket", y="Amount", color="Count",
            color_continuous_scale=[[0, COLORS["primary_light"]], [1, COLORS["danger"]]],
        )
        fig10 = plotly_defaults(fig10, 300)
        st.plotly_chart(fig10, use_container_width=True, config={"displayModeBar": False})

        disp_aging = aging[["Invoice #", "Vendor", "Amount ($)", "Invoice Date", "Days Outstanding", "Bucket"]].copy()
        disp_aging["Amount ($)"] = disp_aging["Amount ($)"].apply(fmt_currency)
        st.dataframe(disp_aging.sort_values("Days Outstanding", ascending=False).head(20), use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with tab_c:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Download Reports</div>', unsafe_allow_html=True)

        r1, r2, r3 = st.columns(3)
        with r1:
            csv_all = df.to_csv(index=False).encode()
            st.download_button("📄 Full Invoice Register (CSV)", csv_all, "invoice_register.csv", "text/csv")
        with r2:
            csv_paid = df[df["Status"] == "Paid"].to_csv(index=False).encode()
            st.download_button("💳 Paid Invoices (CSV)", csv_paid, "paid_invoices.csv", "text/csv")
        with r3:
            csv_ov = df[df["Status"] == "Overdue"].to_csv(index=False).encode()
            st.download_button("⚠️ Overdue Report (CSV)", csv_ov, "overdue_invoices.csv", "text/csv")

        st.markdown("<br/>", unsafe_allow_html=True)
        st.markdown("**Report Parameters**")
        rp1, rp2, rp3 = st.columns(3)
        with rp1:
            rpt_type = st.selectbox("Report Type", ["AP Aging", "Vendor Spend", "Payment Run", "Accruals"])
        with rp2:
            rpt_from = st.date_input("From Date", value=date.today() - timedelta(days=90))
        with rp3:
            rpt_to   = st.date_input("To Date", value=date.today())
        if st.button("Generate Custom Report"):
            st.success(f"✅ {rpt_type} report generated for {rpt_from} → {rpt_to}")
        st.markdown('</div>', unsafe_allow_html=True)


# ──────────────────────────────────────────────
# PAGE: SETTINGS
# ──────────────────────────────────────────────
elif page == "Settings":
    st.markdown('<div class="ap-header"><div><h1>Settings</h1><p>Configure AP module preferences and integrations</p></div></div>', unsafe_allow_html=True)

    s1, s2 = st.columns(2)

    with s1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">General Settings</div>', unsafe_allow_html=True)
        st.selectbox("Default Currency",     ["USD", "EUR", "GBP", "SGD", "AUD"])
        st.selectbox("Fiscal Year Start",    ["January", "April", "July", "October"])
        st.selectbox("Default Payment Terms",["Net 30", "Net 45", "Net 60"])
        st.number_input("Approval Threshold ($) — Auto-approve below", value=500, step=100)
        st.toggle("Enable 3-way PO Matching",  value=True)
        st.toggle("Auto-send Reminders",        value=True)
        st.toggle("Enable Duplicate Detection", value=True)
        if st.button("Save General Settings"):
            st.success("✅ Settings saved.")
        st.markdown('</div>', unsafe_allow_html=True)

    with s2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Approval Workflow Rules</div>', unsafe_allow_html=True)
        st.markdown("**Approval Tiers**")
        st.number_input("Tier 1 — Up to ($)",   value=5_000,   step=500)
        st.number_input("Tier 2 — Up to ($)",   value=50_000,  step=1_000)
        st.number_input("Tier 3 — Above ($)",   value=50_001,  step=1_000, disabled=True)
        st.selectbox("Tier 1 Approver", ["J. Martinez", "S. Patel", "L. Chen"])
        st.selectbox("Tier 2 Approver", ["R. Thompson", "CFO"])
        st.text_input("Escalation Email", value="finance-alerts@company.com")
        if st.button("Save Workflow Rules"):
            st.success("✅ Workflow rules updated.")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Integrations</div>', unsafe_allow_html=True)
    i1, i2, i3, i4 = st.columns(4)
    integrations = [
        ("ERP System",    "SAP S/4HANA",   True),
        ("Banking",       "Citibank API",   True),
        ("OCR Engine",    "AWS Textract",   False),
        ("Audit Trail",   "Workiva",        False),
    ]
    for col, (name, system, connected) in zip([i1, i2, i3, i4], integrations):
        status_str  = "🟢 Connected"   if connected else "🔴 Disconnected"
        btn_label   = "Disconnect"     if connected else "Connect"
        with col:
            st.markdown(f"**{name}**<br/><small>{system}</small><br/>{status_str}", unsafe_allow_html=True)
            st.button(btn_label, key=f"int_{name}")
    st.markdown('</div>', unsafe_allow_html=True)


# ──────────────────────────────────────────────
# FOOTER
# ──────────────────────────────────────────────
st.markdown(f"""
<div style='text-align:center; color:{COLORS["text_light"]}; font-size:0.72rem; padding: 2rem 0 1rem;'>
    Accounts Payable Module &nbsp;·&nbsp; Finance Function &nbsp;·&nbsp; FY 2025
    &nbsp;·&nbsp; Built with Streamlit
</div>
""", unsafe_allow_html=True)
