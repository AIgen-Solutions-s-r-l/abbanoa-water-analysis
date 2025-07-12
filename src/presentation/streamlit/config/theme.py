"""
Theme configuration for the Streamlit dashboard.

This module defines the visual theme and styling for the application.
"""

import streamlit as st


def apply_custom_theme():
    """Apply custom CSS theme to the Streamlit application."""

    # Define custom CSS
    custom_css = """
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Global Styles - Force White Theme */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #ffffff !important;
        color: #262730 !important;
    }
    
    /* Main container */
    .main {
        padding-top: 2rem;
        background-color: #ffffff !important;
    }
    
    /* Force white background for all containers */
    .stApp {
        background-color: #ffffff !important;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
    }
    
    /* Primary color for headers */
    h1 {
        color: #1f77b4;
    }
    
    /* Sidebar styling - White Theme */
    .css-1d391kg, [data-testid="stSidebar"] {
        background-color: #f8f9fa !important;
    }
    
    .css-1d391kg > div {
        background-color: #f8f9fa !important;
    }
    
    /* Sidebar content */
    .css-1d391kg .block-container {
        background-color: #f8f9fa !important;
    }
    
    /* Metric cards */
    [data-testid="metric-container"] {
        background-color: #f0f2f6;
        border: 1px solid #e0e0e0;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }
    
    [data-testid="metric-container"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 2px 6px rgba(0,0,0,0.15);
    }
    
    /* Buttons */
    .stButton > button {
        background-color: #1f77b4;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 500;
        border-radius: 0.25rem;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        background-color: #1557a0;
        transform: translateY(-1px);
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    /* Download buttons */
    .stDownloadButton > button {
        background-color: #2ca02c;
        color: white;
    }
    
    .stDownloadButton > button:hover {
        background-color: #238b23;
    }
    
    /* Selectbox styling */
    .stSelectbox > div > div {
        background-color: white;
        border: 1px solid #e0e0e0;
        border-radius: 0.25rem;
    }
    
    /* Slider styling */
    .stSlider > div > div > div {
        background-color: #1f77b4;
    }
    
    /* Info boxes */
    .stInfo {
        background-color: #e3f2fd;
        border-left: 4px solid #1f77b4;
    }
    
    /* Warning boxes */
    .stWarning {
        background-color: #fff3cd;
        border-left: 4px solid #ff7f0e;
    }
    
    /* Error boxes */
    .stError {
        background-color: #f8d7da;
        border-left: 4px solid #d62728;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        background-color: #f8f9fa;
        padding: 0.5rem;
        border-radius: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
        background-color: transparent;
        border-radius: 0.25rem;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: white;
        border: 1px solid #e0e0e0;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #f0f2f6;
        border-radius: 0.25rem;
        font-weight: 500;
    }
    
    /* Loading spinner */
    .stSpinner > div {
        border-color: #1f77b4;
    }
    
    /* Custom container styling */
    .forecast-header {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    
    /* Chart container */
    .plot-container {
        background-color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main {
            padding: 1rem;
        }
        
        h1 {
            font-size: 1.5rem;
        }
        
        [data-testid="metric-container"] {
            padding: 0.5rem;
        }
    }
    
    /* Animation for smooth transitions */
    * {
        transition: all 0.3s ease;
    }
    
    /* Remove Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #888;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #555;
    }
    </style>
    """

    # Apply the custom CSS
    st.markdown(custom_css, unsafe_allow_html=True)

    # Additional JavaScript for enhanced interactivity
    custom_js = """
    <script>
    // Add smooth scrolling
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });
    
    // Add fade-in animation for elements
    const observerOptions = {
        threshold: 0.1
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
            }
        });
    }, observerOptions);
    
    // Observe all metric containers
    document.querySelectorAll('[data-testid="metric-container"]').forEach(el => {
        observer.observe(el);
    });
    </script>
    """

    # Apply JavaScript (optional, may not work in all Streamlit deployments)
    # st.markdown(custom_js, unsafe_allow_html=True)


def get_color_palette():
    """
    Get the color palette for the dashboard.

    Returns:
        Dictionary of color values
    """
    return {
        "primary": "#1f77b4",
        "secondary": "#ff7f0e",
        "success": "#2ca02c",
        "warning": "#ff7f0e",
        "danger": "#d62728",
        "info": "#17a2b8",
        "light": "#f8f9fa",
        "dark": "#343a40",
        "background": "#ffffff",
        "surface": "#f0f2f6",
        "text": "#212529",
        "text_secondary": "#6c757d",
    }


def format_metric_value(value: float, metric_type: str) -> str:
    """
    Format metric value based on type.

    Args:
        value: Numeric value to format
        metric_type: Type of metric

    Returns:
        Formatted string
    """
    formatters = {
        "flow_rate": lambda x: f"{x:.1f} L/s",
        "pressure": lambda x: f"{x:.2f} bar",
        "reservoir_level": lambda x: f"{x:.1f} m",
        "percentage": lambda x: f"{x:.1f}%",
        "currency": lambda x: f"€{x:,.2f}",
    }

    formatter = formatters.get(metric_type, lambda x: f"{x:.2f}")
    return formatter(value)
