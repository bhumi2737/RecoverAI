import streamlit as st

def render_top_nav():
    st.markdown("""
        <style>
        .top-nav-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-top: -2.5rem;
            margin-bottom: 1.5rem;
            padding: 1rem 2rem;
            background: rgba(15, 23, 42, 0.7);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border-radius: 16px;
            border: 1px solid rgba(255,255,255,0.05);
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
            animation: slideDown 0.5s cubic-bezier(0.16, 1, 0.3, 1);
        }
        
        @keyframes slideDown {
            from { opacity: 0; transform: translateY(-20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .nav-logo {
            font-size: 1.8rem;
            font-weight: 800;
            color: #F8FAFC;
            letter-spacing: -0.05em;
            background: linear-gradient(to right, #ffffff, #94a3b8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .nav-logo span {
            background: linear-gradient(135deg, #38bdf8 0%, #3b82f6 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        /* Make page links look like slick pills */
        [data-testid="stPageLink-NavLink"] {
            text-decoration: none !important;
            font-weight: 600 !important;
            font-size: 14px !important;
            color: #94A3B8 !important;
            padding: 0.6rem 1.2rem !important;
            border-radius: 99px !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            background: transparent !important;
            border: 1px solid transparent !important;
            text-align: center !important;
            position: relative;
            z-index: 9999;
            pointer-events: auto !important;
        }
        [data-testid="stPageLink-NavLink"]:hover {
            color: #38bdf8 !important;
            background: rgba(56, 189, 248, 0.1) !important;
            border: 1px solid rgba(56, 189, 248, 0.2) !important;
            transform: translateY(-1px) !important;
        }
        </style>
        <div class="top-nav-header">
            <div class="nav-logo">RECOVER<span>AI</span></div>
            <!-- Note: Streamlit columns handle the rest -->
        </div>
    """, unsafe_allow_html=True)
    
    cols = st.columns([1, 1.2, 1, 1.5, 1, 1.2, 2])
    with cols[0]:
        st.page_link("pages/2_Home.py", label="Home")
    with cols[1]:
        st.page_link("pages/1_Create_Case.py", label="Create Case")
    with cols[2]:
        st.page_link("pages/3_Review_Cases.py", label="Cases")
    with cols[3]:
        st.page_link("pages/6_Decision_History.py", label="Decision History")
    with cols[4]:
        st.page_link("pages/7_System_Settings.py", label="Guardrails")
    with cols[5]:
        st.page_link("pages/5_Test_Multiple_Cases.py", label="Simulate")
        
    st.markdown("<hr style='border: 0; height: 1px; background: rgba(255,255,255,0.1); margin-top: 0.5rem; margin-bottom: 2rem;'>", unsafe_allow_html=True)
