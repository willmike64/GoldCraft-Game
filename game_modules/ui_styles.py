"""
Unified UI styling system for GoldCraft
Provides consistent, readable styling across all game modules
"""

import streamlit as st

def apply_global_styles():
    """Apply consistent global styles for optimal readability"""
    st.markdown("""
    <style>
    /* Global App Styling */
    .stApp {
        background: linear-gradient(135deg, #f8f6f0 0%, #f0ede5 50%, #f5f2ea 100%);
        color: #2c2c2c !important;
    }
    
    /* Main Content Container */
    .main .block-container {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        padding: 2rem;
        margin: 1rem;
        box-shadow: 0 4px 20px rgba(139, 69, 19, 0.15);
        border: 1px solid rgba(218, 165, 32, 0.2);
    }
    
    /* Content Boxes */
    .content-box {
        background: linear-gradient(145deg, rgba(255, 255, 255, 0.98), rgba(248, 246, 240, 0.98));
        border: 2px solid #DAA520;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 15px rgba(218, 165, 32, 0.2);
        color: #2c2c2c !important;
    }
    
    /* Readable Text Containers */
    .readable-text {
        background: rgba(255, 255, 255, 0.95);
        color: #2c2c2c !important;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #DAA520;
        margin: 0.5rem 0;
        box-shadow: 0 1px 5px rgba(0, 0, 0, 0.1);
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: #8B4513 !important;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.1);
    }
    
    /* Gold accent text */
    .gold-text {
        color: #DAA520 !important;
        font-weight: bold;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.2);
    }
    
    /* All text elements */
    .stMarkdown, .stMarkdown p, .stMarkdown li, .stMarkdown div {
        color: #2c2c2c !important;
    }
    
    .stMarkdown strong {
        color: #8B4513 !important;
    }
    
    /* Lists */
    ul, ol, li {
        color: #2c2c2c !important;
    }
    
    /* Metrics */
    .metric-container {
        background: rgba(255, 255, 255, 0.9);
        border: 1px solid #DAA520;
        border-radius: 8px;
        padding: 0.5rem;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(45deg, #DAA520, #FFD700);
        color: #1a1a1a !important;
        border: none;
        border-radius: 8px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: linear-gradient(45deg, #FFD700, #FFFF00);
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(218, 165, 32, 0.4);
    }
    
    /* Sidebar */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8f6f0 0%, #f0ede5 100%);
    }
    
    /* Info boxes */
    .stInfo {
        background: rgba(255, 255, 255, 0.95);
        color: #2c2c2c !important;
        border-left: 4px solid #17a2b8;
    }
    
    .stSuccess {
        background: rgba(255, 255, 255, 0.95);
        color: #2c2c2c !important;
        border-left: 4px solid #28a745;
    }
    
    .stWarning {
        background: rgba(255, 255, 255, 0.95);
        color: #2c2c2c !important;
        border-left: 4px solid #ffc107;
    }
    
    .stError {
        background: rgba(255, 255, 255, 0.95);
        color: #2c2c2c !important;
        border-left: 4px solid #dc3545;
    }
    
    /* Town Hub Cards */
    .town-card {
        background: rgba(255, 255, 255, 0.95);
        border: 2px solid #DAA520;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 10px rgba(218, 165, 32, 0.2);
        color: #2c2c2c !important;
    }
    
    .town-card h3 {
        color: #8B4513 !important;
        margin: 0 0 0.5rem 0;
    }
    
    .town-card p {
        color: #2c2c2c !important;
        margin: 0;
    }
    
    /* Input fields */
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.95);
        color: #2c2c2c !important;
        border: 1px solid #DAA520;
    }
    
    .stSelectbox > div > div > select {
        background: rgba(255, 255, 255, 0.95);
        color: #2c2c2c !important;
        border: 1px solid #DAA520;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: #8B4513 !important;
    }
    
    /* Radio buttons */
    .stRadio > div {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 8px;
        padding: 0.5rem;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.9);
        color: #8B4513 !important;
    }
    
    /* Data frames */
    .stDataFrame {
        background: rgba(255, 255, 255, 0.95);
    }
    
    /* Progress bars */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #DAA520, #FFD700);
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