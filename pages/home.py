import dash
from dash import html

dash.register_page(__name__, path="/", name="Home")

PRIMARY = "#7B61FF"
SECONDARY = "#4DFFD2"
TEXT_SECONDARY = "#8A8A8A"
SURFACE = "#141414"
BORDER = "#222222"

tools = [
    ("🧮", "Unit Economy", "Calculate margins, CAC, ROAS and breakeven per order", "/unit-economy"),
    ("📈", "Daily ROAS", "Track ad performance day by day with trend analysis", "/daily-roas"),
    ("💸", "Expenses", "Manage bills, pending payments and monthly balance", "/expenses"),
    ("📋", "P&L Builder", "Build monthly profit & loss with waterfall chart", "/pnl"),
    ("💰", "Cash Flow", "90-day forecast with cash gap detection", "/cash-flow"),
    ("🔄", "LTV & Retention", "Lifetime value, LTV:CAC ratio and payback period", "/ltv"),
    ("⏱️", "Pacing", "Monitor ad spend pace vs monthly budget plan", "/pacing"),
    ("🎯", "KPI Dashboard", "All 8 key metrics with health indicators", "/kpi"),
    ("📊", "Overview", "One-screen snapshot of your business today", "/overview"),
]

def card(icon, name, desc, href):
    return html.A(html.Div([
        html.P(icon, style={"fontSize": "28px", "margin": "0 0 8px 0"}),
        html.P(name, style={"fontWeight": "600", "color": "white", "margin": "0 0 4px 0"}),
        html.P(desc, style={"color": TEXT_SECONDARY, "fontSize": "13px", "margin": "0"}),
    ], style={
        "backgroundColor": SURFACE,
        "border": f"1px solid {BORDER}",
        "borderRadius": "12px",
        "padding": "20px",
        "cursor": "pointer",
        "transition": "border-color 0.2s",
    }), href=href, style={"textDecoration": "none"})

layout = html.Div([
    html.H1("finem", style={
        "background": f"linear-gradient(135deg, {PRIMARY}, {SECONDARY})",
        "WebkitBackgroundClip": "text",
        "WebkitTextFillColor": "transparent",
        "fontSize": "48px",
        "fontWeight": "700",
        "marginBottom": "8px"
    }),
    html.P("Your e-commerce finance dashboard", style={
        "color": TEXT_SECONDARY,
        "fontSize": "18px",
        "marginBottom": "40px"
    }),
    html.Div([
        html.Div(
            [card(icon, name, desc, href)
             for i, (icon, name, desc, href) in enumerate(tools) if i % 3 == col],
            style={"display": "flex", "flexDirection": "column", "gap": "16px", "flex": "1"}
        )
        for col in range(3)
    ], style={"display": "flex", "gap": "16px"})
])
