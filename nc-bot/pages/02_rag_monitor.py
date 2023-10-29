import streamlit as st
import plotly.express as px
import pandas as pd
import os
import warnings
from src.models import engine
from sqlalchemy.orm import Session
from src.helpers.rag_monitor_helper import RagMonitorQuery

col1, col2 = st.columns(2)
st.sidebar.header("Choose your filter: ")
# Filter for sidebar on 1-hour, 24-hour, 7-days, 30-days
filter_option = st.sidebar.selectbox("Select your filter", ("1-hour", "24-hour", "2-day", "7-day"))
rag_monitor_query = RagMonitorQuery(session=Session(engine))
print("Filter Option Choosen", filter_option)
filtered_data = rag_monitor_query.get_rag_scores(filter_option)

with col1:
    st.subheader("Inference Latency (s)")
    fig = px.line(filtered_data, x="time_stamp", y="total_duration", markers=True)
    st.plotly_chart(fig, theme="streamlit", use_container_width=True)

with col2:
    st.subheader("Answer Relevancy")
    fig = px.line(filtered_data, x="time_stamp", y="answer_relevancy", markers=True)
    st.plotly_chart(fig, theme="streamlit", use_container_width=True)

cl1, cl2 = st.columns(2)
with cl1:
    st.subheader("Faithfulness")
    fig = px.line(filtered_data, x="time_stamp", y="faithfulness", markers=True)
    st.plotly_chart(fig, theme="streamlit", use_container_width=True)

with cl2:
    st.subheader("Harmfulness")
    fig = px.line(filtered_data, x="time_stamp", y="harmfulness", markers=True)
    st.plotly_chart(fig, theme="streamlit", use_container_width=True)

cl11, cl22 = st.columns(2)

with cl11:
    st.subheader("Context Precision")
    fig = px.line(filtered_data, x="time_stamp", y="context_precision", markers=True)
    st.plotly_chart(fig, theme="streamlit", use_container_width=True)

with cl22:
    st.subheader("Score Correlation")
    corr_df = filtered_data[["context_precision","answer_relevancy"]]
    fig = px.imshow(corr_df.corr())
    st.plotly_chart(fig, theme="streamlit", use_container_width=True)


# with cl1:
#     with st.expander("Category_ViewData"):
#         st.write(category_df.style.background_gradient(cmap="Blues"))
#         csv = category_df.to_csv(index = False).encode('utf-8')
#         st.download_button("Download Data", data = csv, file_name = "Category.csv", mime = "text/csv",
#                             help = 'Click here to download the data as a CSV file')

# with cl2:
#     with st.expander("Region_ViewData"):
#         region = filtered_df.groupby(by = "Region", as_index = False)["Sales"].sum()
#         st.write(region.style.background_gradient(cmap="Oranges"))
#         csv = region.to_csv(index = False).encode('utf-8')
#         st.download_button("Download Data", data = csv, file_name = "Region.csv", mime = "text/csv",
#                         help = 'Click here to download the data as a CSV file')
        
# filtered_df["month_year"] = filtered_df["Order Date"].dt.to_period("M")
# st.subheader('Time Series Analysis')

# linechart = pd.DataFrame(filtered_df.groupby(filtered_df["month_year"].dt.strftime("%Y : %b"))["Sales"].sum()).reset_index()
# fig2 = px.line(linechart, x = "month_year", y="Sales", labels = {"Sales": "Amount"},height=500, width = 1000,template="gridon")
# st.plotly_chart(fig2,use_container_width=True)

# with st.expander("View Data of TimeSeries:"):
#     st.write(linechart.T.style.background_gradient(cmap="Blues"))
#     csv = linechart.to_csv(index=False).encode("utf-8")
#     st.download_button('Download Data', data = csv, file_name = "TimeSeries.csv", mime ='text/csv')

# # Create a treem based on Region, category, sub-Category
# st.subheader("Hierarchical view of Sales using TreeMap")
# fig3 = px.treemap(filtered_df, path = ["Region","Category","Sub-Category"], values = "Sales",hover_data = ["Sales"],
#                   color = "Sub-Category")
# fig3.update_layout(width = 800, height = 650)
# st.plotly_chart(fig3, use_container_width=True)

# chart1, chart2 = st.columns((2))
# with chart1:
#     st.subheader('Segment wise Sales')
#     fig = px.pie(filtered_df, values = "Sales", names = "Segment", template = "plotly_dark")
#     fig.update_traces(text = filtered_df["Segment"], textposition = "inside")
#     st.plotly_chart(fig,use_container_width=True)

# with chart2:
#     st.subheader('Category wise Sales')
#     fig = px.pie(filtered_df, values = "Sales", names = "Category", template = "gridon")
#     fig.update_traces(text = filtered_df["Category"], textposition = "inside")
#     st.plotly_chart(fig,use_container_width=True)

# import plotly.figure_factory as ff
# st.subheader(":point_right: Month wise Sub-Category Sales Summary")
# with st.expander("Summary_Table"):
#     df_sample = df[0:5][["Region","State","City","Category","Sales","Profit","Quantity"]]
#     fig = ff.create_table(df_sample, colorscale = "Cividis")
#     st.plotly_chart(fig, use_container_width=True)

#     st.markdown("Month wise sub-Category Table")
#     filtered_df["month"] = filtered_df["Order Date"].dt.month_name()
#     sub_category_Year = pd.pivot_table(data = filtered_df, values = "Sales", index = ["Sub-Category"],columns = "month")
#     st.write(sub_category_Year.style.background_gradient(cmap="Blues"))

# # Create a scatter plot
# data1 = px.scatter(filtered_df, x = "Sales", y = "Profit", size = "Quantity")
# data1['layout'].update(title="Relationship between Sales and Profits using Scatter Plot.",
#                        titlefont = dict(size=20),xaxis = dict(title="Sales",titlefont=dict(size=19)),
#                        yaxis = dict(title = "Profit", titlefont = dict(size=19)))
# st.plotly_chart(data1,use_container_width=True)

# with st.expander("View Data"):
#     st.write(filtered_df.iloc[:500,1:20:2].style.background_gradient(cmap="Oranges"))

# # Download orginal DataSet
# csv = df.to_csv(index = False).encode('utf-8')
# st.download_button('Download Data', data = csv, file_name = "Data.csv",mime = "text/csv")