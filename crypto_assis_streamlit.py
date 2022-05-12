from time import strftime
from qtpy import API
import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import datetime
import requests
import json
import altair as alt

st.set_page_config(layout="wide")

# if type(st.session_state.get('pf')) != pd.core.frame.DataFrame:
#     st.session_state['pf']=None
if "button1_click" not in st.session_state:
    st.session_state['button1_click']=False

if "button2_click" not in st.session_state:
    st.session_state['button2_click']=False

st.markdown("<h1 style='text-align: center; color: green;'>🪙 Crypto Assistant 🪙</h1>", unsafe_allow_html=True)

#################### user input #########################
#########################################################
st.write('📂 Please initiate your portfolio:')
col1, col2 = st.columns(2)
name = col1.text_input('Portfolio Name',value = 'enter your portfolio name here')
ps_init_assets = col2.number_input('Initial Funding (USD)',min_value = 10, value = 1000,format='%d')

date_ = datetime(2022,5,11)
date_str = date_.strftime("%Y-%m-%d")+"_00:00:00"

st.write('💰 Please choose the coins and ratios of you current portfolio:')
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
coins.append('stable')
ratios.append(0)
#################### user input #########################


###################### params ###########################
#########################################################
coins_dict = {
    coin_1: ratio_1,
    coin_2: ratio_2,
    coin_3: ratio_3
}
params = dict(
    name=name,
    ps_init_assets_str=ps_init_assets,
    date_str=date_str,
    coins_alloc_str = json.dumps(coins_dict)
)

# url = "http://127.0.0.1:8000"
url = "https://cryptoassistantimageamd64-c7z3tydiqq-df.a.run.app"
api_url = f'{url}/get_pf'
# api_url = f'{url}/get_pf_random'
###################### params ###########################


#################### init charts ########################
#########################################################
# call the API
m = st.markdown(""" <style> div.stButton > button{ width:50em;height:3em;background-color:#edf8ee} </style>""", unsafe_allow_html=True)
col1, col2, col3 = st.columns((1,3,1))
if col2.button('Done') and st.session_state['button2_click']==False:
    st.session_state['button1_click']=True
    response = requests.get(
        api_url,
        params=params
    )
    if response.status_code == 200:
        print("API call success")
        print("portfolio name:", response.json().get('portfolio_name', 'portfolio not found'))
        pf_status = response.json().get('portfolio_status', 'portfolio status not found')
        if pf_status == 'ready':
            pf= pd.read_json(response.json().get('portfolio', 'portfolio not found'))
            st.session_state['pf']=pf
        else:
            st.write(pf_status)
    else:
        st.write(f"API call error{response.status_code}")

    if ratio_1 + ratio_2+ ratio_3 != 100:
        st.error('The total ratio should be 100')
    # else:
    #     st.write('📈 Performance of your current portfolio with Buy&Hold Strategy:')
    #     pf = st.session_state['pf']
    #     asset_df_init = pd.DataFrame({'coins':coins,'ratios':ratios})

    # # pie chart of asset allocation
    #     pie_init = px.pie(asset_df_init,values='ratios',names='coins',height=300)

    # # line chart of perfomance in past 20 days
    #     line_init = alt.Chart(pf).mark_line().encode(alt.X('date'),alt.Y('t_bh_val',scale=alt.Scale(zero=False)))

    # # plot charts
    #     col1, col2 = st.columns((1,2))
    #     col1.plotly_chart(pie_init,use_container_width=True)
    #     col2.altair_chart(line_init,use_container_width=True)

if st.session_state['button1_click'] or st.session_state['button2_click']:
    st.write('📈 Performance with Buy&Hold Strategy:')
    pf = st.session_state['pf']
    pf.rename(columns = {'t_bh_val':'Buy&Hold', 't_ai_val':'AI Reallocate','t_ai_stable':'Stable','t_bh_val':'Asset(USD)'}, inplace = True)
    asset_df_init = pd.DataFrame({'coins':coins,'ratios':ratios})

# pie chart of asset allocation
    pie_init = px.pie(asset_df_init,values='ratios',names='coins',
                      height=350,
                      color='coins',
                      color_discrete_map={coin_1:'#9ACD32',
                                 coin_2:'#228B22',
                                 coin_3:'#6B8E23',
                                 'Stable':'#ebaa00'
                                 })

# line chart of perfomance in past 20 days
    line_init = alt.Chart(pf).mark_line().encode(alt.X('date'),alt.Y('Asset(USD)',scale=alt.Scale(zero=False)))

# plot charts
    col1, col2 = st.columns((1,2))
    col1.plotly_chart(pie_init,use_container_width=True)
    col2.altair_chart(line_init,use_container_width=True)
#################### init charts #########################


############## charts after reallocation #################
##########################################################

col1, col2, col3 = st.columns((1,3,1))
if col2.button('💸 Crypto Assistant, help to adjust my porflio, please! 💸'):
    st.session_state['button2_click']=True

# line charts of perfomance comparision in past 20 days
    st.write('📈 Performance with AI Reallocation Strategy:')

    pf = st.session_state['pf']
    pf_val = pf[['date','Asset(USD)','AI Reallocate']]
    pf_val.rename(columns = {'Asset(USD)':'Buy&Hold'}, inplace = True)
    pf_val = pd.melt(pf_val,id_vars =['date'], value_vars =['Buy&Hold','AI Reallocate'])
    pf_val.rename(columns = {'value':'Asset(USD)', 'variable':'Legend'}, inplace = True)

    line_new = alt.Chart(pf_val).mark_line().encode(
                                            alt.X('date'),
                                            alt.Y('Asset(USD)',scale=alt.Scale(zero=False)),
                                            color='Legend',
                                            strokeDash='Legend').properties(
                                                                        width=1510,
                                                                        height=250
                                                                    )
    st.altair_chart(line_new,use_container_width=False)

# bar charts of reallocation in past 20 days
    # prepare dataframe
    ratio_df = pf[['date',f'{coin_1}_ai_alloc',f'{coin_2}_ai_alloc',f'{coin_3}_ai_alloc','Stable']]
    ratio_df.rename(columns = {
                        f'{coin_1}_ai_alloc':coin_1,
                        f'{coin_2}_ai_alloc':coin_2,
                        f'{coin_3}_ai_alloc':coin_3}, inplace = True)
    #exclude negtive ratios
    # ratio_df[coin_1]= ratio_df[coin_1].apply(lambda x: 0 if x<0 else x)
    # ratio_df[coin_2]= ratio_df[coin_2].apply(lambda x: 0 if x<0 else x)
    # ratio_df[coin_3]= ratio_df[coin_3].apply(lambda x: 0 if x<0 else x)
    # prepare the right format for plotting
    ratio_df = pd.melt(ratio_df,id_vars =['date'], value_vars =[coin_1,coin_2,coin_3,'Stable'])
    ratio_df.rename(columns = {'value':'Ratios(%)', 'variable':'Coins'}, inplace = True)
    #plot
    bar_chart = px.bar(ratio_df, x='date', y='Ratios(%)', color='Coins',
                     color_discrete_map={coin_1:'#9ACD32',
                                        coin_2:'#228B22',
                                        coin_3:'#6B8E23',
                                        'Stable':'#ebaa00'
                                        },title='Portfolio Reallocations')
    st.plotly_chart(bar_chart,use_container_width=True)
    # pf

# recllocation pie chart
    ratios_new = [
        pf.iloc[-1][f'{coin_1}_ai_alloc'],
        pf.iloc[-1][f'{coin_2}_ai_alloc'],
        pf.iloc[-1][f'{coin_3}_ai_alloc'],
        pf.iloc[-1]['Stable']
    ]
    asset_df_new = pd.DataFrame({'coins':coins,'init_ratio':ratios,'ratio_new':ratios_new})

    st.markdown("<h4 style='text-align: center;'>📈 Suggested Allocation For Tomorrow 📈</h4>", unsafe_allow_html=True)
    # asset_df_new
    pie_new = px.pie(asset_df_new,values='ratio_new',names='coins',
                     height=400,
                     color='coins',
                     color_discrete_map={coin_1:'#9ACD32',
                                        coin_2:'#228B22',
                                        coin_3:'#6B8E23',
                                        'Stable':'#ebaa00'
                                        })
    col1, col2, col3 = st.columns((1,3,1))
    col2.plotly_chart(pie_new)











# st.write('📅 Please choose the date and time you want to predict:')
# date_ = st.date_input('date',datetime(2022,5,1),max_value=datetime(2022,5,1),min_value=datetime(2018,1,1))
# start_date = date_ - timedelta(days=20)
# start_date_str = start_date.strftime("%Y-%m-%d")+"_00:00:00"
# end_date_str = date_.strftime("%Y-%m-%d")+"_00:00:00"

# 2. click a button to reallocate the asset
# 2.1 call our API and show new performance
# if st.button('Adjust My Porflio'):
#     if st.session_state['performance_click'] and type(st.session_state.get('pf_init')) == pd.core.frame.DataFrame:
#         st.write(f"### Here's your performance of Portfolio_{name}:")
#         pf_init = st.session_state['pf_init']
#         pf_init_ = pf_init[['date','total_perf']].set_index('date')
#         st.bar_chart(pf_init_)
#         init_gains = pf_init_['total_perf'].sum()
#         st.metric(label="overall perfomance",value=f"{round(init_gains,2)}%")

# #     # retrieve the response
#     response = requests.get(
#         api_predict_url,
#         params=params
#     )

#     if response.status_code == 200:
#         print("API call success")
#         pf_new = pd.read_json(response.json().get('portfolio', 'portfolio not found'))
#         st.session_state['pf_new']=pf_new
#         st.markdown('# Your new asset allocation should be💴')

#         ratios_new = []
#         ratios_new.append(pf_new.iloc[-1,3])
#         ratios_new.append(pf_new.iloc[-1,5])
#         ratios_new.append(pf_new.iloc[-1,7])
#         new_asset_df = pd.DataFrame({'coins':coins,'init_ratio':ratios,'ratio_new':ratios_new})
#         new_asset_df['ratio_change'] = new_asset_df['ratio_new']-new_asset_df['init_ratio']
#         st.dataframe(new_asset_df)

#         fig_new = px.pie(new_asset_df,values='ratio_new',names='coins',height=300)
#         st.plotly_chart(fig_new)

#     else:
#         st.write("API call error")

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


# ratio_bar = alt.Chart(ratio_df).mark_bar(size=20).encode(
#                                                 x='date',
#                                                 y='Ratios(%)',
#                                                 color='Coins').properties(
#                                                                     width=1450,
#                                                                     height=250
#                                                                 )
# st.altair_chart(ratio_bar,use_container_width=False)
