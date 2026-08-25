import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import sys
from utils.theme import apply_custom_theme
from utils.navigation import render_top_nav

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.repositories import CaseRepository

st.set_page_config(page_title="Home | RecoverAI", layout="wide")
apply_custom_theme()
render_top_nav()

st.markdown("<h1>Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<p>At-a-glance metrics for all recovery cases processed by the system.</p><br>", unsafe_allow_html=True)

def load_dashboard_data():
    cases = CaseRepository.get_all_cases()
    if not cases:
        st.info("No case data available. Use the Demo Scenarios in the sidebar or run a Batch Simulation.")
        return pd.DataFrame()
        
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
        
    df['recovery_prob'] = df.apply(lambda r: extract_field(r, 'prediction.recovery_probability', 0.0), axis=1)
    df['expected_value'] = df.apply(lambda r: extract_field(r, 'expected_recovery_value', 0.0), axis=1)
    df['ai_action'] = df.apply(lambda r: extract_field(r, 'ai_recommendation.action', 'N/A'), axis=1)
    df['guardrail_decision'] = df.apply(lambda r: extract_field(r, 'guardrail_result.decision', 'PENDING'), axis=1)
    
    if 'status' not in df.columns:
        df['status'] = 'PENDING'
    else:
        df['status'] = df['status'].fillna('PENDING')
        
    return df

df = load_dashboard_data()

if not df.empty:
    total_cases = len(df)
    active_cases = len(df[df['status'] == 'PENDING'])
    total_revenue_at_risk = df['transaction_amount'].sum()
    
    recovered_df = df[df['guardrail_decision'] == 'ALLOW']
    total_revenue_recovered = recovered_df['transaction_amount'].sum()
    recovery_rate = (len(recovered_df) / total_cases * 100) if total_cases > 0 else 0
    stopped_cases = len(df[df['guardrail_decision'].isin(['BLOCK', 'STOP'])])

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="card-panel"><div style="font-size:13px; color:#9CA3AF; text-transform:uppercase; margin-bottom:0.5rem;">Revenue at Risk</div><div style="font-size:28px; font-weight:600; color:#F8FAFC;">₹{total_revenue_at_risk:,.2f}</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="card-panel"><div style="font-size:13px; color:#9CA3AF; text-transform:uppercase; margin-bottom:0.5rem;">Actual Recovered</div><div style="font-size:28px; font-weight:600; color:#10B981;">₹{total_revenue_recovered:,.2f}</div></div>', unsafe_allow_html=True)
    with col3:
        total_expected_value = recovered_df['expected_value'].sum()
        st.markdown(f'<div class="card-panel"><div style="font-size:13px; color:#9CA3AF; text-transform:uppercase; margin-bottom:0.5rem;">Expected Recovery</div><div style="font-size:28px; font-weight:600; color:#0ea5e9;">₹{total_expected_value:,.2f}</div></div>', unsafe_allow_html=True)
    with col4:
        revenue_lost = df[df['guardrail_decision'].isin(['BLOCK', 'STOP'])]['transaction_amount'].sum()
        st.markdown(f'<div class="card-panel"><div style="font-size:13px; color:#9CA3AF; text-transform:uppercase; margin-bottom:0.5rem;">Revenue Stopped</div><div style="font-size:28px; font-weight:600; color:#EF4444;">₹{revenue_lost:,.2f}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Configure shared minimalist layout for Plotly
    plotly_layout = dict(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#9CA3AF'),
        margin=dict(l=20, r=20, t=40, b=20)
    )

    st.markdown("<h3 style='font-size: 16px; color: #D1D5DB; margin-bottom: 0px;'>Recovery Funnel</h3>", unsafe_allow_html=True)
    
    # Calculate Funnel Data
    ai_links = df[df['ai_action'] == 'SEND_PAYMENT_LINK']
    guardrail_allowed = ai_links[ai_links['guardrail_decision'] == 'ALLOW']
    
    funnel_data = dict(
        stage=["Total Failed Payments", "AI Recommended Action", "Guardrail Allowed (Safe)", "Expected Conversions"],
        count=[len(df), len(ai_links), len(guardrail_allowed), int(len(guardrail_allowed) * 0.4)]
    )
    fig_funnel = px.funnel(funnel_data, x='count', y='stage')
    fig_funnel.update_traces(marker=dict(color=['#374151', '#6366F1', '#10B981', '#10B981']))
    fig_funnel.update_layout(**plotly_layout, height=300)
    st.plotly_chart(fig_funnel, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.markdown("<h3 style='font-size: 16px; color: #D1D5DB;'>System Outcomes</h3>", unsafe_allow_html=True)
        outcome_counts = df['guardrail_decision'].value_counts().reset_index()
        outcome_counts.columns = ['Decision', 'Count']
        
        color_map = {
            'ALLOW': '#10B981',
            'BLOCK': '#EF4444',
            'STOP': '#6B7280',
            'ESCALATE': '#F59E0B',
            'REQUIRE_APPROVAL': '#8B5CF6',
            'PENDING': '#374151'
        }
        
        fig2 = px.pie(outcome_counts, values='Count', names='Decision', 
                      color='Decision', color_discrete_map=color_map, hole=0.6)
        fig2.update_layout(**plotly_layout, showlegend=False)
        fig2.update_traces(textposition='outside', textinfo='percent+label')
        st.plotly_chart(fig2, use_container_width=True)
        
    with col_chart2:
        st.markdown("<h3 style='font-size: 16px; color: #D1D5DB;'>Recovery by Failure Reason</h3>", unsafe_allow_html=True)
        reason_df = df.groupby('failure_reason').agg(
            total_cases=('case_id', 'count'),
            recovered=('guardrail_decision', lambda x: (x == 'ALLOW').sum())
        ).reset_index()
        
        fig3 = go.Figure(data=[
            go.Bar(name='Total Cases', y=reason_df['failure_reason'], x=reason_df['total_cases'], orientation='h', marker_color='#374151'),
            go.Bar(name='Recovered', y=reason_df['failure_reason'], x=reason_df['recovered'], orientation='h', marker_color='#6366F1')
        ])
        fig3.update_layout(**plotly_layout, barmode='group')
        st.plotly_chart(fig3, use_container_width=True)
