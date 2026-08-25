import streamlit as st
import uuid
import os
import sys
import pandas as pd
from utils.theme import apply_custom_theme
from utils.navigation import render_top_nav

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.orchestrator import WorkflowOrchestrator
from database.repositories import CaseRepository

st.set_page_config(page_title="Analyst Workspace | RecoverAI", layout="wide")
apply_custom_theme()
render_top_nav()

if 'orchestrator' not in st.session_state:
    st.session_state.orchestrator = WorkflowOrchestrator()

st.markdown("<h1>Analyst Workspace</h1>", unsafe_allow_html=True)
st.markdown("<p>Enter a new failed payment case, log your manual assessment, and compare it against RecoverAI's decision engine.</p>", unsafe_allow_html=True)

# Workflow Indicator
st.markdown("""
<div style="display: flex; justify-content: space-between; align-items: center; background-color: #1E293B; padding: 1rem 2rem; border-radius: 8px; border: 1px solid #334155; margin-bottom: 2rem;">
    <div style="text-align: center; color: #0ea5e9; font-weight: 600;">1. Case Data</div>
    <div style="color: #475569;">→</div>
    <div style="text-align: center; color: #F8FAFC; font-weight: 600;">2. Human Assessment</div>
    <div style="color: #475569;">→</div>
    <div style="text-align: center; color: #F8FAFC; font-weight: 600;">3. AI Analysis</div>
    <div style="color: #475569;">→</div>
    <div style="text-align: center; color: #F8FAFC; font-weight: 600;">4. Final Decision</div>
</div>
""", unsafe_allow_html=True)

col_input, col_result = st.columns([1, 1.2])

with col_input:
    st.markdown("<div class='card-panel'><h3 style='margin-top: 0;'>Case Entry</h3>", unsafe_allow_html=True)
    with st.form("case_entry_form"):
        st.markdown("#### Payment Details")
        tx_amt = st.number_input("Transaction Amount (₹)", min_value=0.0, value=1500.0, step=100.0)
        reason = st.selectbox("Failure Reason", ["network_error", "insufficient_funds", "card_declined", "fraud_suspected"])
        
        st.markdown("#### Customer History")
        c1, c2 = st.columns(2)
        with c1:
            prev_attempts = st.number_input("Previous Recovery Attempts", min_value=0, value=0)
            failed_pmts = st.number_input("Total Failed Payments", min_value=1, value=1)
        with c2:
            succ_pmts = st.number_input("Total Successful Payments", min_value=0, value=5)
            tenure = st.number_input("Customer Tenure (Days)", min_value=0, value=180)
            
        st.markdown("<hr style='border: 0; border-top: 1px solid #334155; margin: 1.5rem 0;'>", unsafe_allow_html=True)
        
        st.markdown("#### Your Assessment (Human)")
        human_risk = st.radio("Estimated Risk Level", ["Low Risk", "Medium Risk", "High Risk"], horizontal=True)
        human_action = st.selectbox("Proposed Action", ["SEND_PAYMENT_LINK", "WAIT", "ESCALATE_TO_HUMAN", "STOP"])
        
        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("Run RecoverAI Engine", type="primary", use_container_width=True)
        
    st.markdown("</div>", unsafe_allow_html=True)

if submitted:
    case_data = {
        "transaction_id": f"txn_{uuid.uuid4().hex[:8]}",
        "customer_id": f"cus_{uuid.uuid4().hex[:8]}",
        "transaction_amount": float(tx_amt),
        "payment_status": "failed",
        "failure_reason": reason,
        "payment_method": "credit_card",
        "successful_payments": int(succ_pmts),
        "failed_payments": int(failed_pmts),
        "total_customer_spend": 5000.0,
        "average_order_value": 1000.0,
        "previous_recovery_attempts": int(prev_attempts),
        "previous_recovery_success": 0,
        "days_since_last_purchase": 5,
        "customer_tenure_days": int(tenure),
        "already_paid": False,
        "contact_attempts": int(prev_attempts)
    }
    
    with st.spinner("Analyzing case and evaluating guardrails..."):
        case_id = CaseRepository.create_case(case_data)
        case_data["case_id"] = case_id
        
        result = st.session_state.orchestrator.process_case(case_data)
        
        CaseRepository.update_case(case_id, {
            "orchestrator_result": result,
            "status": result['guardrail_result']['decision']
        })
        
        st.session_state.last_human_risk = human_risk
        st.session_state.last_human_action = human_action
        st.session_state.last_result = result
        st.session_state.last_case_id = case_id

with col_result:
    if 'last_result' in st.session_state:
        res = st.session_state.last_result
        pred = res.get('prediction', {})
        ai_rec = res.get('ai_recommendation', {})
        guard = res.get('guardrail_result', {})
        
        decision = guard.get('decision', 'UNKNOWN')
        badge_class = f"badge-{decision.lower()}"
        
        st.markdown("<div class='card-panel'><h3 style='margin-top: 0;'>Engine Comparison</h3>", unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("<div style='background-color: #0F172A; padding: 1rem; border-radius: 6px; border: 1px solid #334155;'>", unsafe_allow_html=True)
            st.markdown("<div style='color: #94A3B8; font-size: 12px; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 8px;'>Human Assessment</div>", unsafe_allow_html=True)
            st.markdown(f"**Risk:** {st.session_state.last_human_risk}")
            st.markdown(f"**Action:** `{st.session_state.last_human_action}`")
            st.markdown("</div>", unsafe_allow_html=True)
            
        with c2:
            st.markdown("<div style='background-color: rgba(14, 165, 233, 0.1); padding: 1rem; border-radius: 6px; border: 1px solid rgba(14, 165, 233, 0.3);'>", unsafe_allow_html=True)
            st.markdown("<div style='color: #0ea5e9; font-size: 12px; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600; margin-bottom: 8px;'>RecoverAI Assessment</div>", unsafe_allow_html=True)
            prob = pred.get('recovery_probability', 0)
            ai_risk = "Low Risk" if prob > 0.6 else ("Medium Risk" if prob > 0.3 else "High Risk")
            st.markdown(f"**Risk:** {ai_risk} ({prob*100:.1f}%)")
            st.markdown(f"**Action:** `{ai_rec.get('action')}`")
            st.markdown("</div>", unsafe_allow_html=True)
            
        st.markdown("<hr style='border: 0; border-top: 1px solid #334155; margin: 1.5rem 0;'>", unsafe_allow_html=True)
        st.markdown("#### AI Reasoning")
        st.markdown(f"<p style='color: #E2E8F0; font-size: 15px;'>{ai_rec.get('reason')}</p>", unsafe_allow_html=True)
        
        st.markdown("<hr style='border: 0; border-top: 1px solid #334155; margin: 1.5rem 0;'>", unsafe_allow_html=True)
        st.markdown("#### Final Guardrail Check")
        
        st.markdown(f"""
        <div style="margin-bottom: 1.5rem; display: flex; align-items: center; gap: 1rem; background-color: #0F172A; padding: 1rem; border-radius: 6px; border: 1px solid #334155;">
            <span class="badge {badge_class}">{decision}</span>
            <span style="color: #CBD5E1; font-size: 14px;">{guard.get('reason')}</span>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("View Case Dashboard", type="primary"):
            st.session_state.selected_case_id = st.session_state.last_case_id
            st.switch_page("pages/4_Case_Details.py")
            
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="card-panel" style="height: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center; background-color: transparent !important; border: 1px dashed #475569 !important;">
            <div style="font-size: 2rem; margin-bottom: 1rem;">⚖️</div>
            <p style="color: #94A3B8; text-align: center;">Enter case details and run the engine to see the comparison.</p>
        </div>
        """, unsafe_allow_html=True)
