from random import randint
from sqlite3 import Timestamp
from time import strftime
from qtpy import API
import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
import requests
import json
import numpy as np

if type(st.session_state.get('pf_init')) != pd.core.frame.DataFrame:
    st.session_state['pf_init']=None

if "performance_click" not in st.session_state:
    st.session_state['performance_click']=False

# 1. initial porfolio
# 1.1 ask users to input their types of coin & amount they invest
st.markdown('# Your initial asset allocation💴')

st.write('📕 Please enter your portfolio name:')
name = st.text_input('portfolio name')

st.write('📅 Please choose the date and time you want to predict:')
date_ = st.date_input('date',datetime(2022,5,1),max_value=datetime(2022,5,1),min_value=datetime(2018,1,1))
start_date = date_ - timedelta(days=30)
start_date_str = start_date.strftime("%Y-%m-%d")+"_00:00:00"
end_date_str = date_.strftime("%Y-%m-%d")+"_00:00:00"

st.write('💴 Please choose the coins and ratios of you current portfolio:')
coins = []
ratios = []

col1, col2 = st.columns(2)
coin_1 = col1.selectbox("Please choose your coin1:",('AAVE','BTC','DOT','ETH','FTM','NEAR','SOL','VITE'),0)
ratio_1 = col2.slider('Please choose the ratio you want to invest in coin1:',0,100,50)
coins.append(coin_1)
ratios.append(ratio_1)

col1, col2 = st.columns(2)
coin_2 = col1.selectbox("Please choose your coin2:",('AAVE','BTC','DOT','ETH','FTM','NEAR','SOL','VITE'),1)
if coin_2 == coin_1:
    st.error('Please choose another coin2')
ratio_2 = col2.slider('Please choose the ratio you want to invest in coin2:',0,100,100-ratio_1)
coins.append(coin_2)
ratios.append(ratio_2)

col1, col2 = st.columns(2)
coin_3 = col1.selectbox("Please choose your coin3:",('AAVE','BTC','DOT','ETH','FTM','NEAR','SOL','VITE'),2)
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

# dates = pd.date_range('2022-4-5','2022-5-4').strftime("%Y-%m-%d").to_list()
# init_perform_dict = pd.DataFrame({'date': dates,'gains':[randint(-20,20) for i in range(30)]}).set_index('date')
# st.bar_chart(init_perform_dict)
coins_dict = {
    coin_1: ratio_1,
    coin_2: ratio_2,
    coin_3: ratio_3
}
params = dict(
    name=name,
    start_date_str=start_date_str,
    end_date_str=end_date_str,
    coins_alloc_str = json.dumps(coins_dict)
)

url = "http://127.0.0.1:8000"
api_pf_url = f'{url}/create_b_and_h_pf'
api_predict_url = f'{url}/create_prediction_pf'


if st.button('See my Performance'):
    st.session_state['performance_click']=True
    st.write(f"### Here's your performance of Portfolio_{name}:")
    response = requests.get(
        api_pf_url,
        params=params
    )
    if response.status_code == 200:
        print("API call success")
        print("portfolio name:", response.json().get('portfolio_name', 'portfolio not found'))
        pf_init = pd.read_json(response.json().get('portfolio', 'portfolio not found'))
        st.session_state['pf_init']=pf_init
    else:
        st.write("API call error")

    # 1.4 print the bar chart of total performance
    pf_init = st.session_state['pf_init']
    pf_init_ = pf_init[['date','total_perf']].set_index('date')
    st.bar_chart(pf_init_)
    init_gains = pf_init_['total_perf'].sum()
    st.metric(label="overall perfomance",value=f"{round(init_gains,2)}%")

# 2. click a button to reallocate the asset
# 2.1 call our API and show new performance
if st.button('Adjust My Porflio'):
    if st.session_state['performance_click'] and type(st.session_state.get('pf_init')) == pd.core.frame.DataFrame:
        st.write(f"### Here's your performance of Portfolio_{name}:")
        pf_init = st.session_state['pf_init']
        pf_init_ = pf_init[['date','total_perf']].set_index('date')
        st.bar_chart(pf_init_)
        init_gains = pf_init_['total_perf'].sum()
        st.metric(label="overall perfomance",value=f"{round(init_gains,2)}%")

#     # retrieve the response
    response = requests.get(
        api_predict_url,
        params=params
    )

    if response.status_code == 200:
        print("API call success")
        pf_new = pd.read_json(response.json().get('portfolio', 'portfolio not found'))
        st.session_state['pf_new']=pf_new
        st.markdown('# Your new asset allocation should be💴')

        ratios_new = []
        ratios_new.append(pf_new.iloc[-1,3])
        ratios_new.append(pf_new.iloc[-1,5])
        ratios_new.append(pf_new.iloc[-1,7])
        new_asset_df = pd.DataFrame({'coins':coins,'init_ratio':ratios,'ratio_new':ratios_new})
        new_asset_df['ratio_change'] = new_asset_df['ratio_new']-new_asset_df['init_ratio']
        st.dataframe(new_asset_df)

        fig_new = px.pie(new_asset_df,values='ratio_new',names='coins',height=300)
        st.plotly_chart(fig_new)

    else:
        st.write("API call error")

# 3. new portfolio
# 3.1 show the pie chart of final asset allocation
    # The actual ratio_new should be result from back-end prediction. Here is a fake on below:
# st.write('Your new asset allocation should be:')

# ratios_new = [30,30,40]
# new_asset_df = pd.DataFrame({'coins':coins,'init_ratio':ratios,'ratio_new':ratios_new})
# new_asset_df['ratio_change'] = new_asset_df['ratio_new']-new_asset_df['init_ratio']
# st.dataframe(new_asset_df)

# fig_new = px.pie(new_asset_df,values='ratio_new',names='coins',height=300)
# st.plotly_chart(fig_new)

# # 3.2 plot the bar chart of gains in past 30 days
# st.write("### Your performance of the new portfolio is:")
# new_perform_dict = pd.DataFrame({'date': dates,'gains':[randint(-20,20) for i in range(30)]}).set_index('date')
# st.bar_chart(new_perform_dict)

# # 3.3 print the total gains
# new_gains = new_perform_dict['gains'].sum()
# st.metric(label="overall perfomance",value=f"{new_gains}%",delta=float(new_gains-init_gains))
