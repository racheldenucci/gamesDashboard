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
st.title("")


df = pd.read_csv(r"vgsales.csv", encoding="utf-8")

col1, col2 = st.columns(2)

with col1:
    top_5 = (
        df.groupby(by="Name")
        .agg({"Global_Sales": "sum", "Rank": "min", "Publisher": "first"})
        .reset_index()
    )

    top_5 = top_5.sort_values(by="Global_Sales", ascending=False).head(10)
    top_5.index = np.arange(1, len(top_5) + 1)  # index starting from 1

    st.subheader(":crown: Top Global Sales")
    st.write("Sales (millions)")
    st.dataframe(
        top_5.rename(columns={"Name": "Game", "Global_Sales": "Global Sales"})[
            ["Game", "Publisher", "Global Sales"]
        ]
    )

    st.header("")

    # TOP GAMES PER PLATFORM
    st.subheader("Top Sales per Platform")
    plat = st.selectbox("Select a Platform", options=df["Platform"].unique())
    top_5_plat = (
        df[df["Platform"] == plat]
        .sort_values(by="Global_Sales", ascending=False)
        .head(5)
    )

    fig = px.bar(
        top_5_plat,
        y="Global_Sales",
        x="Name",
        labels={"Global_Sales": "Sales", "Name": ""},
        template="plotly_dark",
        text=top_5_plat["Global_Sales"].apply(lambda y: f"{y: .1f}M"),
    )

    st.plotly_chart(fig)


regions = ["NA_Sales", "JP_Sales", "EU_Sales", "Other_Sales"]

with col2:
    st.subheader("Sales by Publisher")

    top_pubs = df.groupby(by="Publisher").agg({"Global_Sales": "sum"}).reset_index()
    top_pubs = top_pubs.sort_values(by="Global_Sales", ascending=False).head(5)

    fig = px.bar(
        top_pubs,
        y="Publisher",
        x="Global_Sales",
        labels={"Global_Sales": "Global Sales", "Publisher": ""},
        text=top_pubs["Global_Sales"].apply(
            lambda y: f"{y: .1f}M"
        ),  # TODO: think of better way to show numbers in millions?
        template="plotly_dark",
    )

    fig.update_layout(yaxis={"categoryorder": "total ascending"})

    st.plotly_chart(fig)

    st.subheader("")
    top_gen = df.groupby(by="Genre").agg({"Global_Sales": "sum"}).reset_index()

    st.subheader("Sales by Genres")
    fig = px.pie(
        top_gen,
        values="Global_Sales",
        names="Genre",
        color_discrete_sequence=px.colors.sequential.ice,
    )
    st.plotly_chart(fig)


# PLATFORM GAME SALES THROUGH TIME
platf_evo = df.groupby(["Year", "Platform"]).agg({"Global_Sales": "sum"}).reset_index()

fig = px.line(
    platf_evo,
    x="Year",
    y="Global_Sales",
    color="Platform",
    labels={"Global_Sales": "Global Sales (millions)", "Year": ""},
    template="simple_white",
    line_shape="spline",
    color_discrete_sequence=px.colors.qualitative.Light24_r,
)

st.plotly_chart(fig)


col1, col2 = st.columns(2)

with col1:
    region = st.selectbox(
        "Select a Region", options=["North America", "Japan", "Europe", "Others"]
    )
    if region == "North America":
        opt = "NA_Sales"
    elif region == "Japan":
        opt = "JP_Sales"
    elif region == "Europe":
        opt = "EU_Sales"
    elif region == "Others":
        opt = "Other_Sales"

    st.subheader(f"Best Selling in {region}")
    st.write("Sales (millions of copies)")

    top_5_reg_filt = (
        df.groupby(by="Name").agg({opt: "sum", "Publisher": "first"}).reset_index()
    )
    top_5_filter = top_5_reg_filt.sort_values(by=opt, ascending=False).head(5)
    top_5_filter.index = np.arange(1, len(top_5_filter) + 1)

    st.dataframe(top_5_filter.rename(columns={"Name": "Game", opt: f"{region} Sales"}))

with col2:
    st.header("")
    top_pubs_filter = df.groupby(by="Publisher").agg({opt: "sum"}).reset_index()
    top_pubs_filter = top_pubs_filter.sort_values(by=opt, ascending=False).head(5)

    fig = px.bar(
        top_pubs_filter,
        x="Publisher",
        y=opt,
        title="Sales by Publisher",
        template="plotly_dark",
        labels={opt: f"{region} Sales", "Publisher": " "},
        text=top_pubs_filter[opt].apply(lambda y: f"{y: .1f} M"),
    )

    evt_data = st.plotly_chart(fig, on_select="rerun")
if evt_data:
    try:
        publisher = evt_data["selection"]["points"][0]["x"]

        st.subheader(f"{publisher} sales in {region}")

        pub_region_sales_df = df[df["Publisher"] == publisher]
        pub_region_sales_df = (
            pub_region_sales_df.groupby(["Year", "Publisher"])
            .agg({opt: "sum"})
            .reset_index()
        )
        #pub_region_sales_df

        high_year = pub_region_sales_df.loc[pub_region_sales_df[opt].idxmax()]["Year"]
        high_value = pub_region_sales_df[opt].max()

        fig = px.line(
            pub_region_sales_df,
            y=opt,
            x="Year",
            labels={opt: f"{region} Sales", "Year": ""},
            template="plotly_dark",
            markers=True,
            hover_name=opt,
        )
        
        fig.add_annotation(
            x=high_year,
            y=high_value,
            text=f"Sales Peak: {high_value: .1f} M ({high_year:.0f})",
            arrowhead=2,
            ax=50,
            ay=-20,
        )

        fig.update_layout(hoverlabel=dict(bgcolor='#636EFA'),font=dict(size=15))

        st.plotly_chart(fig)
    except KeyError:
        st.error("something went wrong")
    except IndexError:
        with col2:
            st.write("Select a Publisher to see more details")


# PUBLISHER SALES THROUGH TIME
# pub_evo = df.groupby(["Year", "Publisher"]).agg({"Global_Sales": "sum"}).reset_index()
