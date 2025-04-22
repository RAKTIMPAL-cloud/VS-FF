import streamlit as st
import os
import zipfile
import re
import shutil
from PIL import Image
import requests
from io import BytesIO

# Page configuration
st.set_page_config(page_title="Basic Streamlit Test App", layout="centered")

# Title
st.title("🚀 Welcome to My Streamlit Test App")

# Basic input/output
name = st.text_input("Enter your name:")
if name:
    st.success(f"Hello, {name}! 👋")

# Checkbox and conditional content
if st.checkbox("Show a fun fact"):
    st.info("Did you know? Streamlit was acquired by Snowflake in 2022!")

# Button interaction
if st.button("Click me"):
    st.balloons()

# Footer
st.markdown("---")
st.caption("This is a basic test app deployed via GitHub and Streamlit.")
