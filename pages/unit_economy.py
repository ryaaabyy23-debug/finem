import dash
from dash import html, dcc, callback, Input, Output
import plotly.graph_objects as go
import pandas as pd

dash.register_page(__name__, path="/unit-economy", name="Unit Economy")

PRIMARY = "#7B61FF"
SECONDARY = "#4DFFD2"
TEXT_SECONDARY = "#8A8A8A"
SURFACE = "#141414"
BORDER = "#222222"
BACKGROUND = "#0A0A0A"
SUCCESS = "#4DFFD2"
WARNING = "#F5A623"
DANGER = "#FF4D4D"

def number_input(id, label, value, step=0.01):
    return html.Div([
        html.Label(label, style={"color": TEXT_SECONDARY, "fontSize": "13px", "marginBottom": "4px", "display": "block"}),
        html.Div([
            html.Button("−", id=f"{id}-minus", n_clicks=0, style={
                "background": SURFACE, "color": "white", "border": f"1px solid {BORDER}",
                "borderRadius": "6px 0 0 6px", "padding": "8px 12px", "cursor": "pointer", "fontSize": "16px"
            }),
            dcc.Input(id=id, type="number", value=value, step=step, style={
                "backgroundColor": SURFACE, "color": "white", "border": f"1px solid {BORDER}",
                "borderLeft": "none", "borderRight": "none", "padding": "8px 12px",
                "width": "100%", "textAlign": "center", "fontSize": "14px"
            }),
            html.Button("+", id=f"{id}-plus", n_clicks=0, style={
                "background": SURFACE, "color": "white", "border": f"1px solid {BORDER}",
                "borderRadius": "0 6px 6px 0", "padding": "8px 12px", "cursor": "pointer", "fontSize": "16px"
            }),
        ], style={"display": "flex", "alignItems": "center"})
    ], style={"marginBottom": "12px"})

def metric_card(label, value, pct, color):
    return html.Div([
        html.P(label, style={"color": TEXT_SECONDARY, "fontSize": "12px", "margin": "0 0 4px 0", "textTransform": "uppercase", "letterSpacing": "0.5px"}),
        html.P(value, style={"color": color, "fontSize": "28px", "fontWeight": "700", "margin": "0"}),
        html.P(pct, style={"color": color, "fontSize": "14px", "margin": "4px 0 0 0"}),
    ], style={
        "backgroundColor": SURFACE,
        "border": f"1px solid {BORDER}",
        "borderLeft": f"3px solid {color}",
        "borderRadius": "12px",
        "padding": "16px 20px",
        "flex": "1"
    })

layout = html.Div([
    html.H2("Unit Economy — per order & monthly", style={"color": "white", "marginBottom": "24px", "fontWeight": "700"}),

    # Main 2-column layout
    html.Div([

        # LEFT COLUMN
        html.Div([
            html.H3("Unit / order gross margin", style={"color": "white", "marginBottom": "20px"}),

            # AOV
            number_input("aov", "AOV (average order value)", 180.0, 1.0),

            html.P("Variable costs per order", style={"color": "white", "fontWeight": "600", "margin": "16px 0 8px 0"}),

            html.Div([
                html.Div([
                    number_input("landed-cogs", "Landed COGS", 32.0, 0.1),
                    number_input("returns", "Returns (cost per order)", 18.0, 0.1),
                    number_input("package", "Package", 2.0, 0.1),
                ], style={"flex": "1", "marginRight": "16px"}),
                html.Div([
                    number_input("processing", "Processing (fees)", 5.99, 0.01),
                    number_input("tpl", "3PL", 2.5, 0.1),
                    number_input("label", "Label", 8.0, 0.1),
                ], style={"flex": "1"}),
            ], style={"display": "flex"}),

            html.Hr(style={"borderColor": BORDER, "margin": "20px 0"}),

            html.H3("Margins per order", style={"color": "white", "marginBottom": "16px"}),
            number_input("ncac", "nCAC (marketing per order)", 65.0, 1.0),

            # Metric cards
            html.Div(id="metric-cards", style={"display": "flex", "gap": "12px", "margin": "16px 0"}),

            html.Hr(style={"borderColor": BORDER, "margin": "20px 0"}),

            # Waterfall chart
            dcc.Graph(id="waterfall-chart", config={"displayModeBar": False}),

            html.Hr(style={"borderColor": BORDER, "margin": "20px 0"}),

            # Cost breakdown table
            html.H4("Cost breakdown per order", style={"color": "white", "marginBottom": "12px"}),
            html.Div(id="cost-breakdown-table"),

        ], style={"flex": "1", "marginRight": "32px"}),

        # RIGHT COLUMN
        html.Div([
            html.H3("Monthly view", style={"color": "white", "marginBottom": "20px"}),

            html.H4("Orders", style={"color": "white", "marginBottom": "12px"}),
            number_input("new-orders", "New orders", 850, 1),
            number_input("returning-orders", "Returning orders", 170, 1),

            html.Div(id="orders-summary", style={"display": "flex", "gap": "12px", "margin": "12px 0"}),

            html.H4("Contribution margin (monthly)", style={"color": "white", "margin": "20px 0 12px 0"}),
            html.Div(id="monthly-cm-table"),

            html.H4("Operating margin (monthly)", style={"color": "white", "margin": "20px 0 12px 0"}),
            number_input("marketing", "Marketing spend (monthly)", 55250.0, 100.0),
            number_input("warehouse", "Warehouse", 3000.0, 100.0),
            number_input("payroll", "Payroll", 6000.0, 100.0),
            number_input("software", "Software", 3000.0, 100.0),
            number_input("content", "Content + misc", 7000.0, 100.0),

            html.Div(id="operating-profit-card", style={"marginTop": "16px"}),

            html.P("Marketing is treated as variable, other items as fixed costs.",
                   style={"color": TEXT_SECONDARY, "fontSize": "12px", "marginTop": "12px"}),

        ], style={"flex": "1"}),

    ], style={"display": "flex"}),

], style={"color": "white", "fontFamily": "system-ui, sans-serif"})


@callback(
    Output("metric-cards", "children"),
    Output("waterfall-chart", "figure"),
    Output("cost-breakdown-table", "children"),
    Output("orders-summary", "children"),
    Output("monthly-cm-table", "children"),
    Output("operating-profit-card", "children"),
    Input("aov", "value"),
    Input("landed-cogs", "value"),
    Input("returns", "value"),
    Input("processing", "value"),
    Input("tpl", "value"),
    Input("package", "value"),
    Input("label", "value"),
    Input("ncac", "value"),
    Input("new-orders", "value"),
    Input("returning-orders", "value"),
    Input("marketing", "value"),
    Input("warehouse", "value"),
    Input("payroll", "value"),
    Input("software", "value"),
    Input("content", "value"),
)
def update_all(aov, cogs, returns, processing, tpl, package, label, ncac,
               new_orders, returning_orders, marketing, warehouse, payroll, software, content):

    aov = aov or 0
    cogs = cogs or 0
    returns = returns or 0
    processing = processing or 0
    tpl = tpl or 0
    package = package or 0
    label = label or 0
    ncac = ncac or 0
    new_orders = new_orders or 0
    returning_orders = returning_orders or 0
    marketing = marketing or 0
    warehouse = warehouse or 0
    payroll = payroll or 0
    software = software or 0
    content = content or 0

    # Calculations
    variable_costs = cogs + returns + processing + tpl + package + label
    cm = aov - variable_costs
    cm_pct = cm / aov * 100 if aov else 0
    ncac_pct = ncac / aov * 100 if aov else 0
    om = cm - ncac
    om_pct = om / aov * 100 if aov else 0

    # Health colors
    cm_color = SUCCESS if cm_pct > 30 else WARNING if cm_pct > 20 else DANGER
    ncac_color = SUCCESS if ncac < cm else DANGER
    roas = 100 / cm_pct if cm_pct > 0 else 0
    roas_color = SUCCESS if roas > 3 else WARNING if roas > 2 else DANGER
    om_color = SUCCESS if om_pct > 10 else WARNING if om_pct > 0 else DANGER

    # Metric cards
    cards = [
        metric_card("Contribution Margin", f"${cm:,.0f}", f"↑ {cm_pct:.2f}%", cm_color),
        metric_card("nCAC", f"${ncac:,.0f}", f"↑ {ncac_pct:.2f}%", ncac_color),
        metric_card("Operating Margin", f"${om:,.0f}", f"↑ {om_pct:.2f}%", om_color),
    ]

    # Waterfall chart
    fig = go.Figure(go.Waterfall(
        name="Unit Economics",
        orientation="v",
        measure=["absolute", "relative", "relative", "relative", "relative", "relative", "relative", "total", "relative", "total"],
        x=["AOV", "COGS", "Returns", "Processing", "3PL", "Package", "Label", "CM", "nCAC", "Op. Margin"],
        y=[aov, -cogs, -returns, -processing, -tpl, -package, -label, 0, -ncac, 0],
        text=[f"${v:,.2f}" for v in [aov, cogs, returns, processing, tpl, package, label, cm, ncac, om]],
        textposition="outside",
        increasing={"marker": {"color": PRIMARY}},
        decreasing={"marker": {"color": DANGER}},
        totals={"marker": {"color": SECONDARY}},
        connector={"line": {"color": BORDER}},
    ))
    fig.update_layout(
        paper_bgcolor=BACKGROUND,
        plot_bgcolor=SURFACE,
        font={"color": "white", "family": "system-ui"},
        showlegend=False,
        margin={"l": 20, "r": 20, "t": 20, "b": 20},
        xaxis={"showgrid": False, "linecolor": BORDER},
        yaxis={"showgrid": False, "linecolor": BORDER},
        height=320,
    )

    # Cost breakdown table
    rows = [
        ("Landed COGS", cogs),
        ("Returns", returns),
        ("Package", package),
        ("Processing", processing),
        ("3PL", tpl),
        ("Label", label),
    ]
    table = html.Table([
        html.Thead(html.Tr([
            html.Th("Item", style={"color": TEXT_SECONDARY, "padding": "8px 12px", "textAlign": "left", "fontSize": "13px"}),
            html.Th("Cost", style={"color": TEXT_SECONDARY, "padding": "8px 12px", "textAlign": "right", "fontSize": "13px"}),
            html.Th("% of AOV", style={"color": TEXT_SECONDARY, "padding": "8px 12px", "textAlign": "right", "fontSize": "13px"}),
        ])),
        html.Tbody([
            html.Tr([
                html.Td(item, style={"color": "white", "padding": "8px 12px", "fontSize": "13px"}),
                html.Td(f"${cost:.2f}", style={"color": "white", "padding": "8px 12px", "textAlign": "right", "fontSize": "13px"}),
                html.Td(f"{cost/aov*100:.2f}%" if aov else "0%", style={"color": TEXT_SECONDARY, "padding": "8px 12px", "textAlign": "right", "fontSize": "13px"}),
            ], style={"borderTop": f"1px solid {BORDER}"})
            for item, cost in rows
        ])
    ], style={"width": "100%", "borderCollapse": "collapse", "backgroundColor": SURFACE, "borderRadius": "8px"})

    # Monthly calculations
    total_orders = new_orders + returning_orders
    returning_share = returning_orders / total_orders * 100 if total_orders else 0

    orders_summary = [
        html.Div([
            html.P("Total orders", style={"color": TEXT_SECONDARY, "fontSize": "12px", "margin": "0"}),
            html.P(f"{total_orders:,}", style={"color": "white", "fontSize": "24px", "fontWeight": "700", "margin": "0"}),
        ], style={"backgroundColor": SURFACE, "border": f"1px solid {BORDER}", "borderRadius": "8px", "padding": "12px 16px", "flex": "1"}),
        html.Div([
            html.P("Returning share", style={"color": TEXT_SECONDARY, "fontSize": "12px", "margin": "0"}),
            html.P(f"{returning_share:.2f}%", style={"color": "white", "fontSize": "24px", "fontWeight": "700", "margin": "0"}),
        ], style={"backgroundColor": SURFACE, "border": f"1px solid {BORDER}", "borderRadius": "8px", "padding": "12px 16px", "flex": "1"}),
    ]

    revenue_m = aov * total_orders
    monthly_rows = [
        ("Revenue", revenue_m),
        ("COGS", cogs * total_orders),
        ("Returns", returns * total_orders),
        ("Processing", processing * total_orders),
        ("Package", package * total_orders),
        ("3PL", tpl * total_orders),
        ("Labels", label * total_orders),
        ("Contribution", cm * total_orders),
    ]

    monthly_table = html.Table([
        html.Thead(html.Tr([
            html.Th("Item", style={"color": TEXT_SECONDARY, "padding": "8px 12px", "textAlign": "left", "fontSize": "13px"}),
            html.Th("Amount", style={"color": TEXT_SECONDARY, "padding": "8px 12px", "textAlign": "right", "fontSize": "13px"}),
        ])),
        html.Tbody([
            html.Tr([
                html.Td(item, style={"color": "white" if item != "Contribution" else SECONDARY, "padding": "8px 12px", "fontSize": "13px", "fontWeight": "700" if item == "Contribution" else "normal"}),
                html.Td(f"${amount:,.0f}", style={"color": "white" if item != "Contribution" else SECONDARY, "padding": "8px 12px", "textAlign": "right", "fontSize": "13px", "fontWeight": "700" if item == "Contribution" else "normal"}),
            ], style={"borderTop": f"1px solid {BORDER}"})
            for item, amount in monthly_rows
        ])
    ], style={"width": "100%", "borderCollapse": "collapse", "backgroundColor": SURFACE, "borderRadius": "8px"})

    fixed_costs = warehouse + payroll + software + content
    op_profit = cm * total_orders - marketing - fixed_costs
    op_profit_pct = op_profit / revenue_m * 100 if revenue_m else 0
    op_color = SUCCESS if op_profit_pct > 10 else WARNING if op_profit_pct > 0 else DANGER

    op_card = html.Div([
        html.P("Operating profit (monthly)", style={"color": TEXT_SECONDARY, "fontSize": "12px", "margin": "0 0 4px 0"}),
        html.P(f"${op_profit:,.0f}", style={"color": op_color, "fontSize": "36px", "fontWeight": "700", "margin": "0"}),
        html.P(f"↑ {op_profit_pct:.2f}%", style={"color": op_color, "fontSize": "14px", "margin": "4px 0 0 0"}),
    ], style={
        "backgroundColor": SURFACE,
        "border": f"1px solid {BORDER}",
        "borderLeft": f"3px solid {op_color}",
        "borderRadius": "12px",
        "padding": "20px",
    })

    return cards, fig, table, orders_summary, monthly_table, op_card
