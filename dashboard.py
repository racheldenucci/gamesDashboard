import streamlit as st
import pandas as pd
import plotly_express as px
import os

st.set_page_config(page_icon=":video_game:", page_title="Video Game Sales Dashboard")
st.title(":video_game: Video Game Sales")


df = pd.read_csv(r"vgsales.csv", encoding="utf-8")
