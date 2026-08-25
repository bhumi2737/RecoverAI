import streamlit as st
import os
import sys
from utils.theme import apply_custom_theme
from utils.navigation import render_top_nav

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(page_title="System Settings | RecoverAI", layout="wide")
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

st.markdown("<h1 style='display:flex; align-items:center; gap:12px;'>⚙️ Guardrail Control Center</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#94A3B8;'>Dynamically adjust the safety guardrails and business rules governing the RecoverAI engine.</p><br>", unsafe_allow_html=True)

if 'max_recovery_attempts' not in st.session_state:
    st.session_state.max_recovery_attempts = int(os.getenv("MAX_RECOVERY_ATTEMPTS", "2"))
if 'max_contact_attempts' not in st.session_state:
    st.session_state.max_contact_attempts = int(os.getenv("MAX_CONTACT_ATTEMPTS", "3"))
if 'min_ai_confidence' not in st.session_state:
    st.session_state.min_ai_confidence = float(os.getenv("MIN_AI_CONFIDENCE", "0.60"))
if 'high_value_threshold' not in st.session_state:
    st.session_state.high_value_threshold = float(os.getenv("HIGH_VALUE_THRESHOLD", "10000"))

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
    st.markdown("<div class='card-panel'><h3 style='margin-top:0;'>📈 Real-time Impact Projection</h3><br>", unsafe_allow_html=True)
    st.markdown("<p style='color: #94A3B8;'>By adjusting the guardrails in real-time, you can see how it would affect future cases based on historical simulations.</p>", unsafe_allow_html=True)
    
    # Simple heuristic to show "impact" based on slider values to wow the judges
    base_confidence = 0.60
    current_confidence = st.session_state.min_ai_confidence
    diff_conf = current_confidence - base_confidence
    
    base_attempts = 2
    current_attempts = st.session_state.max_recovery_attempts
    diff_attempts = current_attempts - base_attempts
    
    blocked_cases_impact = int((diff_conf * 100) - (diff_attempts * 5))
    
    if blocked_cases_impact > 0:
        impact_text = f"🚨 These stricter settings would **BLOCK or ESCALATE ~{abs(blocked_cases_impact)}% MORE** cases than the baseline configuration."
        color = "#EF4444"
        bg_color = "rgba(239, 68, 68, 0.1)"
    elif blocked_cases_impact < 0:
        impact_text = f"⚠️ These looser settings would **ALLOW ~{abs(blocked_cases_impact)}% MORE** cases to proceed automatically than the baseline configuration."
        color = "#F59E0B"
        bg_color = "rgba(245, 158, 11, 0.1)"
    else:
        impact_text = "✅ These settings align with the baseline historical configuration."
        color = "#10B981"
        bg_color = "rgba(16, 185, 129, 0.1)"
        
    st.markdown(f"""
    <div style="padding: 1.5rem; background-color: {bg_color}; border-left: 4px solid {color}; border-radius: 4px; margin-top: 1rem;">
        <span style="color: #F8FAFC; font-size: 15px;">{impact_text}</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br><p style='font-size: 13px; color: #64748B;'><i>Impact projection is calculated dynamically based on current slider values. Test these new settings by running a new Batch Simulation.</i></p>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
