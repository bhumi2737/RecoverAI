import streamlit as st

def apply_custom_theme():
    st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');
    
    /* Hide Streamlit Native Sidebar completely */
    [data-testid="stSidebar"] { display: none !important; width: 0 !important; }
    [data-testid="stSidebarNav"] { display: none !important; }
    section[data-testid="stSidebar"] { display: none !important; width: 0 !important; }
    [data-testid="collapsedControl"] { display: none !important; }
    header[data-testid="stHeader"] { display: none !important; }
    header { visibility: hidden !important; height: 0 !important; }
    footer { visibility: hidden !important; height: 0 !important; }
    .stApp > header { display: none !important; }
    
    /* Cosmic / Premium Dark Base */
    .stApp {
        background: radial-gradient(circle at top right, #1a1a2e 0%, #0F172A 40%, #020617 100%);
        background-attachment: fixed;
    }
    
    .stApp, .stMarkdown, p, h1, h2, h3, h4, h5, h6, label, div, span {
        font-family: 'Outfit', sans-serif;
        color: #F8FAFC;
    }
    
    /* Micro-animations */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .block-container, 
    [data-testid="block-container"], 
    [data-testid="stMainBlockContainer"],
    [data-testid="stAppViewBlockContainer"] {
        padding-top: 2rem !important;
        padding-left: 5rem !important;
        padding-right: 5rem !important;
        max-width: none !important;
        width: 100% !important;
    }
    
    /* Typography */
    h1 {
        font-size: 2.8rem !important;
        font-weight: 800 !important;
        letter-spacing: -0.03em;
        background: linear-gradient(135deg, #38bdf8 0%, #818cf8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    h2 { font-size: 1.8rem !important; font-weight: 700 !important; color: #F1F5F9 !important; }
    h3 { font-size: 1.4rem !important; font-weight: 600 !important; color: #E2E8F0 !important; }
    
    /* Glassmorphism Cards */
    .card-panel, div[style*="background-color: #111827"] {
        background: rgba(30, 41, 59, 0.4) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 12px !important;
        padding: 1.5rem;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3) !important;
        transition: transform 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease;
    }
    .card-panel:hover {
        transform: translateY(-2px);
        border-color: rgba(14, 165, 233, 0.3) !important;
        box-shadow: 0 12px 40px 0 rgba(14, 165, 233, 0.1) !important;
    }
    
    /* Buttons */
    .stButton>button {
        background: rgba(30, 41, 59, 0.6);
        backdrop-filter: blur(8px);
        color: #F8FAFC;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
        padding: 0.5rem 1.5rem;
    }
    .stButton>button:hover {
        background: rgba(255, 255, 255, 0.1);
        border-color: rgba(255, 255, 255, 0.2);
        box-shadow: 0 0 15px rgba(255, 255, 255, 0.05);
    }
    
    /* Primary Button (Glowing Gradient) */
    .stButton>button[kind="primary"] {
        background: linear-gradient(135deg, #0284c7 0%, #3b82f6 100%);
        color: #ffffff;
        border: none;
        box-shadow: 0 4px 15px rgba(14, 165, 233, 0.4);
    }
    .stButton>button[kind="primary"]:hover {
        background: linear-gradient(135deg, #0369a1 0%, #2563eb 100%);
        box-shadow: 0 6px 20px rgba(14, 165, 233, 0.6);
        transform: translateY(-1px);
    }
    
    /* Inputs */
    .stTextInput>div>div>input, .stNumberInput>div>div>input, .stSelectbox>div>div>div, .stChatInput>div {
        background: rgba(15, 23, 42, 0.6) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 8px !important;
        color: #F8FAFC !important;
        backdrop-filter: blur(4px);
    }
    .stTextInput>div>div>input:focus, .stNumberInput>div>div>input:focus, .stSelectbox>div>div>div:focus, .stChatInput>div:focus-within {
        border-color: #38bdf8 !important;
        box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.2) !important;
    }
    
    /* Monospace for code/IDs */
    code {
        font-family: 'JetBrains Mono', monospace !important;
        background: rgba(255,255,255,0.05) !important;
        color: #7dd3fc !important;
        border-radius: 4px;
        padding: 2px 6px;
    }
    /* Status Badges (Glowing) */
    .badge {
        display: inline-flex;
        align-items: center;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        backdrop-filter: blur(4px);
    }
    .badge-allow, .badge-success, .badge-low { background: rgba(16, 185, 129, 0.1); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); box-shadow: 0 0 10px rgba(16, 185, 129, 0.2); }
    .badge-block, .badge-critical, .badge-high { background: rgba(239, 68, 68, 0.1); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3); box-shadow: 0 0 10px rgba(239, 68, 68, 0.2); }
    .badge-stop { background: rgba(148, 163, 184, 0.1); color: #cbd5e1; border: 1px solid rgba(148, 163, 184, 0.3); }
    .badge-escalate, .badge-warning, .badge-medium { background: rgba(245, 158, 11, 0.1); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3); box-shadow: 0 0 10px rgba(245, 158, 11, 0.2); }
    .badge-require_approval { background: rgba(168, 85, 247, 0.1); color: #c084fc; border: 1px solid rgba(168, 85, 247, 0.3); box-shadow: 0 0 10px rgba(168, 85, 247, 0.2); }
</style>
""", unsafe_allow_html=True)
