import dash
from dash import html, dcc, callback, Input, Output, State
import json
import os
from datetime import datetime, date

dash.register_page(__name__, path="/expenses", name="Expenses")

PRIMARY = "#7B61FF"
SECONDARY = "#4DFFD2"
TEXT_SECONDARY = "#8A8A8A"
SURFACE = "#141414"
BORDER = "#222222"
BACKGROUND = "#0A0A0A"
SUCCESS = "#4DFFD2"
WARNING = "#F5A623"
DANGER = "#FF4D4D"

DATA_FILE = "data/expenses.json"
CATEGORIES = ["META", "Shipping", "Product", "OPEX", "Salary/CEO", "R/R/E", "Other"]
STATUSES = ["Billed ✅", "Pending 🕐", "Scheduled 📅"]

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

def save_data(data):
    os.makedirs("data", exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def check_carry_over(data):
    current_month = datetime.now().strftime("%Y-%m")
    updated = False
    for item in data:
        if item.get("status") == "Pending 🕐":
            item_month = item.get("month", "")
            if item_month and item_month < current_month:
                item["carried_over"] = True
                item["month"] = current_month
                updated = True
    if updated:
        save_data(data)
    return data

def status_color(status):
    if "Billed" in status:
        return SUCCESS
    elif "Pending" in status:
        return WARNING
    return TEXT_SECONDARY

def input_style():
    return {
        "backgroundColor": SURFACE, "color": "white",
        "border": f"1px solid {BORDER}", "borderRadius": "8px",
        "padding": "8px 12px", "width": "100%", "fontSize": "14px"
    }

def label_style():
    return {"color": TEXT_SECONDARY, "fontSize": "12px", "marginBottom": "4px", "display": "block"}

def get_months():
    now = datetime.now()
    months = []
    for i in range(-1, 3):
        m = datetime(now.year, now.month, 1)
        from dateutil.relativedelta import relativedelta
        month = (m + relativedelta(months=i)).strftime("%Y-%m")
        months.append({"label": month, "value": month})
    return months

layout = html.Div([
    html.H2("Expenses Tracker", style={"color": "white", "marginBottom": "24px", "fontWeight": "700"}),

    # Carry-over banner
    html.Div(id="carry-over-banner", style={"marginBottom": "16px"}),

    # Add expense form
    html.Div([
        html.H4("Add Expense", style={"color": "white", "marginBottom": "16px"}),
        html.Div([
            html.Div([
                html.Label("Category", style=label_style()),
                dcc.Dropdown(
                    id="exp-category", options=[{"label": c, "value": c} for c in CATEGORIES],
                    value="META", clearable=False,
                    style={"backgroundColor": SURFACE, "color": "white"}
                )
            ], style={"flex": "1"}),
            html.Div([
                html.Label("Subcategory", style=label_style()),
                dcc.Input(id="exp-subcategory", type="text", placeholder="e.g. Ad spend Q2",
                         style=input_style())
            ], style={"flex": "1"}),
            html.Div([
                html.Label("Amount $", style=label_style()),
                dcc.Input(id="exp-amount", type="number", placeholder="0.00", style=input_style())
            ], style={"flex": "1"}),
            html.Div([
                html.Label("Due Date", style=label_style()),
                dcc.DatePickerSingle(id="exp-due-date", date=str(date.today()), display_format="DD/MM/YYYY")
            ], style={"flex": "1"}),
            html.Div([
                html.Label("Status", style=label_style()),
                dcc.Dropdown(
                    id="exp-status", options=[{"label": s, "value": s} for s in STATUSES],
                    value="Pending 🕐", clearable=False,
                    style={"backgroundColor": SURFACE}
                )
            ], style={"flex": "1"}),
            html.Div([
                html.Label("Month", style=label_style()),
                dcc.Dropdown(
                    id="exp-month",
                    options=[{"label": datetime.now().strftime("%Y-%m"), "value": datetime.now().strftime("%Y-%m")}],
                    value=datetime.now().strftime("%Y-%m"),
                    clearable=False,
                    style={"backgroundColor": SURFACE}
                )
            ], style={"flex": "1"}),
            html.Div([
                html.Label("Notes", style=label_style()),
                dcc.Input(id="exp-notes", type="text", placeholder="Optional note", style=input_style())
            ], style={"flex": "2"}),
        ], style={"display": "flex", "gap": "12px", "flexWrap": "wrap", "marginBottom": "16px"}),

        html.Button("+ Add Expense", id="add-expense-btn", n_clicks=0, style={
            "background": f"linear-gradient(135deg, {PRIMARY}, {SECONDARY})",
            "color": BACKGROUND, "border": "none", "borderRadius": "8px",
            "padding": "10px 24px", "fontWeight": "700", "cursor": "pointer"
        }),
        html.Div(id="add-expense-status", style={"marginTop": "8px"}),
    ], style={
        "backgroundColor": SURFACE, "border": f"1px solid {BORDER}",
        "borderRadius": "12px", "padding": "20px", "marginBottom": "24px"
    }),

    # Filters
    html.Div([
        html.Div([
            html.Label("Filter by Month", style=label_style()),
            dcc.Dropdown(
                id="filter-month",
                value=datetime.now().strftime("%Y-%m"),
                clearable=False,
                style={"backgroundColor": SURFACE}
            )
        ], style={"flex": "1", "maxWidth": "200px"}),
        html.Div([
            html.Label("Filter by Category", style=label_style()),
            dcc.Dropdown(
                id="filter-category",
                options=[{"label": "All", "value": "All"}] + [{"label": c, "value": c} for c in CATEGORIES],
                value="All", clearable=False,
                style={"backgroundColor": SURFACE}
            )
        ], style={"flex": "1", "maxWidth": "200px"}),
    ], style={"display": "flex", "gap": "16px", "marginBottom": "16px"}),

    # Expenses table
    html.Div(id="expenses-table", style={"marginBottom": "24px"}),

    # Summary cards
    html.H3("Monthly Summary", style={"color": "white", "marginBottom": "16px"}),
    html.Div(id="expenses-summary", style={"display": "flex", "gap": "12px", "flexWrap": "wrap"}),

    dcc.Store(id="expenses-store"),

], style={"color": "white", "fontFamily": "system-ui, sans-serif"})


@callback(
    Output("add-expense-status", "children"),
    Output("expenses-store", "data"),
    Input("add-expense-btn", "n_clicks"),
    State("exp-category", "value"),
    State("exp-subcategory", "value"),
    State("exp-amount", "value"),
    State("exp-due-date", "date"),
    State("exp-status", "value"),
    State("exp-month", "value"),
    State("exp-notes", "value"),
    prevent_initial_call=True,
)
def add_expense(n_clicks, category, subcategory, amount, due_date, status, month, notes):
    if not amount:
        return html.P("⚠️ Amount is required", style={"color": WARNING}), dash.no_update

    record = {
        "id": int(datetime.now().timestamp() * 1000),
        "category": category,
        "subcategory": subcategory or "",
        "amount": float(amount),
        "due_date": str(due_date),
        "status": status,
        "month": month,
        "notes": notes or "",
        "carried_over": False,
    }

    data = load_data()
    data.append(record)
    save_data(data)

    return html.P(f"✅ Added {category} ${amount:.2f}", style={"color": SUCCESS}), n_clicks


@callback(
    Output("filter-month", "options"),
    Output("carry-over-banner", "children"),
    Input("expenses-store", "data"),
)
def update_filters(_):
    data = load_data()
    data = check_carry_over(data)

    months = sorted(set(r.get("month", "") for r in data), reverse=True)
    if not months:
        months = [datetime.now().strftime("%Y-%m")]
    options = [{"label": m, "value": m} for m in months]

    carried = [r for r in data if r.get("carried_over")]
    banner = html.Div(
        f"⚠️ {len(carried)} expense(s) carried over from previous month",
        style={
            "backgroundColor": "rgba(245,166,35,0.15)",
            "border": f"1px solid {WARNING}",
            "borderRadius": "8px", "padding": "12px 16px",
            "color": WARNING, "fontSize": "14px"
        }
    ) if carried else html.Div()

    return options, banner


@callback(
    Output("expenses-table", "children"),
    Output("expenses-summary", "children"),
    Input("filter-month", "value"),
    Input("filter-category", "value"),
    Input("expenses-store", "data"),
)
def update_table(month, category, _):
    data = load_data()
    filtered = [r for r in data if r.get("month") == month]
    if category != "All":
        filtered = [r for r in filtered if r.get("category") == category]

    if not filtered:
        return html.P("No expenses for this period.", style={"color": TEXT_SECONDARY}), []

    header = html.Tr([
        html.Th(col, style={"color": TEXT_SECONDARY, "padding": "8px 12px", "fontSize": "12px", "textAlign": "left"})
        for col in ["Category", "Subcategory", "Amount", "Due Date", "Status", "Notes", "Carried Over"]
    ])

    rows = []
    for r in sorted(filtered, key=lambda x: x.get("due_date", "")):
        sc = status_color(r.get("status", ""))
        co = r.get("carried_over", False)
        rows.append(html.Tr([
            html.Td(r.get("category", ""), style={"padding": "8px 12px", "fontSize": "13px", "color": "white"}),
            html.Td(r.get("subcategory", ""), style={"padding": "8px 12px", "fontSize": "13px", "color": TEXT_SECONDARY}),
            html.Td(f"${r.get('amount', 0):,.2f}", style={"padding": "8px 12px", "fontSize": "13px", "color": "white", "fontWeight": "600"}),
            html.Td(r.get("due_date", ""), style={"padding": "8px 12px", "fontSize": "13px", "color": TEXT_SECONDARY}),
            html.Td(r.get("status", ""), style={"padding": "8px 12px", "fontSize": "13px", "color": sc, "fontWeight": "600"}),
            html.Td(r.get("notes", ""), style={"padding": "8px 12px", "fontSize": "13px", "color": TEXT_SECONDARY}),
            html.Td("↗️ Yes" if co else "—", style={"padding": "8px 12px", "fontSize": "13px", "color": WARNING if co else TEXT_SECONDARY}),
        ], style={"borderTop": f"1px solid {BORDER}"}))

    table = html.Div([
        html.Table(
            [html.Thead(header), html.Tbody(rows)],
            style={"width": "100%", "borderCollapse": "collapse", "backgroundColor": SURFACE, "borderRadius": "8px"}
        )
    ], style={"overflowX": "auto"})

    # Summary
    all_month = [r for r in data if r.get("month") == month]
    billed = sum(r["amount"] for r in all_month if "Billed" in r.get("status", ""))
    pending = sum(r["amount"] for r in all_month if "Pending" in r.get("status", ""))
    scheduled = sum(r["amount"] for r in all_month if "Scheduled" in r.get("status", ""))
    total = billed + pending + scheduled

    def sum_card(label, value, color):
        return html.Div([
            html.P(label, style={"color": TEXT_SECONDARY, "fontSize": "11px", "margin": "0 0 4px 0", "textTransform": "uppercase"}),
            html.P(f"${value:,.2f}", style={"color": color, "fontSize": "24px", "fontWeight": "700", "margin": "0"}),
        ], style={
            "backgroundColor": SURFACE, "border": f"1px solid {BORDER}",
            "borderLeft": f"3px solid {color}", "borderRadius": "12px",
            "padding": "16px", "flex": "1", "minWidth": "150px"
        })

    cards = [
        sum_card("Billed ✅", billed, DANGER),
        sum_card("Soon Billed 🕐", pending + scheduled, WARNING),
        sum_card("Total", total, "white"),
    ]

    return table, cards
