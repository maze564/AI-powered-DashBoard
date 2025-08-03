import streamlit as st
import plotly.express as px
import plotly.figure_factory as ff
import pandas as pd
import os
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="Superstore!!!", page_icon=":bar_chart:", layout="wide")
st.title(":bar_chart: AI Powered DataDashBoard")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)

# === File Uploader ===
fl = st.file_uploader(":file_folder: Upload a file", type=["csv", "txt", "xlsx", "xls"])
if fl is not None:
    filename = fl.name
    st.write("📂 Using uploaded file:", filename)

    if filename.endswith(".csv") or filename.endswith(".txt"):
        df = pd.read_csv(fl, encoding="ISO-8859-1")
    else:
        df = pd.read_excel(fl, engine='openpyxl')
else:
    st.info("📌 Using default file: Adidas.xlsx")
    default_path = r"C:/Users/Abdul Muiz/Desktop/ai powered dashboard/Adidas.xlsx"
    df = pd.read_excel(default_path, engine='openpyxl')

# === Clean Columns ===
df.columns = df.columns.str.strip()  # Remove leading/trailing spaces

# === Check required columns exist ===
required_columns = {"Retailer", "RetailerID", "InvoiceDate", "Region", "State", "UnitsSold", "City", "TotalSales"}
missing = required_columns - set(df.columns)
if missing:
    st.error(f"❌ The following required columns are missing from your file: {missing}")
    st.stop()

# === Convert Invoice Date ===
df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], errors='coerce')

# === Filter Date Range ===
col1, col2 = st.columns((2))
startDate = df["InvoiceDate"].min()
endDate = df["InvoiceDate"].max()
with col1:
    date1 = pd.to_datetime(st.date_input("Start Date", startDate))
with col2:
    date2 = pd.to_datetime(st.date_input("End Date", endDate))

df = df[(df["InvoiceDate"] >= date1) & (df["InvoiceDate"] <= date2)].copy()

# === Sidebar Filters ===
st.sidebar.header("Choose your filter: ")
region = st.sidebar.multiselect("Pick your Region", df["Region"].unique())
df2 = df if not region else df[df["Region"].isin(region)]

state = st.sidebar.multiselect("Pick the State", df2["State"].unique())
df3 = df2 if not state else df2[df2["State"].isin(state)]

city = st.sidebar.multiselect("Pick the City", df3["City"].unique())

# === Final Filter ===
filtered_df = df3 if not city else df3[df3["City"].isin(city)]

# === Product Bar Chart ===
product_df = filtered_df.groupby("Product", as_index=False)["TotalSales"].sum()

with col1:
    st.subheader("Product-wise Sales")
    fig = px.bar(product_df, x="Product", y="TotalSales",
                 text=['${:,.2f}'.format(x) for x in product_df["TotalSales"]],
                 template="seaborn")
    st.plotly_chart(fig, use_container_width=True)

# === Region Pie Chart ===
with col2:
    st.subheader("Region wise Sales")
    fig = px.pie(filtered_df, values="TotalSales", names="Region", hole=0.5)
    fig.update_traces(textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

# === View & Download Product & Region Data ===
cl1, cl2 = st.columns((2))
with cl1:
    with st.expander("Product_ViewData"):
        st.write(product_df.style.background_gradient(cmap="Blues"))
        csv = product_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Data", data=csv, file_name="Product.csv", mime="text/csv")

with cl2:
    with st.expander("Region_ViewData"):
        region_df = filtered_df.groupby("Region", as_index=False)["TotalSales"].sum()
        st.write(region_df.style.background_gradient(cmap="Oranges"))
        csv = region_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Data", data=csv, file_name="Region.csv", mime="text/csv")

# === Time Series Line Chart ===
filtered_df["month_year"] = filtered_df["InvoiceDate"].dt.to_period("M")
st.subheader('Time Series Analysis')
linechart = filtered_df.groupby(filtered_df["month_year"].dt.strftime("%Y : %b"))["TotalSales"].sum().reset_index()
fig2 = px.line(linechart, x="month_year", y="TotalSales", labels={"TotalSales": "Amount"},
               height=500, width=1000, template="gridon")
st.plotly_chart(fig2, use_container_width=True)

with st.expander("View Data of TimeSeries:"):
    st.write(linechart.T.style.background_gradient(cmap="Blues"))
    csv = linechart.to_csv(index=False).encode("utf-8")
    st.download_button('Download Data', data=csv, file_name="TimeSeries.csv", mime='text/csv')

# === Scatter Plot ===
st.subheader("Relationship between TotalSales and OperatingProfit using Scatter Plot.")
fig4 = px.scatter(filtered_df, x="TotalSales", y="OperatingProfit", size="UnitsSold")
st.plotly_chart(fig4, use_container_width=True)

# === View Raw Data ===
with st.expander("View Data"):
    st.write(filtered_df.iloc[:500, 1:20:2].style.background_gradient(cmap="Oranges"))

# === Download Clean Data ===
csv = df.to_csv(index=False).encode('utf-8')
st.download_button('Download Full Data', data=csv, file_name="Data.csv", mime="text/csv")
