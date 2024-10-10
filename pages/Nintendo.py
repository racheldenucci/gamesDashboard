import streamlit as st
import pandas as pd


st.header("Nintendo Dashboard")

df = pd.read_csv(r"vgsales.csv", encoding="utf-8")
