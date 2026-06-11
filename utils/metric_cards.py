# utils/cards.py

import streamlit as st

def metric_card(label, value, sub="", color="#FAFAFA", inline_sub=True):

    if inline_sub and sub:
        value_html = (
            f'{value}<span style="font-size:0.6em;font-weight:400;"> ({sub})</span>'
        )
        sub_html = ""
    else:
        value_html = value
        sub_html = f'<div class="sub">{sub}</div>'

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="label">{label}</div>
            <div class="value" style="color:{color};">{value_html}</div>
            {sub_html}
        </div>
        """,
        unsafe_allow_html=True
    )