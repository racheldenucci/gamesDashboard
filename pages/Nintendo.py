import streamlit as st
import pandas as pd
import plotly_express as px

st.set_page_config(page_icon=":video_game:", layout="wide")

st.header("Nintendo Dashboard")

df = pd.read_csv(r"vgsales.csv", encoding="utf-8")
df = df[df["Publisher"] == "Nintendo"]

df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
df = df.dropna(subset=["Year"])  # remove null values

years = sorted(df["Year"].unique().astype(int))

c1, c2, c3, c4 = st.columns(4)
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
sales_start_year = df[df["Year"] == start]["Global_Sales"].sum()
sales_end_year = df[df["Year"] == end]["Global_Sales"].sum()

sales_var = ((sales_end_year - sales_start_year) / sales_start_year) * 100

with c1:
    st.metric(f"Sales in {start}", value=f"{sales_start_year:.1f} M")
with c2:
    st.metric(
        f"Sales in {end}", value=f"{sales_end_year:.1f} M", delta=f"{sales_var:.2f}%"
    )

# SALES EVOLUTION THROUGH TIME
st.subheader("Yearly Sales")
sales_evo = filt_df.groupby("Year").agg({"Global_Sales": "sum"}).reset_index()
fig = px.line(
    sales_evo,
    x="Year",
    y="Global_Sales",
    labels={"Year": "", "Global_Sales": "Global Sales (millions)"},
    template="simple_white",
    markers=True,
    color_discrete_sequence=["orchid"],
)
fig.update_traces(hovertemplate=None)
fig.update_layout(hovermode="x unified")

st.plotly_chart(fig)

# TOP 5 GAMES
c1, c2 = st.columns(2)
with c1:
    top_5 = (
        filt_df.groupby("Name")
        .agg({"Global_Sales": "sum", "Genre": "first", "Year": "first"})
        .reset_index()
    )
    top_5 = top_5.sort_values("Global_Sales", ascending=False).head(5)

    fig = px.bar(
        top_5,
        x="Name",
        y="Global_Sales",
        labels={"Name": "", "Global_Sales": "Global Sales"},
        template="presentation",
        color_discrete_sequence=["violet"],
        hover_name="Name",
        hover_data=["Genre", "Year"],
        text=top_5["Global_Sales"].apply(lambda y: f"{y:.1f} M"),
    )
    fig.update_yaxes(showgrid=False)
    fig.update_layout(hoverlabel=dict(bgcolor="orchid"))

    st.plotly_chart(fig)
