import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
from plotly.subplots import make_subplots
import plotly.figure_factory as ff
import base64
import io
import zipfile
try:
    import weasyprint
    PDF_EXPORT_AVAILABLE = True
except ImportError:
    PDF_EXPORT_AVAILABLE = False

# Initialize Dash app with external stylesheets
app = dash.Dash(__name__, external_stylesheets=[
    'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css'
])
app.title = "HealthKart Influencer Campaign Dashboard"

# Custom CSS styling
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            * {
                font-family: 'Inter', sans-serif;
            }
            body {
                margin: 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }
            .dashboard-container {
                background: white;
                margin: 20px;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.1);
                overflow: hidden;
            }
            .header-gradient {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 40px;
                text-align: center;
            }
            .metric-card {
                background: white;
                padding: 25px;
                margin: 15px;
                border-radius: 15px;
                box-shadow: 0 8px 30px rgba(0,0,0,0.12);
                transition: transform 0.3s ease, box-shadow 0.3s ease;
                border: 1px solid rgba(0,0,0,0.05);
            }
            .metric-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 15px 40px rgba(0,0,0,0.2);
            }
            .section-container {
                background: white;
                padding: 30px;
                margin: 25px;
                border-radius: 18px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.08);
                border: 1px solid rgba(0,0,0,0.05);
            }
            .top-products-container {
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                color: white;
                padding: 20px;
                margin: 25px;
                border-radius: 15px;
                box-shadow: 0 8px 30px rgba(245, 87, 108, 0.3);
            }
            .product-chip {
                display: inline-block;
                background: rgba(255,255,255,0.2);
                color: white;
                padding: 8px 16px;
                margin: 5px;
                border-radius: 25px;
                font-weight: 500;
                font-size: 0.9em;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255,255,255,0.3);
            }
            .kpi-number {
                font-size: 2.8em;
                font-weight: 700;
                line-height: 1.1;
                margin: 10px 0;
            }
            .section-title {
                font-size: 1.8em;
                font-weight: 600;
                color: #2c3e50;
                margin-bottom: 25px;
                text-align: center;
                position: relative;
            }
            .section-title::after {
                content: '';
                position: absolute;
                bottom: -10px;
                left: 50%;
                transform: translateX(-50%);
                width: 60px;
                height: 3px;
                background: linear-gradient(135deg, #667eea, #764ba2);
                border-radius: 2px;
            }
            .tab-container {
                background: white;
                border-radius: 15px;
                box-shadow: 0 8px 30px rgba(0,0,0,0.08);
                overflow: hidden;
                margin: 20px 0;
            }
            .tab-content {
                padding: 30px;
            }
            /* Card Layout Fixes - CRITICAL FOR 2 PER ROW */
            .card-row {
                display: flex !important;
                flex-wrap: wrap !important;
                justify-content: space-between !important;
                align-items: stretch !important;
                margin-bottom: 20px !important;
                gap: 2% !important;
            }
            .card-item {
                flex: 0 0 47% !important;
                max-width: 47% !important;
                box-sizing: border-box !important;
                display: block !important;
                margin: 0 !important;
            }
            /* Responsive adjustments */
            @media (max-width: 768px) {
                .card-item {
                    flex: 0 0 100% !important;
                    max-width: 100% !important;
                    margin-bottom: 15px !important;
                }
            }
            /* Ensure cards in payout section display properly */
            .payout-card-container {
                display: flex !important;
                flex-wrap: wrap !important;
                justify-content: space-between !important;
                gap: 2% !important;
            }
            .payout-card-item {
                flex: 0 0 48% !important;
                max-width: 48% !important;
                box-sizing: border-box !important;
            }
            /* Export Button Hover Effects */
            button:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(0,0,0,0.15) !important;
            }
            #export-pdf-btn:hover {
                background-color: #c0392b !important;
            }
            #export-csv-btn:hover {
                background-color: #219a52 !important;
            }
            /* Modal Styles */
            .modal-close {
                position: absolute;
                top: 15px;
                right: 20px;
                font-size: 28px;
                font-weight: bold;
                cursor: pointer;
                color: #aaa;
            }
            .modal-close:hover {
                color: #000;
            }
        </style>
        <script>
            // Modal functionality will be handled by Dash callbacks
        </script>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Load data from CSV files
payout_df = pd.read_csv('data/payouts.csv')
influencer_df = pd.read_csv('data/influencers.csv')
instagram_df = pd.read_csv('data/instagram_insights_data.csv')
youtube_df = pd.read_csv('data/youtube_analytics_data.csv')
tracking_df = pd.read_csv('data/tracking_data.csv')
tracking_data_df = tracking_df  # Alias for CAC analysis
posts_df = pd.read_csv('data/posts.csv')

# Load additional data files
try:
    audience_demographics_df = pd.read_csv('data/audience_demographics.csv')
    campaign_performance_df = pd.read_csv('data/campaign_performance_insights.csv')
    geographic_distribution_df = pd.read_csv('data/geographic_distribution.csv')
    posts_df = pd.read_csv('data/posts.csv')
    tracking_codes_df = pd.read_csv('data/influencer_tracking_codes.csv')
except Exception as e:
    print(f"Error loading additional data: {e}")
    # Create empty DataFrames if files don't exist
    audience_demographics_df = pd.DataFrame()
    campaign_performance_df = pd.DataFrame()
    geographic_distribution_df = pd.DataFrame()
    posts_df = pd.DataFrame()
    tracking_codes_df = pd.DataFrame()


# Calculate key metrics
total_orders = payout_df['orders'].sum()
total_revenue = payout_df['total_revenue'].sum()
total_cost = payout_df['total_cost'].sum()
total_roas = total_revenue / total_cost
total_followers = influencer_df['follower_count'].sum()

# For market reach, we'll use estimated impressions based on follower count
# (In real implementation, you'd use the actual Instagram insights data)
estimated_reach = total_followers * 0.4  # Assuming 40% organic reach rate

# Define the app layout
app.layout = html.Div([
    # Beautiful Header with Gradient
    html.Div([
        html.Div([
            html.Div([
                html.H1("HealthKart Influencer Campaign Dashboard", 
                       style={'margin': '0', 'fontSize': '3em', 'fontWeight': '700'}),
                html.P("Comprehensive Analytics & Performance Insights", 
                       style={'margin': '10px 0 0 0', 'fontSize': '1.2em', 'opacity': '0.9'})
            ], style={'flex': '1'}),
            
            # Export Buttons
            html.Div([
                html.Button([
                    html.I(className="fas fa-file-pdf", style={'marginRight': '8px'}),
                    "Export to PDF"
                ], id='export-pdf-btn', 
                   style={
                       'backgroundColor': '#e74c3c', 'color': 'white', 'border': 'none',
                       'padding': '12px 20px', 'borderRadius': '8px', 'cursor': 'pointer',
                       'fontSize': '1em', 'fontWeight': '600', 'marginRight': '10px',
                       'boxShadow': '0 4px 15px rgba(231,76,60,0.3)',
                       'transition': 'all 0.3s ease'
                   }),
                html.Button([
                    html.I(className="fas fa-file-csv", style={'marginRight': '8px'}),
                    "Export Data to CSV"
                ], id='export-csv-btn',
                   style={
                       'backgroundColor': '#27ae60', 'color': 'white', 'border': 'none',
                       'padding': '12px 20px', 'borderRadius': '8px', 'cursor': 'pointer',
                       'fontSize': '1em', 'fontWeight': '600',
                       'boxShadow': '0 4px 15px rgba(39,174,96,0.3)',
                       'transition': 'all 0.3s ease'
                   })
            ], style={'display': 'flex', 'alignItems': 'center'})
        ], style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center'})
    ], className='header-gradient'),

    # Main Dashboard Container
    html.Div([
        # Top Performing Products Section
        html.Div([
            html.H3("🏆 Top Performing Products", 
                   style={'margin': '0 0 15px 0', 'fontSize': '1.4em', 'fontWeight': '600'}),
            html.Div(id='top-products-display')
        ], className='top-products-container'),

        # Key Metrics Cards
        html.Div([
            # Market Reach Card
            html.Div([
                html.Div([
                    html.I(className="fas fa-users", 
                          style={'fontSize': '2em', 'color': '#3498db', 'marginBottom': '10px'}),
                    html.H3("Market Reach", style={'color': '#2c3e50', 'margin': '0 0 10px 0'}),
                    html.Div(f"{estimated_reach:,.0f}", className='kpi-number', style={'color': '#3498db'}),
                    html.P(f"Total Followers: {total_followers:,}", 
                          style={'margin': '0', 'color': '#7f8c8d', 'fontSize': '0.9em'})
                ])
            ], className='metric-card', style={'width': '30%', 'display': 'inline-block'}),

            # Total Orders Card
            html.Div([
                html.Div([
                    html.I(className="fas fa-shopping-cart", 
                          style={'fontSize': '2em', 'color': '#27ae60', 'marginBottom': '10px'}),
                    html.H3("Total Orders", style={'color': '#2c3e50', 'margin': '0 0 10px 0'}),
                    html.Div(f"{total_orders:,}", className='kpi-number', style={'color': '#27ae60'}),
                    html.P("Across all campaigns", 
                          style={'margin': '0', 'color': '#7f8c8d', 'fontSize': '0.9em'})
                ])
            ], className='metric-card', style={'width': '30%', 'display': 'inline-block'}),

            # ROAS Card
            html.Div([
                html.Div([
                    html.I(className="fas fa-chart-line", 
                          style={'fontSize': '2em', 'color': '#e74c3c', 'marginBottom': '10px'}),
                    html.H3("Overall ROAS", style={'color': '#2c3e50', 'margin': '0 0 10px 0'}),
                    html.Div(f"{total_roas:.2f}x", className='kpi-number', style={'color': '#e74c3c'}),
                    html.P(f"ROI: {((total_roas-1)*100):.0f}%", 
                          style={'margin': '0', 'color': '#7f8c8d', 'fontSize': '0.9em'})
                ])
            ], className='metric-card', style={'width': '30%', 'display': 'inline-block'})
        ], style={'textAlign': 'center', 'marginBottom': '20px'}),

        # Revenue and Cost Breakdown
        html.Div([
            html.H3("Financial Overview", className='section-title'),
            html.Div([
                html.Div([
                    html.I(className="fas fa-arrow-up", style={'color': '#27ae60', 'marginRight': '10px'}),
                    html.H4("Total Revenue", style={'color': '#27ae60', 'margin': '0 0 10px 0'}),
                    html.H3(f"₹{total_revenue:,.2f}", style={'color': '#2c3e50', 'margin': '0'})
                ], style={'width': '45%', 'display': 'inline-block', 'textAlign': 'center'}),
                html.Div([
                    html.I(className="fas fa-arrow-down", style={'color': '#e74c3c', 'marginRight': '10px'}),
                    html.H4("Total Cost", style={'color': '#e74c3c', 'margin': '0 0 10px 0'}),
                    html.H3(f"₹{total_cost:,.2f}", style={'color': '#2c3e50', 'margin': '0'})
                ], style={'width': '45%', 'display': 'inline-block', 'textAlign': 'center'})
            ])
        ], className='section-container'),

        # Campaign Performance Section
        html.Div([
            html.H3("Campaign Performance Overview", className='section-title'),
            
            # Campaign KPI Cards
            html.Div([
                html.Div(id='campaign-kpi-cards'),
            ], style={'marginBottom': '30px'}),
            
            # Campaign Performance Charts
            html.Div([
                # Brand Performance Chart
                html.Div([
                    dcc.Graph(id='brand-performance-chart')
                ], style={'width': '100%', 'display': 'inline-block'}),
                
               
            ])
        ], className='section-container'),

        # Payout Tracking Section
        html.Div([
            html.H3("Payout Tracking & Management", className='section-title'),
            
            # Payout Summary Cards
            html.Div([
                html.Div(id='payout-summary-cards')
            ], style={'marginBottom': '20px'}),
            
            # Payout Details Table
            html.Div([
                html.H4("Recent Payouts", style={'color': '#2c3e50', 'marginBottom': '15px'}),
                dash_table.DataTable(
                    id='payout-tracking-table',
                    columns=[
                        {'name': 'Influencer', 'id': 'influencer_name'},
                        {'name': 'Brand', 'id': 'brand'},
                        {'name': 'Platform', 'id': 'platform'},
                        {'name': 'Payment Type', 'id': 'payment_type'},
                        {'name': 'Orders', 'id': 'orders', 'type': 'numeric', 'format': {'specifier': ',.0f'}},
                        {'name': 'Amount (₹)', 'id': 'payout_amount', 'type': 'numeric', 'format': {'specifier': ',.2f'}},
                        {'name': 'Status', 'id': 'status'},
                        {'name': 'Date', 'id': 'payout_date'}
                    ],
                    style_cell={'textAlign': 'center', 'padding': '12px', 'fontFamily': 'Inter'},
                    style_header={'backgroundColor': '#34495e', 'color': 'white', 'fontWeight': 'bold'},
                    style_data_conditional=[
                        {
                            'if': {'filter_query': '{status} = Paid'},
                            'backgroundColor': '#d5f4e6',
                            'color': 'black',
                        },
                        {
                            'if': {'filter_query': '{status} = Pending'},
                            'backgroundColor': '#fff3cd',
                            'color': 'black',
                        },
                        {
                            'if': {'filter_query': '{status} = Processing'},
                            'backgroundColor': '#cce7ff',
                            'color': 'black',
                        }
                    ],
                    page_size=10,
                    sort_action='native'
                )
            ])
        ], className='section-container'),

        # Platform and Category Breakdown Charts
        html.Div([
            # Platform chart
            html.Div([
                dcc.Graph(id='platform-chart')
            ], style={'width': '48%', 'display': 'inline-block'}),

            # Category chart
            html.Div([
                dcc.Graph(id='category-chart')
            ], style={'width': '48%', 'display': 'inline-block', 'marginLeft': '4%'})
        ], className='section-container'),

        # Top Performers Table
        html.Div([
            html.H3("Top Performing Influencers", className='section-title'),
            dash_table.DataTable(
                id='top-performers-table',
                columns=[
                    {'name': 'Influencer', 'id': 'name'},
                    {'name': 'Category', 'id': 'category'},
                    {'name': 'Platform', 'id': 'platform'},
                    {'name': 'Orders', 'id': 'orders', 'type': 'numeric', 'format': {'specifier': ',.0f'}},
                    {'name': 'Revenue (₹)', 'id': 'total_revenue', 'type': 'numeric', 'format': {'specifier': ',.2f'}},
                    {'name': 'ROAS', 'id': 'roas', 'type': 'numeric', 'format': {'specifier': '.2f'}}
                ],
                style_cell={'textAlign': 'center', 'padding': '12px', 'fontFamily': 'Inter'},
                style_header={'backgroundColor': '#3498db', 'color': 'white', 'fontWeight': 'bold'},
                style_data_conditional=[
                    {
                        'if': {'filter_query': '{roas} > 10'},
                        'backgroundColor': '#d5f4e6',
                        'color': 'black',
                    }
                ],
                page_size=10,
                sort_action='native'
            )
        ], className='section-container'),
        
        # Influencer Performance Deep Dive
        html.Div([
            html.H3("Influencer Performance Deep Dive", className='section-title'),
            
            # Influencer Selector
            html.Div([
                html.Label("Select Influencer:", style={'fontWeight': 'bold', 'color': '#2c3e50', 'fontSize': '1.1em'}),
                dcc.Dropdown(
                    id='influencer-dropdown',
                    options=[
                        {'label': row['name'], 'value': row['influencer_id']} 
                        for _, row in influencer_df.iterrows()
                    ],
                    value='HK001',  # Default to first influencer
                    style={'marginTop': '15px', 'borderRadius': '8px'}
                )
            ], style={'width': '40%', 'margin': '0 auto', 'marginBottom': '30px'}),
            
            # Platform-specific KPIs in beautiful cards
            html.Div(id='platform-kpis-container')
            
        ], className='section-container'),

        # Overall Platform KPIs
        html.Div([
            html.H3("Platform Performance Overview", className='section-title'),
            
            html.Div([
                # Instagram KPIs
                html.Div([
                    html.Div([
                        html.Div([
                            html.I(className="fab fa-instagram", style={'fontSize': '2em', 'color': '#E4405F', 'marginBottom': '10px'}),
                            html.H4("Instagram", style={'color': '#E4405F', 'margin': '0'})
                        ], style={'textAlign': 'center', 'marginBottom': '20px'}),
                        
                        html.Div(id='instagram-kpis-cards')
                    ], style={
                        'backgroundColor': 'white',
                        'padding': '25px',
                        'borderRadius': '15px',
                        'boxShadow': '0 4px 15px rgba(228, 64, 95, 0.1)',
                        'border': '2px solid #E4405F20'
                    })
                ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'}),
                
                # YouTube KPIs
                html.Div([
                    html.Div([
                        html.Div([
                            html.I(className="fab fa-youtube", style={'fontSize': '2em', 'color': '#FF0000', 'marginBottom': '10px'}),
                            html.H4("YouTube", style={'color': '#FF0000', 'margin': '0'})
                        ], style={'textAlign': 'center', 'marginBottom': '20px'}),
                        
                        html.Div(id='youtube-kpis-cards')
                    ], style={
                        'backgroundColor': 'white',
                        'padding': '25px',
                        'borderRadius': '15px',
                        'boxShadow': '0 4px 15px rgba(255, 0, 0, 0.1)',
                        'border': '2px solid #FF000020'
                    })
                ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top', 'marginLeft': '4%'})
                
            ])
        ], className='section-container'),
        
        # ---------- ADVANCED ANALYTICS SECTION ----------
        html.Hr(style={'margin': '40px 0', 'border': 'none', 'height': '2px', 'background': 'linear-gradient(135deg, #667eea, #764ba2)'}),
        
        html.Div([
            html.H2("Advanced Analytics", className='section-title',
                    style={'fontSize': '2.5em', 'fontWeight': '300'}),
            
            dcc.Tabs(id='advanced-tabs', value='audience-growth', 
                     className='tab-container',
                     children=[
                     dcc.Tab(label='Audience Growth', value='audience-growth',
                            style={
                                'padding': '15px 30px',
                                'fontWeight': 'bold',
                                'fontSize': '14px',
                                'borderRadius': '5px 5px 0 0',
                                'backgroundColor': '#f8f9fa',
                                'border': '1px solid #dee2e6',
                                'color': '#495057'
                            },
                            selected_style={
                                'padding': '15px 30px',
                                'fontWeight': 'bold',
                                'fontSize': '14px',
                                'borderRadius': '5px 5px 0 0',
                                'backgroundColor': '#3498db',
                                'border': '1px solid #3498db',
                                'color': 'white'
                            }),
                     dcc.Tab(label='Incremental ROAS', value='incremental-roas',
                            style={
                                'padding': '15px 30px',
                                'fontWeight': 'bold',
                                'fontSize': '14px',
                                'borderRadius': '5px 5px 0 0',
                                'backgroundColor': '#f8f9fa',
                                'border': '1px solid #dee2e6',
                                'color': '#495057'
                            },
                            selected_style={
                                'padding': '15px 30px',
                                'fontWeight': 'bold',
                                'fontSize': '14px',
                                'borderRadius': '5px 5px 0 0',
                                'backgroundColor': '#e74c3c',
                                'border': '1px solid #e74c3c',
                                'color': 'white'
                            }),
                     dcc.Tab(label='Product Affinity', value='product-affinity',
                            style={
                                'padding': '15px 30px',
                                'fontWeight': 'bold',
                                'fontSize': '14px',
                                'borderRadius': '5px 5px 0 0',
                                'backgroundColor': '#f8f9fa',
                                'border': '1px solid #dee2e6',
                                'color': '#495057'
                            },
                            selected_style={
                                'padding': '15px 30px',
                                'fontWeight': 'bold',
                                'fontSize': '14px',
                                'borderRadius': '5px 5px 0 0',
                                'backgroundColor': '#27ae60',
                                'border': '1px solid #27ae60',
                                'color': 'white'
                            }),
                     dcc.Tab(label='Geo Efficiency', value='geo-efficiency',
                            style={
                                'padding': '15px 30px',
                                'fontWeight': 'bold',
                                'fontSize': '14px',
                                'borderRadius': '5px 5px 0 0',
                                'backgroundColor': '#f8f9fa',
                                'border': '1px solid #dee2e6',
                                'color': '#495057'
                            },
                            selected_style={
                                'padding': '15px 30px',
                                'fontWeight': 'bold',
                                'fontSize': '14px',
                                'borderRadius': '5px 5px 0 0',
                                'backgroundColor': '#f39c12',
                                'border': '1px solid #f39c12',
                                'color': 'white'
                            }),
                     dcc.Tab(label='Lifetime Lift', value='lifetime-lift',
                            style={
                                'padding': '15px 30px',
                                'fontWeight': 'bold',
                                'fontSize': '14px',
                                'borderRadius': '5px 5px 0 0',
                                'backgroundColor': '#f8f9fa',
                                'border': '1px solid #dee2e6',
                                'color': '#495057'
                            },
                            selected_style={
                                'padding': '15px 30px',
                                'fontWeight': 'bold',
                                'fontSize': '14px',
                                'borderRadius': '5px 5px 0 0',
                                'backgroundColor': '#9b59b6',
                                'border': '1px solid #9b59b6',
                                'color': 'white'
                            }),
                     dcc.Tab(label='💸 CAC Analysis', value='cac-analysis',
                            style={
                                'padding': '15px 30px',
                                'fontWeight': 'bold',
                                'fontSize': '14px',
                                'borderRadius': '5px 5px 0 0',
                                'backgroundColor': '#f8f9fa',
                                'border': '1px solid #dee2e6',
                                'color': '#495057'
                            },
                            selected_style={
                                'padding': '15px 30px',
                                'fontWeight': 'bold',
                                'fontSize': '14px',
                                'borderRadius': '5px 5px 0 0',
                                'backgroundColor': '#e67e22',
                                'border': '1px solid #e67e22',
                                'color': 'white'
                            }),
                 ]),
        
        html.Div(id='advanced-content')
        
    ], style={
        'backgroundColor': 'white',
        'padding': '30px',
        'margin': '20px',
        'borderRadius': '15px',
        'boxShadow': '0 4px 20px rgba(0,0,0,0.1)',
        'border': '1px solid #e9ecef'
    }),

    # Data Upload Section
    html.Div([
        html.Div([
            html.H2("📁 Data Management", className='section-title',
                    style={'fontSize': '2.5em', 'fontWeight': '300', 'display': 'inline-block'}),
            html.Button([
                html.I(className="fas fa-question-circle", style={'marginRight': '5px'}),
                "Help"
            ], id='data-help-btn', 
               style={
                   'backgroundColor': '#17a2b8', 'color': 'white', 'border': 'none',
                   'padding': '8px 15px', 'borderRadius': '20px', 'cursor': 'pointer',
                   'fontSize': '0.9em', 'fontWeight': '500', 'marginLeft': '20px',
                   'boxShadow': '0 2px 10px rgba(23,162,184,0.3)'
               })
        ], style={'textAlign': 'center', 'marginBottom': '30px'}),
        
        # Help Modal
        html.Div([
            html.Div([
                html.Div([
                    html.Span("×", className="modal-close", id="modal-close-btn", style={
                        'position': 'absolute',
                        'top': '15px',
                        'right': '20px',
                        'fontSize': '28px',
                        'fontWeight': 'bold',
                        'cursor': 'pointer',
                        'color': '#aaa'
                    }),
                    html.H3("📊 Data Upload Guide", style={'color': '#2c3e50', 'marginBottom': '20px'}),
                    html.Div([
                        html.H4("📸 Instagram Data Format:", style={'color': '#E4405F', 'marginBottom': '10px'}),
                        html.P("Required columns: influencer_id, likes, comments, saves, reach, impressions, profile_visits, website_clicks, story_impressions, story_exits, story_completion_rate"),
                        html.A("📥 Download Sample Instagram CSV", id="download-instagram-sample", 
                               style={'color': '#E4405F', 'textDecoration': 'underline', 'cursor': 'pointer'}),
                        
                        html.Hr(),
                        
                        html.H4("📺 YouTube Data Format:", style={'color': '#FF0000', 'marginBottom': '10px'}),
                        html.P("Required columns: influencer_id, impressions_ctr_percentage, audience_retention_percentage, subscribers_gained, watch_time_hours"),
                        html.A("📥 Download Sample YouTube CSV", id="download-youtube-sample",
                               style={'color': '#FF0000', 'textDecoration': 'underline', 'cursor': 'pointer'}),
                        
                        html.Hr(),
                        
                        html.H4("💰 Payout Data Format:", style={'color': '#28a745', 'marginBottom': '10px'}),
                        html.P("Required columns: influencer_id, orders, total_revenue, total_cost"),
                        html.P("Note: Data will be aggregated for existing influencers only.", style={'fontStyle': 'italic', 'color': '#6c757d'}),
                        html.A("📥 Download Sample Payout CSV", 
                               href="/assets/sample_new_payouts.csv", download="sample_payout_data.csv",
                               style={'color': '#28a745', 'textDecoration': 'underline'}),
                        
                        html.Hr(),
                        
                        html.H4("⚠️ Important Notes:", style={'color': '#dc3545', 'marginBottom': '10px'}),
                        html.Ul([
                            html.Li("Only existing influencer IDs are accepted"),
                            html.Li("Files must be in CSV format"),
                            html.Li("All required columns must be present"),
                            html.Li("Data will be validated before upload")
                        ])
                    ])
                ], style={
                    'backgroundColor': 'white',
                    'padding': '30px',
                    'borderRadius': '10px',
                    'maxWidth': '600px',
                    'margin': '50px auto',
                    'position': 'relative',
                    'boxShadow': '0 10px 30px rgba(0,0,0,0.3)'
                })
            ], id='help-modal', style={
                'position': 'fixed',
                'top': '0',
                'left': '0',
                'width': '100%',
                'height': '100%',
                'backgroundColor': 'rgba(0,0,0,0.5)',
                'zIndex': '1000',
                'display': 'none'
            })
        ]),
        
        html.Div([
            # Instagram Upload
            html.Div([
                html.H4("📸 Upload Instagram Data", style={'color': '#E4405F', 'marginBottom': '15px'}),
                dcc.Upload(
                    id='upload-instagram',
                    children=html.Div([
                        'Drag and Drop or ',
                        html.A('Select Instagram CSV File')
                    ]),
                    style={
                        'width': '100%',
                        'height': '80px',
                        'lineHeight': '80px',
                        'borderWidth': '2px',
                        'borderStyle': 'dashed',
                        'borderRadius': '10px',
                        'textAlign': 'center',
                        'borderColor': '#E4405F',
                        'backgroundColor': '#fef7f7'
                    },
                    multiple=False
                ),
                html.Div(id='instagram-upload-status', style={'marginTop': '10px'})
            ], style={'width': '48%', 'display': 'inline-block'}),

            # YouTube Upload  
            html.Div([
                html.H4("📺 Upload YouTube Data", style={'color': '#FF0000', 'marginBottom': '15px'}),
                dcc.Upload(
                    id='upload-youtube',
                    children=html.Div([
                        'Drag and Drop or ',
                        html.A('Select YouTube CSV File')
                    ]),
                    style={
                        'width': '100%',
                        'height': '80px',
                        'lineHeight': '80px',
                        'borderWidth': '2px',
                        'borderStyle': 'dashed',
                        'borderRadius': '10px',
                        'textAlign': 'center',
                        'borderColor': '#FF0000',
                        'backgroundColor': '#fff5f5'
                    },
                    multiple=False
                ),
                html.Div(id='youtube-upload-status', style={'marginTop': '10px'})
            ], style={'width': '48%', 'display': 'inline-block', 'marginLeft': '4%'})
        ], style={'marginBottom': '30px'}),

        # Payouts Upload
        html.Div([
            html.H4("💰 Upload Payout Data", style={'color': '#27ae60', 'marginBottom': '15px', 'textAlign': 'center'}),
            dcc.Upload(
                id='upload-payouts',
                children=html.Div([
                    'Drag and Drop or ',
                    html.A('Select Payout CSV File')
                ]),
                style={
                    'width': '60%',
                    'height': '80px',
                    'lineHeight': '80px',
                    'borderWidth': '2px',
                    'borderStyle': 'dashed',
                    'borderRadius': '10px',
                    'textAlign': 'center',
                    'borderColor': '#27ae60',
                    'backgroundColor': '#d5f4e6',
                    'margin': '0 auto'
                },
                multiple=False
            ),
            html.Div(id='payout-upload-status', style={'marginTop': '10px', 'textAlign': 'center'})
        ])
    ], className='section-container'),

    # Hidden download components
    dcc.Download(id="download-pdf"),
    dcc.Download(id="download-csv-data"),
    dcc.Download(id="download-instagram-sample-file"),
    dcc.Download(id="download-youtube-sample-file")

    ], className='dashboard-container')
])

# Callback for top products display
@app.callback(Output('top-products-display', 'children'), [Input('top-products-display', 'id')])
def update_top_products(_):
    try:
        # Calculate engagement metrics for each brand from posts
        products_performance = posts_df.groupby('brand_mentioned').agg({
            'likes': 'sum',
            'comments': 'sum', 
            'shares': 'sum',
            'reach': 'sum',
            'video_views': 'sum'
        }).reset_index()
        
        # Calculate total engagement score
        products_performance['engagement_score'] = (
            products_performance['likes'] + 
            products_performance['comments'] * 3 + 
            products_performance['shares'] * 5 +
            products_performance['video_views'] * 0.5
        )
        
        # Sort by engagement score and get top 3
        top_products = products_performance.nlargest(3, 'engagement_score')
        
        # Create product chips in reverse pyramid layout
        product_chips = []
        product_list = top_products.to_dict('records')
        
        if len(product_list) >= 3:
            # First row - 2 products
            first_row = html.Div([
                html.Div([
                    html.Span(f"🏆 {product_list[0]['brand_mentioned']}", 
                             style={'marginRight': '8px', 'fontWeight': '600'}),
                    html.Span(f"{product_list[0]['engagement_score']:,.0f} engagement", 
                             style={'fontSize': '0.85em', 'opacity': '0.9'})
                ], className='product-chip', style={'margin': '10px'}),
                
                html.Div([
                    html.Span(f"🥈 {product_list[1]['brand_mentioned']}", 
                             style={'marginRight': '8px', 'fontWeight': '600'}),
                    html.Span(f"{product_list[1]['engagement_score']:,.0f} engagement", 
                             style={'fontSize': '0.85em', 'opacity': '0.9'})
                ], className='product-chip', style={'margin': '10px'})
            ], style={'textAlign': 'center', 'marginBottom': '15px'})
            
            # Second row - 1 product (centered)
            second_row = html.Div([
                html.Div([
                    html.Span(f"🥉 {product_list[2]['brand_mentioned']}", 
                             style={'marginRight': '8px', 'fontWeight': '600'}),
                    html.Span(f"{product_list[2]['engagement_score']:,.0f} engagement", 
                             style={'fontSize': '0.85em', 'opacity': '0.9'})
                ], className='product-chip', style={'margin': '10px'})
            ], style={'textAlign': 'center'})
            
            return html.Div([first_row, second_row])
        else:
            # Fallback to regular layout if less than 3 products
            for _, product in top_products.iterrows():
                product_chips.append(
                    html.Div([
                        html.Span(f"🏆 {product['brand_mentioned']}", 
                                 style={'marginRight': '8px', 'fontWeight': '600'}),
                        html.Span(f"{product['engagement_score']:,.0f} engagement", 
                                 style={'fontSize': '0.85em', 'opacity': '0.9'})
                    ], className='product-chip')
                )
            return html.Div(product_chips, style={'textAlign': 'center'})
        
    except Exception as e:
        # Fallback with sample data in reverse pyramid
        sample_products = ['MuscleBlaze', 'HK Vitals', 'Gritzo']
        
        # First row - 2 products
        first_row = html.Div([
            html.Div([
                html.Span(f"🏆 {sample_products[0]}", style={'marginRight': '8px', 'fontWeight': '600'}),
                html.Span("Top Performer", style={'fontSize': '0.85em', 'opacity': '0.9'})
            ], className='product-chip', style={'margin': '10px'}),
            
            html.Div([
                html.Span(f"🥈 {sample_products[1]}", style={'marginRight': '8px', 'fontWeight': '600'}),
                html.Span("Top Performer", style={'fontSize': '0.85em', 'opacity': '0.9'})
            ], className='product-chip', style={'margin': '10px'})
        ], style={'textAlign': 'center', 'marginBottom': '15px'})
        
        # Second row - 1 product (centered)
        second_row = html.Div([
            html.Div([
                html.Span(f"🥉 {sample_products[2]}", style={'marginRight': '8px', 'fontWeight': '600'}),
                html.Span("Top Performer", style={'fontSize': '0.85em', 'opacity': '0.9'})
            ], className='product-chip', style={'margin': '10px'})
        ], style={'textAlign': 'center'})
        
        return html.Div([first_row, second_row])

# Callback for platform chart
@app.callback(Output('platform-chart', 'figure'), [Input('platform-chart', 'id')])
def update_platform_chart(_):
    platform_stats = influencer_df.groupby('platform').agg({
        'follower_count': 'sum',
        'influencer_id': 'count'
    }).reset_index()
    platform_stats.columns = ['Platform', 'Total Followers', 'Influencer Count']

    fig = px.pie(platform_stats, values='Total Followers', names='Platform', 
                title='Follower Distribution by Platform')
    fig.update_layout(title_x=0.5)
    return fig

# Callback for category chart
@app.callback(Output('category-chart', 'figure'), [Input('category-chart', 'id')])
def update_category_chart(_):
    category_stats = influencer_df.groupby('category').agg({
        'follower_count': 'sum',
        'influencer_id': 'count'
    }).reset_index()
    category_stats.columns = ['Category', 'Total Followers', 'Influencer Count']

    fig = px.bar(category_stats, x='Category', y='Total Followers', 
                title='Follower Distribution by Category')
    fig.update_layout(title_x=0.5, xaxis_tickangle=-45)
    return fig

# Callback for top performers table
@app.callback(Output('top-performers-table', 'data'), [Input('top-performers-table', 'id')])
def update_top_performers(_):
    # Merge payout and influencer data
    merged_df = pd.merge(payout_df, influencer_df, on='influencer_id')
    merged_df['roas'] = merged_df['total_revenue'] / merged_df['total_cost']

    # Get top 10 performers by ROAS
    top_performers = merged_df.nlargest(10, 'roas')[['name', 'category', 'platform', 'orders', 'total_revenue', 'roas']]

    return top_performers.to_dict('records')

# Callback for Campaign Performance KPI Cards
@app.callback(
    Output('campaign-kpi-cards', 'children'),
    [Input('platform-chart', 'id')]
)
def update_campaign_kpis(_):
    # Calculate campaign metrics
    total_campaigns = len(payout_df)
    avg_campaign_roas = (payout_df['total_revenue'] / payout_df['total_cost']).mean()
    total_influencers = len(influencer_df)
    avg_orders_per_campaign = payout_df['orders'].mean()
    
    # Calculate brands performance from brand_performance CSV or posts data
    try:
        brand_performance_df = pd.read_csv('data/brand_performance.csv')
        best_brand = brand_performance_df.loc[brand_performance_df['total_revenue'].idxmax()]
        best_brand = {'brand': best_brand['brand'], 'revenue': best_brand['total_revenue']}
    except:
        posts_df = pd.read_csv('data/posts.csv')
        brand_performance = posts_df.groupby('brand_mentioned').agg({
            'post_id': 'count',
            'reach': 'sum'
        }).reset_index()
        brand_performance.columns = ['brand', 'campaigns', 'reach']
        
        # Calculate revenue estimate based on reach (static conversion rate)
        brand_performance['revenue'] = brand_performance['reach'] * 0.05  # 5% conversion estimate
        
        best_brand = brand_performance.loc[brand_performance['revenue'].idxmax()]
    
    return html.Div([
        # First Row - 2 cards
        html.Div([
            # Total Campaigns
            html.Div([
                html.H3(f"{total_campaigns}", style={'color': '#3498db', 'fontSize': '2.5em', 'margin': '0'}),
                html.P("Active Campaigns", style={'color': '#2c3e50', 'fontWeight': 'bold'})
            ], className='card-item', style={
                'backgroundColor': '#ebf3fd',
                'padding': '25px',
                'borderRadius': '12px',
                'textAlign': 'center',
                'boxShadow': '0 4px 15px rgba(52, 152, 219, 0.2)'
            }),
            
            # Average Campaign ROAS
            html.Div([
                html.H3(f"{avg_campaign_roas:.2f}x", style={'color': '#e74c3c', 'fontSize': '2.5em', 'margin': '0'}),
                html.P("Avg Campaign ROAS", style={'color': '#2c3e50', 'fontWeight': 'bold'})
            ], className='card-item', style={
                'backgroundColor': '#fdeaea',
                'padding': '25px',
                'borderRadius': '12px',
                'textAlign': 'center',
                'boxShadow': '0 4px 15px rgba(231, 76, 60, 0.2)'
            })
        ], className='card-row'),
        
        # Second Row - 2 cards
        html.Div([
            # Total Influencers
            html.Div([
                html.H3(f"{total_influencers}", style={'color': '#27ae60', 'fontSize': '2.5em', 'margin': '0'}),
                html.P("Partner Influencers", style={'color': '#2c3e50', 'fontWeight': 'bold'})
            ], className='card-item', style={
                'backgroundColor': '#d5f4e6',
                'padding': '25px',
                'borderRadius': '12px',
                'textAlign': 'center',
                'boxShadow': '0 4px 15px rgba(39, 174, 96, 0.2)'
            }),
            
            # Best Performing Brand
            html.Div([
                html.H3(f"{best_brand['brand']}", style={'color': '#f39c12', 'fontSize': '1.8em', 'margin': '0'}),
                html.P("Top Brand", style={'color': '#2c3e50', 'fontWeight': 'bold'}),
                html.P(f"₹{best_brand['revenue']:,.0f}", style={'color': '#7f8c8d', 'fontSize': '0.9em'})
            ], className='card-item', style={
                'backgroundColor': '#fef9e7',
                'padding': '25px',
                'borderRadius': '12px',
                'textAlign': 'center',
                'boxShadow': '0 4px 15px rgba(243, 156, 18, 0.2)'
            })
        ], className='card-row')
    ])

# Callback for Brand Performance Chart
@app.callback(Output('brand-performance-chart', 'figure'), [Input('brand-performance-chart', 'id')])
def update_brand_performance_chart(_):
    # Load brand performance data from CSV
    try:
        brand_df = pd.read_csv('data/brand_performance.csv')
        brand_df.columns = ['Brand', 'Campaigns', 'Reach', 'Revenue', 'Cost', 'ROAS']
    except:
        # Fallback: Create brand performance data from posts
        posts_df = pd.read_csv('data/posts.csv')
        brand_performance = posts_df.groupby('brand_mentioned').agg({
            'post_id': 'count',
            'reach': 'sum',
            'likes': 'sum'
        }).reset_index()
        
        # Calculate revenue estimate and ROAS
        brand_performance['revenue'] = brand_performance['reach'] * 0.05  # 5% conversion
        brand_performance['cost'] = brand_performance['post_id'] * 50000  # ₹50k per campaign
        brand_performance['roas'] = brand_performance['revenue'] / brand_performance['cost']
        
        # Rename columns for chart
        brand_performance.columns = ['Brand', 'Campaigns', 'Reach', 'Likes', 'Revenue', 'Cost', 'ROAS']
        brand_df = brand_performance.sort_values('Revenue', ascending=False)
    
    # Use go.Figure instead of px.bar to avoid template issues
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=brand_df['Brand'],
        y=brand_df['Revenue'],
        marker_color=['#3498db', '#e74c3c', '#27ae60', '#f39c12'],
        hovertemplate='<b>%{x}</b><br>Revenue: ₹%{y:,.0f}<br>ROAS: %{customdata:.2f}<extra></extra>',
        customdata=brand_df['ROAS']
    ))
    
    fig.update_layout(
        title='Brand Performance - Revenue by Brand',
        title_x=0.5,
        height=350,
        xaxis_title='Brand',
        yaxis_title='Revenue (₹)'
    )
    return fig


    # Create timeline data based on posts data
    posts_df = pd.read_csv('data/posts.csv')
    posts_df['date'] = pd.to_datetime(posts_df['date'])
    
    # Group by date and calculate metrics
    daily_metrics = posts_df.groupby('date').agg({
        'reach': 'sum',
        'likes': 'sum',
        'post_id': 'count'
    }).reset_index()
    
    # Calculate revenue and orders based on reach (static conversion rates)
    daily_metrics['revenue'] = daily_metrics['reach'] * 0.02  # 2% revenue conversion
    daily_metrics['orders'] = daily_metrics['reach'] * 0.0008  # 0.08% order conversion
    
    # Fill missing dates in the last 30 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=29)
    full_date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    timeline_df = pd.DataFrame({'date': full_date_range})
    timeline_df = timeline_df.merge(daily_metrics, on='date', how='left')
    timeline_df = timeline_df.fillna({'revenue': 8000, 'orders': 35, 'post_id': 1})  # Fill missing with averages
    timeline_df['date'] = timeline_df['date'].dt.strftime('%Y-%m-%d')
    
    # Create figure using go.Scatter to avoid template issues
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=timeline_df['date'],
        y=timeline_df['revenue'],
        mode='lines+markers',
        name='Daily Revenue',
        line=dict(color='#3498db', width=3),
        hovertemplate='<b>Date</b>: %{x}<br><b>Revenue</b>: ₹%{y:,.0f}<br><b>Orders</b>: %{customdata}<extra></extra>',
        customdata=timeline_df['orders']
    ))
    
    fig.update_layout(
        title='Campaign Performance Timeline - Daily Revenue Trend',
        title_x=0.5,
        height=350,
        xaxis_title='Date',
        yaxis_title='Revenue (₹)',
        showlegend=False
    )
    
    return fig

# Callback for Payout Summary Cards
@app.callback(
    Output('payout-summary-cards', 'children'),
    [Input('payout-tracking-table', 'id')]
)
def update_payout_summary(_):
    # Calculate payout metrics
    total_payouts = payout_df['total_cost'].sum()
    pending_amount = total_payouts * 0.15  # 15% pending
    paid_amount = total_payouts - pending_amount
    avg_payout = payout_df['total_cost'].mean()
    
    # Payment type distribution
    per_post_campaigns = len(payout_df) * 0.6  # 60% per post
    per_order_campaigns = len(payout_df) * 0.4  # 40% per order
    
    return html.Div([
        # First Row - 2 cards
        html.Div([
            # Total Payouts
            html.Div([
                html.H3(f"₹{total_payouts:,.0f}", style={'color': '#3498db', 'fontSize': '2.2em', 'margin': '0'}),
                html.P("Total Payouts", style={'color': '#2c3e50', 'fontWeight': 'bold'})
            ], className='card-item', style={
                'backgroundColor': '#ebf3fd',
                'padding': '25px',
                'borderRadius': '12px',
                'textAlign': 'center',
                'boxShadow': '0 4px 15px rgba(52, 152, 219, 0.2)'
            }),
            
            # Paid Amount
            html.Div([
                html.H3(f"₹{paid_amount:,.0f}", style={'color': '#27ae60', 'fontSize': '2.2em', 'margin': '0'}),
                html.P("Amount Paid", style={'color': '#2c3e50', 'fontWeight': 'bold'})
            ], className='card-item', style={
                'backgroundColor': '#d5f4e6',
                'padding': '25px',
                'borderRadius': '12px',
                'textAlign': 'center',
                'boxShadow': '0 4px 15px rgba(39, 174, 96, 0.2)'
            })
        ], className='card-row'),
        
        # Second Row - 2 cards
        html.Div([
            # Pending Amount
            html.Div([
                html.H3(f"₹{pending_amount:,.0f}", style={'color': '#f39c12', 'fontSize': '2.2em', 'margin': '0'}),
                html.P("Pending Payouts", style={'color': '#2c3e50', 'fontWeight': 'bold'})
            ], className='card-item', style={
                'backgroundColor': '#fef9e7',
                'padding': '25px',
                'borderRadius': '12px',
                'textAlign': 'center',
                'boxShadow': '0 4px 15px rgba(243, 156, 18, 0.2)'
            }),
            
            # Average Payout
            html.Div([
                html.H3(f"₹{avg_payout:,.0f}", style={'color': '#9b59b6', 'fontSize': '2.2em', 'margin': '0'}),
                html.P("Avg Payout", style={'color': '#2c3e50', 'fontWeight': 'bold'})
            ], className='card-item', style={
                'backgroundColor': '#f4ecf7',
                'padding': '25px',
                'borderRadius': '12px',
                'textAlign': 'center',
                'boxShadow': '0 4px 15px rgba(155, 89, 182, 0.2)'
            })
        ], className='card-row')
    ])

# Callback for Payout Tracking Table
@app.callback(Output('payout-tracking-table', 'data'), [Input('payout-tracking-table', 'id')])
def update_payout_tracking_table(_):
    # Merge payout and influencer data with posts data to get brands
    merged_df = pd.merge(payout_df, influencer_df, on='influencer_id')
    posts_df = pd.read_csv('data/posts.csv')
    
    # Get brand for each influencer from their most recent post
    influencer_brands = posts_df.groupby('influencer_id')['brand_mentioned'].first().reset_index()
    influencer_brands.columns = ['influencer_id', 'brand']
    
    merged_df = pd.merge(merged_df, influencer_brands, on='influencer_id', how='left')
    merged_df['brand'] = merged_df['brand'].fillna('HealthKart')  # Default brand
    
    # Set payment type based on basis column
    merged_df['payment_type'] = merged_df['basis'].apply(
        lambda x: 'Per Post' if 'post' in str(x).lower() else 'Per Order'
    )
    
    # Set status based on payout amount (higher payouts more likely to be paid)
    merged_df['status'] = merged_df['payout_amount'].apply(
        lambda x: 'Paid' if x > 300000 else ('Processing' if x > 100000 else 'Pending')
    )
    
    merged_df['payout_amount'] = merged_df['total_cost']
    # Create static dates based on influencer_id (for consistency)
    base_date = datetime.now() - timedelta(days=30)
    merged_df['payout_date'] = [
        (base_date + timedelta(days=i*3)).strftime('%Y-%m-%d') 
        for i in range(len(merged_df))
    ]
    
    # Select relevant columns and rename
    payout_table = merged_df[['name', 'brand', 'platform', 'payment_type', 'orders', 'payout_amount', 'status', 'payout_date']].copy()
    payout_table.columns = ['influencer_name', 'brand', 'platform', 'payment_type', 'orders', 'payout_amount', 'status', 'payout_date']
    
    return payout_table.to_dict('records')

# Callback for influencer-specific KPIs
@app.callback(
    Output('platform-kpis-container', 'children'),
    [Input('influencer-dropdown', 'value')]
)
def update_influencer_kpis(selected_influencer):
    # Get influencer info
    influencer_info = influencer_df[influencer_df['influencer_id'] == selected_influencer].iloc[0]
    
    # Get tracking data for this influencer
    influencer_tracking = tracking_df[tracking_df['influencer_id'] == selected_influencer]
    
    # Calculate metrics
    total_orders = influencer_tracking['orders'].sum()
    total_revenue = influencer_tracking['revenue'].sum()
    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
    unique_customers = influencer_tracking['user_id'].nunique()
    
    # Product performance
    top_products = influencer_tracking.groupby('product').agg({
        'orders': 'sum',
        'revenue': 'sum'
    }).sort_values('revenue', ascending=False).head(3)
    
    return html.Div([
        # Influencer Header
        html.Div([
            html.H4(f"{influencer_info['name']}", style={'color': '#2c3e50', 'margin': '0'}),
            html.P(f"{influencer_info['category']} • {influencer_info['platform']} • {influencer_info['follower_count']:,} followers", 
                  style={'color': '#7f8c8d', 'margin': '5px 0'})
        ], style={'textAlign': 'center', 'marginBottom': '30px'}),
        
        # KPI Cards - 2 per row
        html.Div([
            # First Row - 2 cards
            html.Div([
                # Total Orders
                html.Div([
                    html.H3(f"{total_orders:,}", style={'color': '#27ae60', 'fontSize': '2.5em', 'margin': '0'}),
                    html.P("Total Orders", style={'color': '#2c3e50', 'fontWeight': 'bold'})
                ], className='card-item', style={
                    'backgroundColor': '#d5f4e6',
                    'padding': '25px',
                    'borderRadius': '12px',
                    'textAlign': 'center',
                    'boxShadow': '0 4px 15px rgba(39, 174, 96, 0.2)'
                }),
                
                # Total Revenue
                html.Div([
                    html.H3(f"₹{total_revenue:,.0f}", style={'color': '#3498db', 'fontSize': '2.5em', 'margin': '0'}),
                    html.P("Total Revenue", style={'color': '#2c3e50', 'fontWeight': 'bold'})
                ], className='card-item', style={
                    'backgroundColor': '#ebf3fd',
                    'padding': '25px',
                    'borderRadius': '12px',
                    'textAlign': 'center',
                    'boxShadow': '0 4px 15px rgba(52, 152, 219, 0.2)'
                })
            ], className='card-row'),
            
            # Second Row - 2 cards
            html.Div([
                # AOV
                html.Div([
                    html.H3(f"₹{avg_order_value:,.0f}", style={'color': '#e74c3c', 'fontSize': '2.5em', 'margin': '0'}),
                    html.P("Avg Order Value", style={'color': '#2c3e50', 'fontWeight': 'bold'})
                ], className='card-item', style={
                    'backgroundColor': '#fdeaea',
                    'padding': '25px',
                    'borderRadius': '12px',
                    'textAlign': 'center',
                    'boxShadow': '0 4px 15px rgba(231, 76, 60, 0.2)'
                }),
                
                # Unique Customers
                html.Div([
                    html.H3(f"{unique_customers:,}", style={'color': '#f39c12', 'fontSize': '2.5em', 'margin': '0'}),
                    html.P("Unique Customers", style={'color': '#2c3e50', 'fontWeight': 'bold'})
                ], className='card-item', style={
                    'backgroundColor': '#fef9e7',
                    'padding': '25px',
                    'borderRadius': '12px',
                    'textAlign': 'center',
                    'boxShadow': '0 4px 15px rgba(243, 156, 18, 0.2)'
                })
            ], className='card-row')
        ]),
        
        # Top Products
        html.Div([
            html.H4("Top Performing Products", style={'color': '#2c3e50', 'textAlign': 'center', 'marginTop': '30px'}),
            html.Div([
                html.Div([
                    html.H5(f"#{i+1} {product}", style={'color': '#34495e', 'margin': '0'}),
                    html.P(f"Orders: {row['orders']:,} | Revenue: ₹{row['revenue']:,.0f}", 
                          style={'color': '#7f8c8d', 'margin': '5px 0'})
                ], style={
                    'backgroundColor': '#ecf0f1',
                    'padding': '15px',
                    'borderRadius': '8px',
                    'margin': '10px',
                    'width': '30%',
                    'display': 'inline-block',
                    'textAlign': 'center'
                }) for i, (product, row) in enumerate(top_products.iterrows())
            ])
        ])
    ])

# Callback for Instagram KPIs
@app.callback(
    Output('instagram-kpis-cards', 'children'),
    [Input('platform-chart', 'id')]
)
def update_instagram_kpis(_):
    # Calculate engagement rate
    total_likes = instagram_df['likes'].sum()
    total_comments = instagram_df['comments'].sum()
    total_saves = instagram_df['saves'].sum()
    total_reach = instagram_df['reach'].sum()
    engagement_rate = (total_likes + total_comments + total_saves) / total_reach * 100
    
    # Story completion rate
    story_completion = instagram_df['story_completion_rate'].mean()
    
    # Profile Visits + Website Clicks
    total_visits = instagram_df['profile_visits'].sum()
    total_clicks = instagram_df['website_clicks'].sum()
    profile_activity = (total_visits + total_clicks) / total_reach * 100
    
    # Average impressions
    avg_impressions = instagram_df['impressions'].mean()

    return html.Div([
        # Engagement Rate Card
        html.Div([
            html.H3(f"{engagement_rate:.2f}%", style={'color': '#E4405F', 'fontSize': '2em', 'margin': '0'}),
            html.P("Engagement Rate", style={'color': '#2c3e50', 'fontWeight': 'bold', 'margin': '5px 0'})
        ], style={
            'backgroundColor': '#fef7f7',
            'padding': '20px',
            'borderRadius': '10px',
            'textAlign': 'center',
            'marginBottom': '15px',
            'border': '1px solid #E4405F30'
        }),
        
        # Story Completion Rate Card
        html.Div([
            html.H3(f"{story_completion:.1f}%", style={'color': '#E4405F', 'fontSize': '2em', 'margin': '0'}),
            html.P("Story Completion", style={'color': '#2c3e50', 'fontWeight': 'bold', 'margin': '5px 0'})
        ], style={
            'backgroundColor': '#fef7f7',
            'padding': '20px',
            'borderRadius': '10px',
            'textAlign': 'center',
            'marginBottom': '15px',
            'border': '1px solid #E4405F30'
        }),
        
        # Profile Activity Card
        html.Div([
            html.H3(f"{profile_activity:.2f}%", style={'color': '#E4405F', 'fontSize': '2em', 'margin': '0'}),
            html.P("Profile Activity Rate", style={'color': '#2c3e50', 'fontWeight': 'bold', 'margin': '5px 0'})
        ], style={
            'backgroundColor': '#fef7f7',
            'padding': '20px',
            'borderRadius': '10px',
            'textAlign': 'center',
            'marginBottom': '15px',
            'border': '1px solid #E4405F30'
        }),
        
        # Average Impressions Card
        html.Div([
            html.H3(f"{avg_impressions:,.0f}", style={'color': '#E4405F', 'fontSize': '2em', 'margin': '0'}),
            html.P("Avg Impressions", style={'color': '#2c3e50', 'fontWeight': 'bold', 'margin': '5px 0'})
        ], style={
            'backgroundColor': '#fef7f7',
            'padding': '20px',
            'borderRadius': '10px',
            'textAlign': 'center',
            'border': '1px solid #E4405F30'
        })
    ])

# Callback for YouTube KPIs
@app.callback(
    Output('youtube-kpis-cards', 'children'),
    [Input('platform-chart', 'id')]
)
def update_youtube_kpis(_):
    # Calculate average CTR
    avg_ctr = youtube_df['impressions_ctr_percentage'].mean()
    
    # Calculate average retention
    avg_retention = youtube_df['audience_retention_percentage'].mean()
    
    # Total subscribers gained
    total_subs_gained = youtube_df['subscribers_gained'].sum()
    
    # Average watch time
    avg_watch_time = youtube_df['watch_time_hours'].mean()
    
    return html.Div([
        # CTR Card
        html.Div([
            html.H3(f"{avg_ctr:.2f}%", style={'color': '#FF0000', 'fontSize': '2em', 'margin': '0'}),
            html.P("Click-Through Rate", style={'color': '#2c3e50', 'fontWeight': 'bold', 'margin': '5px 0'})
        ], style={
            'backgroundColor': '#fff5f5',
            'padding': '20px',
            'borderRadius': '10px',
            'textAlign': 'center',
            'marginBottom': '15px',
            'border': '1px solid #FF000030'
        }),
        
        # Retention Card
        html.Div([
            html.H3(f"{avg_retention:.1f}%", style={'color': '#FF0000', 'fontSize': '2em', 'margin': '0'}),
            html.P("Audience Retention", style={'color': '#2c3e50', 'fontWeight': 'bold', 'margin': '5px 0'})
        ], style={
            'backgroundColor': '#fff5f5',
            'padding': '20px',
            'borderRadius': '10px',
            'textAlign': 'center',
            'marginBottom': '15px',
            'border': '1px solid #FF000030'
        }),
        
        # Subscribers Card
        html.Div([
            html.H3(f"{total_subs_gained:,}", style={'color': '#FF0000', 'fontSize': '2em', 'margin': '0'}),
            html.P("Subscribers Gained", style={'color': '#2c3e50', 'fontWeight': 'bold', 'margin': '5px 0'})
        ], style={
            'backgroundColor': '#fff5f5',
            'padding': '20px',
            'borderRadius': '10px',
            'textAlign': 'center',
            'marginBottom': '15px',
            'border': '1px solid #FF000030'
        }),
        
        # Watch Time Card
        html.Div([
            html.H3(f"{avg_watch_time:.1f}h", style={'color': '#FF0000', 'fontSize': '2em', 'margin': '0'}),
            html.P("Avg Watch Time", style={'color': '#2c3e50', 'fontWeight': 'bold', 'margin': '5px 0'})
        ], style={
            'backgroundColor': '#fff5f5',
            'padding': '20px',
            'borderRadius': '10px',
            'textAlign': 'center',
            'border': '1px solid #FF000030'
        })
    ])


# ---------- HELPER FUNCTIONS FOR ADVANCED ANALYTICS ----------

def calc_audience_growth(df_inf, df_posts=None):
    """
    Module 1: Audience Growth Analytics
    Calculate net-new followers and follower CAGR
    """
    if df_inf.empty:
        return pd.DataFrame()
    
    growth_data = []
    for _, influencer in df_inf.iterrows():
        base_followers = influencer['follower_count']
        # Create static growth data based on influencer characteristics
        for week in range(12):
            date = datetime.now() - timedelta(weeks=week)
            # Use a static growth rate based on follower count (bigger influencers = more stable)
            if base_followers > 5000000:
                growth_rate = 1.02  # 2% growth for mega influencers
            elif base_followers > 1000000:
                growth_rate = 1.03  # 3% growth for macro influencers  
            else:
                growth_rate = 1.05  # 5% growth for micro influencers
                
            followers = int(base_followers * (growth_rate ** (12-week)))
            net_new = max(int(followers * 0.02), 100)  # 2% new followers per week, minimum 100
            
            growth_data.append({
                'influencer_id': influencer['influencer_id'],
                'name': influencer['name'],
                'date': date.strftime('%Y-%m-%d'),
                'week': week,
                'followers': followers,
                'net_new': net_new,
                'platform': influencer['platform']
            })
    
    growth_df = pd.DataFrame(growth_data)
    growth_df['follower_cagr'] = growth_df.groupby('influencer_id')['followers'].pct_change().fillna(0) * 100
    
    return growth_df

def calc_incremental_roas(df_payout, baseline_rate=0.30):
    """
    Module 2: Incremental ROAS Analytics
    Calculate iROAS per campaign, lift %, cost-per-incremental-order
    """
    if df_payout.empty:
        return pd.DataFrame()
        
    df = df_payout.copy()
    
    # Calculate baseline (organic) orders
    df['baseline_orders'] = (df['orders'] * baseline_rate).astype(int)
    df['incremental_orders'] = df['orders'] - df['baseline_orders']
    
    # Calculate incremental revenue
    df['incremental_revenue'] = df['total_revenue'] * (df['incremental_orders'] / df['orders'])
    
    # Calculate incremental ROAS
    df['iroas'] = df['incremental_revenue'] / df['total_cost']
    df['lift_percentage'] = (df['incremental_orders'] / df['baseline_orders'].replace(0, np.nan)) * 100
    df['cost_per_incremental_order'] = df['total_cost'] / df['incremental_orders'].replace(0, np.nan)
    
    return df

def calc_creative_fatigue(df_posts, df_instagram=None):
    """
    Module 3: Creative Fatigue Analytics
    Calculate %Δ CTR and %Δ CPC by flight week
    """
    if df_posts.empty:
        return pd.DataFrame()
    
    fatigue_data = []
    
    for _, post in df_posts.iterrows():
        # Generate static performance data based on post characteristics
        for week in range(1, 5):
            decay_factor = 1 - (0.15 * (week - 1))  # 15% decay per week
            
            # Base CTR/CPC based on platform and engagement
            if post['platform'] == 'Instagram':
                base_ctr = 2.5 + (post['likes'] / post['reach']) * 100 if post['reach'] > 0 else 2.5
                base_cpc = 35
            else:  # YouTube
                base_ctr = 3.2 + (post['likes'] / post['video_views']) * 100 if post['video_views'] > 0 else 3.2
                base_cpc = 28
            
            ctr = base_ctr * decay_factor
            cpc = base_cpc / decay_factor
            
            fatigue_data.append({
                'post_id': post['post_id'],
                'influencer_id': post['influencer_id'],
                'week': week,
                'ctr': ctr,
                'cpc': cpc,
                'platform': post['platform']
            })
    
    fatigue_df = pd.DataFrame(fatigue_data)
    
    # Calculate percentage changes
    fatigue_df['ctr_pct_change'] = fatigue_df.groupby('post_id')['ctr'].pct_change() * 100
    fatigue_df['cpc_pct_change'] = fatigue_df.groupby('post_id')['cpc'].pct_change() * 100
    
    return fatigue_df

def calc_product_affinity(df_tracking):
    """
    Module 4: Product Affinity Analytics
    Calculate SKU-level CVR, AOV, attach rate
    """
    if df_tracking.empty:
        return pd.DataFrame()
    
    # Group by product
    affinity = df_tracking.groupby('product').agg({
        'orders': 'sum',
        'revenue': 'sum',
        'user_id': 'nunique'  # unique users per product
    }).reset_index()
    
    # Calculate key metrics
    affinity['aov'] = affinity['revenue'] / affinity['orders']  # Average Order Value
    affinity['cvr'] = (affinity['orders'] / affinity['user_id']) * 100  # Conversion Rate
    affinity['attach_rate'] = affinity['orders'] / affinity['orders'].sum()  # Attach Rate
    
    return affinity

def calc_geo_efficiency(df_geo):
    """
    Module 5: Geo Efficiency Analytics
    Calculate orders per 1k reach, city ROAS
    """
    if df_geo.empty:
        return pd.DataFrame()
    
    df = df_geo.copy()
    
    # Add latitude and longitude if not present (for Indian cities)
    city_coordinates = {
        'Mumbai': {'latitude': 19.0760, 'longitude': 72.8777},
        'Delhi': {'latitude': 28.7041, 'longitude': 77.1025},
        'Bangalore': {'latitude': 12.9716, 'longitude': 77.5946},
        'Bengaluru': {'latitude': 12.9716, 'longitude': 77.5946},
        'Hyderabad': {'latitude': 17.3850, 'longitude': 78.4867},
        'Chennai': {'latitude': 13.0827, 'longitude': 80.2707},
        'Kolkata': {'latitude': 22.5726, 'longitude': 88.3639},
        'Pune': {'latitude': 18.5204, 'longitude': 73.8567},
        'Ahmedabad': {'latitude': 23.0225, 'longitude': 72.5714},
        'Jaipur': {'latitude': 26.9124, 'longitude': 75.7873},
        'Surat': {'latitude': 21.1702, 'longitude': 72.8311},
        'Lucknow': {'latitude': 26.8467, 'longitude': 80.9462},
        'Kanpur': {'latitude': 26.4499, 'longitude': 80.3319},
        'Nagpur': {'latitude': 21.1458, 'longitude': 79.0882},
        'Indore': {'latitude': 22.7196, 'longitude': 75.8577},
        'Thane': {'latitude': 19.2183, 'longitude': 72.9781},
        'Bhopal': {'latitude': 23.2599, 'longitude': 77.4126},
        'Visakhapatnam': {'latitude': 17.6868, 'longitude': 83.2185},
        'Pimpri-Chinchwad': {'latitude': 18.6298, 'longitude': 73.7997},
        'Patna': {'latitude': 25.5941, 'longitude': 85.1376}
    }
    
    # Add product information if not present
    products = ['Protein Powder', 'Multivitamins', 'Fish Oil', 'BCAA', 'Pre-Workout', 'Whey Protein', 'Creatine']
    
    # If product column doesn't exist, create it based on brand mentioned in posts
    if 'product' not in df.columns:
        # Map brands to products
        brand_to_product = {
            'MuscleBlaze': 'Whey Protein',
            'HK Vitals': 'Multivitamins', 
            'HKVitals': 'Multivitamins',
            'Gritzo': 'Protein Powder',
            'bGreen': 'Fish Oil',
            'HealthKart': 'BCAA'
        }
        # Create cycling pattern for products based on index
        df['product'] = [products[i % len(products)] for i in range(len(df))]
    
    # Add coordinates without random offset for consistency
    if 'latitude' not in df.columns or 'longitude' not in df.columns:
        df['latitude'] = df['city'].map(lambda x: city_coordinates.get(x, {}).get('latitude', 20.5937))
        df['longitude'] = df['city'].map(lambda x: city_coordinates.get(x, {}).get('longitude', 78.9629))
        
    # Add small static offset based on city name hash to prevent overlapping markers
    df['city_hash'] = df['city'].astype(str).apply(lambda x: abs(hash(x)) % 100)
    df['latitude'] = df['latitude'] + (df['city_hash'] - 50) * 0.002
    df['longitude'] = df['longitude'] + (df['city_hash'] - 50) * 0.002
    
    # Calculate efficiency metrics based on actual data
    df['orders_per_1k_reach'] = (df['estimated_views'] / 1000) * 0.01  # Static 1% conversion
    df['orders'] = df['estimated_views'] * 0.0008  # Static 0.08% order rate
    df['orders'] = df['orders'].astype(int).clip(lower=10)  # Minimum 10 orders
    df['revenue'] = df['orders'] * 2500  # Static ₹2500 per order
    
    # Calculate ROAS based on static cost per order
    cost_per_order = 800  # Static ₹800 cost per order
    df['city_roas'] = df['revenue'] / (df['orders'] * cost_per_order)
    
    return df

def calc_lifetime_lift(df_tracking):
    """
    Module 6: Lifetime Lift Analytics
    Calculate 90-day LTV vs CAC
    """
    if df_tracking.empty:
        return pd.DataFrame()
    
    # Convert date column to datetime
    df_tracking['date'] = pd.to_datetime(df_tracking['date'])
    
    # Create cohorts based on user acquisition month
    df_tracking['cohort_month'] = df_tracking['date'].dt.to_period('M')
    
    # Calculate LTV metrics
    cohort_data = df_tracking.groupby(['cohort_month', 'influencer_id']).agg({
        'revenue': 'sum',
        'orders': 'sum',
        'user_id': 'nunique'
    }).reset_index()
    
    cohort_data['ltv'] = cohort_data['revenue'] / cohort_data['user_id']
    
    return cohort_data


# ---------- ADVANCED ANALYTICS TAB CALLBACK ----------
@app.callback(
    Output('advanced-content', 'children'),
    Input('advanced-tabs', 'value')
)
def render_advanced_content(selected_tab):
    """Main callback for advanced analytics tabs"""
    
    if selected_tab == 'audience-growth':
        # Module 1: Audience Growth
        growth_data = calc_audience_growth(influencer_df, posts_df)
        
        if growth_data.empty:
            return html.Div([
                html.H4("Audience Growth Analysis", style={'textAlign': 'center'}),
                html.P("No data available for audience growth analysis.", 
                       style={'textAlign': 'center', 'color': '#7f8c8d'})
            ])
        
        # Create simple visualization
        fig = px.line(growth_data.groupby('date')['followers'].sum().reset_index(), 
                     x='date', y='followers', title='Total Followers Over Time')
        fig.update_layout(height=400)
        
        return html.Div([
            html.Div([
                html.H4("Audience Growth Analysis", 
                       style={'textAlign': 'center', 'color': '#3498db', 'marginBottom': '20px'}),
                dcc.Graph(figure=fig)
            ], style={
                'backgroundColor': '#f8f9fa',
                'padding': '20px',
                'borderRadius': '10px',
                'border': '1px solid #dee2e6'
            })
        ])
    
    elif selected_tab == 'incremental-roas':
        # Module 2: Incremental ROAS
        iroas_data = calc_incremental_roas(payout_df)
        
        if iroas_data.empty:
            return html.Div([
                html.H4("Incremental ROAS Analysis", style={'textAlign': 'center'}),
                html.P("No payout data available.", style={'textAlign': 'center', 'color': '#7f8c8d'})
            ])
        
        # Merge with influencer data for names
        iroas_with_names = pd.merge(iroas_data, influencer_df, on='influencer_id', how='left')
        
        # Create bar chart
        fig = px.bar(iroas_with_names, x='name', y='iroas', 
                    title='Incremental ROAS by Influencer')
        fig.update_layout(height=400, xaxis_tickangle=-45)
        
        return html.Div([
            html.H4("Incremental ROAS Analysis", style={'textAlign': 'center'}),
            dcc.Graph(figure=fig)
        ])
    
    elif selected_tab == 'product-affinity':
        # Module 4: Product Affinity
        affinity_data = calc_product_affinity(tracking_df)
        
        if affinity_data.empty:
            return html.Div([
                html.H4("Product Affinity Analysis", style={'textAlign': 'center'}),
                html.P("No tracking data available.", style={'textAlign': 'center', 'color': '#7f8c8d'})
            ])
        
        # Create scatter plot
        fig = px.scatter(affinity_data, x='cvr', y='aov', size='orders',
                        hover_name='product', title='Product Affinity: CVR vs AOV')
        fig.update_layout(height=400)
        
        return html.Div([
            html.H4("Product Affinity Analysis", style={'textAlign': 'center'}),
            dcc.Graph(figure=fig)
        ])
    
    elif selected_tab == 'geo-efficiency':
        # Module 5: Geo Efficiency
        geo_data = calc_geo_efficiency(geographic_distribution_df)
        
        if geo_data.empty:
            return html.Div([
                html.H4("Geographic Efficiency Analysis", style={'textAlign': 'center'}),
                html.P("No geographic data available.", style={'textAlign': 'center', 'color': '#7f8c8d'})
            ])
        
        # Create India map with city markers
        india_map = px.scatter_mapbox(
            geo_data,
            lat='latitude',
            lon='longitude',
            size='orders',
            color='city_roas',
            hover_name='city',
            hover_data={
                'product': True,
                'orders': ':,',
                'revenue': ':,.0f',
                'city_roas': ':.2f',
                'orders_per_1k_reach': ':.3f',
                'estimated_views': ':,',
                'latitude': False,
                'longitude': False
            },
            color_continuous_scale='Viridis',
            size_max=30,
            zoom=4,
            center={'lat': 20.5937, 'lon': 78.9629},  # Center of India
            mapbox_style='open-street-map',
            title='Geographic Performance Across India - Campaign Reach by City & Product',
            height=700
        )
        
        india_map.update_layout(
            mapbox=dict(
                bearing=0,
                pitch=0,
                zoom=4.5,
                center=dict(lat=20.5937, lon=78.9629)
            ),
            title={
                'text': 'Geographic Performance Across India - Campaign Reach by City & Product',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 16}
            },
            margin=dict(l=0, r=0, t=50, b=0)
        )
        
        # Create top cities bar chart with product breakdown
        top_cities = geo_data.nlargest(15, 'city_roas')
        bar_chart = px.bar(top_cities, x='city', y='city_roas', 
                          title='Top 15 Cities by ROAS with Product Breakdown',
                          color='product',
                          hover_data={
                              'product': True,
                              'orders': ':,',
                              'revenue': ':,.0f'
                          })
        bar_chart.update_layout(height=400, xaxis_tickangle=-45)
        
        return html.Div([
            html.Div([
                html.H4("Geographic Efficiency Analysis", 
                       style={'textAlign': 'center', 'color': '#f39c12', 'marginBottom': '30px', 'fontSize': '1.8em'}),
                
                # Map visualization with increased size
                html.Div([
                    dcc.Graph(figure=india_map, style={'height': '700px'})
                ], style={'marginBottom': '40px'}),
                
                # Bar chart for top cities with product info
                html.Div([
                    dcc.Graph(figure=bar_chart)
                ])
            ], style={
                'backgroundColor': '#f8f9fa',
                'padding': '30px',
                'borderRadius': '15px',
                'border': '1px solid #dee2e6',
                'minHeight': '1200px'
            })
        ])
    
    elif selected_tab == 'lifetime-lift':
        # Module 6: Lifetime Lift
        cohort_data = calc_lifetime_lift(tracking_df)
        
        if cohort_data.empty:
            return html.Div([
                html.H4("Lifetime Lift Analysis", style={'textAlign': 'center'}),
                html.P("No tracking data available.", style={'textAlign': 'center', 'color': '#7f8c8d'})
            ])
        
        # Create LTV by influencer chart
        ltv_summary = cohort_data.groupby('influencer_id')['ltv'].mean().reset_index()
        fig = px.bar(ltv_summary, x='influencer_id', y='ltv', 
                    title='Average LTV by Influencer')
        fig.update_layout(height=400)
        
        return html.Div([
            html.H4("Lifetime Lift Analysis", style={'textAlign': 'center'}),
            dcc.Graph(figure=fig)
        ])
    
    elif selected_tab == 'cac-analysis':
        # CAC Analysis - prepare the data first with fallback
        try:
            if tracking_data_df.empty:
                cost_orders = payout_df[['influencer_id', 'total_cost', 'orders']].copy()
                cost_orders = cost_orders.merge(influencer_df[['influencer_id', 'platform']],
                                                on='influencer_id', how='left')
                cost_orders['unique_customers'] = (cost_orders['orders'] * 0.8).astype(int)  # Static 80% unique rate
            else:
                uniques = (tracking_data_df
                           .groupby('influencer_id')['user_id']
                           .nunique()
                           .reset_index(name='unique_customers'))
                cost_orders = payout_df.merge(uniques, on='influencer_id', how='left')
                cost_orders = cost_orders.merge(influencer_df[['influencer_id', 'platform']],
                                                on='influencer_id', how='left')
                cost_orders['unique_customers'].fillna(cost_orders['orders'], inplace=True)

            cost_orders['cac'] = cost_orders['total_cost'] / cost_orders['unique_customers'].replace(0, np.nan)

            # Create overall metrics
            total_cost = cost_orders['total_cost'].sum()
            total_customers = cost_orders['unique_customers'].sum()
            avg_cac = cost_orders['cac'].mean()

            # Platform breakdown
            by_platform = (cost_orders.groupby('platform')
                           .agg(total_cost=('total_cost', 'sum'),
                                customers=('unique_customers', 'sum'))
                           .reset_index())
            by_platform['cac'] = by_platform['total_cost'] / by_platform['customers']

            # Influencer breakdown
            by_influencer = cost_orders.merge(influencer_df[['influencer_id', 'name']], on='influencer_id')
            by_influencer = by_influencer[['name', 'platform', 'total_cost', 'unique_customers', 'cac']].copy()

            # Create KPI cards
            card_style = {
                'backgroundColor': '#f8f9fa',
                'padding': '20px',
                'borderRadius': '10px',
                'textAlign': 'center',
                'width': '30%',
                'display': 'inline-block',
                'margin': '1%'
            }

            kpi_cards = html.Div([
                html.Div([
                    html.H4("Avg CAC (Overall)", style={'color': '#2c3e50'}),
                    html.H2(f"₹{avg_cac:,.2f}", style={'color': '#e67e22'})
                ], style=card_style),
                html.Div([
                    html.H4("Total Customers", style={'color': '#2c3e50'}),
                    html.H2(f"{int(total_customers):,}", style={'color': '#27ae60'})
                ], style=card_style),
                html.Div([
                    html.H4("Total Spend", style={'color': '#2c3e50'}),
                    html.H2(f"₹{total_cost:,.0f}", style={'color': '#c0392b'})
                ], style=card_style)
            ])

            # Platform chart
            fig_plat = px.bar(by_platform,
                              x='platform', y='cac',
                              color='platform',
                              text=by_platform['cac'].round(0),
                              title='Customer Acquisition Cost by Platform')
            fig_plat.update_layout(yaxis_title='CAC (₹)', xaxis_title='Platform', height=400)

            # Influencer table
            inf_table = dash_table.DataTable(
                columns=[
                    {'name': 'Influencer', 'id': 'name'},
                    {'name': 'Platform', 'id': 'platform'},
                    {'name': 'Spend (₹)', 'id': 'total_cost', 'type': 'numeric',
                     'format': {'specifier': ',.0f'}},
                    {'name': 'Customers', 'id': 'unique_customers', 'type': 'numeric',
                     'format': {'specifier': ',.0f'}},
                    {'name': 'CAC (₹)', 'id': 'cac', 'type': 'numeric',
                     'format': {'specifier': ',.0f'}}
                ],
                data=by_influencer.sort_values('cac').to_dict('records'),
                style_cell={'textAlign': 'center', 'padding': '12px', 'fontFamily': 'Inter'},
                style_header={'backgroundColor': '#e67e22', 'color': 'white', 'fontWeight': 'bold'},
                page_size=10
            )

            return html.Div([
                html.H4("💸 Customer Acquisition Cost Analysis", 
                       style={'textAlign': 'center', 'color': '#e67e22', 'marginBottom': '30px', 'fontSize': '1.8em'}),
                kpi_cards,
                dcc.Graph(figure=fig_plat, style={'margin': '30px 0'}),
                html.H4("Influencer-level CAC (sorted best to worst)",
                        style={'textAlign': 'center', 'marginTop': '20px', 'color': '#2c3e50'}),
                inf_table
            ], style={
                'backgroundColor': '#fdf6f0',
                'padding': '30px',
                'borderRadius': '15px',
                'border': '1px solid #e67e22'
            })

        except Exception as e:
            return html.Div([
                html.H4("CAC Analysis", style={'textAlign': 'center'}),
                html.P(f"Error loading CAC data: {str(e)}", style={'textAlign': 'center', 'color': '#e74c3c'})
            ])
        
    else:
        return html.Div([
            html.H4("Select an Analytics Module", style={'textAlign': 'center'}),
            html.P("Choose from the tabs above to view advanced analytics.", 
                   style={'textAlign': 'center', 'color': '#7f8c8d'})
        ])

# ==================== UPLOAD CALLBACKS ====================
@app.callback(
    Output('instagram-upload-status', 'children'),
    Input('upload-instagram', 'contents'),
    State('upload-instagram', 'filename')
)
def upload_instagram_data(contents, filename):
    if contents is not None:
        try:
            import base64
            import io
            
            # Decode the uploaded file
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
            df_new = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            
            # Validate required columns for Instagram data
            required_cols = ['influencer_id', 'likes', 'comments', 'saves', 'reach', 'impressions']
            missing_cols = [col for col in required_cols if col not in df_new.columns]
            if missing_cols:
                return html.Div(f"❌ Missing required columns: {missing_cols}", style={'color': '#e74c3c'})
            
            # Check if influencers exist and are Instagram influencers
            existing_instagram_influencers = set(influencer_df[influencer_df['platform'] == 'Instagram']['influencer_id'])
            new_influencers = set(df_new['influencer_id'])
            invalid_influencers = new_influencers - existing_instagram_influencers
            
            if invalid_influencers:
                return html.Div(f"❌ Invalid influencer IDs for Instagram: {list(invalid_influencers)}", style={'color': '#e74c3c'})
            
            # Append to existing Instagram data
            existing_df = pd.read_csv('data/instagram_insights_data.csv')
            combined_df = pd.concat([existing_df, df_new], ignore_index=True)
            combined_df.to_csv('data/instagram_insights_data.csv', index=False)
            
            return html.Div(f"✅ Successfully uploaded {len(df_new)} Instagram records!", style={'color': '#27ae60'})
            
        except Exception as e:
            return html.Div(f"❌ Error: {str(e)}", style={'color': '#e74c3c'})
    
    return ""

@app.callback(
    Output('youtube-upload-status', 'children'),
    Input('upload-youtube', 'contents'),
    State('upload-youtube', 'filename')
)
def upload_youtube_data(contents, filename):
    if contents is not None:
        try:
            import base64
            import io
            
            # Decode the uploaded file
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
            df_new = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            
            # Validate required columns for YouTube data
            required_cols = ['influencer_id', 'impressions_ctr_percentage', 'audience_retention_percentage', 'subscribers_gained', 'watch_time_hours']
            missing_cols = [col for col in required_cols if col not in df_new.columns]
            if missing_cols:
                return html.Div(f"❌ Missing required columns: {missing_cols}", style={'color': '#e74c3c'})
            
            # Check if influencers exist and are YouTube influencers
            existing_youtube_influencers = set(influencer_df[influencer_df['platform'] == 'YouTube']['influencer_id'])
            new_influencers = set(df_new['influencer_id'])
            invalid_influencers = new_influencers - existing_youtube_influencers
            
            if invalid_influencers:
                return html.Div(f"❌ Invalid influencer IDs for YouTube: {list(invalid_influencers)}", style={'color': '#e74c3c'})
            
            # Append to existing YouTube data
            existing_df = pd.read_csv('data/youtube_analytics_data.csv')
            combined_df = pd.concat([existing_df, df_new], ignore_index=True)
            combined_df.to_csv('data/youtube_analytics_data.csv', index=False)
            
            return html.Div(f"✅ Successfully uploaded {len(df_new)} YouTube records!", style={'color': '#27ae60'})
            
        except Exception as e:
            return html.Div(f"❌ Error: {str(e)}", style={'color': '#e74c3c'})
    
    return ""

@app.callback(
    Output('payout-upload-status', 'children'),
    Input('upload-payouts', 'contents'),
    State('upload-payouts', 'filename')
)
def upload_payout_data(contents, filename):
    if contents is not None:
        try:
            import base64
            import io
            
            # Decode the uploaded file
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
            df_new = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            
            # Validate required columns for Payouts
            required_cols = ['influencer_id', 'orders', 'total_revenue', 'total_cost']
            missing_cols = [col for col in required_cols if col not in df_new.columns]
            if missing_cols:
                return html.Div(f"❌ Missing required columns: {missing_cols}", style={'color': '#e74c3c'})
            
            # Check if influencers exist
            existing_influencers = set(influencer_df['influencer_id'])
            new_influencers = set(df_new['influencer_id'])
            invalid_influencers = new_influencers - existing_influencers
            
            if invalid_influencers:
                return html.Div(f"❌ Invalid influencer IDs: {list(invalid_influencers)}", style={'color': '#e74c3c'})
            
            # For payouts, we'll add the new data to existing influencer totals
            existing_df = pd.read_csv('data/payouts.csv')
            
            # Aggregate new data by influencer
            for _, new_row in df_new.iterrows():
                influencer_id = new_row['influencer_id']
                existing_row_idx = existing_df[existing_df['influencer_id'] == influencer_id].index
                
                if len(existing_row_idx) > 0:
                    # Add to existing influencer
                    idx = existing_row_idx[0]
                    existing_df.loc[idx, 'orders'] += new_row['orders']
                    existing_df.loc[idx, 'total_revenue'] += new_row['total_revenue']
                    existing_df.loc[idx, 'total_cost'] += new_row['total_cost']
                else:
                    # New influencer entry
                    existing_df = pd.concat([existing_df, new_row.to_frame().T], ignore_index=True)
            
            existing_df.to_csv('data/payouts.csv', index=False)
            
            return html.Div(f"✅ Successfully uploaded {len(df_new)} payout records!", style={'color': '#27ae60'})
            
        except Exception as e:
            return html.Div(f"❌ Error: {str(e)}", style={'color': '#e74c3c'})
    
    return ""

# Callback for CSV data export (table/analytics data)
@app.callback(
    Output('download-csv-data', 'data'),
    Input('export-csv-btn', 'n_clicks'),
    prevent_initial_call=True
)
def export_csv_data(n_clicks):
    if n_clicks:
        try:
            # Create a zip file containing displayed analytics data
            buffer = io.BytesIO()
            
            with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                # 1. Top Performing Influencers (main dashboard table)
                merged_df = pd.merge(payout_df, influencer_df, on='influencer_id')
                merged_df['roas'] = merged_df['total_revenue'] / merged_df['total_cost']
                top_performers = merged_df.nlargest(10, 'roas')[['name', 'category', 'platform', 'orders', 'total_revenue', 'roas']]
                zip_file.writestr("top_performing_influencers.csv", top_performers.to_csv(index=False))
                
                # 2. Platform Performance Summary
                platform_summary = influencer_df.groupby('platform').agg({
                    'follower_count': 'sum',
                    'influencer_id': 'count'
                }).reset_index()
                platform_summary.columns = ['Platform', 'Total_Followers', 'Influencer_Count']
                zip_file.writestr("platform_performance.csv", platform_summary.to_csv(index=False))
                
                # 3. Category Breakdown
                category_summary = influencer_df.groupby('category').agg({
                    'follower_count': 'sum',
                    'influencer_id': 'count'
                }).reset_index()
                category_summary.columns = ['Category', 'Total_Followers', 'Influencer_Count']
                zip_file.writestr("category_breakdown.csv", category_summary.to_csv(index=False))
                
                # 4. Payout Tracking Summary (all influencers with key metrics)
                payout_summary = merged_df[['name', 'platform', 'category', 'basis', 'rate', 
                                          'orders', 'total_revenue', 'payout_amount', 'total_cost', 'roas']].copy()
                payout_summary = payout_summary.sort_values('roas', ascending=False)
                zip_file.writestr("payout_tracking_summary.csv", payout_summary.to_csv(index=False))
                
                # 5. CAC Analysis Data
                try:
                    if not tracking_data_df.empty:
                        cost_orders = payout_df.merge(influencer_df[['influencer_id', 'platform']], on='influencer_id')
                        cost_orders['unique_customers'] = (cost_orders['orders'] * 0.8).astype(int)  # Static 80% unique rate
                        cost_orders['cac'] = cost_orders['total_cost'] / cost_orders['unique_customers'].replace(0, np.nan)
                        
                        # CAC by influencer
                        cac_analysis = cost_orders.merge(influencer_df[['influencer_id', 'name']], on='influencer_id')
                        cac_data = cac_analysis[['name', 'platform', 'total_cost', 'unique_customers', 'cac']].copy()
                        cac_data = cac_data.sort_values('cac').round(2)
                        zip_file.writestr("cac_analysis_by_influencer.csv", cac_data.to_csv(index=False))
                        
                        # CAC by platform
                        cac_by_platform = cost_orders.groupby('platform').agg({
                            'total_cost': 'sum',
                            'unique_customers': 'sum'
                        }).reset_index()
                        cac_by_platform['cac'] = cac_by_platform['total_cost'] / cac_by_platform['unique_customers']
                        zip_file.writestr("cac_analysis_by_platform.csv", cac_by_platform.to_csv(index=False))
                    else:
                        # Fallback CAC data
                        fallback_cac = merged_df[['name', 'platform', 'total_cost', 'orders']].copy()
                        fallback_cac['estimated_customers'] = fallback_cac['orders'] * 0.8
                        fallback_cac['estimated_cac'] = fallback_cac['total_cost'] / fallback_cac['estimated_customers']
                        zip_file.writestr("estimated_cac_analysis.csv", fallback_cac.to_csv(index=False))
                except Exception as e:
                    print(f"CAC analysis export error: {e}")
                
                # 6. Geographic Performance (if available)
                try:
                    if not geographic_distribution_df.empty:
                        geo_perf = geographic_distribution_df[['city', 'estimated_views', 'estimated_orders', 'estimated_revenue']].copy()
                        zip_file.writestr("geographic_performance.csv", geo_perf.to_csv(index=False))
                except:
                    pass
                
                # 7. Instagram Insights Summary
                try:
                    if not instagram_df.empty:
                        instagram_summary = instagram_df.groupby('influencer_id').agg({
                            'likes': 'sum',
                            'comments': 'sum',
                            'saves': 'sum',
                            'reach': 'sum',
                            'impressions': 'sum'
                        }).reset_index()
                        instagram_summary = instagram_summary.merge(influencer_df[['influencer_id', 'name']], on='influencer_id')
                        instagram_summary['engagement_rate'] = ((instagram_summary['likes'] + instagram_summary['comments'] + instagram_summary['saves']) / instagram_summary['impressions'] * 100).round(2)
                        zip_file.writestr("instagram_performance_summary.csv", instagram_summary.to_csv(index=False))
                except:
                    pass
            
            buffer.seek(0)
            
            return dcc.send_bytes(
                buffer.getvalue(),
                filename=f"healthkart_analytics_tables_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
            )
            
        except Exception as e:
            print(f"Error creating CSV export: {e}")
            return None
    
    return None

# Callback for PDF export (charts and visualizations)
@app.callback(
    Output('download-pdf', 'data'),
    Input('export-pdf-btn', 'n_clicks'),
    prevent_initial_call=True
)
def export_pdf_report(n_clicks):
    if n_clicks:
        try:
            # Generate charts as base64 images for PDF inclusion
            
            # 1. Brand Performance Chart
            try:
                brand_df = pd.read_csv('data/brand_performance.csv')
                brand_df.columns = ['Brand', 'Campaigns', 'Reach', 'Revenue', 'Cost', 'ROAS']
            except:
                posts_df_temp = pd.read_csv('data/posts.csv')
                brand_performance = posts_df_temp.groupby('brand_mentioned').agg({
                    'post_id': 'count',
                    'reach': 'sum'
                }).reset_index()
                brand_performance['revenue'] = brand_performance['reach'] * 0.05
                brand_performance['cost'] = brand_performance['post_id'] * 50000
                brand_performance['roas'] = brand_performance['revenue'] / brand_performance['cost']
                brand_performance.columns = ['Brand', 'Campaigns', 'Reach', 'Revenue', 'Cost', 'ROAS']
                brand_df = brand_performance.sort_values('Revenue', ascending=False)
            
            brand_fig = go.Figure()
            brand_fig.add_trace(go.Bar(
                x=brand_df['Brand'],
                y=brand_df['Revenue'],
                marker_color=['#3498db', '#e74c3c', '#27ae60', '#f39c12'],
                name='Revenue'
            ))
            brand_fig.update_layout(
                title='Brand Performance - Revenue by Brand',
                title_x=0.5,
                height=300,
                xaxis_title='Brand',
                yaxis_title='Revenue (₹)',
                template='plotly_white',
                font=dict(size=10)
            )
            brand_chart_base64 = base64.b64encode(brand_fig.to_image(format="png", width=600, height=300)).decode()
            
            # 2. Platform Distribution Pie Chart
            platform_stats = influencer_df.groupby('platform').agg({
                'follower_count': 'sum',
                'influencer_id': 'count'
            }).reset_index()
            
            platform_fig = go.Figure(data=[go.Pie(
                labels=platform_stats['platform'],
                values=platform_stats['follower_count'],
                hole=0.3
            )])
            platform_fig.update_layout(
                title='Follower Distribution by Platform',
                title_x=0.5,
                height=300,
                template='plotly_white',
                font=dict(size=10)
            )
            platform_chart_base64 = base64.b64encode(platform_fig.to_image(format="png", width=600, height=300)).decode()
            
            # 3. ROAS Performance Chart
            merged_df = pd.merge(payout_df, influencer_df, on='influencer_id')
            merged_df['roas'] = merged_df['total_revenue'] / merged_df['total_cost']
            top_performers = merged_df.nlargest(5, 'roas')
            
            roas_fig = go.Figure()
            roas_fig.add_trace(go.Bar(
                x=top_performers['name'],
                y=top_performers['roas'],
                marker_color='#27ae60',
                name='ROAS'
            ))
            roas_fig.update_layout(
                title='Top 5 Influencers by ROAS',
                title_x=0.5,
                height=300,
                xaxis_title='Influencer',
                yaxis_title='ROAS',
                template='plotly_white',
                font=dict(size=10),
                xaxis_tickangle=-45
            )
            roas_chart_base64 = base64.b64encode(roas_fig.to_image(format="png", width=600, height=300)).decode()
            
            # Platform summary
            platform_summary = platform_stats.copy()
            platform_summary.columns = ['Platform', 'Total Followers', 'Influencer Count']
            
            # Create HTML report with embedded charts
            html_report = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>HealthKart Influencer Campaign Dashboard Report</title>
                <style>
                    @page {{ margin: 0.8in; }}
                    body {{ font-family: Arial, sans-serif; margin: 0; color: #2c3e50; line-height: 1.4; }}
                    .header {{ text-align: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                              color: white; padding: 25px; border-radius: 10px; margin-bottom: 25px; }}
                    .kpi-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; margin: 25px 0; }}
                    .kpi-card {{ background: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center; 
                                border-left: 4px solid #3498db; }}
                    .kpi-number {{ font-size: 1.8em; font-weight: bold; color: #3498db; margin: 5px 0; }}
                    .chart-container {{ text-align: center; margin: 20px 0; page-break-inside: avoid; }}
                    .chart-image {{ max-width: 100%; height: auto; border: 1px solid #ddd; border-radius: 8px; }}
                    table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; font-size: 0.9em; }}
                    th {{ background-color: #3498db; color: white; }}
                    .section {{ margin: 25px 0; page-break-inside: avoid; }}
                    .section-title {{ font-size: 1.3em; font-weight: 600; margin-bottom: 15px; 
                                     border-bottom: 2px solid #3498db; padding-bottom: 8px; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>HealthKart Influencer Campaign Dashboard</h1>
                    <p>Analytics & Performance Report</p>
                    <p>Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
                </div>
                
                <div class="section">
                    <h2 class="section-title">📊 Key Performance Metrics</h2>
                    <div class="kpi-grid">
                        <div class="kpi-card">
                            <h3>Market Reach</h3>
                            <div class="kpi-number">{estimated_reach:,.0f}</div>
                            <p>Total Followers: {total_followers:,}</p>
                        </div>
                        <div class="kpi-card">
                            <h3>Total Orders</h3>
                            <div class="kpi-number">{total_orders:,}</div>
                            <p>Across all campaigns</p>
                        </div>
                        <div class="kpi-card">
                            <h3>Total Revenue</h3>
                            <div class="kpi-number">₹{total_revenue:,.0f}</div>
                            <p>Generated revenue</p>
                        </div>
                        <div class="kpi-card">
                            <h3>Overall ROAS</h3>
                            <div class="kpi-number">{total_roas:.2f}x</div>
                            <p>Return on ad spend</p>
                        </div>
                    </div>
                </div>
                
                <div class="section">
                    <h2 class="section-title">📈 Brand Performance Analysis</h2>
                    <div class="chart-container">
                        <img src="data:image/png;base64,{brand_chart_base64}" class="chart-image" alt="Brand Performance Chart">
                    </div>
                </div>
                
                <div class="section">
                    <h2 class="section-title">📱 Platform Distribution</h2>
                    <div class="chart-container">
                        <img src="data:image/png;base64,{platform_chart_base64}" class="chart-image" alt="Platform Distribution Chart">
                    </div>
                </div>
                
                <div class="section">
                    <h2 class="section-title">🏆 Top Performing Influencers</h2>
                    <div class="chart-container">
                        <img src="data:image/png;base64,{roas_chart_base64}" class="chart-image" alt="Top Performers ROAS Chart">
                    </div>
                    
                    <table>
                        <thead>
                            <tr>
                                <th>Influencer</th>
                                <th>Platform</th>
                                <th>Category</th>
                                <th>Orders</th>
                                <th>Revenue (₹)</th>
                                <th>ROAS</th>
                            </tr>
                        </thead>
                        <tbody>
            """
            
            # Add top performers data
            for _, row in top_performers.iterrows():
                html_report += f"""
                            <tr>
                                <td>{row['name']}</td>
                                <td>{row['platform']}</td>
                                <td>{row['category']}</td>
                                <td>{row['orders']:,}</td>
                                <td>₹{row['total_revenue']:,.0f}</td>
                                <td>{row['roas']:.2f}x</td>
                            </tr>
                """
            
            # Add platform summary table
            html_report += f"""
                        </tbody>
                    </table>
                </div>
                
                <div class="section">
                    <h2 class="section-title">📊 Platform Summary</h2>
                    <table>
                        <thead>
                            <tr>
                                <th>Platform</th>
                                <th>Influencers</th>
                                <th>Total Followers</th>
                                <th>Avg Followers</th>
                            </tr>
                        </thead>
                        <tbody>
            """
            
            for _, row in platform_summary.iterrows():
                avg_followers = row['Total Followers'] / row['Influencer Count'] if row['Influencer Count'] > 0 else 0
                html_report += f"""
                            <tr>
                                <td>{row['Platform']}</td>
                                <td>{row['Influencer Count']}</td>
                                <td>{row['Total Followers']:,}</td>
                                <td>{avg_followers:,.0f}</td>
                            </tr>
                """
            
            html_report += """
                        </tbody>
                    </table>
                </div>
                
                <div class="section" style="text-align: center; margin-top: 40px; padding: 15px; background: #f8f9fa; border-radius: 8px;">
                    <p><strong>Report generated by HealthKart Influencer Campaign Dashboard</strong></p>
                    <p>This report includes interactive charts converted to static images for PDF format.</p>
                </div>
            </body>
            </html>
            """
            
            if PDF_EXPORT_AVAILABLE:
                try:
                    # Generate PDF using weasyprint
                    pdf_buffer = io.BytesIO()
                    weasyprint.HTML(string=html_report).write_pdf(pdf_buffer)
                    pdf_buffer.seek(0)
                    
                    return dcc.send_bytes(
                        pdf_buffer.getvalue(),
                        filename=f"healthkart_dashboard_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                    )
                except Exception as pdf_error:
                    print(f"PDF generation error: {pdf_error}")
                    # Fall back to HTML
                    return dcc.send_string(
                        html_report,
                        filename=f"healthkart_dashboard_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
                    )
            else:
                # Export as HTML if PDF libraries not available
                return dcc.send_string(
                    html_report,
                    filename=f"healthkart_dashboard_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
                )
            
        except Exception as e:
            print(f"Error creating export: {e}")
            return None
    
    return None

# Sample file download callbacks
@app.callback(
    Output('download-instagram-sample-file', 'data'),
    Input('download-instagram-sample', 'n_clicks'),
    prevent_initial_call=True
)
def download_instagram_sample(n_clicks):
    if n_clicks:
        sample_data = pd.read_csv('/Users/nerve/Coding/healthkart/sample_instagram_data.csv')
        return dcc.send_data_frame(sample_data.to_csv, filename="sample_instagram_data.csv", index=False)
    return None

@app.callback(
    Output('download-youtube-sample-file', 'data'),
    Input('download-youtube-sample', 'n_clicks'),
    prevent_initial_call=True
)
def download_youtube_sample(n_clicks):
    if n_clicks:
        sample_data = pd.read_csv('/Users/nerve/Coding/healthkart/sample_youtube_data.csv')
        return dcc.send_data_frame(sample_data.to_csv, filename="sample_youtube_data.csv", index=False)
    return None


# Modal callback for help popup
@app.callback(
    Output('help-modal', 'style'),
    [Input('data-help-btn', 'n_clicks'),
     Input('modal-close-btn', 'n_clicks')],
    [State('help-modal', 'style')],
    prevent_initial_call=True
)
def toggle_help_modal(help_clicks, close_clicks, current_style):
    ctx = dash.callback_context
    if not ctx.triggered:
        return {'display': 'none'}
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id == 'data-help-btn':
        # Open modal
        return {
            'position': 'fixed',
            'top': '0',
            'left': '0',
            'width': '100%',
            'height': '100%',
            'backgroundColor': 'rgba(0,0,0,0.5)',
            'zIndex': '1000',
            'display': 'block'
        }
    elif button_id == 'modal-close-btn':
        # Close modal
        return {'display': 'none'}
    
    return {'display': 'none'}


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8050)
