import streamlit as st
import pandas as pd
import os
import sys
from utils.theme import apply_custom_theme
from utils.navigation import render_top_nav

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.repositories import CaseRepository

st.set_page_config(page_title="Review Cases | RecoverAI", layout="wide")
apply_custom_theme()
render_top_nav()

st.markdown("<h1>Review Recovery Cases</h1>", unsafe_allow_html=True)
st.markdown("<p>Explore individual failed-payment cases and understand how RecoverAI reached each decision.</p>", unsafe_allow_html=True)

st.markdown("""
<div style="background-color: #111827; padding: 1rem; border-radius: 8px; border: 1px solid #1F2937; margin-bottom: 2rem;">
    <h4 style="margin-top: 0; color: #E5E7EB; font-size: 14px;">What can I do here?</h4>
    <ul style="color: #9CA3AF; font-size: 14px; margin-bottom: 0;">
        <li>Select a case below</li>
        <li>Review its payment and risk information</li>
        <li>See the predicted recovery potential</li>
        <li>Understand the recommended action</li>
        <li>Check the final decision and safety checks</li>
    </ul>
</div>
""", unsafe_allow_html=True)

cases = CaseRepository.get_all_cases()

if not cases:
    st.info("No cases found in the database. Head over to **Try Example Scenarios** in the sidebar or go to **Test Multiple Cases** to generate some data.")
else:
    df = pd.DataFrame(cases)
    if 'case_id' not in df.columns and '_id' in df.columns:
        df['case_id'] = df['_id'].astype(str)
        
    def extract_field(row, field_path, default=None):
        if 'orchestrator_result' in row and isinstance(row['orchestrator_result'], dict):
            res = row['orchestrator_result']
            parts = field_path.split('.')
            for part in parts:
                if res and isinstance(res, dict) and part in res:
                    res = res[part]
                else:
                    return default
            return res
        return default
        
    df['Recovery Probability'] = df.apply(lambda r: extract_field(r, 'prediction.recovery_probability', 0.0), axis=1)
    df['AI Recommendation'] = df.apply(lambda r: extract_field(r, 'ai_recommendation.action', 'N/A'), axis=1)
    df['Guardrail Decision'] = df.apply(lambda r: extract_field(r, 'guardrail_result.decision', 'PENDING'), axis=1)
    
    if 'status' not in df.columns:
        df['Status'] = 'PENDING'
    else:
        df['Status'] = df['status'].fillna('PENDING')
        
    df['Amount at Risk'] = df['transaction_amount'].apply(lambda x: f"₹{x:,.2f}")
    df['Case ID'] = df['case_id'].apply(lambda x: x[:8] + "...")
    
    display_df = df[['Case ID', 'customer_id', 'Amount at Risk', 'failure_reason', 
                     'Recovery Probability', 'AI Recommendation', 'Guardrail Decision', 'Status', 'case_id']]
    display_df.columns = ['Case ID', 'Customer', 'Amount at Risk', 'Failure Reason', 
                          'Recovery Probability', 'AI Recommendation', 'Guardrail Decision', 'Status', 'full_case_id']
                          
    display_df['Recovery Probability'] = display_df['Recovery Probability'].apply(lambda x: f"{x*100:.1f}%")

    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.multiselect("Status", display_df['Status'].unique())
    with col2:
        reason_filter = st.multiselect("Failure Reason", display_df['Failure Reason'].unique())
    with col3:
        guardrail_filter = st.multiselect("Guardrail Decision", display_df['Guardrail Decision'].unique())
        
    filtered_df = display_df.copy()
    if status_filter:
        filtered_df = filtered_df[filtered_df['Status'].isin(status_filter)]
    if reason_filter:
        filtered_df = filtered_df[filtered_df['Failure Reason'].isin(reason_filter)]
    if guardrail_filter:
        filtered_df = filtered_df[filtered_df['Guardrail Decision'].isin(guardrail_filter)]

    st.dataframe(
        filtered_df.drop('full_case_id', axis=1), 
        use_container_width=True,
        hide_index=True
    )
    
    st.markdown("<br><hr style='border-top: 1px solid #1F2937;'><br>", unsafe_allow_html=True)
    st.markdown("<h3>Inspect Case Details</h3>", unsafe_allow_html=True)
    
    def format_case_option(case_id):
        row = filtered_df[filtered_df['full_case_id'] == case_id].iloc[0]
        customer = row['Customer']
        amount = row['Amount at Risk']
        return f"Customer: {customer} | {amount} (Case: {case_id[:8]}...)"

    col_sel, col_btn = st.columns([3, 1])
    with col_sel:
        selected_case = st.selectbox(
            "Select a Case", 
            filtered_df['full_case_id'].tolist(), 
            format_func=format_case_option,
            label_visibility="collapsed"
        )
    with col_btn:
        if st.button("View Details", key=f"btn_{selected_case}", type="primary", use_container_width=True):
            st.session_state.selected_case_id = selected_case
            st.switch_page("pages/4_Case_Details.py")
