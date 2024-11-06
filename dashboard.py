import streamlit as st
import plotly.express as ex 
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import cm
import os
import warnings 
warnings.filterwarnings("ignore")
st.set_page_config(page_title="SuperStore!!!",page_icon=":bar_chart:",layout="wide")
st.title(":bar_chart: Super Store EDA")


df = None
# Removing default nav bar 
hide_streamlit_style = """
            <style>

            header {visibility: hidden;}
            </style>
            """

st.markdown(hide_streamlit_style, unsafe_allow_html=True)
# Our title is too much down. in middle we do following to reduce padding
st.markdown("<style> div.block-container{padding-top:1rem}</style> ",unsafe_allow_html=True)

#Now st.fileuploader allows user to upload files
file=st.file_uploader(":file_folder: Upload file",type=["csv","xlsx","xls","txt"])

if file is not None:
    file_name = file.name
    st.write(file_name)
    
    # Check file type and read accordingly
    if file_name.endswith(".csv"):
        df = pd.read_csv(file, encoding="ISO-8859-1")
    elif file_name.endswith((".xlsx", ".xls")):
        df = pd.read_excel(file)
    else:
        st.error("Unsupported file type")
else:
    os.chdir(r"C:\Users\User\Desktop\BSCS\5th Semester\Data Science\Store Dashboard Project") 
    df = pd.read_csv("Superstore.csv",encoding= "ISO-8859-1")   


#allowing user to filter data using date range
# we create two columns like start and end date for range
col1,col2= st.columns((2))
df["Order Date"]=pd.to_datetime(df["Order Date"])

# Getting the min max range for filter 
start_date =pd.to_datetime( df["Order Date"]).min()
end_date = pd.to_datetime(df["Order Date"]).max()

with col1:
    start_dates_selected = pd.to_datetime(st.date_input("Start Date",start_date))
with col2:
    end_dates_selected = pd.to_datetime(st.date_input("End Date",end_date))

df1 = df[(df["Order Date"]>start_date)& (df["Order Date"]<end_date)].copy()

# choosing region for super store
st.sidebar.header("Choose your filter")
region = st.sidebar.multiselect("Pick Region",df["Region"].unique())

if not region:
    df2 = df.copy()
else:
    df2 = df[df["Region"].isin(region)]

state = st.sidebar.multiselect("Pick State",df2["State"].unique())
if not state:
    df3 = df2.copy()
else:
    df3 = df2[df["State"].isin(state)]
city = st.sidebar.multiselect("Pick a city",df3["City"].unique())
if not city:
    df4 = df3.copy()
else:
    df4 = df3[df3["City"].isin(city)]  

#NOW  AS WE HAVE SHOWN THE REGION CITIES AND STATES TO BE SHOWN ACCORDINGLY NOW LETS FILTER THE DATE ACCORDINGLY

if not region  and not state and not city:
    filtered_df = df
elif not state and not city:
    filtered_df = df[df["Region"].isin(region)]
elif not region and not city:
    filtered_df = df[df["State"].isin(state)]
elif not region and not state:
    filtered_df = df[df["City"].isin(city)] 
elif region and state:
    filtered_df = df3[df["Region"].isin(region) & df3["State"].isin(state)]
elif region and city:
    filtered_df = df3[df["Region"].isin(region) & df3["City"].isin(city)]
elif city and state:
    filtered_df = df3[df["City"].isin(city) & df3["State"].isin(state)] 
else:
    filtered_df = df[df["Region"].isin(region) & df["City"].isin(city) & df["State"].isin(state)] 

    
category_df = filtered_df.groupby(["Category"])["Sales"].sum().reset_index()   

with col1:
    st.subheader("Category wise sales")
    fig = ex.bar(category_df,x="Category",y="Sales",text=['${:,.2f}'.format(x) for x in category_df["Sales"]],
    template = "seaborn")
    st.plotly_chart(fig,use_container_width=True,height = 100)
with col2:
    st.subheader("Region wise sales")  
    fig = ex.pie(filtered_df,values="Sales",names="Region",hole=0.5)  
    fig.update_traces(text=filtered_df["Region"],textposition="outside")
    st.plotly_chart(fig,use_container_width=True)

cl1,cl2 = st.columns((2))

with cl1:
    with st.expander("Category_ViewData"):
        category_df_styled = category_df.style.applymap(lambda x: f"background-color: {plt.cm.Blues(x / max(category_df['Sales']))}", subset=['Sales'])
        st.write(category_df)
        csv = category_df.to_csv(index= False).encode("utf-8")
        st.download_button("Download Data",data = csv,file_name="Category.csv",help = "download data")

with cl2:
    with st.expander("Region_ViewData"):
        region = filtered_df.groupby("Region")["Sales"].sum().reset_index()
        region_styled = region.style.applymap(lambda x: f"background-color: {plt.cm.Oranges(x / max(region['Sales']))}", subset=['Sales'])
        st.write(region)
        csv = region.to_csv(index= False).encode("utf-8")
        st.download_button("Download Data",data = csv,file_name="Region.csv",help = "download data")    

filtered_df["month_year"] = filtered_df["Order Date"].dt.to_period("M")
st.subheader("Time Series Analysis")
linechart = pd.DataFrame(filtered_df.groupby(filtered_df["month_year"].dt.strftime("%Y: %b"))["Sales"].sum()).reset_index()
fig2 = ex.line(linechart,x="month_year",y="Sales",height=500,width=500,template="gridon")
st.plotly_chart(fig2,use_container_width=True)

with st.expander("View time series Data"):
    st.write(linechart)
    csv =  linechart.to_csv(index=False).encode('utf-8')
    st.download_button("download data",data=csv,file_name="TimeSeries.csv")

#Segment wise sales
chart1,chart2 = st.columns((2))
with chart1:
    st.subheader("Segement wise chart")
    fig = ex.pie(filtered_df,values="Sales",names="Segment", template="plotly_dark")
    fig.update_traces(text = filtered_df["Segment"],textposition="inside")
    st.plotly_chart(fig,use_container_width=True)

with chart2:
    st.subheader("Category wise chart")
    fig = ex.pie(filtered_df,values="Sales",names="Category", template="gridon")
    fig.update_traces(text = filtered_df["Category"],textposition="inside")
    st.plotly_chart(fig,use_container_width=True)


st.markdown("Month wise sub category Table")
filtered_df ["month"] = filtered_df["Order Date"].dt.month_name()
subcategory_year = pd.pivot_table(filtered_df,values="Sales", index="Sub-Category",columns="month")
st.write(subcategory_year)



# Assuming 'filtered_df' is your filtered DataFrame based on user input
st.subheader("Scatter Plot: Sales vs. Profit")

# Create the scatter plot using Plotly Express
scatter_fig = ex.scatter(
    filtered_df,
    x="Sales",
    y="Profit",
    color="Category",  # Optional: differentiates points by category
    size="Sales",      # Optional: scales the point size based on Sales
    hover_data=["Region", "Segment"],  # Additional data to show on hover
    title="Sales vs. Profit Scatter Plot",
    template="plotly_white"  # You can change this to another template as needed
)

# Display the plot in Streamlit
st.plotly_chart(scatter_fig, use_container_width=True)