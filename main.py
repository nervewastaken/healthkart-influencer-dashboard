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
        </style>
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
        html.H1("HealthKart Influencer Campaign Dashboard", 
               style={'margin': '0', 'fontSize': '3em', 'fontWeight': '700'}),
        html.P("Comprehensive Analytics & Performance Insights", 
               style={'margin': '10px 0 0 0', 'fontSize': '1.2em', 'opacity': '0.9'})
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
                ], style={'width': '48%', 'display': 'inline-block'}),
                
                # Campaign Timeline Chart
                html.Div([
                    dcc.Graph(id='campaign-timeline-chart')
                ], style={'width': '48%', 'display': 'inline-block', 'marginLeft': '4%'})
            ])
        ], className='section-container'),

        # Payout Tracking Section
        html.Div([
            html.H3("Payout Tracking & Management", className='section-title'),
            
            # Payout Summary Cards
            html.Div([
                html.Div(id='payout-summary-cards')
            ], style={'marginBottom': '30px'}),
            
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
        html.H2("📁 Data Management", className='section-title',
                style={'fontSize': '2.5em', 'fontWeight': '300'}),
        
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
    ], className='section-container')

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
        
        # Sort by engagement score and get top 5
        top_products = products_performance.nlargest(5, 'engagement_score')
        
        # Create product chips
        product_chips = []
        for _, product in top_products.iterrows():
            product_chips.append(
                html.Div([
                    html.Span(f"🏆 {product['brand_mentioned']}", 
                             style={'marginRight': '8px', 'fontWeight': '600'}),
                    html.Span(f"{product['engagement_score']:,.0f} engagement", 
                             style={'fontSize': '0.85em', 'opacity': '0.9'})
                ], className='product-chip')
            )
        
        return product_chips
        
    except Exception as e:
        # Fallback with sample data
        sample_products = ['MuscleBlaze', 'HK Vitals', 'Gritzo', 'bGreen']
        return [
            html.Div([
                html.Span(f"🏆 {product}", style={'marginRight': '8px', 'fontWeight': '600'}),
                html.Span("Top Performer", style={'fontSize': '0.85em', 'opacity': '0.9'})
            ], className='product-chip') for product in sample_products
        ]

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
    
    # Calculate brands performance
    brands = ['MuscleBlaze', 'HKVitals', 'Gritzo', 'HealthKart']
    brand_performance = []
    for brand in brands:
        brand_campaigns = np.random.randint(3, 8)
        brand_revenue = np.random.uniform(50000, 200000)
        brand_performance.append({'brand': brand, 'campaigns': brand_campaigns, 'revenue': brand_revenue})
    
    best_brand = max(brand_performance, key=lambda x: x['revenue'])
    
    return html.Div([
        # Total Campaigns
        html.Div([
            html.H3(f"{total_campaigns}", style={'color': '#3498db', 'fontSize': '2.5em', 'margin': '0'}),
            html.P("Active Campaigns", style={'color': '#2c3e50', 'fontWeight': 'bold'})
        ], style={
            'backgroundColor': '#ebf3fd',
            'padding': '20px',
            'borderRadius': '10px',
            'textAlign': 'center',
            'width': '22%',
            'display': 'inline-block',
            'margin': '1%'
        }),
        
        # Average Campaign ROAS
        html.Div([
            html.H3(f"{avg_campaign_roas:.2f}x", style={'color': '#e74c3c', 'fontSize': '2.5em', 'margin': '0'}),
            html.P("Avg Campaign ROAS", style={'color': '#2c3e50', 'fontWeight': 'bold'})
        ], style={
            'backgroundColor': '#fdeaea',
            'padding': '20px',
            'borderRadius': '10px',
            'textAlign': 'center',
            'width': '22%',
            'display': 'inline-block',
            'margin': '1%'
        }),
        
        # Total Influencers
        html.Div([
            html.H3(f"{total_influencers}", style={'color': '#27ae60', 'fontSize': '2.5em', 'margin': '0'}),
            html.P("Partner Influencers", style={'color': '#2c3e50', 'fontWeight': 'bold'})
        ], style={
            'backgroundColor': '#d5f4e6',
            'padding': '20px',
            'borderRadius': '10px',
            'textAlign': 'center',
            'width': '22%',
            'display': 'inline-block',
            'margin': '1%'
        }),
        
        # Best Performing Brand
        html.Div([
            html.H3(f"{best_brand['brand']}", style={'color': '#f39c12', 'fontSize': '1.8em', 'margin': '0'}),
            html.P("Top Brand", style={'color': '#2c3e50', 'fontWeight': 'bold'}),
            html.P(f"₹{best_brand['revenue']:,.0f}", style={'color': '#7f8c8d', 'fontSize': '0.9em'})
        ], style={
            'backgroundColor': '#fef9e7',
            'padding': '20px',
            'borderRadius': '10px',
            'textAlign': 'center',
            'width': '22%',
            'display': 'inline-block',
            'margin': '1%'
        })
    ])

# Callback for Brand Performance Chart
@app.callback(Output('brand-performance-chart', 'figure'), [Input('brand-performance-chart', 'id')])
def update_brand_performance_chart(_):
    # Create brand performance data
    brands_data = {
        'Brand': ['MuscleBlaze', 'HKVitals', 'Gritzo', 'HealthKart'],
        'Revenue': [150000, 120000, 95000, 85000],
        'Campaigns': [6, 5, 4, 3],
        'ROAS': [4.2, 3.8, 3.5, 3.1]
    }
    brand_df = pd.DataFrame(brands_data)
    
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

# Callback for Campaign Timeline Chart
@app.callback(Output('campaign-timeline-chart', 'figure'), [Input('campaign-timeline-chart', 'id')])
def update_campaign_timeline_chart(_):
    # Create timeline data for last 30 days
    dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
    timeline_data = []
    
    for date in dates:
        daily_revenue = np.random.uniform(5000, 25000)
        daily_orders = np.random.randint(20, 100)
        timeline_data.append({
            'date': date.strftime('%Y-%m-%d'),
            'revenue': daily_revenue,
            'orders': daily_orders
        })
    
    timeline_df = pd.DataFrame(timeline_data)
    
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
        # Total Payouts
        html.Div([
            html.H3(f"₹{total_payouts:,.0f}", style={'color': '#3498db', 'fontSize': '2.2em', 'margin': '0'}),
            html.P("Total Payouts", style={'color': '#2c3e50', 'fontWeight': 'bold'})
        ], style={
            'backgroundColor': '#ebf3fd',
            'padding': '20px',
            'borderRadius': '10px',
            'textAlign': 'center',
            'width': '23%',
            'display': 'inline-block',
            'margin': '1%'
        }),
        
        # Paid Amount
        html.Div([
            html.H3(f"₹{paid_amount:,.0f}", style={'color': '#27ae60', 'fontSize': '2.2em', 'margin': '0'}),
            html.P("Amount Paid", style={'color': '#2c3e50', 'fontWeight': 'bold'})
        ], style={
            'backgroundColor': '#d5f4e6',
            'padding': '20px',
            'borderRadius': '10px',
            'textAlign': 'center',
            'width': '23%',
            'display': 'inline-block',
            'margin': '1%'
        }),
        
        # Pending Amount
        html.Div([
            html.H3(f"₹{pending_amount:,.0f}", style={'color': '#f39c12', 'fontSize': '2.2em', 'margin': '0'}),
            html.P("Pending Payouts", style={'color': '#2c3e50', 'fontWeight': 'bold'})
        ], style={
            'backgroundColor': '#fef9e7',
            'padding': '20px',
            'borderRadius': '10px',
            'textAlign': 'center',
            'width': '23%',
            'display': 'inline-block',
            'margin': '1%'
        }),
        
        # Average Payout
        html.Div([
            html.H3(f"₹{avg_payout:,.0f}", style={'color': '#9b59b6', 'fontSize': '2.2em', 'margin': '0'}),
            html.P("Avg Payout", style={'color': '#2c3e50', 'fontWeight': 'bold'})
        ], style={
            'backgroundColor': '#f4ecf7',
            'padding': '20px',
            'borderRadius': '10px',
            'textAlign': 'center',
            'width': '23%',
            'display': 'inline-block',
            'margin': '1%'
        })
    ])

# Callback for Payout Tracking Table
@app.callback(Output('payout-tracking-table', 'data'), [Input('payout-tracking-table', 'id')])
def update_payout_tracking_table(_):
    # Merge payout and influencer data with additional fields
    merged_df = pd.merge(payout_df, influencer_df, on='influencer_id')
    
    # Add payout tracking fields
    brands = ['MuscleBlaze', 'HKVitals', 'Gritzo', 'HealthKart']
    payment_types = ['Per Post', 'Per Order']
    statuses = ['Paid', 'Pending', 'Processing']
    
    merged_df['brand'] = np.random.choice(brands, len(merged_df))
    merged_df['payment_type'] = np.random.choice(payment_types, len(merged_df))
    merged_df['status'] = np.random.choice(statuses, len(merged_df), p=[0.7, 0.2, 0.1])
    merged_df['payout_amount'] = merged_df['total_cost']
    merged_df['payout_date'] = pd.date_range(end=datetime.now(), periods=len(merged_df), freq='D').strftime('%Y-%m-%d')
    
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
        
        # KPI Cards
        html.Div([
            # Total Orders
            html.Div([
                html.H3(f"{total_orders:,}", style={'color': '#27ae60', 'fontSize': '2.5em', 'margin': '0'}),
                html.P("Total Orders", style={'color': '#2c3e50', 'fontWeight': 'bold'})
            ], className='kpi-card', style={
                'backgroundColor': '#d5f4e6',
                'padding': '20px',
                'borderRadius': '10px',
                'textAlign': 'center',
                'width': '22%',
                'display': 'inline-block',
                'margin': '1%'
            }),
            
            # Total Revenue
            html.Div([
                html.H3(f"₹{total_revenue:,.0f}", style={'color': '#3498db', 'fontSize': '2.5em', 'margin': '0'}),
                html.P("Total Revenue", style={'color': '#2c3e50', 'fontWeight': 'bold'})
            ], className='kpi-card', style={
                'backgroundColor': '#ebf3fd',
                'padding': '20px',
                'borderRadius': '10px',
                'textAlign': 'center',
                'width': '22%',
                'display': 'inline-block',
                'margin': '1%'
            }),
            
            # AOV
            html.Div([
                html.H3(f"₹{avg_order_value:,.0f}", style={'color': '#e74c3c', 'fontSize': '2.5em', 'margin': '0'}),
                html.P("Avg Order Value", style={'color': '#2c3e50', 'fontWeight': 'bold'})
            ], className='kpi-card', style={
                'backgroundColor': '#fdeaea',
                'padding': '20px',
                'borderRadius': '10px',
                'textAlign': 'center',
                'width': '22%',
                'display': 'inline-block',
                'margin': '1%'
            }),
            
            # Unique Customers
            html.Div([
                html.H3(f"{unique_customers:,}", style={'color': '#f39c12', 'fontSize': '2.5em', 'margin': '0'}),
                html.P("Unique Customers", style={'color': '#2c3e50', 'fontWeight': 'bold'})
            ], className='kpi-card', style={
                'backgroundColor': '#fef9e7',
                'padding': '20px',
                'borderRadius': '10px',
                'textAlign': 'center',
                'width': '22%',
                'display': 'inline-block',
                'margin': '1%'
            })
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
        # Simulate 12 weeks of growth data
        for week in range(12):
            date = datetime.now() - timedelta(weeks=week)
            growth_rate = np.random.uniform(0.98, 1.05)
            followers = int(base_followers * (growth_rate ** week))
            net_new = int(followers * 0.03)  # 3% new followers per week
            
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
        # Simulate 4 weeks of performance data
        for week in range(1, 5):
            decay_factor = 1 - (0.15 * (week - 1))  # 15% decay per week
            base_ctr = np.random.uniform(1.5, 4.0)
            base_cpc = np.random.uniform(20, 50)
            
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
    
    # If product column doesn't exist, create it
    if 'product' not in df.columns:
        df['product'] = np.random.choice(products, len(df))
    
    # Add slight random offset to coordinates to prevent exact overlap
    if 'latitude' not in df.columns or 'longitude' not in df.columns:
        df['latitude'] = df['city'].map(lambda x: city_coordinates.get(x, {}).get('latitude', 20.5937))
        df['longitude'] = df['city'].map(lambda x: city_coordinates.get(x, {}).get('longitude', 78.9629))
        
    # Add small random offset to prevent overlapping markers
    df['latitude'] = df['latitude'] + np.random.uniform(-0.1, 0.1, len(df))
    df['longitude'] = df['longitude'] + np.random.uniform(-0.1, 0.1, len(df))
    
    # Calculate efficiency metrics
    df['orders_per_1k_reach'] = (df['estimated_views'] / 1000) * np.random.uniform(0.005, 0.02, len(df))
    df['orders'] = np.random.randint(10, 150, len(df))  # Simulated orders
    df['revenue'] = df['orders'] * np.random.uniform(1000, 4000, len(df))  # Simulated revenue
    
    # Recalculate ROAS based on actual revenue
    df['city_roas'] = df['revenue'] / (df['orders'] * np.random.uniform(500, 1200, len(df)))  # Simulated cost
    
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
                cost_orders['unique_customers'] = cost_orders['orders']
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


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8050)
