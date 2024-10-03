import streamlit as st
import pandas as pd
import numpy as np
import plotly_express as px
import plotly.graph_objects as go
import os

st.set_page_config(
    page_icon=":video_game:", page_title="Video Game Sales Dashboard", layout="wide"
)
st.title(":video_game: Video Game Sales")

df = pd.read_csv(r"vgsales.csv", encoding="utf-8")

col1, col2 = st.columns(2)

with col1:
    top_5 = (
        df.groupby(by="Name")
        .agg({"Global_Sales": "sum", "Rank": "min", "Publisher": "first"})
        .reset_index()
    )

    top_5 = top_5.sort_values(by="Global_Sales", ascending=False).head(5)

    top_5.index = np.arange(1, len(top_5) + 1)  # index starting from 1

    st.subheader(":crown: Top Global Sales")
    st.dataframe(
        top_5.rename(
            columns={"Name": "Game", "Global_Sales": "Global Sales (milions)"}
        )[["Game", "Publisher", "Global Sales (milions)"]],
    )

    top_gen = df.groupby(by="Genre").agg({"Global_Sales": "sum"}).reset_index()

    st.subheader("Genres")
    fig = px.pie(
        top_gen,
        values="Global_Sales",
        names="Genre",
        color_discrete_sequence=px.colors.sequential.ice,
    )
    st.plotly_chart(fig)


with col2:
    # top_pubs = (
    #     df.groupby(by="Publisher")
    #     .agg({"Global_Sales": "sum"})
    #     .reset_index()
    # )

    # top_pubs = top_pubs.sort_values(by="Global_Sales", ascending=False).head(5)

    # st.subheader(":crown: Top Publishers")
    # st.dataframe(
    #     top_pubs.rename(columns={"Global_Sales": "Global Sales (milions)"})[
    #         ["Publisher", "Global Sales (milions)"]
    #     ]

    # )

    st.subheader("Sales by Publisher")

    top_pubs = df.groupby(by="Publisher").agg({"Global_Sales": "sum"}).reset_index()

    top_pubs = top_pubs.sort_values(by="Global_Sales", ascending=False).head(5)

    fig = px.bar(
        top_pubs,
        y="Publisher",
        x="Global_Sales",
        labels={"Global_Sales": "Global Sales (milions)"},
        text=top_pubs["Global_Sales"].apply(
            lambda y: f"{y: .1f}"
        ),  # TODO: think of better way to show numbers in millions?
        template="plotly_dark",
    )

    fig.update_yaxes(title_text="")
    fig.update_layout(yaxis={"categoryorder": "total ascending"})

    st.plotly_chart(fig)


platf_evo = df.groupby(["Year", "Platform"]).agg({"Global_Sales": "sum"}).reset_index()

fig = px.line(
    platf_evo,
    x="Year",
    y="Global_Sales",
    color="Platform",
    labels={"Global_Sales": "Global Sales (millions)"},
    template='simple_white',
    color_discrete_sequence=px.colors.qualitative.Light24_r
)
fig.update_xaxes(title_text="")
st.plotly_chart(fig)


region = st.selectbox('Select a Region', options=['North America', 'Japan', 'Europe', 'Others'])
if(region == 'North America'):
    opt = 'NA_Sales'
elif(region == 'Japan'):
    opt = 'JP_Sales'
elif(region=='Europe'):
    opt='EU_Sales'
elif(region=='Others'):
    opt='Other_Sales'

top_pubs_filter = df.groupby(by='Publisher').agg({opt: 'sum'}).reset_index()
top_pubs_filter = top_pubs_filter.sort_values(by=opt, ascending=False).head(5)

fig = px.bar(top_pubs_filter, x='Publisher', y=opt, template='simple_white', labels={opt:region, 'Publisher':' '})
st.plotly_chart(fig)

