import streamlit as st
import pandas as pd
import plotly_express as px
import plotly.graph_objects as go
import os

st.set_page_config(page_icon=":video_game:", page_title="Video Game Sales Dashboard", layout='wide')
st.title(":video_game: Video Game Sales")

df = pd.read_csv(r"vgsales.csv", encoding="utf-8")

col1, col2 = st.columns(2)

with col1:
    top_5 = df.sort_values(by="Rank").head(5)

    st.subheader(":crown: Top Global Sales")
    st.dataframe(
        top_5.rename(
            columns={"Name": "Game", "Global_Sales": "Global Sales (milions)"}
        )[["Rank", "Game", "Publisher", "Global Sales (milions)"]],
        hide_index=True,
    )

with col2:
    top_pubs = (
        df.groupby(by="Publisher")
        .agg({"Rank": "min", "Name": "first", "Global_Sales": "sum"})
        .reset_index()
    )

    top_pubs = top_pubs.sort_values(by="Rank").head(5)

    st.subheader(":crown: Top Publishers")
    st.dataframe(
        top_pubs.rename(columns={"Global_Sales": "Global Sales (milions)"})[
            ["Rank", "Publisher", "Global Sales (milions)"]
        ],
        hide_index=True,
    )


# fig = px.bar(
#     top_5,
#     x="Name",
#     y="Global_Sales",
#     labels={"Global_Sales": "Global Sales (milions)", "Name": "Game"},
# )
# st.plotly_chart(fig)
