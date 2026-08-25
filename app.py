import streamlit as st
import os
import uuid
from typing import Dict, Any

import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.orchestrator import WorkflowOrchestrator
from database.repositories import CaseRepository
from utils.theme import apply_custom_theme

# Minimal page config (no emojis)
st.set_page_config(
    page_title="RecoverAI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_custom_theme()

st.switch_page("pages/2_Home.py")
