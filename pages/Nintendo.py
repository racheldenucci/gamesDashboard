import streamlit as st
import pandas as pd
import plotly_express as px
import plotly.graph_objects as go
from prophet import Prophet

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
    st.subheader(f"Best Sellers")
    st.write(f"({start} - {end})")
    top_5 = (
        filt_df.groupby("Name")
        .agg({"Global_Sales": "sum", "Genre": "first", "Year": "first"})
        .reset_index()
    )
    top_5 = top_5.sort_values("Global_Sales", ascending=False).head(5)

    top_5_fig = px.bar(
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
    top_5_fig.update_yaxes(showgrid=False)
    top_5_fig.update_layout(hoverlabel=dict(bgcolor="orchid"))

    evt_data = st.plotly_chart(top_5_fig, on_select="rerun")

if evt_data:
    try:
        game = evt_data["selection"]["points"][0]["hovertext"]

        with c2:
            st.subheader(f"{game} Sales")
            st.write(f"({start} - {end})")
            game_df = filt_df[filt_df["Name"] == game].iloc[0]
            region_sales = pd.DataFrame(
                {
                    "Region": ["North America", "Europe", "Japan", "Others"],
                    "Sales": [
                        game_df["NA_Sales"],
                        game_df["EU_Sales"],
                        game_df["JP_Sales"],
                        game_df["Other_Sales"],
                    ],
                }
            )

            fig = px.bar(
                region_sales,
                x="Region",
                y="Sales",
                labels={"Region": ""},
                template="presentation",
                color_discrete_sequence=["violet"],
                text=region_sales["Sales"].apply(lambda y: f"{y:.1f} M"),
            )
            st.plotly_chart(fig)
    except KeyError:
        st.error("Sorry, something went wrong")
    except IndexError:
        st.write("Select a game to see details")

else:
    st.write("please select a game")


# FORECASTING WITH PROPHET
st.subheader("Forecasting")
df["Year"] = pd.to_datetime(df["Year"], format="%Y")
ts = df.groupby("Year").agg({"Global_Sales": "sum"}).reset_index()

ts.columns = ["ds", "y"]

# changepoint_prior_scale is way too high and VERY incorrect
model = Prophet(yearly_seasonality=False, changepoint_prior_scale=0.8).fit(ts)
future = model.make_future_dataframe(10, freq="YS")
forecast = model.predict(future)

# --- would show significant changes if there were any
# from prophet.plot import add_changepoints_to_plot
# fig = model.plot(forecast)
# add_changepoints_to_plot(fig.gca(), model, forecast)
# st.write(fig)

# st.write(model.plot_components(forecast))
# st.line_chart(forecast, y='yhat', x='ds')

only_future_forecast = forecast[forecast['ds']>='2016-01-01']

fig = px.line(
    only_future_forecast, x="ds", y="yhat", labels={"ds": "Year", "yhat": "Forecasted Sales"} 
)
fig.data[0].update(line=dict(dash='dash'))

fig.add_scatter(x=ts['ds'], y=ts['y'], mode='lines', name='Actual Sales', line=dict(color='orchid'))
fig.add_vline(x='2016', line_dash='dash', line_color='gray', line_width=1)
fig.add_annotation(
    x='2016',
    y = max(ts['y']),
    text='Sales Forecasting', 
    showarrow=False,
    bgcolor='#0E1117'

)
st.plotly_chart(fig)
