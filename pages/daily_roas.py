import dash
from dash import html, dcc, callback, Input, Output, State, ALL
import plotly.graph_objects as go
import json
import os
from datetime import date, datetime

dash.register_page(__name__, path="/daily-roas", name="Daily ROAS")

PRIMARY = "#7B61FF"
SECONDARY = "#4DFFD2"
TEXT_SECONDARY = "#8A8A8A"
SURFACE = "#141414"
BORDER = "#222222"
BACKGROUND = "#0A0A0A"
SUCCESS = "#4DFFD2"
WARNING = "#F5A623"
DANGER = "#FF4D4D"

DATA_FILE = "data/daily_roas.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

def save_data(data):
    os.makedirs("data", exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def roas_color(roas):
    if roas >= 3:
        return SUCCESS
    elif roas >= 1.5:
        return WARNING
    return DANGER

def roas_bg(roas):
    if roas >= 3:
        return "rgba(77,255,210,0.08)"
    elif roas >= 1.5:
        return "rgba(245,166,35,0.08)"
    return "rgba(255,77,77,0.08)"

def input_field(label, id, placeholder="", value=None, input_type="number"):
    return html.Div([
        html.Label(label, style={"color": TEXT_SECONDARY, "fontSize": "12px", "marginBottom": "4px", "display": "block"}),
        dcc.Input(
            id=id, type=input_type, placeholder=placeholder, value=value,
            style={
                "backgroundColor": SURFACE, "color": "white",
                "border": f"1px solid {BORDER}", "borderRadius": "8px",
                "padding": "8px 12px", "width": "100%", "fontSize": "14px"
            }
        )
    ], style={"flex": "1", "minWidth": "100px"})

def metric_card(label, value, color="white"):
    return html.Div([
        html.P(label, style={"color": TEXT_SECONDARY, "fontSize": "11px", "margin": "0 0 4px 0", "textTransform": "uppercase"}),
        html.P(value, style={"color": color, "fontSize": "22px", "fontWeight": "700", "margin": "0"}),
    ], style={
        "backgroundColor": SURFACE, "border": f"1px solid {BORDER}",
        "borderLeft": f"3px solid {color}", "borderRadius": "12px",
        "padding": "16px", "flex": "1"
    })

layout = html.Div([
    html.H2("Daily ROAS Tracker", style={"color": "white", "marginBottom": "24px", "fontWeight": "700"}),

    # Entry form
    html.Div([
        html.Div([
            html.Div([
                html.Label("Date", style={"color": TEXT_SECONDARY, "fontSize": "12px", "marginBottom": "4px", "display": "block"}),
                dcc.DatePickerSingle(
                    id="entry-date", date=str(date.today()),
                    display_format="DD/MM/YYYY",
                    style={"backgroundColor": SURFACE}
                )
            ], style={"minWidth": "140px"}),
            input_field("Ad Spend $", "ad-spend"),
            input_field("FB Tax $", "fb-tax", "auto ~5%"),
            input_field("SP% $", "sp-pct", "Shopify fee"),
            input_field("GOGS $", "gogs", "Cost of goods"),
            input_field("Revenue $", "revenue-input"),
            input_field("Orders", "orders-input", input_type="number"),
        ], style={"display": "flex", "gap": "12px", "flexWrap": "wrap", "marginBottom": "16px"}),

        # Auto-calculated preview
        html.Div(id="entry-preview", style={"marginBottom": "16px"}),

        html.Button("+ Add Entry", id="add-entry-btn", n_clicks=0, style={
            "background": f"linear-gradient(135deg, {PRIMARY}, {SECONDARY})",
            "color": BACKGROUND, "border": "none", "borderRadius": "8px",
            "padding": "10px 24px", "fontWeight": "700", "cursor": "pointer", "fontSize": "14px"
        }),
        html.Div(id="add-entry-status", style={"marginTop": "8px"}),
    ], style={
        "backgroundColor": SURFACE, "border": f"1px solid {BORDER}",
        "borderRadius": "12px", "padding": "20px", "marginBottom": "24px"
    }),

    # Month selector
    html.Div([
        html.Label("Select Month", style={"color": TEXT_SECONDARY, "fontSize": "12px", "marginBottom": "4px", "display": "block"}),
        dcc.Dropdown(
            id="month-selector",
            style={"backgroundColor": SURFACE, "color": "white", "border": f"1px solid {BORDER}"},
            clearable=False
        ),
    ], style={"marginBottom": "24px", "maxWidth": "300px"}),

    # Records table
    html.Div(id="records-table", style={"marginBottom": "24px"}),

    # Charts tabs
    html.Div([
        dcc.Tabs(id="roas-tabs", value="month", children=[
            dcc.Tab(label="День", value="day", style={"backgroundColor": SURFACE, "color": TEXT_SECONDARY},
                    selected_style={"backgroundColor": PRIMARY, "color": "white"}),
            dcc.Tab(label="Тиждень", value="week", style={"backgroundColor": SURFACE, "color": TEXT_SECONDARY},
                    selected_style={"backgroundColor": PRIMARY, "color": "white"}),
            dcc.Tab(label="Місяць", value="month", style={"backgroundColor": SURFACE, "color": TEXT_SECONDARY},
                    selected_style={"backgroundColor": PRIMARY, "color": "white"}),
        ]),
        html.Div(id="tabs-content", style={"marginTop": "16px"}),
    ], style={
        "backgroundColor": SURFACE, "border": f"1px solid {BORDER}",
        "borderRadius": "12px", "padding": "20px", "marginBottom": "24px"
    }),

    # Monthly summary cards
    html.H3("Monthly Summary", style={"color": "white", "marginBottom": "16px"}),
    html.Div(id="monthly-summary", style={"display": "flex", "gap": "12px", "flexWrap": "wrap"}),

    # Store for refresh trigger
    dcc.Store(id="data-store"),

], style={"color": "white", "fontFamily": "system-ui, sans-serif"})


@callback(
    Output("entry-preview", "children"),
    Input("ad-spend", "value"),
    Input("fb-tax", "value"),
    Input("sp-pct", "value"),
    Input("gogs", "value"),
    Input("revenue-input", "value"),
    Input("orders-input", "value"),
)
def update_preview(ad_spend, fb_tax, sp_pct, gogs, revenue, orders):
    ad_spend = ad_spend or 0
    fb_tax = fb_tax or (ad_spend * 0.05)
    sp_pct = sp_pct or 0
    gogs = gogs or 0
    revenue = revenue or 0
    orders = orders or 1

    aov = revenue / orders if orders else 0
    roas = revenue / ad_spend if ad_spend else 0
    margin = revenue - ad_spend - fb_tax - sp_pct - gogs
    rc = roas_color(roas)

    return html.Div([
        html.Span(f"AOV: ${aov:.2f}", style={"color": TEXT_SECONDARY, "marginRight": "24px", "fontSize": "14px"}),
        html.Span(f"ROAS: {roas:.2f}x", style={"color": rc, "fontWeight": "700", "marginRight": "24px", "fontSize": "14px"}),
        html.Span(f"Margin: ${margin:.2f}", style={"color": SUCCESS if margin > 0 else DANGER, "fontSize": "14px"}),
    ])


@callback(
    Output("add-entry-status", "children"),
    Output("data-store", "data"),
    Input("add-entry-btn", "n_clicks"),
    State("entry-date", "date"),
    State("ad-spend", "value"),
    State("fb-tax", "value"),
    State("sp-pct", "value"),
    State("gogs", "value"),
    State("revenue-input", "value"),
    State("orders-input", "value"),
    prevent_initial_call=True,
)
def add_entry(n_clicks, entry_date, ad_spend, fb_tax, sp_pct, gogs, revenue, orders):
    if not ad_spend or not revenue:
        return html.P("⚠️ Fill in at least Ad Spend and Revenue", style={"color": WARNING}), dash.no_update

    ad_spend = float(ad_spend)
    fb_tax = float(fb_tax) if fb_tax else round(ad_spend * 0.05, 2)
    sp_pct = float(sp_pct) if sp_pct else 0
    gogs = float(gogs) if gogs else 0
    revenue = float(revenue)
    orders = int(orders) if orders else 0

    aov = revenue / orders if orders else 0
    roas = revenue / ad_spend if ad_spend else 0
    margin = revenue - ad_spend - fb_tax - sp_pct - gogs

    record = {
        "date": str(entry_date),
        "ad_spend": ad_spend,
        "fb_tax": fb_tax,
        "sp_pct": sp_pct,
        "gogs": gogs,
        "revenue": revenue,
        "orders": orders,
        "aov": round(aov, 2),
        "roas": round(roas, 2),
        "margin": round(margin, 2),
    }

    data = load_data()
    data.append(record)
    save_data(data)

    return html.P(f"✅ Entry added for {entry_date}", style={"color": SUCCESS}), n_clicks


@callback(
    Output("month-selector", "options"),
    Output("month-selector", "value"),
    Input("data-store", "data"),
)
def update_month_selector(_):
    data = load_data()
    if not data:
        current = datetime.now().strftime("%Y-%m")
        return [{"label": current, "value": current}], current

    months = sorted(set(r["date"][:7] for r in data), reverse=True)
    options = [{"label": m, "value": m} for m in months]
    return options, months[0]


@callback(
    Output("records-table", "children"),
    Output("monthly-summary", "children"),
    Input("month-selector", "value"),
    Input("data-store", "data"),
)
def update_table_and_summary(month, _):
    data = load_data()
    if not month:
        month = datetime.now().strftime("%Y-%m")

    month_data = [r for r in data if r["date"].startswith(month)]

    if not month_data:
        return html.P("No data for this month. Add entries above.", style={"color": TEXT_SECONDARY}), []

    # Table
    header = html.Tr([
        html.Th(col, style={"color": TEXT_SECONDARY, "padding": "8px 12px", "fontSize": "12px", "textAlign": "left", "fontWeight": "600"})
        for col in ["Date", "Revenue", "Ad Spend", "FB Tax", "SP%", "GOGS", "Orders", "AOV", "ROAS", "Margin $"]
    ])

    rows = []
    for i, r in enumerate(sorted(month_data, key=lambda x: x["date"])):
        rc = roas_color(r["roas"])
        bg = roas_bg(r["roas"])
        rows.append(html.Tr([
            html.Td(r["date"], style={"padding": "8px 12px", "fontSize": "13px"}),
            html.Td(f"${r['revenue']:,.0f}", style={"padding": "8px 12px", "fontSize": "13px"}),
            html.Td(f"${r['ad_spend']:,.0f}", style={"padding": "8px 12px", "fontSize": "13px"}),
            html.Td(f"${r['fb_tax']:,.0f}", style={"padding": "8px 12px", "fontSize": "13px"}),
            html.Td(f"${r['sp_pct']:,.0f}", style={"padding": "8px 12px", "fontSize": "13px"}),
            html.Td(f"${r['gogs']:,.0f}", style={"padding": "8px 12px", "fontSize": "13px"}),
            html.Td(f"{r['orders']}", style={"padding": "8px 12px", "fontSize": "13px"}),
            html.Td(f"${r['aov']:,.2f}", style={"padding": "8px 12px", "fontSize": "13px"}),
            html.Td(f"{r['roas']:.2f}x", style={"padding": "8px 12px", "fontSize": "13px", "color": rc, "fontWeight": "700"}),
            html.Td(f"${r['margin']:,.0f}", style={"padding": "8px 12px", "fontSize": "13px", "color": SUCCESS if r["margin"] > 0 else DANGER}),
        ], style={"backgroundColor": bg, "borderTop": f"1px solid {BORDER}"}))

    table = html.Div([
        html.H3(f"Records — {month}", style={"color": "white", "marginBottom": "12px"}),
        html.Div([
            html.Table(
                [html.Thead(header), html.Tbody(rows)],
                style={"width": "100%", "borderCollapse": "collapse", "backgroundColor": SURFACE, "borderRadius": "8px"}
            )
        ], style={"overflowX": "auto"})
    ])

    # Summary cards
    total_rev = sum(r["revenue"] for r in month_data)
    total_spend = sum(r["ad_spend"] for r in month_data)
    avg_roas = total_rev / total_spend if total_spend else 0
    total_margin = sum(r["margin"] for r in month_data)
    total_orders = sum(r["orders"] for r in month_data)
    avg_aov = total_rev / total_orders if total_orders else 0
    rc = roas_color(avg_roas)

    cards = [
        metric_card("Total Revenue", f"${total_rev:,.0f}", PRIMARY),
        metric_card("Total Ad Spend", f"${total_spend:,.0f}", TEXT_SECONDARY),
        metric_card("Avg ROAS", f"{avg_roas:.2f}x", rc),
        metric_card("Total Margin", f"${total_margin:,.0f}", SUCCESS if total_margin > 0 else DANGER),
        metric_card("Total Orders", f"{total_orders:,}", SECONDARY),
        metric_card("Avg AOV", f"${avg_aov:.2f}", "white"),
    ]

    return table, cards


@callback(
    Output("tabs-content", "children"),
    Input("roas-tabs", "value"),
    Input("month-selector", "value"),
    Input("data-store", "data"),
)
def update_tabs(tab, month, _):
    data = load_data()
    if not month:
        month = datetime.now().strftime("%Y-%m")
    month_data = sorted([r for r in data if r["date"].startswith(month)], key=lambda x: x["date"])

    if not month_data:
        return html.P("No data available.", style={"color": TEXT_SECONDARY})

    if tab == "month":
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=[r["date"] for r in month_data],
            y=[r["roas"] for r in month_data],
            mode="lines+markers",
            line={"color": PRIMARY, "width": 2},
            marker={"color": [roas_color(r["roas"]) for r in month_data], "size": 8},
            name="ROAS"
        ))
        fig.add_hline(y=3, line_dash="dash", line_color=SUCCESS, annotation_text="Target 3x")
        fig.update_layout(
            paper_bgcolor=BACKGROUND, plot_bgcolor=SURFACE,
            font={"color": "white"}, height=300,
            xaxis={"showgrid": False}, yaxis={"showgrid": False},
            margin={"l": 20, "r": 20, "t": 20, "b": 20}
        )
        return dcc.Graph(figure=fig, config={"displayModeBar": False})

    elif tab == "week":
        from collections import defaultdict
        weekly = defaultdict(lambda: {"revenue": 0, "spend": 0, "orders": 0, "margin": 0, "count": 0})
        for r in month_data:
            d = datetime.strptime(r["date"], "%Y-%m-%d")
            week = f"W{d.isocalendar()[1]}"
            weekly[week]["revenue"] += r["revenue"]
            weekly[week]["spend"] += r["ad_spend"]
            weekly[week]["orders"] += r["orders"]
            weekly[week]["margin"] += r["margin"]
            weekly[week]["count"] += 1

        weeks = sorted(weekly.keys())
        fig = go.Figure()
        fig.add_trace(go.Bar(x=weeks, y=[weekly[w]["revenue"] for w in weeks], name="Revenue", marker_color=PRIMARY))
        fig.add_trace(go.Bar(x=weeks, y=[weekly[w]["spend"] for w in weeks], name="Ad Spend", marker_color=DANGER))
        fig.update_layout(
            paper_bgcolor=BACKGROUND, plot_bgcolor=SURFACE,
            font={"color": "white"}, height=300, barmode="group",
            xaxis={"showgrid": False}, yaxis={"showgrid": False},
            margin={"l": 20, "r": 20, "t": 20, "b": 20}
        )
        return dcc.Graph(figure=fig, config={"displayModeBar": False})

    elif tab == "day":
        if not month_data:
            return html.P("No data.", style={"color": TEXT_SECONDARY})
        last = month_data[-1]
        rc = roas_color(last["roas"])
        return html.Div([
            html.H4(f"Last entry: {last['date']}", style={"color": "white", "marginBottom": "16px"}),
            html.Div([
                metric_card("Revenue", f"${last['revenue']:,.0f}", PRIMARY),
                metric_card("Ad Spend", f"${last['ad_spend']:,.0f}", TEXT_SECONDARY),
                metric_card("ROAS", f"{last['roas']:.2f}x", rc),
                metric_card("Margin", f"${last['margin']:,.0f}", SUCCESS if last["margin"] > 0 else DANGER),
                metric_card("Orders", f"{last['orders']}", SECONDARY),
                metric_card("AOV", f"${last['aov']:.2f}", "white"),
            ], style={"display": "flex", "gap": "12px", "flexWrap": "wrap"})
        ])

    return html.Div()
