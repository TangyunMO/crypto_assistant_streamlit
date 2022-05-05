from random import randint
from sqlite3 import Timestamp
from qtpy import API
import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import datetime
import requests

# 1. initial porfolio
# 1.1 ask users to input their types of coin & amount they invest
st.markdown('# Your initial asset allocation💴')

test_timestamp = Timestamp(2022,5,2,10)
st.write(f"Test timestamp: {test_timestamp}")

coins = []
ratios = []

col1, col2 = st.columns(2)
coin_1 = col1.selectbox("Please choose your coin1:",('AAVE','BTC','ETH','FTM','NEAR','SOL','VITE'),0)
ratio_1 = col2.slider('Please choose the ratio you want to invest in coin1:',0,100,50)
coins.append(coin_1)
ratios.append(ratio_1)

col1, col2 = st.columns(2)
coin_2 = col1.selectbox("Please choose your coin2:",('AAVE','BTC','ETH','FTM','NEAR','SOL','VITE'),1)
if coin_2 == coin_1:
    st.error('Please choose another coin2')
ratio_2 = col2.slider('Please choose the ratio you want to invest in coin2:',0,100,100-ratio_1)
coins.append(coin_2)
ratios.append(ratio_2)

col1, col2 = st.columns(2)
coin_3 = col1.selectbox("Please choose your coin3:",('AAVE','BTC','ETH','FTM','NEAR','SOL','VITE'),2)
if coin_3 == coin_2 or coin_3 == coin_1:
    st.error('Please choose another coin3')
ratio_3 = col2.slider('Please choose the ratio you want to invest in coin3:',0,100,100-ratio_1-ratio_2)
coins.append(coin_3)
ratios.append(ratio_3)

# 1.2 calculate the percentages of each coin and generate a pie chart
if ratio_1 + ratio_2+ ratio_3 != 100:
    st.error('The total ratio should be 100')
else:
    st.write('Your current asset allocation is:')

    init_asset_df = pd.DataFrame({'coins':coins,'ratios':ratios})
    st.dataframe(init_asset_df)

    fig_init = px.pie(init_asset_df,values='ratios',names='coins',height=300)
    st.plotly_chart(fig_init)

#    1.3 plot the bar chart of gains in past 30 days
st.write("### Here's your performance of the current portfolio:")
    # we need an API to get the real peformance of the portfolio. Here is a fake one below:
REALTIME_PRICE_URL = 'REALTIME_PRICE_URL'
dates = pd.date_range('2022-4-5','2022-5-4').strftime("%Y-%m-%d").to_list()
init_perform_dict = pd.DataFrame({'date': dates,'gains':[randint(-20,20) for i in range(30)]}).set_index('date')
st.bar_chart(init_perform_dict)

#    1.4 print the total gains
init_gains = init_perform_dict['gains'].sum()
st.metric(label="overall perfomance",value=f"{init_gains}%")


# 2. click a button to reallocate the asset
# 2.1 call our API to predict the indicators of each coin
MODEL_URL = 'MODEL_URL'

params = {
    'coins':[coin_1,coin_2,coin_3],
    'ratios':[ratio_1,ratio_2,ratio_3]
}

st.button('Adjust My Porflio')
# if st.button('Adjust My Porflio'):
#     if len(coins)==3 and len(ratios)==3:
#         res = requests.get(f"{MODEL_URL}predict", params=params).json()
#         st.json(res)

# 3. new portfolio
# 3.1 show the pie chart of final asset allocation
    # The actual ratio_new should be result from back-end prediction. Here is a fake on below:
st.write('Your new asset allocation should be:')

ratios_new = [30,30,40]
new_asset_df = pd.DataFrame({'coins':coins,'init_ratio':ratios,'ratio_new':ratios_new})
new_asset_df['ratio_change'] = new_asset_df['ratio_new']-new_asset_df['init_ratio']
st.dataframe(new_asset_df)

fig_new = px.pie(new_asset_df,values='ratio_new',names='coins',height=300)
st.plotly_chart(fig_new)

# 3.2 plot the bar chart of gains in past 30 days
st.write("### Your performance of the new portfolio is:")
new_perform_dict = pd.DataFrame({'date': dates,'gains':[randint(-20,20) for i in range(30)]}).set_index('date')
st.bar_chart(new_perform_dict)

# 3.3 print the total gains
new_gains = new_perform_dict['gains'].sum()
st.metric(label="overall perfomance",value=f"{new_gains}%",delta=float(new_gains-init_gains))
