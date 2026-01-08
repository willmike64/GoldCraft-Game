"""
Unified UI styling system for GoldCraft
Provides consistent, readable styling across all game modules
"""

import streamlit as st

def apply_global_styles():
    """Apply consistent global styles for optimal readability"""
    st.markdown("""
    <style>
    /* Global App Styling - High Contrast */
    .stApp {
        background: #ffffff !important;
        color: #1a1a1a !important;
    }
    
    /* Main Content Container */
    .main .block-container {
        background: #ffffff !important;
        border-radius: 10px;
        padding: 2rem;
        margin: 1rem;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        border: 1px solid #e0e0e0;
    }
    
    /* Content Boxes - High Contrast */
    .content-box {
        background: #ffffff !important;
        border: 2px solid #DAA520;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 10px rgba(218, 165, 32, 0.2);
        color: #1a1a1a !important;
    }
    
    /* Readable Text Containers - Maximum Contrast */
    .readable-text {
        background: #ffffff !important;
        color: #1a1a1a !important;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #DAA520;
        margin: 0.5rem 0;
        box-shadow: 0 1px 5px rgba(0, 0, 0, 0.1);
        border: 1px solid #e0e0e0;
    }
    
    /* Headers - Dark Text */
    h1, h2, h3, h4, h5, h6 {
        color: #1a1a1a !important;
        font-weight: bold !important;
    }
    
    /* Gold accent text - Darker for readability */
    .gold-text {
        color: #B8860B !important;
        font-weight: bold;
        text-shadow: none;
    }
    
    /* All text elements - Force dark text */
    .stMarkdown, .stMarkdown p, .stMarkdown li, .stMarkdown div, .stMarkdown span {
        color: #1a1a1a !important;
        background: transparent;
    }
    
    .stMarkdown strong {
        color: #1a1a1a !important;
        font-weight: bold;
    }
    
    /* Lists */
    ul, ol, li {
        color: #1a1a1a !important;
    }
    
    /* Metrics - High Contrast */
    .metric-container {
        background: #ffffff !important;
        border: 1px solid #DAA520;
        border-radius: 8px;
        padding: 0.5rem;
        color: #1a1a1a !important;
    }
    
    /* Buttons - High Contrast */
    .stButton > button {
        background: #DAA520 !important;
        color: #ffffff !important;
        border: 2px solid #B8860B !important;
        border-radius: 8px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: #B8860B !important;
        color: #ffffff !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 10px rgba(218, 165, 32, 0.3);
    }
    
    /* Sidebar - Light Background */
    .css-1d391kg {
        background: #f8f9fa !important;
        color: #1a1a1a !important;
    }
    
    /* Info boxes - High Contrast */
    .stInfo {
        background: #ffffff !important;
        color: #1a1a1a !important;
        border-left: 4px solid #17a2b8 !important;
        border: 1px solid #bee5eb !important;
    }
    
    .stSuccess {
        background: #ffffff !important;
        color: #1a1a1a !important;
        border-left: 4px solid #28a745 !important;
        border: 1px solid #c3e6cb !important;
    }
    
    .stWarning {
        background: #ffffff !important;
        color: #1a1a1a !important;
        border-left: 4px solid #ffc107 !important;
        border: 1px solid #ffeaa7 !important;
    }
    
    .stError {
        background: #ffffff !important;
        color: #1a1a1a !important;
        border-left: 4px solid #dc3545 !important;
        border: 1px solid #f5c6cb !important;
    }
    
    /* Town Hub Cards - High Contrast */
    .town-card {
        background: #ffffff !important;
        border: 2px solid #DAA520;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 8px rgba(218, 165, 32, 0.2);
        color: #1a1a1a !important;
    }
    
    .town-card h3 {
        color: #1a1a1a !important;
        margin: 0 0 0.5rem 0;
        font-weight: bold;
    }
    
    .town-card p {
        color: #1a1a1a !important;
        margin: 0;
    }
    
    /* Input fields - High Contrast */
    .stTextInput > div > div > input {
        background: #ffffff !important;
        color: #1a1a1a !important;
        border: 2px solid #DAA520 !important;
    }
    
    .stSelectbox > div > div > select {
        background: #ffffff !important;
        color: #1a1a1a !important;
        border: 2px solid #DAA520 !important;
    }
    
    /* Tabs - High Contrast */
    .stTabs [data-baseweb="tab-list"] {
        background: #ffffff !important;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: #1a1a1a !important;
        font-weight: bold;
    }
    
    /* Radio buttons - High Contrast */
    .stRadio > div {
        background: #ffffff !important;
        border-radius: 8px;
        padding: 0.5rem;
        border: 1px solid #e0e0e0;
    }
    
    .stRadio label {
        color: #1a1a1a !important;
    }
    
    /* Expander - High Contrast */
    .streamlit-expanderHeader {
        background: #ffffff !important;
        color: #1a1a1a !important;
        border: 1px solid #e0e0e0;
    }
    
    /* Data frames */
    .stDataFrame {
        background: #ffffff !important;
        color: #1a1a1a !important;
    }
    
    /* Progress bars */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #DAA520, #B8860B) !important;
    }
    
    /* Sidebar text */
    .css-1d391kg .stMarkdown {
        color: #1a1a1a !important;
    }
    
    /* Force all text to be dark */
    * {
        color: #1a1a1a !important;
    }
    
    /* Exception for buttons and specific elements that need white text */
    .stButton > button, .stButton > button * {
        color: #ffffff !important;
    }
    
    /* Tooltip styling for expedition choices */
    .tooltip .tooltiptext {
        background-color: #ffffff !important;
        color: #1a1a1a !important;
        border: 2px solid #DAA520 !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2) !important;
    }
    
    /* Travel tooltip styling */
    .travel-tooltip .tooltiptext {
        background-color: #ffffff !important;
        color: #1a1a1a !important;
        border: 2px solid #DAA520 !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2) !important;
    }
    </style>
    """, unsafe_allow_html=True)

def create_content_box(content):
    """Create a styled content box with readable text"""
    return f'<div class="content-box">{content}</div>'

def create_readable_text(content):
    """Create readable text with proper background"""
    return f'<div class="readable-text">{content}</div>'

def create_gold_text(content):
    """Create gold-colored accent text"""
    return f'<span class="gold-text">{content}</span>'

def create_town_card(title, description):
    """Create a styled town card"""
    return f'''
    <div class="town-card">
        <h3>{title}</h3>
        <p>{description}</p>
    </div>
    '''