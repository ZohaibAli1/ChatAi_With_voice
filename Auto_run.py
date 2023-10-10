import Clap_Detect
import streamlit_app
import subprocess

Clap_Detect()
subprocess.Popen(["streamlit", "run", "streamlit_app.py"])
streamlit_app()
