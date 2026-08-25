import streamlit as st
import pandas as pd
import os
import sys
from utils.theme import apply_custom_theme
from utils.navigation import render_top_nav

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.orchestrator import WorkflowOrchestrator
from database.repositories import CaseRepository

st.set_page_config(page_title="Test Multiple Cases | RecoverAI", layout="wide")
apply_custom_theme()
render_top_nav()

st.markdown("<h1>Test Multiple Recovery Cases</h1>", unsafe_allow_html=True)
st.markdown("<p><b>Generate synthetic failed-payment cases and see how RecoverAI processes them through the recovery and safety pipeline.</b></p>", unsafe_allow_html=True)

st.markdown("""
<div style="background-color: #111827; padding: 1.5rem; border-radius: 8px; border: 1px solid #1F2937; margin-bottom: 2rem;">
    <h4 style="margin-top: 0; color: #E5E7EB;">What happens when you run a simulation?</h4>
    <ol style="color: #9CA3AF; margin-bottom: 0;">
        <li>Synthetic recovery cases are generated.</li>
        <li>Each case is analyzed by the existing RecoverAI pipeline.</li>
        <li>The system evaluates the recommended action.</li>
        <li>Guardrails determine the final outcome.</li>
        <li>The results are summarized below.</li>
    </ol>
</div>
""", unsafe_allow_html=True)

if 'orchestrator' not in st.session_state:
    from services.orchestrator import WorkflowOrchestrator
    st.session_state.orchestrator = WorkflowOrchestrator()

data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "payment_recovery_data.csv")

if not os.path.exists(data_path):
    st.error("Synthetic dataset not found.")
    st.stop()

col1, col2 = st.columns([1, 2])
with col1:
    st.markdown("**Number of cases to process**")
    st.markdown("<p style='font-size: 13px; color: #9CA3AF;'>Choose how many synthetic payment recovery cases you want to test.</p>", unsafe_allow_html=True)
    num_cases = st.slider("Cases", min_value=10, max_value=200, value=50, step=10, label_visibility="collapsed")
    
if st.button("▶ Run Simulation", type="primary"):
    df = pd.read_csv(data_path)
    sample_df = df.sample(n=num_cases)
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    results = {'ALLOW': 0, 'BLOCK': 0, 'STOP': 0, 'ESCALATE': 0, 'REQUIRE_APPROVAL': 0}
    total_at_risk = 0.0
    expected_rec = 0.0
    
    processed = 0
    for _, row in sample_df.iterrows():
        case_data = {
            "transaction_id": row['transaction_id'],
            "customer_id": row['customer_id'],
            "transaction_amount": float(row['transaction_amount']),
            "payment_status": "failed",
            "failure_reason": row['failure_reason'],
            "payment_method": row['payment_method'],
            "successful_payments": int(row['successful_payments']),
            "failed_payments": int(row['failed_payments']),
            "total_customer_spend": float(row['total_customer_spend']),
            "average_order_value": float(row['average_order_value']),
            "previous_recovery_attempts": int(row['previous_recovery_attempts']),
            "previous_recovery_success": int(row['previous_recovery_success']),
            "days_since_last_purchase": int(row['days_since_last_purchase']),
            "customer_tenure_days": int(row['customer_tenure_days']),
            "already_paid": False,
            "contact_attempts": int(row['previous_recovery_attempts'])
        }
        
        case_id = CaseRepository.create_case(case_data)
        case_data["case_id"] = case_id
        
        status_text.text(f"Processing... {processed + 1}/{num_cases}")
        
        res = st.session_state.orchestrator.process_case(case_data)
        
        CaseRepository.update_case(case_id, {
            "orchestrator_result": res,
            "status": res['guardrail_result']['decision']
        })
        
        dec = res['guardrail_result']['decision']
        results[dec] = results.get(dec, 0) + 1
        
        total_at_risk += case_data['transaction_amount']
        if dec == 'ALLOW':
            expected_rec += res.get('expected_recovery_value', 0.0)
            
        processed += 1
        progress_bar.progress(processed / num_cases)
        
    status_text.text("Simulation Complete!")
    
    st.markdown("<br><h3>Simulation Results</h3>", unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style="display: flex; gap: 2rem; margin-bottom: 2rem;">
        <div>
            <div style="font-size: 13px; color: #9CA3AF; text-transform: uppercase; font-weight: bold;">Total Amount at Risk</div>
            <div style="font-size: 13px; color: #6B7280; margin-bottom: 5px;">The combined value of all failed payment cases processed in this simulation.</div>
            <div style="font-size: 24px; color: #F9FAFB;">₹{total_at_risk:,.2f}</div>
        </div>
        <div>
            <div style="font-size: 13px; color: #9CA3AF; text-transform: uppercase; font-weight: bold;">Expected Recovery</div>
            <div style="font-size: 13px; color: #6B7280; margin-bottom: 5px;">The amount currently expected to be recovered based on cases approved to proceed.</div>
            <div style="font-size: 24px; color: #10B981;">₹{expected_rec:,.2f}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("#### Decision Outcomes")
    st.markdown("""
    <ul style='color: #9CA3AF; font-size: 14px;'>
        <li>🟢 <b>Allowed</b> — Safe to proceed automatically.</li>
        <li>🔴 <b>Blocked</b> — Prevented by a safety or business rule.</li>
        <li>🟡 <b>Escalated</b> — Requires human review.</li>
        <li>🔵 <b>Stopped</b> — Safely cancelled before completion.</li>
        <li>🟣 <b>Requires Approval</b> — Waiting for additional authorization.</li>
    </ul>
    """, unsafe_allow_html=True)
    
    r_col1, r_col2, r_col3, r_col4, r_col5 = st.columns(5)
    with r_col1: st.metric("ALLOWED", results['ALLOW'])
    with r_col2: st.metric("BLOCKED", results['BLOCK'])
    with r_col3: st.metric("STOPPED", results['STOP'])
    with r_col4: st.metric("ESCALATED", results['ESCALATE'])
    with r_col5: st.metric("REQ APPROVAL", results['REQUIRE_APPROVAL'])

    if results['ALLOW'] == 0:
        st.info("These results indicate that the current cases did not meet the conditions for automatic recovery. Review the decision history to understand why cases were blocked or escalated.")
