import streamlit as st
import pandas as pd
import plotly_express as px

st.set_page_config(page_icon=":video_game:")

st.header("Nintendo Dashboard")

df = pd.read_csv(r"vgsales.csv", encoding="utf-8")
df = df[df["Publisher"] == "Nintendo"]

df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
df = df.dropna(subset=["Year"])  # remove null values

years = sorted(df["Year"].unique().astype(int))

c1, c2, c3 = st.columns(3)
with c1:
    start = st.selectbox("Start Year", options=years, index=0)
with c2:
    end = st.selectbox(
        "End Year",
        options=years[years.index(start) :],
        index=len(years[years.index(start) :]) - 1,
    )  # must be >= start

if start > end:
    st.error("Please select a start year before or equal to end year.")
else:
    filt_df = df[(df["Year"] >= start) & (df["Year"] <= end)]

# if start == end:
#     st.write(f"showing games from {start}")
# else:
#     st.write(f"showing games from {start} to {end}")

sales_evo = filt_df.groupby("Year").agg({"Global_Sales": "sum"}).reset_index()
fig = px.line(
    sales_evo,
    x="Year",
    y="Global_Sales",
    labels={"Year": "", "Global_Sales": "Global Sales (millions)"},
    template="simple_white",
    markers=True,
)
st.plotly_chart(fig)


sales_start_year = df[df["Year"] == start]["Global_Sales"].sum()
sales_end_year = df[df["Year"] == end]["Global_Sales"].sum()

sales_var = ((sales_end_year - sales_start_year) / sales_start_year) * 100

with c1:
    st.metric(f"Sales in {start}", value=f"{sales_start_year:.1f} M")
with c2:
    st.metric(
        f"Sales in {end}", value=f"{sales_end_year:.1f} M", delta=f"{sales_var:.2f}%"
    )
