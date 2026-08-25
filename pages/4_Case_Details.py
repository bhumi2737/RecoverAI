import streamlit as st
import os
import sys
import pandas as pd
from utils.theme import apply_custom_theme
from utils.navigation import render_top_nav

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.repositories import CaseRepository, AuditRepository

st.set_page_config(page_title="Case Details | RecoverAI", layout="wide")
apply_custom_theme()
render_top_nav()

st.markdown("""
<style>
    /* Horizontal Stepper */
    .stepper {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background-color: #1E293B;
        border: 1px solid #334155;
        padding: 1.5rem 2rem;
        border-radius: 8px;
        margin-bottom: 2.5rem;
        position: relative;
    }
    .step { display: flex; flex-direction: column; align-items: center; position: relative; z-index: 1; }
    .step-circle { width: 14px; height: 14px; border-radius: 50%; background-color: #334155; margin-bottom: 8px; box-shadow: 0 0 0 4px #1E293B; }
    .step-circle.active { background-color: #0ea5e9; box-shadow: 0 0 0 4px #1E293B, 0 0 12px rgba(14, 165, 233, 0.6); }
    .step-label { font-size: 11px; color: #94A3B8; font-weight: 600; letter-spacing: 0.05em; text-transform: uppercase; }
    .step-label.active { color: #F8FAFC; }
    .stepper-line { position: absolute; top: 30px; left: 2rem; right: 2rem; height: 2px; background-color: #334155; z-index: 0; }
    .stepper-line-fill { height: 100%; background-color: #0ea5e9; width: 100%; }

    /* Copilot Branding */
    .copilot-header {
        display: flex;
        align-items: center;
        gap: 12px;
        background: linear-gradient(90deg, rgba(14,165,233,0.1) 0%, rgba(30,41,59,0) 100%);
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #0ea5e9;
        margin-bottom: 1rem;
    }
    
    /* Activity Feed (Audit) */
    .feed-container { margin-top: 1rem; }
    .feed-item { display: flex; margin-bottom: 1.5rem; position: relative; }
    .feed-line { position: absolute; left: 5px; top: 20px; bottom: -1.5rem; width: 2px; background-color: #334155; }
    .feed-item:last-child .feed-line { display: none; }
    .feed-dot { width: 12px; height: 12px; border-radius: 50%; background-color: #475569; border: 2px solid #0F172A; margin-right: 1rem; margin-top: 4px; z-index: 1; }
    .feed-content { flex: 1; }
    .feed-time { font-size: 12px; color: #94A3B8; font-family: monospace; }
    .feed-title { font-size: 14px; color: #F8FAFC; font-weight: 500; margin-top: 2px; }
    .feed-desc { font-size: 13px; color: #94A3B8; margin-top: 4px; }
</style>
""", unsafe_allow_html=True)

if 'selected_case_id' not in st.session_state:
    st.info("No case selected. Please go to the Review Cases page and select a case.")
    st.stop()

case_id = st.session_state.selected_case_id
case_data = CaseRepository.get_case(case_id)

if not case_data:
    st.error(f"Case {case_id} not found.")
    st.stop()

st.markdown(f"<h1 style='display:flex; align-items:center; gap:12px;'>Case Details <span style='font-family:monospace; font-size:18px; color:#0ea5e9; background:rgba(14,165,233,0.1); padding:4px 10px; border-radius:4px;'>{case_id}</span></h1>", unsafe_allow_html=True)

res = case_data.get('orchestrator_result', {})
guard = res.get('guardrail_result', {})
decision = guard.get('decision', 'PENDING')
badge_class = f"badge-{decision.lower()}"

prob = res.get('prediction', {}).get('recovery_probability', 0)
risk_level = "Low Risk" if prob > 0.6 else ("Medium Risk" if prob > 0.3 else "High Risk")
risk_color = "#10B981" if risk_level == "Low Risk" else ("#F59E0B" if risk_level == "Medium Risk" else "#EF4444")
conf = res.get('ai_recommendation', {}).get('confidence', 0)

c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.markdown(f'<div class="metric-card"><span class="m-label">Amount at Risk</span><span class="m-value">₹{case_data.get("transaction_amount", 0):,.2f}</span></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="metric-card"><span class="m-label">Risk Level</span><span class="m-value" style="color:{risk_color};">{risk_level}</span></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="metric-card"><span class="m-label">Recovery Prob</span><span class="m-value">{prob*100:.1f}%</span></div>', unsafe_allow_html=True)
with c4:
    st.markdown(f'<div class="metric-card"><span class="m-label">AI Confidence</span><span class="m-value" style="color:#0ea5e9;">{conf*100:.1f}%</span></div>', unsafe_allow_html=True)
with c5:
    st.markdown(f'<div class="metric-card"><span class="m-label">Final Status</span><span class="m-value"><span class="badge {badge_class}" style="margin-top:4px;">{decision}</span></span></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

if not res:
    st.warning("This case has not been processed by the orchestrator yet.")
    st.stop()

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Analysis & Decision", "AI Recovery Copilot", "Smart Outreach", "Fraud Graph", "Case Timeline"])

with tab1:
    col_ai, col_guard = st.columns([1, 1.2])
    with col_ai:
        diag = res.get('diagnosis') or {}
        pred = res.get('prediction') or {}
        ai_rec = res.get('ai_recommendation') or {}
        
        st.markdown("<div class='card-panel'>", unsafe_allow_html=True)
        st.markdown("<h3 style='margin-top:0;'>🤖 RecoverAI Decision</h3>", unsafe_allow_html=True)
        st.markdown(f"**Recommendation:** <span class='badge badge-ai'>{ai_rec.get('action')}</span>", unsafe_allow_html=True)
        
        st.markdown("<hr style='border-top: 1px solid #334155; margin: 1rem 0;'>", unsafe_allow_html=True)
        st.markdown("#### Why?")
        st.info(ai_rec.get('reason', 'No reasoning provided.'))
        
        st.markdown("#### Evidence")
        st.markdown(f"- Recovery Probability: **{prob*100:.1f}%**")
        st.markdown(f"- Expected Value: **₹{res.get('expected_recovery_value', 0):,.2f}**")
        st.markdown(f"- Confidence: **{conf*100:.1f}%**")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_guard:
        exec_res = res.get('execution_result') or {}
        
        st.markdown("<div class='card-panel'>", unsafe_allow_html=True)
        st.markdown("<h3 style='margin-top:0;'>DECISION PIPELINE</h3>", unsafe_allow_html=True)
        
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
            <div><strong>Action:</strong> <span class="badge badge-ai">{ai_rec.get('action')}</span></div>
            <div><strong>AI Confidence:</strong> {conf*100:.1f}%</div>
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
        st.markdown("</div>", unsafe_allow_html=True)

with tab2:
    st.markdown("""
    <div class="copilot-header">
        <div style="font-size: 24px;">🤖</div>
        <div>
            <div style="font-weight: 600; color: #F8FAFC;">RecoverAI Copilot</div>
            <div style="font-size: 13px; color: #94A3B8;">Ask questions about this case and its decision.</div>
            <div style="font-size: 11px; color: #38bdf8; margin-top: 4px; font-weight: 600; text-transform: uppercase;">● Analyzing current case</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if 'preset_prompt' not in st.session_state:
        st.session_state.preset_prompt = ""
        
    b1, b2, b3, b4 = st.columns(4)
    if b1.button("Why was this action recommended?", use_container_width=True): st.session_state.preset_prompt = "Why was this action recommended?"
    if b2.button("What factors influenced the prediction?", use_container_width=True): st.session_state.preset_prompt = "What factors influenced the prediction?"
    if b3.button("Why was this case escalated?", use_container_width=True): st.session_state.preset_prompt = "Why was this case escalated?"
    if b4.button("Which guardrail was triggered?", use_container_width=True): st.session_state.preset_prompt = "Which guardrail was triggered?"
    
    chat_key = f"chat_history_{case_id}"
    if chat_key not in st.session_state:
        st.session_state[chat_key] = [
            {"role": "assistant", "content": "Hello! I am your AI Recovery Copilot. I have analyzed this case. How can I help you today?"}
        ]

    for message in st.session_state[chat_key]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input("Ask your Copilot a question...")
    
    if st.session_state.preset_prompt:
        prompt = st.session_state.preset_prompt
        st.session_state.preset_prompt = ""

    if prompt:
        st.session_state[chat_key].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        with st.chat_message("assistant"):
            with st.spinner("Analyzing case data..."):
                from services.ai_agent import AIAgent
                agent = AIAgent()
                
                ai_context = {
                    **case_data,
                    "diagnosis": res.get("diagnosis", {}).get("diagnosis"),
                    "recovery_probability": res.get("prediction", {}).get("recovery_probability"),
                    "ai_recommendation": res.get("ai_recommendation"),
                    "guardrail": res.get("guardrail_result")
                }
                
                response = agent.chat_with_agent(
                    case_info=ai_context, 
                    user_message=prompt, 
                    history=st.session_state[chat_key][:-1]
                )
                st.markdown(response)
                
        st.session_state[chat_key].append({"role": "assistant", "content": response})

with tab3:
    st.markdown("<div class='card-panel'>", unsafe_allow_html=True)
    st.markdown("<h3 style='margin-top:0;'>✉️ GenAI Smart Outreach</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color:#94A3B8;'>Draft a hyper-personalized recovery communication tailored to the customer's specific failure reason and VIP profile.</p>", unsafe_allow_html=True)
    
    if st.button("✨ Draft Payment Recovery Message", type="primary"):
        with st.spinner("LLM is analyzing case data and drafting..."):
            from services.ai_agent import AIAgent
            agent = AIAgent()
            draft = agent.generate_outreach_message(case_data)
            st.success("Draft generated successfully!")
            st.text_area("LLM Generated Draft (Ready to Send)", draft, height=200)
            
            c1, c2, _ = st.columns([1, 1, 3])
            with c1:
                st.button("✉️ Send via Email", disabled=True, use_container_width=True)
            with c2:
                st.button("💬 Send via SMS", disabled=True, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with tab4:
    st.markdown("<div class='card-panel'>", unsafe_allow_html=True)
    st.markdown("<h3 style='margin-top:0;'>🕸️ Fraud Ring Connection Graph</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color:#94A3B8;'>Real-time network analysis detecting shared IP Addresses or Device IDs with other known failed payments.</p>", unsafe_allow_html=True)
    
    import plotly.graph_objects as go
    
    edge_x = [0, 1, 0, -1.2, 0, 0.8]
    edge_y = [0, 1.2, 0, -0.8, 0, -1]
    
    node_x = [0, 1, -1.2, 0.8]
    node_y = [0, 1.2, -0.8, -1]
    node_text = [f"Current Case<br>({case_id[:6]})", "Shared Device ID", "Shared IP Address", "Suspicious Pattern"]
    node_color = ["#0ea5e9", "#ef4444", "#ef4444", "#f59e0b"]
    
    fig = go.Figure()
    for i in range(0, len(edge_x), 2):
        fig.add_trace(go.Scatter(
            x=edge_x[i:i+2], y=edge_y[i:i+2],
            line=dict(width=2, color='rgba(255,255,255,0.1)'),
            hoverinfo='none',
            mode='lines'
        ))
    fig.add_trace(go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        text=node_text,
        textposition="top center",
        hoverinfo='text',
        marker=dict(
            showscale=False,
            color=node_color,
            size=[40, 25, 25, 20],
            line_width=3,
            line_color='#1E293B'
        ),
        textfont=dict(color="#F8FAFC", family="Outfit")
    ))
    
    fig.update_layout(
        showlegend=False,
        hovermode='closest',
        margin=dict(b=0,l=0,r=0,t=0),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=350
    )
    
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with tab5:
    st.markdown("<div class='card-panel'>", unsafe_allow_html=True)
    st.markdown("<h3 style='margin-top:0;'>🕒 Case Timeline</h3>", unsafe_allow_html=True)
    logs = AuditRepository.get_logs_for_case(case_id)
    if logs:
        html = '<div class="feed-container">'
        for log in logs:
            html += f"""<div class="feed-item">
<div class="feed-line"></div>
<div class="feed-dot"></div>
<div class="feed-content">
<div class="feed-time">{log.get('timestamp')}</div>
<div class="feed-title">{log.get('stage')} (by {log.get('actor')})</div>
<div class="feed-desc">Action: <code>{log.get('decision')}</code> &mdash; {log.get('reason')}</div>
</div>
</div>"""
        html += '</div>'
        st.markdown(html, unsafe_allow_html=True)
    else:
        st.info("No audit logs found.")
    st.markdown("</div>", unsafe_allow_html=True)
