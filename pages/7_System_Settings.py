import streamlit as st
import os
import sys
from utils.theme import apply_custom_theme
from utils.navigation import render_top_nav

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(page_title="Guardrail Control Center | RecoverAI", layout="wide")
apply_custom_theme()
render_top_nav()

st.markdown("""
<style>
    .card-panel {
        background-color: #1E293B;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        height: 100%;
    }
    .stSlider > div > div > div > div {
        background-color: #0ea5e9 !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='display:flex; align-items:center; gap:12px;'>⚙️ AI Guardrail Control Center</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#94A3B8;'>Deterministic safety rules that validate every AI recommendation before execution.</p><br>", unsafe_allow_html=True)

if 'max_recovery_attempts' not in st.session_state:
    st.session_state.max_recovery_attempts = int(os.getenv("MAX_RECOVERY_ATTEMPTS", "2"))
if 'max_contact_attempts' not in st.session_state:
    st.session_state.max_contact_attempts = int(os.getenv("MAX_CONTACT_ATTEMPTS", "3"))
if 'min_ai_confidence' not in st.session_state:
    st.session_state.min_ai_confidence = float(os.getenv("MIN_AI_CONFIDENCE", "0.60"))
if 'high_value_threshold' not in st.session_state:
    st.session_state.high_value_threshold = float(os.getenv("HIGH_VALUE_THRESHOLD", "10000"))

st.markdown("""
<div style="background-color: rgba(16, 185, 129, 0.1); border-left: 4px solid #10B981; padding: 1rem; border-radius: 4px; margin-bottom: 2rem;">
    <div style="color: #34d399; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; font-size: 13px; margin-bottom: 4px;">SAFETY STATUS</div>
    <div style="color: #F8FAFC; font-weight: 500;">● Guardrails Active &mdash; AI recommendations require deterministic validation before execution.</div>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1.2, 1])

with col1:
    st.markdown("<div class='card-panel'><h3 style='margin-top:0;'>🛡️ Rule Configuration</h3><br>", unsafe_allow_html=True)
    
    st.slider(
        "Maximum Recovery Attempts", 
        min_value=1, max_value=10, 
        key="max_recovery_attempts",
        help="The maximum number of times we will try to recover a payment before permanently stopping."
    )
    
    st.slider(
        "Maximum Contact Attempts", 
        min_value=1, max_value=10, 
        key="max_contact_attempts",
        help="The maximum number of times we can contact the customer about a failure."
    )
    
    st.slider(
        "Minimum AI Confidence Threshold", 
        min_value=0.0, max_value=1.0, step=0.05,
        key="min_ai_confidence",
        help="If the AI's confidence in its recommendation falls below this threshold, the case is escalated to a human."
    )
    
    st.number_input(
        "High Value Transaction Threshold (₹)", 
        min_value=1000.0, step=500.0,
        key="high_value_threshold",
        help="Transactions above this amount require human approval even if the AI recommends sending a link."
    )
    
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='card-panel'><h3 style='margin-top:0;'>📈 Active Rule Impact</h3><br>", unsafe_allow_html=True)
    st.markdown("<p style='color: #94A3B8;'>The Orchestrator actively enforces these values across all incoming payment failures.</p>", unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style="padding: 1rem; background-color: #0F172A; border: 1px solid #334155; border-radius: 6px; margin-bottom: 1rem;">
        <strong style="color: #F8FAFC;">Recovery Limit:</strong><br>
        <span style="color: #94A3B8; font-size: 14px;">Any case with more than <span style="color: #38bdf8;">{st.session_state.max_recovery_attempts}</span> previous attempts will be safely blocked by the system, prioritizing customer experience.</span>
    </div>
    
    <div style="padding: 1rem; background-color: #0F172A; border: 1px solid #334155; border-radius: 6px; margin-bottom: 1rem;">
        <strong style="color: #F8FAFC;">Confidence Minimum:</strong><br>
        <span style="color: #94A3B8; font-size: 14px;">AI must have at least <span style="color: #38bdf8;">{st.session_state.min_ai_confidence*100:.0f}%</span> confidence in its recommendation. Otherwise, it will automatically escalate to a human.</span>
    </div>
    
    <div style="padding: 1rem; background-color: #0F172A; border: 1px solid #334155; border-radius: 6px;">
        <strong style="color: #F8FAFC;">Value Approval:</strong><br>
        <span style="color: #94A3B8; font-size: 14px;">Payments exceeding <span style="color: #38bdf8;">₹{st.session_state.high_value_threshold:,.2f}</span> cannot be autonomously recovered and will always require an analyst's sign-off.</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
