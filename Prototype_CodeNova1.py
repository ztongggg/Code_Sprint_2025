import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import json
import urllib.request
import os
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
from urllib.parse import quote

# =============================================================================
# CONFIGURATION
# =============================================================================
AZURE_OPENAI_KEY = "555cd3b2c585440bbc01237fd7965e0c"
AZURE_OPENAI_ENDPOINT = "https://psacodesprint2025.azure-api.net/gpt-4-1-mini"
DEPLOYMENT_NAME = "gpt-4.1-mini"
API_VERSION = "2025-01-01-preview"

POWERBI_EMBED_URL = "https://powerbiembeddedexample-gsffd0h3fxe2hmgm.southeastasia-01.azurewebsites.net"
POWERBI_ACCESS_TOKEN = ""  

# =============================================================================
# PAGE SETUP
# =============================================================================
st.set_page_config(
    page_title="PSA Network Insights AI",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# CUSTOM CSS - DARK FUTURISTIC THEME
# =============================================================================
st.markdown("""
<style>
    /* Global Dark Theme */
    .stApp {
        background: #0B132B;
        color: #E0E0E0;
    }
    
    .main-header {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #00A8E8, #5BC0EB);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .subtitle {
        color: #A0AEC0;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    /* Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, #1C2541 0%, #3A506B 100%);
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.3);
        margin: 0.5rem 0;
        transition: all 0.3s ease;
        border-left: 5px solid #00A8E8;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 24px rgba(0,168,232,0.3);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #00A8E8;
        margin: 0.5rem 0;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #A0AEC0;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
    }
    
    /* Comparison Cards */
    .comparison-card {
        background: #1C2541;
        padding: 1.2rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        margin: 1rem 0;
        border: 1px solid #3A506B;
    }
    
    /* Alert Banner */
    .alert-critical {
        background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%);
        padding: 1.2rem;
        border-radius: 12px;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(239, 68, 68, 0.5);
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.85; }
    }
    
    /* Action Cards */
    .action-card {
        background: #1C2541;
        border-left: 5px solid #38BDF8;
        padding: 1.5rem;
        margin: 1rem 0;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        color: #E0E0E0;
    }
    
    .priority-high {
        border-left-color: #EF4444;
        background: linear-gradient(to right, rgba(239, 68, 68, 0.1), #1C2541);
    }
    
    .priority-medium {
        border-left-color: #FACC15;
        background: linear-gradient(to right, rgba(250, 204, 21, 0.1), #1C2541);
    }
    
    /* Chat Messages */
    .chat-user {
        background: linear-gradient(135deg, #00A8E8 0%, #007EA7 100%);
        color: white;
        padding: 1.2rem;
        border-radius: 15px 15px 5px 15px;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(0, 168, 232, 0.4);
    }
    
    .chat-assistant {
        background: #1C2541;
        padding: 1.5rem;
        border-radius: 15px 15px 15px 5px;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        border-left: 4px solid #00A8E8;
        color: #E0E0E0;
    }
    
    /* Section Divider */
    .section-divider {
        height: 1px;
        background: linear-gradient(to right, transparent, #3A506B, transparent);
        margin: 2rem 0;
    }
    
    /* Filter Indicator - NEW */
    .filter-indicator {
        background: linear-gradient(135deg, #00A8E8, #007EA7);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        font-weight: 600;
        font-size: 0.85rem;
    }
    
    /* Role Badge - NEW */
    .role-badge {
        background: linear-gradient(135deg, #A855F7, #9333EA);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        display: inline-block;
        margin: 0.5rem 0;
        font-weight: 600;
        font-size: 0.9rem;
    }
    
    /* Red button for Get PEEL Analysis */
    [data-testid="stButton"] button[kind="secondary"] {
        background: linear-gradient(135deg, #EF4444, #DC2626) !important;
        color: white !important;
        box-shadow: 0 4px 12px rgba(239, 68, 68, 0.4) !important;
    }
            
    /* Button Variations */
    .btn-primary {
        background: linear-gradient(135deg, #A855F7, #9333EA) !important;
        color: white !important;
        box-shadow: 0 4px 12px rgba(168, 85, 247, 0.4) !important;
    }
    
    .btn-secondary {
        background: linear-gradient(135deg, #00A8E8, #007EA7) !important;
        color: white !important;
        box-shadow: 0 4px 8px rgba(0,168,232,0.3) !important;
    }
    
    .btn-tertiary {
        background: linear-gradient(135deg, #3A506B, #1C2541) !important;
        color: #E0E0E0 !important;
        border: 1px solid #5BC0EB !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #1C2541;
        padding: 0.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #0B132B;
        color: #A0AEC0;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #00A8E8, #007EA7);
        color: white;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1C2541 0%, #0B132B 100%);
    }
    
    [data-testid="stSidebar"] * {
        color: #E0E0E0 !important;
    }
    
    /* Sustainability Theme */
    .sustainability-card {
        background: linear-gradient(135deg, rgba(34, 197, 94, 0.2) 0%, #1C2541 100%);
        border-left: 5px solid #22C55E;
    }
    
    /* Input fields */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background-color: #1C2541;
        color: #E0E0E0;
        border: 1px solid #3A506B;
    }
    
    .stSelectbox>div>div {
        background-color: #1C2541;
        color: #E0E0E0;
    }
    
    /* Sliders */
    .stSlider>div>div>div {
        background-color: #3A506B;
    }
        
</style>
""", unsafe_allow_html=True)

# =============================================================================
# DATA LOADING
# =============================================================================
@st.cache_data
def load_data():
    """Load and preprocess vessel operations data"""
    folder = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(folder, "data.csv")
    
    if not os.path.exists(path):
        st.error(f"CSV file not found at: {path}")
        return pd.DataFrame()
    
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
    
    # Parse datetime columns
    time_cols = ['final_btr_(local_time)', 'abt_(local_time)', 'atb_(local_time)', 'atu_(local_time)']
    for col in time_cols:
        if col in df.columns:
            try:
                df[col] = pd.to_datetime(df[col], errors='coerce')
            except:
                pass
    
    # Convert Y/N to numeric
    yn_columns = ['arrival_accuracy_(final_btr)', 'assured_port_time_achieved_(%)']
    for col in yn_columns:
        if col in df.columns and df[col].dtype == 'object':
            if df[col].astype(str).str.upper().isin(['Y', 'N', 'YES', 'NO']).any():
                df[col] = df[col].astype(str).str.upper().map({'Y': 1, 'YES': 1, 'N': 0, 'NO': 0})
    
    # Convert numeric columns
    numeric_cols = ['wait_time_(hours):_atb-btr', 'wait_time_(hours):_abt-btr', 
                    'wait_time_(hours):_atb-abt', 'berth_time_(hours):_atu_-_atb',
                    'arrival_variance_(within_4h_target)', 'bunker_saved_(usd)', 
                    'carbon_abatement_(tonnes)']
    
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    return df

df_original = load_data()

# =============================================================================
# SESSION STATE INITIALIZATION
# =============================================================================
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'action_plan' not in st.session_state:
    st.session_state.action_plan = None
if 'system_start_time' not in st.session_state:
    st.session_state.system_start_time = datetime.now()
if 'scenario_calculated' not in st.session_state:
    st.session_state.scenario_calculated = False
if 'dashboard_context' not in st.session_state:
    st.session_state.dashboard_context = {}
if 'active_filters' not in st.session_state:
    st.session_state.active_filters = {}
if 'user_role' not in st.session_state:
    st.session_state.user_role = "Operations Manager"

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================
def get_performance_color(value, metric_type):
    """Return color based on performance"""
    if metric_type == 'arrival_accuracy':
        if value >= 95: return '#22C55E'
        elif value >= 90: return '#00A8E8'
        elif value >= 85: return '#FACC15'
        else: return '#EF4444'
    elif metric_type == 'wait_time':
        if value <= 2: return '#22C55E'
        elif value <= 4: return '#00A8E8'
        elif value <= 6: return '#FACC15'
        else: return '#EF4444'
    return '#6B7280'

def get_performance_label(value, metric_type):
    """Return performance label"""
    if metric_type == 'arrival_accuracy':
        if value >= 95: return 'Excellent'
        elif value >= 90: return 'Good'
        elif value >= 85: return 'Warning'
        else: return 'Critical'
    elif metric_type == 'wait_time':
        if value <= 2: return 'Excellent'
        elif value <= 4: return 'Good'
        elif value <= 6: return 'Warning'
        else: return 'Critical'
    return 'Unknown'
# =============================================================================
# ROLE-SPECIFIC CUSTOMIZATION
# =============================================================================
def get_role_specific_metrics(role, df):
    """Return role-specific metrics to display"""
    metrics = {}
    
    if role == "Executive (C-Suite)":
        metrics['title'] = "Executive KPIs"
        metrics['focus'] = [
            ('Network Efficiency', f"{df['arrival_accuracy_(final_btr)'].mean() * 100:.1f}%" if 'arrival_accuracy_(final_btr)' in df.columns else "N/A"),
            ('Cost Savings', f"${df['bunker_saved_(usd)'].sum()/1000000:.1f}M" if 'bunker_saved_(usd)' in df.columns else "N/A"),
            ('Carbon Impact', f"{df['carbon_abatement_(tonnes)'].sum():.0f}t CO₂" if 'carbon_abatement_(tonnes)' in df.columns else "N/A"),
            ('Operators Active', f"{df['operator'].nunique()}" if 'operator' in df.columns else "N/A")
        ]
    elif role == "Operations Manager":
        metrics['title'] = "Operational Metrics"
        metrics['focus'] = [
            ('Avg Wait Time', f"{df['wait_time_(hours):_atb-btr'].mean():.1f}h" if 'wait_time_(hours):_atb-btr' in df.columns else "N/A"),
            ('Critical Delays', f"{len(df[df['wait_time_(hours):_atb-btr'] > 6])}" if 'wait_time_(hours):_atb-btr' in df.columns else "N/A"),
            ('On-Time Rate', f"{df['arrival_accuracy_(final_btr)'].mean() * 100:.1f}%" if 'arrival_accuracy_(final_btr)' in df.columns else "N/A"),
            ('Vessels Today', f"{len(df)}")
        ]
    elif role == "Terminal Manager":
        metrics['title'] = "Terminal Performance"
        metrics['focus'] = [
            ('My Vessels', f"{len(df)}"),
            ('Berth Utilization', f"{df['berth_time_(hours):_atu_-_atb'].mean():.1f}h" if 'berth_time_(hours):_atu_-_atb' in df.columns else "N/A"),
            ('Wait Time', f"{df['wait_time_(hours):_atb-btr'].mean():.1f}h" if 'wait_time_(hours):_atb-btr' in df.columns else "N/A"),
            ('Active Berths', f"{df['berth'].nunique()}" if 'berth' in df.columns else "N/A")
        ]
    elif role == "Data Analyst":
        metrics['title'] = "Statistical Overview"
        metrics['focus'] = [
            ('Data Points', f"{len(df):,}"),
            ('Std Dev (Wait)', f"{df['wait_time_(hours):_atb-btr'].std():.2f}h" if 'wait_time_(hours):_atb-btr' in df.columns else "N/A"),
            ('Outliers (>2σ)', f"{len(df[df['wait_time_(hours):_atb-btr'] > df['wait_time_(hours):_atb-btr'].mean() + 2*df['wait_time_(hours):_atb-btr'].std()])}" if 'wait_time_(hours):_atb-btr' in df.columns else "N/A"),
            ('Completeness', f"{(1 - df.isna().sum().sum() / (len(df) * len(df.columns))) * 100:.1f}%")
        ]
    elif role == "Sustainability Officer":
        metrics['title'] = "Environmental Impact"
        metrics['focus'] = [
            ('Total Carbon Saved', f"{df['carbon_abatement_(tonnes)'].sum():.0f}t" if 'carbon_abatement_(tonnes)' in df.columns else "N/A"),
            ('Avg per Vessel', f"{df['carbon_abatement_(tonnes)'].mean():.1f}t" if 'carbon_abatement_(tonnes)' in df.columns else "N/A"),
            ('Fuel Savings', f"${df['bunker_saved_(usd)'].sum()/1000:.0f}K" if 'bunker_saved_(usd)' in df.columns else "N/A"),
            ('Green Score', f"{(df['carbon_abatement_(tonnes)'].sum() / len(df)):.1f}t/vessel" if 'carbon_abatement_(tonnes)' in df.columns else "N/A")
        ]
    
    return metrics

def get_role_specific_ai_instruction(role):
    """Return detailed AI instructions for each role"""
    instructions = {
        "Executive (C-Suite)": """
**Role Context:** You are advising C-Level executives who need:
- High-level strategic insights (not operational details)
- ROI and financial impact quantification
- Board-ready recommendations
- Risk assessments and mitigation strategies
- Competitive positioning insights

**Response Style:**
- Start with bottom-line impact (revenue, cost, risk)
- Use business language (avoid technical jargon)
- Provide executive summary format
- Include 3-5 year strategic outlook
- Quantify everything in financial terms
""",
        "Operations Manager": """
**Role Context:** You are advising Operations Managers who need:
- Actionable operational improvements
- Root cause analysis of delays/issues
- Resource allocation recommendations
- Process optimization strategies
- Team-level action items

**Response Style:**
- Focus on immediate fixes (24-48h actions)
- Identify bottlenecks and blockers
- Provide step-by-step operational guidance
- Include crew/equipment implications
- Prioritize quick wins vs. long-term projects
""",
        "Terminal Manager": """
**Role Context:** You are advising Terminal Managers who need:
- Terminal-specific performance benchmarks
- Comparison to network average
- Crew scheduling insights
- Equipment utilization analysis
- Vessel-level troubleshooting

**Response Style:**
- Compare their terminal to others
- Focus on controllable factors
- Provide shift-level recommendations
- Include berth-specific insights
- Highlight crew performance opportunities
""",
        "Data Analyst": """
**Role Context:** You are advising Data Analysts who need:
- Statistical analysis and correlations
- Trend identification and forecasting
- Data quality insights
- Pattern recognition
- Predictive modeling recommendations

**Response Style:**
- Use statistical terminology
- Provide correlation coefficients
- Show data distributions
- Identify anomalies and outliers
- Suggest further analysis methods
""",
        "Sustainability Officer": """
**Role Context:** You are advising Sustainability Officers who need:
- Carbon footprint analysis
- Environmental impact quantification
- Green initiative recommendations
- ESG reporting metrics
- Sustainability benchmark comparisons

**Response Style:**
- Emphasize environmental benefits
- Convert to CO₂ equivalents
- Compare to industry standards
- Link to sustainability goals (Net Zero, etc.)
- Provide ESG report-ready metrics
"""
    }
    
    return instructions.get(role, instructions["Operations Manager"])

# Update the create_dashboard_aware_prompt function
def create_dashboard_aware_prompt(user_query, filtered_df, dashboard_context):
    """Create prompt with dashboard context awareness and role customization"""
    
    role = dashboard_context.get('user_role', 'Operations Manager')
    role_instruction = get_role_specific_ai_instruction(role)
    
    # Build context string
    context_parts = [
        f"**Current Dashboard View (User: {role}):**",
        f"- Viewing: {dashboard_context.get('total_vessels', 0)} vessels"
    ]
    
    # Show active filters
    active_filters = dashboard_context.get('filters_applied', {})
    if active_filters:
        filter_desc = []
        for key, value in active_filters.items():
            if value:
                if isinstance(value, list):
                    filter_desc.append(f"{key}: {', '.join(map(str, value[:3]))}")
                else:
                    filter_desc.append(f"{key}: {value}")
        if filter_desc:
            context_parts.append(f"- **Active Filters:** {'; '.join(filter_desc)}")
    
    # Add visible metrics
    if 'avg_accuracy' in dashboard_context:
        context_parts.append(f"- On-Time Rate: {dashboard_context['avg_accuracy']:.1f}% ({dashboard_context.get('on_time_vessels', 0)} vessels)")
    
    if 'avg_wait_time' in dashboard_context:
        context_parts.append(f"- Average Wait Time: {dashboard_context['avg_wait_time']:.1f} hours")
    
    if 'total_carbon' in dashboard_context:
        context_parts.append(f"- Carbon Saved: {dashboard_context['total_carbon']:.0f} tonnes")
    
    if 'total_bunker' in dashboard_context:
        context_parts.append(f"- Cost Saved: ${dashboard_context['total_bunker']:,.0f}")
    
    context_str = "\n".join(context_parts)
    
    prompt = f"""You are analyzing PSA's operational dashboard for a {role}.

{context_str}

{role_instruction}

**CRITICAL:** Your analysis must be based ONLY on the filtered data currently visible in the dashboard.

**User Question:** {user_query}

Provide analysis using PEEL structure tailored for {role}:

### 🎯 POINT (Main Finding for {role})
[Clear answer based on CURRENT filtered view, framed for this role's priorities]

### 📊 EVIDENCE (From Current Dashboard View)
[Use the metrics shown above - acknowledge filters if active]
[Present data in format most relevant to {role}]

### 💡 EXPLAIN (Analysis & Context)
[Explain what the current filtered view shows]
**Important Context:**
- Note if filters are limiting the view
- Mention if broader analysis would differ

### 🎯 LINK (Recommendations for {role})
[Provide role-appropriate actions based on their responsibilities and decision-making authority]
**Immediate Actions:**
- [Specific to user role and their authority level]

**Expected Impact:**
- [Quantified benefits in terms relevant to this role]

Be specific about what's currently visible vs. total dataset."""
    
    return prompt
    """Apply active filters to dataframe"""
    filtered = df.copy()
    
    if filters.get('operators'):
        filtered = filtered[filtered['operator'].isin(filters['operators'])]
    
    if filters.get('business_units'):
        filtered = filtered[filtered['bu'].isin(filters['business_units'])]
    
    if filters.get('wait_time_range'):
        min_wait, max_wait = filters['wait_time_range']
        if 'wait_time_(hours):_atb-btr' in filtered.columns:
            filtered = filtered[
                (filtered['wait_time_(hours):_atb-btr'] >= min_wait) &
                (filtered['wait_time_(hours):_atb-btr'] <= max_wait)
            ]
    
    if filters.get('port_time_range'):
        min_port, max_port = filters['port_time_range']
        if 'assured_port_time_achieved_(%)' in filtered.columns:
            filtered = filtered[
                (filtered['assured_port_time_achieved_(%)'] >= min_port) &
                (filtered['assured_port_time_achieved_(%)'] <= max_port)
            ]
    
    if filters.get('bunker_range'):
        min_bunker, max_bunker = filters['bunker_range']
        if 'bunker_saved_(usd)' in filtered.columns:
            filtered = filtered[
                (filtered['bunker_saved_(usd)'] >= min_bunker) &
                (filtered['bunker_saved_(usd)'] <= max_bunker)
            ]
    
    if filters.get('carbon_range'):
        min_carbon, max_carbon = filters['carbon_range']
        if 'carbon_abatement_(tonnes)' in filtered.columns:
            filtered = filtered[
                (filtered['carbon_abatement_(tonnes)'] >= min_carbon) &
                (filtered['carbon_abatement_(tonnes)'] <= max_carbon)
            ]
    
    if filters.get('quick_filter'):
        qf = filters['quick_filter']
        if qf == "Critical Issues Only" and 'wait_time_(hours):_atb-btr' in filtered.columns:
            filtered = filtered[filtered['wait_time_(hours):_atb-btr'] > 6]
        elif qf == "Delays > 4 hours" and 'wait_time_(hours):_atb-btr' in filtered.columns:
            filtered = filtered[filtered['wait_time_(hours):_atb-btr'] > 4]
        elif qf == "Delays > 6 hours" and 'wait_time_(hours):_atb-btr' in filtered.columns:
            filtered = filtered[filtered['wait_time_(hours):_atb-btr'] > 6]
        elif qf == "High Performers Only" and 'arrival_accuracy_(final_btr)' in filtered.columns:
            filtered = filtered[filtered['arrival_accuracy_(final_btr)'] == 1]
        elif qf == "Low Carbon Performance" and 'carbon_abatement_(tonnes)' in filtered.columns:
            threshold = df['carbon_abatement_(tonnes)'].quantile(0.25)
            filtered = filtered[filtered['carbon_abatement_(tonnes)'] < threshold]
        elif qf == "Below Target Accuracy" and 'arrival_accuracy_(final_btr)' in filtered.columns:
            filtered = filtered[filtered['arrival_accuracy_(final_btr)'] == 0]
    
    return filtered

def capture_dashboard_state(filtered_df):
    """Capture current dashboard state for AI context"""
    context = {
        'total_vessels': len(filtered_df),
        'filters_applied': st.session_state.active_filters.copy(),
        'user_role': st.session_state.user_role,
        'timestamp': datetime.now().isoformat()
    }
    
    if not filtered_df.empty:
        if 'arrival_accuracy_(final_btr)' in filtered_df.columns:
            context['avg_accuracy'] = float(filtered_df['arrival_accuracy_(final_btr)'].mean() * 100)
            context['on_time_vessels'] = int(filtered_df['arrival_accuracy_(final_btr)'].sum())
        
        if 'wait_time_(hours):_atb-btr' in filtered_df.columns:
            context['avg_wait_time'] = float(filtered_df['wait_time_(hours):_atb-btr'].mean())
            context['max_wait_time'] = float(filtered_df['wait_time_(hours):_atb-btr'].max())
        
        if 'carbon_abatement_(tonnes)' in filtered_df.columns:
            context['total_carbon'] = float(filtered_df['carbon_abatement_(tonnes)'].sum())
        
        if 'bunker_saved_(usd)' in filtered_df.columns:
            context['total_bunker'] = float(filtered_df['bunker_saved_(usd)'].sum())
        
        if 'operator' in filtered_df.columns:
            context['visible_operators'] = filtered_df['operator'].unique().tolist()[:5]
        
        if 'bu' in filtered_df.columns:
            context['visible_regions'] = filtered_df['bu'].unique().tolist()[:5]
    
    st.session_state.dashboard_context = context
    return context

def build_powerbi_url_with_filters(base_url, filters):
    """Build Power BI URL with filter parameters"""
    if not base_url or base_url == "https://app.powerbi.com/reportEmbed?reportId=xxx&groupId=xxx&config=xxx":
        return base_url
    
    filter_parts = []
    
    if filters.get('operators'):
        operators_filter = " or ".join([f"Operator eq '{op}'" for op in filters['operators']])
        filter_parts.append(f"({operators_filter})")
    
    if filters.get('business_units'):
        bu_filter = " or ".join([f"BU eq '{bu}'" for bu in filters['business_units']])
        filter_parts.append(f"({bu_filter})")
    
    if filter_parts:
        filter_string = " and ".join(filter_parts)
        encoded_filter = quote(f"$filter={filter_string}")
        return f"{base_url}&{encoded_filter}"
    
    return base_url

# =============================================================================
# NEW - DASHBOARD AWARENESS FUNCTIONS
# =============================================================================
def apply_filters_to_dataframe(df, filters):
    """Apply active filters to dataframe"""
    filtered = df.copy()
    
    if filters.get('operators'):
        filtered = filtered[filtered['operator'].isin(filters['operators'])]
    
    if filters.get('business_units'):
        filtered = filtered[filtered['bu'].isin(filters['business_units'])]
    
    if filters.get('wait_time_range'):
        min_wait, max_wait = filters['wait_time_range']
        if 'wait_time_(hours):_atb-btr' in filtered.columns:
            filtered = filtered[
                (filtered['wait_time_(hours):_atb-btr'] >= min_wait) &
                (filtered['wait_time_(hours):_atb-btr'] <= max_wait)
            ]
    
    if filters.get('port_time_range'):
        min_port, max_port = filters['port_time_range']
        if 'assured_port_time_achieved_(%)' in filtered.columns:
            filtered = filtered[
                (filtered['assured_port_time_achieved_(%)'] >= min_port) &
                (filtered['assured_port_time_achieved_(%)'] <= max_port)
            ]
    
    if filters.get('bunker_range'):
        min_bunker, max_bunker = filters['bunker_range']
        if 'bunker_saved_(usd)' in filtered.columns:
            filtered = filtered[
                (filtered['bunker_saved_(usd)'] >= min_bunker) &
                (filtered['bunker_saved_(usd)'] <= max_bunker)
            ]
    
    if filters.get('carbon_range'):
        min_carbon, max_carbon = filters['carbon_range']
        if 'carbon_abatement_(tonnes)' in filtered.columns:
            filtered = filtered[
                (filtered['carbon_abatement_(tonnes)'] >= min_carbon) &
                (filtered['carbon_abatement_(tonnes)'] <= max_carbon)
            ]
    
    if filters.get('quick_filter'):
        qf = filters['quick_filter']
        if qf == "Critical Issues Only" and 'wait_time_(hours):_atb-btr' in filtered.columns:
            filtered = filtered[filtered['wait_time_(hours):_atb-btr'] > 6]
        elif qf == "Delays > 4 hours" and 'wait_time_(hours):_atb-btr' in filtered.columns:
            filtered = filtered[filtered['wait_time_(hours):_atb-btr'] > 4]
        elif qf == "Delays > 6 hours" and 'wait_time_(hours):_atb-btr' in filtered.columns:
            filtered = filtered[filtered['wait_time_(hours):_atb-btr'] > 6]
        elif qf == "High Performers Only" and 'arrival_accuracy_(final_btr)' in filtered.columns:
            filtered = filtered[filtered['arrival_accuracy_(final_btr)'] == 1]
        elif qf == "Low Carbon Performance" and 'carbon_abatement_(tonnes)' in filtered.columns:
            threshold = df['carbon_abatement_(tonnes)'].quantile(0.25)
            filtered = filtered[filtered['carbon_abatement_(tonnes)'] < threshold]
        elif qf == "Below Target Accuracy" and 'arrival_accuracy_(final_btr)' in filtered.columns:
            filtered = filtered[filtered['arrival_accuracy_(final_btr)'] == 0]
    
    return filtered

def capture_dashboard_state(filtered_df):
    """Capture current dashboard state for AI context"""
    context = {
        'total_vessels': len(filtered_df),
        'filters_applied': st.session_state.active_filters.copy(),
        'user_role': st.session_state.user_role,
        'timestamp': datetime.now().isoformat()
    }
    
    if not filtered_df.empty:
        if 'arrival_accuracy_(final_btr)' in filtered_df.columns:
            context['avg_accuracy'] = float(filtered_df['arrival_accuracy_(final_btr)'].mean() * 100)
            context['on_time_vessels'] = int(filtered_df['arrival_accuracy_(final_btr)'].sum())
        
        if 'wait_time_(hours):_atb-btr' in filtered_df.columns:
            context['avg_wait_time'] = float(filtered_df['wait_time_(hours):_atb-btr'].mean())
            context['max_wait_time'] = float(filtered_df['wait_time_(hours):_atb-btr'].max())
        
        if 'carbon_abatement_(tonnes)' in filtered_df.columns:
            context['total_carbon'] = float(filtered_df['carbon_abatement_(tonnes)'].sum())
        
        if 'bunker_saved_(usd)' in filtered_df.columns:
            context['total_bunker'] = float(filtered_df['bunker_saved_(usd)'].sum())
        
        if 'operator' in filtered_df.columns:
            context['visible_operators'] = filtered_df['operator'].unique().tolist()[:5]
        
        if 'bu' in filtered_df.columns:
            context['visible_regions'] = filtered_df['bu'].unique().tolist()[:5]
    
    st.session_state.dashboard_context = context
    return context

def build_powerbi_url_with_filters(base_url, filters):
    """Build Power BI URL with filter parameters"""
    if not base_url or base_url == "https://app.powerbi.com/reportEmbed?reportId=xxx&groupId=xxx&config=xxx":
        return base_url
    
    filter_parts = []
    
    if filters.get('operators'):
        operators_filter = " or ".join([f"Operator eq '{op}'" for op in filters['operators']])
        filter_parts.append(f"({operators_filter})")
    
    if filters.get('business_units'):
        bu_filter = " or ".join([f"BU eq '{bu}'" for bu in filters['business_units']])
        filter_parts.append(f"({bu_filter})")
    
    if filter_parts:
        filter_string = " and ".join(filter_parts)
        encoded_filter = quote(f"$filter={filter_string}")
        return f"{base_url}&{encoded_filter}"
    
    return base_url

# =============================================================================
# ANALYTICS FUNCTIONS
# =============================================================================
def analyze_psa_data(df):
    """Comprehensive data analysis"""
    if df.empty:
        return None
    
    analysis = {
        'summary': {},
        'performance': {},
        'delays': {},
        'sustainability': {},
        'comparisons': {}
    }
    
    # Summary metrics
    analysis['summary'] = {
        'total_vessels': len(df),
        'total_operators': df['operator'].nunique() if 'operator' in df.columns else 0,
        'total_berths': df['berth'].nunique() if 'berth' in df.columns else 0,
        'total_countries': df['bu'].nunique() if 'bu' in df.columns else 0,
    }
    
    # Performance analysis
    if 'arrival_accuracy_(final_btr)' in df.columns and pd.api.types.is_numeric_dtype(df['arrival_accuracy_(final_btr)']):
        accuracy_pct = df['arrival_accuracy_(final_btr)'].mean() * 100
        analysis['performance']['avg_arrival_accuracy'] = accuracy_pct
        analysis['performance']['on_time_vessels'] = int(df['arrival_accuracy_(final_btr)'].sum())
        analysis['performance']['delayed_vessels'] = len(df) - int(df['arrival_accuracy_(final_btr)'].sum())
        analysis['performance']['accuracy_color'] = get_performance_color(accuracy_pct, 'arrival_accuracy')
        analysis['performance']['accuracy_label'] = get_performance_label(accuracy_pct, 'arrival_accuracy')
    
    # Delay analysis
    if 'wait_time_(hours):_atb-btr' in df.columns and pd.api.types.is_numeric_dtype(df['wait_time_(hours):_atb-btr']):
        avg_wait = df['wait_time_(hours):_atb-btr'].mean()
        analysis['delays']['avg_wait_time'] = avg_wait
        analysis['delays']['max_wait_time'] = df['wait_time_(hours):_atb-btr'].max()
        analysis['delays']['vessels_with_delays'] = len(df[df['wait_time_(hours):_atb-btr'] > 0])
        analysis['delays']['wait_color'] = get_performance_color(avg_wait, 'wait_time')
        analysis['delays']['wait_label'] = get_performance_label(avg_wait, 'wait_time')
    
    # Sustainability metrics
    if 'carbon_abatement_(tonnes)' in df.columns and pd.api.types.is_numeric_dtype(df['carbon_abatement_(tonnes)']):
        analysis['sustainability']['total_carbon_saved'] = df['carbon_abatement_(tonnes)'].sum()
        analysis['sustainability']['avg_per_vessel'] = df['carbon_abatement_(tonnes)'].mean()
    
    if 'bunker_saved_(usd)' in df.columns and pd.api.types.is_numeric_dtype(df['bunker_saved_(usd)']):
        analysis['sustainability']['total_bunker_saved'] = df['bunker_saved_(usd)'].sum()
        analysis['sustainability']['avg_per_vessel'] = df['bunker_saved_(usd)'].mean()
    
    # Operator comparisons
    if 'operator' in df.columns:
        operator_stats = []
        for op in df['operator'].unique():
            op_df = df[df['operator'] == op]
            op_stats = {'operator': op, 'vessels': len(op_df)}
            
            if 'arrival_accuracy_(final_btr)' in op_df.columns and pd.api.types.is_numeric_dtype(op_df['arrival_accuracy_(final_btr)']):
                op_stats['accuracy'] = op_df['arrival_accuracy_(final_btr)'].mean() * 100
            
            if 'wait_time_(hours):_atb-btr' in op_df.columns:
                op_stats['wait_time'] = op_df['wait_time_(hours):_atb-btr'].mean()
            
            if 'carbon_abatement_(tonnes)' in op_df.columns:
                op_stats['carbon'] = op_df['carbon_abatement_(tonnes)'].sum()
            
            operator_stats.append(op_stats)
        
        analysis['comparisons']['operators'] = operator_stats
    
    return analysis

# =============================================================================
# AI FUNCTIONS WITH DASHBOARD AWARENESS
# =============================================================================
def create_dashboard_aware_prompt(user_query, filtered_df, dashboard_context):
    """Create prompt with dashboard context awareness"""
    
    # Build context string
    context_parts = [
        f"**Current Dashboard View (User Role: {dashboard_context.get('user_role', 'User')}):**",
        f"- Viewing: {dashboard_context.get('total_vessels', 0)} vessels"
    ]
    
    # Show active filters
    active_filters = dashboard_context.get('filters_applied', {})
    if active_filters:
        filter_desc = []
        for key, value in active_filters.items():
            if value:
                if isinstance(value, list):
                    filter_desc.append(f"{key}: {', '.join(map(str, value[:3]))}")
                else:
                    filter_desc.append(f"{key}: {value}")
        if filter_desc:
            context_parts.append(f"- **Active Filters:** {'; '.join(filter_desc)}")
    
    # Add visible metrics
    if 'avg_accuracy' in dashboard_context:
        context_parts.append(f"- On-Time Rate: {dashboard_context['avg_accuracy']:.1f}% ({dashboard_context.get('on_time_vessels', 0)} vessels)")
    
    if 'avg_wait_time' in dashboard_context:
        context_parts.append(f"- Average Wait Time: {dashboard_context['avg_wait_time']:.1f} hours")
    
    if 'total_carbon' in dashboard_context:
        context_parts.append(f"- Carbon Saved: {dashboard_context['total_carbon']:.0f} tonnes")
    
    if 'total_bunker' in dashboard_context:
        context_parts.append(f"- Cost Saved: ${dashboard_context['total_bunker']:,.0f}")
    
    context_str = "\n".join(context_parts)
    
    # Role-specific guidance
    role_guidance = {
        "Executive (C-Suite)": "Focus on strategic impact, ROI, and high-level priorities.",
        "Operations Manager": "Focus on operational efficiency, bottlenecks, and actionable improvements.",
        "Terminal Manager": "Focus on terminal-specific performance and crew/equipment optimization.",
        "Data Analyst": "Focus on patterns, correlations, and statistical insights.",
        "Sustainability Officer": "Focus on environmental impact and green initiatives."
    }
    
    role_context = role_guidance.get(dashboard_context.get('user_role', ''), "")
    
    prompt = f"""You are analyzing PSA's operational dashboard for a {dashboard_context.get('user_role', 'user')}.

{context_str}

**Role Context:** {role_context}

**CRITICAL:** Your analysis must be based ONLY on the filtered data currently visible in the dashboard.

**User Question:** {user_query}

Provide analysis using PEEL structure:

### 🎯 POINT (Main Finding)
[Clear answer based on CURRENT filtered view]

### 📊 EVIDENCE (From Current Dashboard View)
[Use the metrics shown above - acknowledge filters if active]
- Create comparison tables where relevant

### 💡 EXPLAIN (Analysis & Context)
[Explain what the current filtered view shows]
**Important Context:**
- Note if filters are limiting the view
- Mention if broader analysis would differ

### 🎯 LINK (Recommendations for {dashboard_context.get('user_role', 'User')})
[Provide role-appropriate actions]
**Immediate Actions:**
- [Specific to user role]

**Expected Impact:**
- [Quantified benefits]

Be specific about what's currently visible vs. total dataset."""
    
    return prompt

def create_peel_prompt(user_query, df, analysis):
    """Original PEEL prompt (fallback when no dashboard context)"""
    
    summary = f"""**Data Context:**
- Total Vessels: {len(df)}
- Operators: {df['operator'].nunique() if 'operator' in df.columns else 'N/A'}
- Countries/BUs: {df['bu'].nunique() if 'bu' in df.columns else 'N/A'}
"""
    
    if analysis and 'performance' in analysis:
        perf = analysis['performance']
        if 'avg_arrival_accuracy' in perf:
            summary += f"\n- On-Time Arrival Rate: {perf['avg_arrival_accuracy']:.1f}%"
    
    if analysis and 'sustainability' in analysis:
        sust = analysis['sustainability']
        if 'total_carbon_saved' in sust:
            summary += f"\n- Total Carbon Saved: {sust['total_carbon_saved']:.2f} tonnes"
    
    prompt = f"""You are a strategic analyst for PSA International. Answer using the PEEL structure:

**PEEL Response Format (MANDATORY):**

### 🎯 POINT (Main Answer)
[State your main finding/answer clearly in 1-2 sentences]

### 📊 EVIDENCE (Key Indicators & Data)
[Present data that supports your point]
- List 3-5 key indicators identified
- Include specific numbers and comparisons
- Create comparison table if relevant

| Indicator | Current | Target | Status |
|-----------|---------|--------|--------|

### 💡 EXPLAIN (Analysis & Assumptions)
[Explain what data means and state assumptions]
**Assumptions Made:**
1. [Assumption 1]
2. [Assumption 2]

**Analysis:**
[Explain trends, patterns, root causes]

### 🎯 LINK (Actions & Recommendations)
[Connect to PSA's goals and provide actionable steps]
**Immediate Actions (24-48h):**
- [Action 1]
- [Action 2]

**Expected Impact:**
- [Quantified benefit 1]
- [Quantified benefit 2]

### 📈 VISUALIZATIONS NEEDED
[Specify charts needed - I will create them]
- Chart 1: [type] showing [what]
- Chart 2: [type] showing [what]

---

**Data Summary:**
{summary}

**User Query:** {user_query}

Be specific with numbers, create tables for comparisons, state all assumptions clearly."""
    
    return prompt

def call_psa_api(prompt):
    """Call Azure OpenAI API"""
    try:
        if not AZURE_OPENAI_KEY:
            return "⚠️ **Configuration Error:** Please add your APIM Subscription Key"
        
        api_url = f"{AZURE_OPENAI_ENDPOINT}/openai/deployments/{DEPLOYMENT_NAME}/chat/completions?api-version={API_VERSION}"
        api_url_with_key = f"{api_url}&subscription-key={AZURE_OPENAI_KEY}"
        
        headers = {"Content-Type": "application/json"}
        
        body = {
            "messages": [
                {"role": "system", "content": "You are a strategic analyst. Always use PEEL structure. Include tables and specific numbers."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 2500
        }
        
        data = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(api_url_with_key, headers=headers, data=data, method="POST")
        
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode("utf-8"))
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
            return "⚠️ No response from API"
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

# =============================================================================
# VISUALIZATION FUNCTIONS
# =============================================================================
def create_comprehensive_visuals(df, query_context=""):
    """Create multiple visual analytics"""
    visuals = []
    
    # 1. Arrival Accuracy Comparison
    if 'operator' in df.columns and 'arrival_accuracy_(final_btr)' in df.columns:
        if pd.api.types.is_numeric_dtype(df['arrival_accuracy_(final_btr)']):
            acc_by_op = (df.groupby('operator')['arrival_accuracy_(final_btr)'].mean() * 100).sort_values(ascending=False)
            
            colors = [get_performance_color(val, 'arrival_accuracy') for val in acc_by_op.values]
            
            fig = go.Figure(data=[go.Bar(
                x=acc_by_op.index,
                y=acc_by_op.values,
                marker_color=colors,
                text=[f'{val:.1f}%' for val in acc_by_op.values],
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>On-Time Rate: %{y:.1f}%<extra></extra>'
            )])
            
            fig.add_hline(y=95, line_dash="dash", line_color="red", annotation_text="Target: 95%")
            fig.update_layout(
                title='On-Time Arrival Rate by Operator',
                xaxis_title='Operator',
                yaxis_title='On-Time Arrival Rate (%)',
                height=450,
                showlegend=False,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(size=12, color='#E0E0E0')
            )
            
            visuals.append(('arrival_comparison', fig))
    
    # 2. Wait Time Distribution
    if 'wait_time_(hours):_atb-btr' in df.columns and pd.api.types.is_numeric_dtype(df['wait_time_(hours):_atb-btr']):
        fig = px.histogram(
            df,
            x='wait_time_(hours):_atb-btr',
            nbins=40,
            title='Wait Time Distribution',
            labels={'wait_time_(hours):_atb-btr': 'Wait Time (hours)', 'count': 'Number of Vessels'},
            color_discrete_sequence=['#00A8E8']
        )
        fig.update_layout(
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#E0E0E0')
        )
        
        visuals.append(('wait_distribution', fig))
    
    # 3. Carbon Savings by Service
    if 'service' in df.columns and 'carbon_abatement_(tonnes)' in df.columns:
        if pd.api.types.is_numeric_dtype(df['carbon_abatement_(tonnes)']):
            carbon_by_service = df.groupby('service')['carbon_abatement_(tonnes)'].sum().sort_values(ascending=False).head(10)
            
            fig = go.Figure(data=[go.Bar(
                x=carbon_by_service.values,
                y=carbon_by_service.index,
                orientation='h',
                marker=dict(
                    color=carbon_by_service.values,
                    colorscale='Greens',
                    showscale=True,
                    colorbar=dict(title="Tonnes CO₂")
                ),
                text=[f'{val:.1f}t' for val in carbon_by_service.values],
                textposition='outside'
            )])
            
            fig.update_layout(
                title='Top 10 Services by Carbon Savings',
                xaxis_title='Carbon Saved (tonnes)',
                yaxis_title='Service',
                height=500,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#E0E0E0')
            )
            
            visuals.append(('carbon_services', fig))
    
    return visuals

# =============================================================================
# SIDEBAR - FILTERS & NAVIGATION
# =============================================================================
with st.sidebar:
    st.markdown("## 🚢 PSA Network AI")
    st.markdown("**Dashboard Interpreter**")
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # NEW - USER ROLE SELECTION
    st.markdown("### 👥 Your Role")
    user_role = st.selectbox(
        "I am viewing as:",
        [
            "Executive (C-Suite)",
            "Operations Manager",
            "Terminal Manager",
            "Data Analyst",
            "Sustainability Officer"
        ],
        index=["Executive (C-Suite)", "Operations Manager", "Terminal Manager", "Data Analyst", "Sustainability Officer"].index(st.session_state.user_role) if st.session_state.user_role in ["Executive (C-Suite)", "Operations Manager", "Terminal Manager", "Data Analyst", "Sustainability Officer"] else 1,
        help="AI will tailor insights to your role"
    )
    st.session_state.user_role = user_role
    
    st.markdown(f'<div class="role-badge">🎭 {user_role}</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # FILTERS SECTION
    st.markdown("### 🔍 Dashboard Filters")
    st.caption("*Filters affect both dashboard and AI analysis*")
    
    temp_filters = {}
    
    if not df_original.empty:
        # Operator filter
        if 'operator' in df_original.columns:
            selected_operators = st.multiselect(
                "Operators",
                options=sorted(df_original['operator'].unique().tolist()),
                default=st.session_state.active_filters.get('operators', []),
                help="Filter by shipping operator"
            )
            if selected_operators:
                temp_filters['operators'] = selected_operators
        
        # Business Unit/Country filter
        if 'bu' in df_original.columns:
            selected_bu = st.multiselect(
                "Business Unit / Country",
                options=sorted(df_original['bu'].unique().tolist()),
                default=st.session_state.active_filters.get('business_units', []),
                help="Filter by business unit or country"
            )
            if selected_bu:
                temp_filters['business_units'] = selected_bu
        
        # Port Time filter (slider)
        if 'assured_port_time_achieved_(%)' in df_original.columns:
            port_time_range = st.slider(
                "Port Time Achieved (%)",
                0, 100, 
                st.session_state.active_filters.get('port_time_range', (0, 100)),
                help="Filter by port time achievement percentage"
            )
            if port_time_range != (0, 100):
                temp_filters['port_time_range'] = port_time_range
        
        # Bunker Saved filter (slider)
        if 'bunker_saved_(usd)' in df_original.columns:
            bunker_min = float(df_original['bunker_saved_(usd)'].min())
            bunker_max = float(df_original['bunker_saved_(usd)'].max())
            if bunker_min < bunker_max:
                bunker_range = st.slider(
                    "Bunker Saved (USD)",
                    bunker_min, bunker_max,
                    st.session_state.active_filters.get('bunker_range', (bunker_min, bunker_max)),
                    help="Filter by fuel cost savings"
                )
                if bunker_range != (bunker_min, bunker_max):
                    temp_filters['bunker_range'] = bunker_range
        
        # Carbon Abatement filter (slider)
        if 'carbon_abatement_(tonnes)' in df_original.columns:
            carbon_min = float(df_original['carbon_abatement_(tonnes)'].min())
            carbon_max = float(df_original['carbon_abatement_(tonnes)'].max())
            if carbon_min < carbon_max:
                carbon_range = st.slider(
                    "Carbon Saved (Tonnes)",
                    carbon_min, carbon_max,
                    st.session_state.active_filters.get('carbon_range', (carbon_min, carbon_max)),
                    help="Filter by carbon emissions saved"
                )
                if carbon_range != (carbon_min, carbon_max):
                    temp_filters['carbon_range'] = carbon_range
        
        # Preset filters
        st.markdown("**Quick Filters:**")
        priority_filter = st.selectbox(
            "Show",
            [
                "All Data",
                "Critical Issues Only",
                "Delays > 4 hours",
                "Delays > 6 hours", 
                "High Performers Only",
                "Low Carbon Performance",
                "Below Target Accuracy"
            ],
            index=["All Data", "Critical Issues Only", "Delays > 4 hours", "Delays > 6 hours", "High Performers Only", "Low Carbon Performance", "Below Target Accuracy"].index(st.session_state.active_filters.get('quick_filter', 'All Data')),
            label_visibility="collapsed"
        )
        if priority_filter != "All Data":
            temp_filters['quick_filter'] = priority_filter
    
    # Update filters button
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Apply Filters", use_container_width=True, type="primary", key="apply_filters_btn"):
            st.session_state.active_filters = temp_filters
            st.rerun()
    
    with col2:
        if st.button("🔄 Reset", use_container_width=True, key="reset_filters_btn"):
            st.session_state.active_filters = {}
            st.rerun()
    
    # Show active filters
    if st.session_state.active_filters:
        st.markdown("### 🎯 Active Filters")
        for key, value in st.session_state.active_filters.items():
            if value:
                display_name = key.replace('_', ' ').title()
                if isinstance(value, (list, tuple)) and not isinstance(value[0] if value else None, str):
                    display_value = f"{value[0]:.0f} - {value[1]:.0f}"
                elif isinstance(value, list):
                    display_value = ', '.join(map(str, value[:3]))
                    if len(value) > 3:
                        display_value += f" (+{len(value)-3})"
                else:
                    display_value = str(value)
                
                st.markdown(f"""
                <div class="filter-indicator">
                    <strong>{display_name}</strong><br/>
                    <small>{display_value}</small>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # ACTION BUTTONS
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

# Apply filters to get current dataframe
df = apply_filters_to_dataframe(df_original, st.session_state.active_filters)

# Capture dashboard state
dashboard_context = capture_dashboard_state(df)

# =============================================================================
# HEADER
# =============================================================================
st.markdown('<p class="main-header">Good morning, PSA Operations Team 🚢</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">AI-Powered Dashboard Interpreter | Real-time Analytics · Predictive Intelligence</p>', unsafe_allow_html=True)

# Show filter status
if st.session_state.active_filters:
    filter_count = len([v for v in st.session_state.active_filters.values() if v])
    st.info(f"📊 **{filter_count} filter(s) active** - Viewing {len(df):,} of {len(df_original):,} vessels | AI will analyze current filtered view")

# =============================================================================
# CRITICAL ALERTS
# =============================================================================
if not df.empty:
    analysis = analyze_psa_data(df)
    
    if analysis and 'performance' in analysis:
        if analysis['performance'].get('avg_arrival_accuracy', 100) < 90:
            st.markdown(f"""
            <div class="alert-critical">
                <h3>🚨 CRITICAL ALERT: Low Arrival Accuracy</h3>
                <p>Current on-time arrival rate: {analysis['performance']['avg_arrival_accuracy']:.1f}% (Target: 95%)</p>
                <p><b>Impact:</b> {analysis['performance']['delayed_vessels']} vessels delayed | <b>Action:</b> Review berth scheduling immediately</p>
            </div>
            """, unsafe_allow_html=True)

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

# =============================================================================
# EXECUTIVE DASHBOARD (Always visible)
# =============================================================================
if not df.empty:
    st.markdown("### 📊 Executive Dashboard - Key Metrics")
    
    analysis = analyze_psa_data(df)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">🚢 Total Vessels</div>
            <div class="metric-value">{len(df)}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if 'performance' in analysis and 'avg_arrival_accuracy' in analysis['performance']:
            acc = analysis['performance']['avg_arrival_accuracy']
            color = analysis['performance']['accuracy_color']
            delta = acc - 95
            
            st.markdown(f"""
            <div class="metric-card" style="border-left-color: {color};">
                <div class="metric-label">✅ On-Time Arrival</div>
                <div class="metric-value">{acc:.1f}%</div>
                <div class="metric-delta {'delta-positive' if delta >= 0 else 'delta-negative'}">{delta:+.1f}% vs target</div>
            </div>
            """, unsafe_allow_html=True)
    
    with col3:
        if 'delays' in analysis and 'avg_wait_time' in analysis['delays']:
            wait = analysis['delays']['avg_wait_time']
            color = analysis['delays']['wait_color']
            
            st.markdown(f"""
            <div class="metric-card" style="border-left-color: {color};">
                <div class="metric-label">⏱️ Avg Wait Time</div>
                <div class="metric-value">{wait:.1f}h</div>
                <div class="metric-delta">{analysis['delays']['wait_label']}</div>
            </div>
            """, unsafe_allow_html=True)
    
    with col4:
        if 'sustainability' in analysis and 'total_carbon_saved' in analysis['sustainability']:
            carbon = analysis['sustainability']['total_carbon_saved']
            
            st.markdown(f"""
            <div class="metric-card sustainability-card">
                <div class="metric-label">🌱 Carbon Saved</div>
                <div class="metric-value">{carbon:.0f}t</div>
            </div>
            """, unsafe_allow_html=True)
    
    with col5:
        if 'sustainability' in analysis and 'total_bunker_saved' in analysis['sustainability']:
            bunker = analysis['sustainability']['total_bunker_saved']
            
            st.markdown(f"""
            <div class="metric-card" style="border-left-color: #3b82f6;">
                <div class="metric-label">💰 Cost Saved</div>
                <div class="metric-value">${bunker/1000:.0f}K</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Operator Comparison
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown("### 🏆 Top 5 Operators - Performance Comparison")
    
    if 'comparisons' in analysis and 'operators' in analysis['comparisons']:
        ops_stats = analysis['comparisons']['operators']
        ops_stats_sorted = sorted(ops_stats, key=lambda x: x.get('accuracy', 0), reverse=True)[:5]
        
        cols = st.columns(len(ops_stats_sorted))
        
        for idx, (col, op_stat) in enumerate(zip(cols, ops_stats_sorted)):
            with col:
                acc = op_stat.get('accuracy', 0)
                acc_color = get_performance_color(acc, 'arrival_accuracy')
                acc_label = get_performance_label(acc, 'arrival_accuracy')
                
                st.markdown(f"""
                <div class="comparison-card">
                    <h4 style="color: {acc_color}; margin: 0;">{op_stat['operator']}</h4>
                    <div style="padding: 0.5rem 0;">
                        <div style="display: flex; justify-content: space-between; margin: 0.3rem 0;">
                            <span>On-Time:</span>
                            <strong style="color: {acc_color};">{acc:.1f}%</strong>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin: 0.3rem 0;">
                            <span>Vessels:</span>
                            <strong>{op_stat['vessels']}</strong>
                        </div>
                        <div style="text-align: center; margin-top: 0.8rem; padding: 0.4rem; background: {acc_color}20; border-radius: 6px;">
                            <span style="color: {acc_color}; font-weight: 600; font-size: 0.9rem;">{acc_label}</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

# =============================================================================
# MAIN TABS
# =============================================================================
tab1, tab2, tab3, tab4, tab5, tab6, tab7= st.tabs([
    "💬 AI Assistant",
    "📊 Power BI Dashboard", 
    "📈 Analytics",
    "🎯 Action Plan",
    "🎮 Scenario Planner",
    "📋 Raw Data",
    "⚙️ System Status"
])

# =============================================================================
# TAB 1: AI ASSISTANT (ENHANCED WITH DASHBOARD AWARENESS)
# =============================================================================
with tab1:
    st.markdown(f"### 🤖 AI Dashboard Interpreter for {st.session_state.user_role}")
    st.markdown("*Ask questions about what you're currently viewing - AI understands your filters and role*")
    
    # ROLE-SPECIFIC QUICK QUESTIONS
    st.markdown("#### ⚡ Quick Questions for Your Role")
    
    quick_questions_by_role = {
        "Executive (C-Suite)": [
            "What are the top 3 strategic priorities based on current performance?",
            "What's our ROI on operational improvements?",
            "Where should we invest next quarter?"
        ],
        "Operations Manager": [
            "Which terminals need immediate attention?",
            "What's causing the delays I'm seeing?",
            "How can we improve berth utilization?"
        ],
        "Terminal Manager": [
            "How does my terminal compare to network average?",
            "Which vessels have longest wait times?",
            "What operational changes would reduce delays?"
        ],
        "Data Analyst": [
            "What patterns exist in the delay data?",
            "Show correlation between wait time and accuracy",
            "Predict next month's performance"
        ],
        "Sustainability Officer": [
            "Which routes have best carbon performance?",
            "How much more carbon could we save?",
            "What's our sustainability ranking by operator?"
        ]
    }
    
    role_questions = quick_questions_by_role.get(st.session_state.user_role, quick_questions_by_role["Operations Manager"])
    
    cols = st.columns(len(role_questions))
    for idx, (col, question) in enumerate(zip(cols, role_questions)):
        with col:
            if st.button(f"Q{idx+1}", use_container_width=True, key=f"role_q_{idx}", type="primary" if idx==0 else "secondary"):
                st.session_state.pending_query = question
                st.rerun()
    
    # Show questions as captions
    for idx, q in enumerate(role_questions):
        st.caption(f"**Q{idx+1}:** {q}")
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # Process pending query
    if 'pending_query' in st.session_state:
        query = st.session_state.pending_query
        del st.session_state.pending_query
        
        with st.spinner("🔍 Analyzing your dashboard view..."):
            # Use dashboard-aware prompt
            prompt = create_dashboard_aware_prompt(query, df, dashboard_context)
            response = call_psa_api(prompt)
            
            st.session_state.chat_history.append({
                'role': 'user',
                'content': query,
                'context': dashboard_context.copy()
            })
            st.session_state.chat_history.append({
                'role': 'assistant',
                'content': response,
                'visuals_needed': True
            })
            st.rerun()
    
    # USER INPUT SECTION
    st.markdown("#### 💭 Ask About Your Dashboard")
    user_query = st.text_area(
        "Ask about what you're currently viewing:",
        placeholder=f"e.g., Why is the metric low? What should I focus on as {st.session_state.user_role}?",
        height=100,
        key="user_query_input_main"
    )
    
    if st.button("🚀 Ask AI (Dashboard-Aware)", use_container_width=True, type="primary", key="get_analysis_btn"):
        if not user_query:
            st.warning("Please enter a question")
        elif df.empty:
            st.warning("No data available")
        else:
            with st.spinner("🤔 Analyzing your current dashboard view..."):
                # Use dashboard-aware prompt
                prompt = create_dashboard_aware_prompt(user_query, df, dashboard_context)
                response = call_psa_api(prompt)
                
                st.session_state.chat_history.append({
                    'role': 'user',
                    'content': user_query,
                    'context': dashboard_context.copy()
                })
                st.session_state.chat_history.append({
                    'role': 'assistant',
                    'content': response,
                    'visuals_needed': True
                })
                st.rerun()
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # CONVERSATION HISTORY
    st.markdown("#### 📝 Conversation History")
    
    if len(st.session_state.chat_history) == 0:
        st.info(f"👋 No questions yet, {st.session_state.user_role}! Use the quick questions above or ask your own.")
    
    for msg_idx, msg in enumerate(st.session_state.chat_history):
        if msg['role'] == 'user':
            # Show context when question was asked
            context_info = ""
            if 'context' in msg:
                ctx = msg['context']
                filter_summary = []
                if ctx.get('filters_applied'):
                    for k, v in ctx['filters_applied'].items():
                        if v:
                            filter_summary.append(f"{k.replace('_', ' ').title()}")
                if filter_summary:
                    context_info = f"<small style='color: #A0AEC0;'>🎯 Filters: {', '.join(filter_summary[:3])}</small><br/>"
                if ctx.get('total_vessels'):
                    context_info += f"<small style='color: #A0AEC0;'>📊 Viewing: {ctx['total_vessels']} vessels</small><br/>"
            
            st.markdown(f"""
            <div style="background: #1C2541; padding: 1rem; border-radius: 10px; margin: 1rem 0; border-left: 4px solid #00A8E8;">
                {context_info}
                <b style="color: #00A8E8;">👤 Your Question:</b><br>
                <span style="color: #E0E0E0;">{msg['content']}</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            # AI RESPONSE
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #1C2541 0%, #0B132B 100%); 
                        padding: 2rem; border-radius: 15px; margin: 1rem 0; 
                        border-left: 5px solid #A855F7; box-shadow: 0 8px 16px rgba(168, 85, 247, 0.3);">
                <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                    <span style="font-size: 1.5rem; margin-right: 0.5rem;">🤖</span>
                    <b style="color: #A855F7; font-size: 1.2rem;">AI Analysis (Based on Current View)</b>
                </div>
                <div style="color: #E0E0E0; line-height: 1.8;">
            """, unsafe_allow_html=True)
            
            st.markdown(msg['content'])
            
            st.markdown("</div></div>", unsafe_allow_html=True)
            
            # Visuals in expandable section
            if msg.get('visuals_needed', False) and not df.empty:
                with st.expander("📊 Supporting Charts & Data", expanded=False):
                    visuals = create_comprehensive_visuals(df)
                    for idx, (name, fig) in enumerate(visuals):
                        st.plotly_chart(fig, use_container_width=True, key=f"viz_{msg_idx}_{name}_{idx}")

# =============================================================================
# TAB 2: POWER BI DASHBOARD
# =============================================================================
with tab2:
    st.markdown("### 📊 PSA Global Network Dashboard")
    
    # Build Power BI URL with filters
    powerbi_url = build_powerbi_url_with_filters(POWERBI_EMBED_URL, st.session_state.active_filters)
    
    if POWERBI_EMBED_URL and POWERBI_EMBED_URL != "https://app.powerbi.com/reportEmbed?reportId=xxx&groupId=xxx&config=xxx":
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown("**Interactive Power BI Dashboard** - Synchronized with sidebar filters")
        with col2:
            if st.button("💬 Ask AI", use_container_width=True, key="ask_ai_powerbi"):
                st.switch_page("pages/💬_AI_Assistant.py") if hasattr(st, 'switch_page') else st.info("Switch to AI Assistant tab")
        
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        
        iframe_html = f"""
        <iframe 
            width="100%" 
            height="700" 
            src="{powerbi_url}"
            frameborder="0" 
            allowFullScreen="true">
        </iframe>
        """
        components.html(iframe_html, height=720, scrolling=True)
    else:
        st.warning("⚠️ Power BI Dashboard not configured")
        st.info("""
        **How Dashboard Integration Works:**
        
        1. Add your Power BI embed URL to `POWERBI_EMBED_URL`
        2. Apply filters in the sidebar
        3. Filters sync to Power BI automatically
        4. AI interprets what's visible in filtered view
        5. Ask questions - AI knows your context
        
        **Current Features:**
        ✅ Filters applied to data
        ✅ AI reads filtered metrics
        ✅ Role-based insights
        """)
        
        # Show sample visualization with filtered data
        st.markdown("#### 📊 Sample Visualization (Current Filtered View)")
        
        if not df.empty and 'operator' in df.columns:
            if 'arrival_accuracy_(final_btr)' in df.columns:
                acc_by_op = (df.groupby('operator')['arrival_accuracy_(final_btr)'].mean() * 100).sort_values(ascending=False)
                
                fig = go.Figure(data=[go.Bar(
                    x=acc_by_op.index,
                    y=acc_by_op.values,
                    marker_color='#00A8E8',
                    text=[f'{val:.1f}%' for val in acc_by_op.values],
                    textposition='outside'
                )])
                
                fig.update_layout(
                    title='On-Time Arrival Rate by Operator (Current Filtered View)',
                    xaxis_title='Operator',
                    yaxis_title='On-Time Rate (%)',
                    height=450,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#E0E0E0')
                )
                
                st.plotly_chart(fig, use_container_width=True)

# =============================================================================
# TAB 3: ANALYTICS
# =============================================================================
with tab3:
    st.markdown("### 📈 Advanced Analytics & Insights")
    
    if df.empty:
        st.warning("No data loaded")
    else:
        visuals = create_comprehensive_visuals(df)
        
        st.markdown("#### 🎯 Performance Overview")
        viz_cols = st.columns(2)
        
        for idx, (name, fig) in enumerate(visuals[:2]):
            with viz_cols[idx % 2]:
                st.plotly_chart(fig, use_container_width=True, key=f"analytics_{name}_{idx}")
        
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        
        st.markdown("#### 🌱 Sustainability Metrics")
        for idx, (name, fig) in enumerate(visuals[2:], start=2):
            st.plotly_chart(fig, use_container_width=True, key=f"analytics_{name}_{idx}")
        
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        
        # Performance Table
        st.markdown("#### 🏆 Detailed Performance Rankings")
        
        if 'operator' in df.columns:
            perf_data = []
            
            for operator in df['operator'].unique():
                op_df = df[df['operator'] == operator]
                
                row = {'Operator': operator, 'Vessels': len(op_df)}
                
                if 'arrival_accuracy_(final_btr)' in op_df.columns and pd.api.types.is_numeric_dtype(op_df['arrival_accuracy_(final_btr)']):
                    acc = op_df['arrival_accuracy_(final_btr)'].mean() * 100
                    row['On-Time %'] = f"{acc:.1f}%"
                    row['Performance'] = get_performance_label(acc, 'arrival_accuracy')
                
                if 'wait_time_(hours):_atb-btr' in op_df.columns:
                    row['Avg Wait (h)'] = f"{op_df['wait_time_(hours):_atb-btr'].mean():.1f}"
                
                if 'carbon_abatement_(tonnes)' in op_df.columns:
                    row['Carbon (t)'] = f"{op_df['carbon_abatement_(tonnes)'].sum():.0f}"
                
                perf_data.append(row)
            
            perf_df = pd.DataFrame(perf_data)
            
            if 'On-Time %' in perf_df.columns:
                perf_df = perf_df.sort_values('Vessels', ascending=False)
            
            st.dataframe(perf_df, use_container_width=True, height=400)

# =============================================================================
# TAB 4: ACTION PLAN
# =============================================================================
with tab4:
    st.markdown("### 🎯 Strategic Action Plan Generator")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("📋 Generate AI Suggestion", type="primary", use_container_width=True, key="gen_action_plan"):
            if df.empty:
                st.warning("No data available")
            else:
                with st.spinner("🔄 Creating action plan..."):
                    analysis = analyze_psa_data(df)
                    
                    prompt = f"""Create executive action plan for PSA:

**Data**: {len(df)} vessels, {analysis['performance'].get('avg_arrival_accuracy', 0):.1f}% on-time

Format:
# 🎯 PSA Action Plan

## 🔴 IMMEDIATE (24-48h)
| Action | Owner | Impact |

## 🟡 SHORT-TERM (1-2 weeks)

## 🟢 STRATEGIC (1-3 months)

## 📊 Success Metrics
| Metric | Current | Target |

## 💰 ROI"""
                    
                    st.session_state.action_plan = call_psa_api(prompt)
                    st.rerun()
    
    with col2:
        if st.button("💬 Customize Action Plan", use_container_width=True, key="custom_action_plan"):
            st.session_state.show_action_chat = True
            st.rerun()
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # ACTION PLAN DISPLAY (IN ONE BLOCK)
    if st.session_state.action_plan:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #1C2541 0%, #0B132B 100%); 
                    padding: 2.5rem; border-radius: 15px; 
                    border-left: 5px solid #00A8E8; 
                    box-shadow: 0 8px 20px rgba(0, 168, 232, 0.3); 
                    margin: 2rem 0;">
            <div style="display: flex; align-items: center; margin-bottom: 1.5rem;">
                <span style="font-size: 2rem; margin-right: 0.5rem;">📋</span>
                <h3 style="color: #00A8E8; margin: 0;">Strategic Action Plan</h3>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown(st.session_state.action_plan)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # CHATBOT FOR CUSTOMIZATION
    if st.session_state.get('show_action_chat', False):
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        st.markdown("#### 💬 Customize Your Action Plan")
        
        if 'action_chat_history' not in st.session_state:
            st.session_state.action_chat_history = []
        
        # Display chat
        for chat_msg in st.session_state.action_chat_history:
            if chat_msg['role'] == 'user':
                st.markdown(f"""
                <div style="background: #00A8E8; color: white; padding: 1rem; border-radius: 10px; margin: 0.5rem 0;">
                    <b>You:</b> {chat_msg['content']}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="background: #1C2541; color: #E0E0E0; padding: 1rem; border-radius: 10px; margin: 0.5rem 0;">
                    <b style="color: #A855F7;">AI:</b> {chat_msg['content']}
                </div>
                """, unsafe_allow_html=True)
        
        # Chat input
        user_customization = st.text_input(
            "What changes would you like?",
            placeholder="e.g., Add more focus on sustainability, prioritize Terminal X",
            key="action_chat_input"
        )
        
        if st.button("Send", key="send_action_chat"):
            if user_customization:
                st.session_state.action_chat_history.append({'role': 'user', 'content': user_customization})
                
                # Generate updated plan
                update_prompt = f"""Update the action plan based on this request: {user_customization}

Current plan:
{st.session_state.action_plan}

Provide the updated complete action plan."""
                
                updated_plan = call_psa_api(update_prompt)
                st.session_state.action_plan = updated_plan
                st.session_state.action_chat_history.append({'role': 'assistant', 'content': "I've updated the action plan based on your request!"})
                st.rerun()

# =============================================================================
# TAB 5: SCENARIO PLANNER
# =============================================================================
with tab5:
    st.markdown("### 🎮 What-If Scenario Simulator")
    st.markdown("*Model operational improvements and see projected impact*")
    
    if df.empty:
        st.warning("No data available")
    else:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("#### 🎛️ Adjust Parameters")
            
            wait_time_reduction = st.slider(
                "Wait Time Reduction (%)",
                0, 50, 25,
                help="Simulate reducing average wait time"
            )
            
            accuracy_improvement = st.slider(
                "Arrival Accuracy Target (%)",
                85, 100, 95,
                help="Set target on-time arrival rate"
            )
            
            berth_efficiency = st.slider(
                "Berth Efficiency Gain (%)",
                0, 30, 15,
                help="Simulate faster cargo operations"
            )
            
            st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
            
            if st.button("🔮 Calculate Impact", type="primary", use_container_width=True):
                st.session_state.scenario_calculated = True
                st.rerun()
        
        with col2:
            st.markdown("#### 📈 Projected Impact")
            
            if st.session_state.get('scenario_calculated', False):
                # Current metrics
                current_carbon = df['carbon_abatement_(tonnes)'].sum() if 'carbon_abatement_(tonnes)' in df.columns else 0
                current_bunker = df['bunker_saved_(usd)'].sum() if 'bunker_saved_(usd)' in df.columns else 0
                current_wait = df['wait_time_(hours):_atb-btr'].mean() if 'wait_time_(hours):_atb-btr' in df.columns else 0
                
                # Projected metrics
                projected_carbon = current_carbon * (1 + (wait_time_reduction + berth_efficiency) / 100)
                projected_bunker = current_bunker * (1 + (wait_time_reduction + berth_efficiency) / 100)
                projected_wait = current_wait * (1 - wait_time_reduction / 100)
                
                # Display metrics
                metric_col1, metric_col2, metric_col3 = st.columns(3)
                
                with metric_col1:
                    st.metric(
                        "🌱 Carbon Savings",
                        f"{projected_carbon:.0f}t",
                        delta=f"+{projected_carbon - current_carbon:.0f}t",
                        delta_color="normal"
                    )
                
                with metric_col2:
                    st.metric(
                        "💰 Cost Savings",
                        f"${projected_bunker/1000:.0f}K",
                        delta=f"+${(projected_bunker - current_bunker)/1000:.0f}K",
                        delta_color="normal"
                    )
                
                with metric_col3:
                    st.metric(
                        "⏱️ Avg Wait Time",
                        f"{projected_wait:.1f}h",
                        delta=f"{projected_wait - current_wait:.1f}h",
                        delta_color="inverse"
                    )
                
                # Visualization
                st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
                st.markdown("#### 📊 Before vs After Comparison")
                
                comparison_data = pd.DataFrame({
                    'Metric': ['Carbon Saved (t)', 'Cost Saved ($K)', 'Avg Wait (h)'],
                    'Current': [current_carbon, current_bunker/1000, current_wait],
                    'Projected': [projected_carbon, projected_bunker/1000, projected_wait]
                })
                
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    name='Current',
                    x=comparison_data['Metric'],
                    y=comparison_data['Current'],
                    marker_color='#6B7280'
                ))
                fig.add_trace(go.Bar(
                    name='Projected',
                    x=comparison_data['Metric'],
                    y=comparison_data['Projected'],
                    marker_color='#22C55E'
                ))
                
                fig.update_layout(
                    barmode='group',
                    height=400,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#E0E0E0')
                )
                
                st.plotly_chart(fig, use_container_width=True, key="scenario_comparison_chart")
                
                # Impact summary
                st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
                st.markdown("#### 💡 Impact Summary")
                
                accuracy_current = df['arrival_accuracy_(final_btr)'].mean() * 100 if 'arrival_accuracy_(final_btr)' in df.columns else 0
                
                st.markdown(f"""
                <div class="action-card sustainability-card">
                    <h4>By implementing these improvements:</h4>
                    <ul>
                        <li><strong>{(projected_carbon - current_carbon):.0f} additional tonnes</strong> of CO₂ saved</li>
                        <li><strong>${(projected_bunker - current_bunker):,.0f}</strong> in additional fuel cost savings</li>
                        <li><strong>{(current_wait - projected_wait) * len(df):.0f} total hours</strong> saved across all vessels</li>
                        <li><strong>{accuracy_improvement - accuracy_current:.1f}%</strong> improvement in on-time arrivals</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("Adjust parameters and click 'Calculate Impact' to see projections")

# =============================================================================
# TAB 6: RAW DATA
# =============================================================================
with tab6:
    st.markdown("### 📋 Raw Dataset Explorer")
    
    if df.empty:
        st.warning("No data loaded")
    else:
        # Summary cards
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Records", f"{len(df):,}")
        with col2:
            st.metric("Columns", len(df.columns))
        with col3:
            if not df.empty and hasattr(df.index, 'date'):
                st.metric("Date Range", f"{df.index[0]} to {df.index[-1]}")
            else:
                st.metric("Date Range", "N/A")
        with col4:
            memory_usage = df.memory_usage(deep=True).sum() / 1024**2
            st.metric("Memory", f"{memory_usage:.2f} MB")
        
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        
        # Search and filter
        col1, col2 = st.columns([3, 1])
        with col1:
            search_term = st.text_input("🔍 Search", placeholder="Search across all columns...")
        with col2:
            rows_display = st.selectbox("Rows per page", [25, 50, 100, 500], index=1)
        
        # Apply search
        display_df = df.copy()
        if search_term:
            mask = display_df.astype(str).apply(lambda x: x.str.contains(search_term, case=False, na=False)).any(axis=1)
            display_df = display_df[mask]
            st.info(f"Found {len(display_df)} matching records")
        
        # Display data
        st.dataframe(
            display_df.head(rows_display),
            use_container_width=True,
            height=600
        )
        
        # Download button
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Download Filtered Dataset (CSV)",
            data=csv,
            file_name=f"psa_filtered_data_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )

# =============================================================================
# TAB 7: SYSTEM STATUS
# =============================================================================
with tab7:
    st.markdown("### ⚙️ System Status & Performance")
    
    col1, col2 = st.columns(2)
    
    # CONNECTION STATUS
    with col1:
        st.markdown("#### 🔌 Connection Status")
        
        status_data = {
            'Component': ['Azure OpenAI API', 'Power BI Dashboard', 'Data Source', 'Dashboard Awareness'],
            'Status': [
                '✅ Connected' if AZURE_OPENAI_KEY else '❌ Not Configured',
                '✅ Connected' if POWERBI_EMBED_URL and POWERBI_EMBED_URL != "https://app.powerbi.com/reportEmbed?reportId=xxx&groupId=xxx&config=xxx" else '❌ Not Configured',
                '✅ Loaded' if not df_original.empty else '❌ No Data',
                '✅ Active' if st.session_state.dashboard_context else '⚠️ No Context'
            ],
            'Details': [
                f'Endpoint: {DEPLOYMENT_NAME}' if AZURE_OPENAI_KEY else 'Add API key',
                'Embedded' if POWERBI_EMBED_URL and POWERBI_EMBED_URL != "https://app.powerbi.com/reportEmbed?reportId=xxx&groupId=xxx&config=xxx" else 'Add embed URL',
                f'{len(df_original)} records' if not df_original.empty else 'No data.csv file',
                f'{len(st.session_state.active_filters)} filters' if st.session_state.active_filters else 'No filters'
            ]
        }
        
        status_df = pd.DataFrame(status_data)
        st.dataframe(status_df, use_container_width=True, hide_index=True)
    
    # SYSTEM METRICS
    with col2:
        st.markdown("#### 📊 System Metrics")
        
        uptime = datetime.now() - st.session_state.system_start_time
        uptime_str = f"{uptime.seconds // 3600}h {(uptime.seconds % 3600) // 60}m"
        
        metrics_data = {
            'Metric': ['Uptime', 'Chat Messages', 'Active Filters', 'Filtered Records', 'User Role'],
            'Value': [
                uptime_str,
                len(st.session_state.chat_history),
                len([v for v in st.session_state.active_filters.values() if v]),
                f"{len(df):,} of {len(df_original):,}",
                st.session_state.user_role
            ]
        }
        
        metrics_df = pd.DataFrame(metrics_data)
        st.dataframe(metrics_df, use_container_width=True, hide_index=True)
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # DASHBOARD CONTEXT
    st.markdown("#### 🎯 Current Dashboard Context")
    
    if st.session_state.dashboard_context:
        context_display = {
            'Metric': [],
            'Value': []
        }
        
        for key, value in st.session_state.dashboard_context.items():
            if key not in ['filters_applied', 'timestamp']:
                display_key = key.replace('_', ' ').title()
                if isinstance(value, float):
                    display_value = f"{value:.2f}"
                elif isinstance(value, list):
                    display_value = ', '.join(map(str, value[:5]))
                    if len(value) > 5:
                        display_value += f" (+{len(value)-5})"
                else:
                    display_value = str(value)
                
                context_display['Metric'].append(display_key)
                context_display['Value'].append(display_value)
        
        context_df = pd.DataFrame(context_display)
        st.dataframe(context_df, use_container_width=True, hide_index=True)
    else:
        st.info("No dashboard context captured yet. Apply filters or ask a question to capture context.")
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # DATA QUALITY REPORT
    st.markdown("#### 📋 Data Quality Report")
    
    if not df_original.empty:
        quality_report = []
        
        for col in df_original.columns[:15]:  # Show first 15 columns
            missing_pct = (df_original[col].isna().sum() / len(df_original)) * 100
            unique_vals = df_original[col].nunique()
            
            quality_report.append({
                'Column': col.replace('_', ' ').title(),
                'Missing %': f"{missing_pct:.1f}%",
                'Unique Values': unique_vals,
                'Data Type': str(df_original[col].dtype),
                'Quality': '✅ Good' if missing_pct < 5 else '⚠️ Check' if missing_pct < 20 else '❌ Poor'
            })
        
        quality_df = pd.DataFrame(quality_report)
        st.dataframe(quality_df, use_container_width=True, height=400)
    else:
        st.info("No data loaded for quality analysis")
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # CONFIGURATION
    st.markdown("#### ⚙️ Configuration")
    
    with st.expander("📝 API Configuration", expanded=False):
        st.code(f"""
Azure OpenAI Configuration:
- Endpoint: {AZURE_OPENAI_ENDPOINT}
- Deployment: {DEPLOYMENT_NAME}
- API Version: {API_VERSION}
- Status: {'✅ Configured' if AZURE_OPENAI_KEY else '❌ Missing Key'}
        """)
    
    with st.expander("📊 Power BI Configuration", expanded=False):
        if POWERBI_EMBED_URL and POWERBI_EMBED_URL != "https://app.powerbi.com/reportEmbed?reportId=xxx&groupId=xxx&config=xxx":
            st.code(f"Power BI Embed URL: {POWERBI_EMBED_URL[:50]}...")
        else:
            st.warning("Power BI not configured. Add embed URL to enable dashboard.")
    
    with st.expander("🔧 System Information", expanded=False):
        st.code(f"""
System Information:
- Python Version: 3.10+
- Streamlit Version: Latest
- Session Start: {st.session_state.system_start_time.strftime('%Y-%m-%d %H:%M:%S')}
- Data Source: data.csv
- Total Records: {len(df_original) if not df_original.empty else 0}
- Filtered Records: {len(df) if not df.empty else 0}
- Columns: {len(df_original.columns) if not df_original.empty else 0}
- User Role: {st.session_state.user_role}
- Active Filters: {len([v for v in st.session_state.active_filters.values() if v])}
        """)


# =============================================================================
# FOOTER
# =============================================================================
st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

footer_cols = st.columns(4)

with footer_cols[0]:
    st.markdown("""
    **🚢 PSA CodeSprint 2025**  
    AI-Powered Dashboard Interpreter
    """)

with footer_cols[1]:
    st.markdown("""
    **📊 Key Features**  
    ✅ Dashboard-Aware AI  
    ✅ Role-Based Insights  
    ✅ Filter Synchronization
    """)

with footer_cols[2]:
    st.markdown("""
    **🎯 Strategic Goals**  
    🌐 Global Coordination  
    ⏱️ Delay Reduction  
    🌱 Sustainability
    """)

with footer_cols[3]:
    st.markdown(f"""
    **👤 Current Session**  
    Role: {st.session_state.user_role}  
    Filters: {len([v for v in st.session_state.active_filters.values() if v])} active  
    Data: {len(df):,} records
    """)

st.markdown("---")
st.markdown("*Built with ❤️ for PSA International | AI-Enhanced Decision Making · Dashboard Intelligence · Stakeholder-Driven Insights*")
        