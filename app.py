import dash
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc

app = Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True
)
server = app.server

PRIMARY = "#7B61FF"
SECONDARY = "#4DFFD2"
TEXT_SECONDARY = "#8A8A8A"
SURFACE = "#141414"
BORDER = "#222222"
BACKGROUND = "#0A0A0A"

nav_links = [
    ("🏠", "Home", "/"),
    ("🧮", "Unit Economy", "/unit-economy"),
    ("📈", "Daily ROAS", "/daily-roas"),
    ("💸", "Expenses", "/expenses"),
    ("📋", "P&L Builder", "/pnl"),
    ("💰", "Cash Flow", "/cash-flow"),
    ("🔄", "LTV & Retention", "/ltv"),
    ("⏱️", "Pacing", "/pacing"),
    ("🎯", "KPI Dashboard", "/kpi"),
]

sidebar = html.Div([
    html.H1("finem", style={
        "background": f"linear-gradient(135deg, {PRIMARY}, {SECONDARY})",
        "WebkitBackgroundClip": "text",
        "WebkitTextFillColor": "transparent",
        "fontSize": "32px",
        "fontWeight": "700",
        "margin": "0"
    }),
    html.P("finance dashboard", style={
        "color": TEXT_SECONDARY,
        "fontSize": "12px",
        "margin": "4px 0 24px 0"
    }),
    html.Div([
        dcc.Link(html.Div([
            html.Span(icon, style={"marginRight": "8px"}),
            name
        ], style={
            "padding": "10px 12px",
            "borderRadius": "8px",
            "color": TEXT_SECONDARY,
            "fontSize": "14px",
            "cursor": "pointer",
            "marginBottom": "4px",
        }), href=href)
        for icon, name, href in nav_links
    ])
], style={
    "width": "220px",
    "minHeight": "100vh",
    "backgroundColor": "#0D0D0D",
    "borderRight": f"1px solid {BORDER}",
    "padding": "24px 16px",
    "position": "fixed",
    "top": "0",
    "left": "0",
    "overflowY": "auto",
})

app.layout = html.Div([
    dcc.Location(id="url"),
    sidebar,
    html.Div([
        dash.page_container
    ], style={
        "marginLeft": "220px",
        "padding": "32px",
        "backgroundColor": BACKGROUND,
        "minHeight": "100vh",
        "color": "white",
        "fontFamily": "system-ui, sans-serif",
    })
], style={"backgroundColor": BACKGROUND})

if __name__ == "__main__":
    app.run(debug=True)
