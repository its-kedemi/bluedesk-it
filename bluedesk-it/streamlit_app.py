"""Preview of the BlueDesk IT website inside Streamlit.

This only displays the page. Streamlit can't run the contact-form handler,
so the form will not send mail here. Use the Render deployment for the live site.
"""
import pathlib

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="BlueDesk IT", layout="wide")
st.markdown("<style>header,footer{visibility:hidden}.block-container{padding:0}</style>", unsafe_allow_html=True)
html = (pathlib.Path(__file__).parent / "index.html").read_text(encoding="utf-8")
components.html(html, height=4200, scrolling=True)
