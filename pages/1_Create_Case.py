import streamlit as st
import uuid
import os
import sys
import pandas as pd
import time
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
st.markdown("<p>Evaluate a payment recovery case with human judgment and RecoverAI.</p>", unsafe_allow_html=True)

# Workflow Indicator
st.markdown("""
<div style="display: flex; justify-content: space-between; align-items: center; background-color: #1E293B; padding: 1rem 2rem; border-radius: 8px; border: 1px solid #334155; margin-bottom: 2rem;">
    <div style="text-align: center; color: #0ea5e9; font-weight: 600;">01 Case Data</div>
    <div style="color: #475569;">→</div>
    <div style="text-align: center; color: #F8FAFC; font-weight: 600;">02 Human Assessment</div>
    <div style="color: #475569;">→</div>
    <div style="text-align: center; color: #F8FAFC; font-weight: 600;">03 AI Analysis</div>
    <div style="color: #475569;">→</div>
    <div style="text-align: center; color: #F8FAFC; font-weight: 600;">04 Guardrail Decision</div>
</div>
""", unsafe_allow_html=True)

col_input, col_result = st.columns([1, 1.2])

with col_input:
    st.markdown("<div class='card-panel'><h3 style='margin-top: 0;'>Case Entry</h3>", unsafe_allow_html=True)
    with st.form("case_entry_form"):
        st.markdown("#### CUSTOMER")
        c1, c2 = st.columns(2)
        with c1:
            tenure = st.number_input("Customer Tenure (Days)", min_value=0, value=180)
            succ_pmts = st.number_input("Total Successful Payments", min_value=0, value=5)
        with c2:
            failed_pmts = st.number_input("Total Failed Payments", min_value=1, value=1)
            
        st.markdown("#### PAYMENT")
        c3, c4 = st.columns(2)
        with c3:
            tx_amt = st.number_input("Transaction Amount (₹)", min_value=0.0, value=1500.0, step=100.0)
            days_since = st.number_input("Days Since Last Purchase", min_value=0, value=5)
        with c4:
            reason = st.selectbox("Failure Reason", ["network_error", "insufficient_funds", "card_declined", "fraud_suspected"])
            payment_method = st.selectbox("Payment Method", ["credit_card", "upi", "net_banking"])
            
        st.markdown("#### RECOVERY HISTORY")
        c5, c6 = st.columns(2)
        with c5:
            prev_attempts = st.number_input("Previous Recovery Attempts", min_value=0, value=0)
            contact_attempts = st.number_input("Contact Attempts", min_value=0, value=0)
        with c6:
            already_paid = st.checkbox("Already Paid?", value=False)
            
        st.markdown("<hr style='border: 0; border-top: 1px solid #334155; margin: 1.5rem 0;'>", unsafe_allow_html=True)
        
        st.markdown("#### HUMAN ASSESSMENT")
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
        "payment_method": payment_method,
        "successful_payments": int(succ_pmts),
        "failed_payments": int(failed_pmts),
        "total_customer_spend": 5000.0,
        "average_order_value": 1000.0,
        "previous_recovery_attempts": int(prev_attempts),
        "previous_recovery_success": 0,
        "days_since_last_purchase": int(days_since),
        "customer_tenure_days": int(tenure),
        "already_paid": already_paid,
        "contact_attempts": int(contact_attempts)
    }
    
    progress_placeholder = st.empty()
    with progress_placeholder.container():
        st.info("RecoverAI is analyzing this case...\n\n✓ Diagnosing payment failure\n\n○ Estimating recovery probability")
        
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
    progress_placeholder.empty()

with col_result:
    if 'last_result' in st.session_state:
        res = st.session_state.last_result
        diag = res.get('diagnosis') or {}
        pred = res.get('prediction') or {}
        ai_rec = res.get('ai_recommendation') or {}
        guard = res.get('guardrail_result') or {}
        exec_res = res.get('execution_result') or {}
        
        prob = pred.get('recovery_probability', 0.0)
        ai_risk = "Low Risk" if prob > 0.6 else ("Medium Risk" if prob > 0.3 else "High Risk")
        ai_action = ai_rec.get('action', 'UNKNOWN')
        ai_conf = ai_rec.get('confidence', 0.0)
        
        decision = guard.get('decision', 'UNKNOWN')
        badge_class = f"badge-{decision.lower()}"
        
        # Agreement logic
        human_risk = st.session_state.last_human_risk
        human_action = st.session_state.last_human_action
        risk_aligned = (human_risk == ai_risk)
        action_aligned = (human_action == ai_action)
        
        st.markdown("<div class='card-panel' style='padding-top: 1rem;'>", unsafe_allow_html=True)
        if risk_aligned and action_aligned:
            st.markdown("""<div style="background-color: rgba(16, 185, 129, 0.1); border-left: 4px solid #10B981; padding: 1rem; border-radius: 4px; margin-bottom: 1rem;">
                <span style="color: #34d399; font-weight: 600;">✓ Human and AI assessment aligned</span>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown("""<div style="background-color: rgba(245, 158, 11, 0.1); border-left: 4px solid #F59E0B; padding: 1rem; border-radius: 4px; margin-bottom: 1rem;">
                <span style="color: #fbbf24; font-weight: 600;">⚠ Human and AI assessment differ</span>
            </div>""", unsafe_allow_html=True)

        st.markdown("""
        <table class="comparison-table">
            <tr>
                <th style="width: 50%;">HUMAN</th>
                <th style="width: 50%;" class="ai-col">RECOVERAI</th>
            </tr>
            <tr>
                <td><strong>Risk:</strong> {}</td>
                <td class="ai-col"><strong>Risk:</strong> {}</td>
            </tr>
            <tr>
                <td><strong>Recommended Action:</strong><br><code>{}</code></td>
                <td class="ai-col"><strong>Recommended Action:</strong><br><code style="color: #38bdf8;">{}</code></td>
            </tr>
            <tr>
                <td></td>
                <td class="ai-col"><strong>Confidence:</strong> {:.1f}%<br><strong>Recovery Probability:</strong> {:.1f}%</td>
            </tr>
        </table>
        """.format(
            human_risk, ai_risk,
            human_action, ai_action,
            ai_conf * 100, prob * 100
        ), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<h3 style='margin-top: 1rem; font-size: 16px;'>DECISION PIPELINE</h3>", unsafe_allow_html=True)
        
        # 1. DIAGNOSIS
        st.markdown(f"""
        <div class="pipeline-stage">
            <div class="pipeline-title">1. DIAGNOSIS</div>
            <div><strong>Result:</strong> {diag.get('diagnosis', 'N/A')}</div>
            <div><strong>Confidence:</strong> {diag.get('confidence', 0)*100:.1f}%</div>
        </div>
        <div class="pipeline-arrow">↓</div>
        """, unsafe_allow_html=True)
        
        # 2. ML PREDICTION
        st.markdown(f"""
        <div class="pipeline-stage">
            <div class="pipeline-title">2. ML PREDICTION</div>
            <div><strong>Recovery Probability:</strong> {prob*100:.1f}%</div>
            <div><span style="color:#94A3B8; font-size: 13px;">Model: {pred.get('model_version', 'Unknown')}</span></div>
        </div>
        """, unsafe_allow_html=True)
        
        model_sig = pred.get('model_signal')
        if model_sig and isinstance(model_sig, list):
            with st.expander("Why did the model predict this?"):
                st.markdown("<p style='font-size: 13px; color: #94A3B8;'>Model signals indicate statistical influence, not causation.</p>", unsafe_allow_html=True)
                for item in model_sig:
                    k = item.get("Feature", "Unknown")
                    v = item.get("Coefficient", 0)
                    color = "#10B981" if v > 0 else "#EF4444"
                    st.markdown(f"- **{k}:** <span style='color:{color};'>{v:.4f}</span>", unsafe_allow_html=True)

        st.markdown("<div class='pipeline-arrow'>↓</div>", unsafe_allow_html=True)

        # 3. AI RECOMMENDATION
        st.markdown(f"""
        <div class="pipeline-stage">
            <div class="pipeline-title">3. AI RECOMMENDATION</div>
            <div><strong>Action:</strong> <span class="badge badge-ai">{ai_action}</span></div>
            <div><strong>AI Confidence:</strong> {ai_conf*100:.1f}%</div>
            <div style="margin-top: 8px; color: #CBD5E1; font-size: 14px;"><strong>Reason:</strong> {ai_rec.get('reason')}</div>
        </div>
        <div class="pipeline-arrow">↓</div>
        """, unsafe_allow_html=True)
        
        # 4. GUARDRAIL VALIDATION
        rules = guard.get('rules_triggered', [])
        rules_text = ", ".join([f"`{r}`" for r in rules]) if rules else "None"
        st.markdown(f"""
        <div class="pipeline-stage">
            <div class="pipeline-title">4. GUARDRAIL VALIDATION</div>
            <div><strong>Decision:</strong> <span class="badge {badge_class}">{decision}</span></div>
            <div><strong>Rules Triggered:</strong> {rules_text}</div>
            <div style="margin-top: 8px; color: #CBD5E1; font-size: 14px;"><strong>Reason:</strong> {guard.get('reason')}</div>
        </div>
        <div class="pipeline-arrow">↓</div>
        """, unsafe_allow_html=True)
        
        # 5. FINAL DECISION
        exec_status = exec_res.get('status', 'PENDING').upper()
        st.markdown(f"""
        <div class="pipeline-stage" style="border-color: #38bdf8;">
            <div class="pipeline-title" style="color: #38bdf8;">5. FINAL DECISION</div>
            <div><strong>Execution Status:</strong> {exec_status}</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("View Case Dashboard", type="primary"):
            st.session_state.selected_case_id = st.session_state.last_case_id
            st.switch_page("pages/4_Case_Details.py")
            
    else:
        st.markdown("""
        <div class="card-panel" style="height: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center; background-color: transparent !important; border: 1px dashed #475569 !important;">
            <div style="font-size: 2rem; margin-bottom: 1rem;">⚖️</div>
            <p style="color: #94A3B8; text-align: center;">Enter case details and run the engine to see the comparison.</p>
        </div>
        """, unsafe_allow_html=True)
