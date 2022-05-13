from time import strftime
from qtpy import API
import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import datetime
import requests
import json
import altair as alt
from PIL import Image

############################
## SERVER CONF.
# url = "http://127.0.0.1:8000"
url = "https://cryptoassistantimageamd64-c7z3tydiqq-df.a.run.app"

# date_ = datetime(2022,5,13)
date_ = datetime.now()
############################

st.set_page_config(
     page_title="Crypto Assistant",
     page_icon=Image.open('./favicon.ico'),
     layout="wide",
     menu_items={
         'About': 'Disclamer: Crypto Assistant cannot take any responsibilities'\
                        'in case of loss or profits with the advises presented below. '\
                        '(However, if profits, you can send us a cut😀 ;)'
     }
)

hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        </style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)

if "avalable_coins" not in st.session_state:
    st.session_state['avalable_coins'] = []

avalable_coins = st.session_state['avalable_coins']

if len(avalable_coins) == 0:
    #dl server avalaible coins
    api_url = f'{url}/get_avalaible_coins'
    response = requests.get(api_url)
    if response.status_code != 200:
        st.error(("API call error"))
    else:
        print("API call success")
        avalable_coins = response.json().get('avalaible_coins', [])
        st.session_state['avalable_coins']=avalable_coins

# avalable_coins = ['AAVE', 'ADA', 'BTC', 'DOT', 'ETH', 'FTM', 'NEAR', 'SOL', 'VITE']

if len(avalable_coins) > 0:
    if "button1_click" not in st.session_state:
        st.session_state['button1_click']=False

    if "button2_click" not in st.session_state:
        st.session_state['button2_click']=False

    st.markdown("<h1 style='text-align: center; color: green;'>🪙 "\
                "Crypto Assistant 🪙</h1>", unsafe_allow_html=True)

    #################### user input #########################
    #########################################################
    st.write('📂 Please initiate your portfolio:')
    col1, col2 = st.columns(2)
    name = col1.text_input('Portfolio Name')
    ps_init_assets = col2.number_input('Initial Funding (USD)',
                                    min_value = 0,
                                    format='%d',
                                    step=1000)

    date_str = date_.strftime("%Y-%m-%d")+"_00:00:00"
    st.write('Analysis date:', date_.date())

    st.write('💰 Please choose the coins and ratios of you current portfolio:')
    coins = []
    ratios = []

    # init values:
    ratio_1 = 50
    ratio_2 = 20
    ratio_3 = 30

    col1, col2, col3 = st.columns(3)
    coin_1 = col1.selectbox("Please choose your coin1:", avalable_coins, 3)
    ratio_1 = 100-ratio_1-ratio_2
    if ratio_1 < 0:
        ratio_1 = 0
    ratio_1 = col2.slider('Please choose the ratio you want to invest in coin1:',
                        0, 100, ratio_1)
    coins.append(coin_1)
    ratios.append(ratio_1)

    # col1, col2, col3 = st.columns(3)
    coin_2 = col1.selectbox("Please choose your coin2:", avalable_coins, 6)
    if coin_2 == coin_1:
        st.error('Please choose another coin2')
    ratio_2 = 100-ratio_1-ratio_2
    if ratio_2 < 0:
        ratio_2 = 0
    ratio_2 = col2.slider('Please choose the ratio you want to invest in coin2:',
                        0, 100, ratio_2)
    coins.append(coin_2)
    ratios.append(ratio_2)

    # col1, col2, col3 = st.columns(3)
    coin_3 = col1.selectbox("Please choose your coin3:", avalable_coins, 2)
    if coin_3 == coin_2 or coin_3 == coin_1:
        st.error('Please choose another coin3')
    ratio_3 = 100-ratio_1-ratio_2
    if ratio_3 < 0:
        ratio_3 = 0
    ratio_3 = col2.slider('Please choose the ratio you want to invest in coin3:',
                        0, 100, ratio_3)
    if ratio_3 < 0:
        ratio_3 = 0
    coins.append(coin_3)
    ratios.append(ratio_3)

    # col1, col2, col3 = st.columns(3)

    asset_df_init = pd.DataFrame({'coins':coins,'ratios':ratios})
    # pie chart of asset allocation
    pie_coins = px.pie(asset_df_init,values='ratios',names='coins',
                        height=350,
                        color='coins',
                        color_discrete_map={
                            coin_1:'#9ACD32',
                            coin_2:'#228B22',
                            coin_3:'#6B8E23'
                        },
                        hole=.6)

    col3.plotly_chart(pie_coins,use_container_width=True)

    coins.append('Stable')
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

    api_url = f'{url}/get_pf'
    # api_url = f'{url}/get_pf_random'
    ###################### params ###########################


    #################### init charts ########################
    #########################################################
    # call the API
    m = st.markdown(""" <style> div.stButton > button{ width:50em;height:3em;"\
                    "background-color:#edf8ee} </style>""", unsafe_allow_html=True)

    agree = st.checkbox('Disclaimers: Crypto Assistant cannot take any responsibilities'\
                        'in case of loss or profits with the advises presented below. '\
                        '(However, if profits, you can send us a cut😀 ;)')

    col1, col2, col3 = st.columns((1,3,1))
    if col2.button('Done') and st.session_state['button2_click']==False:
        # st.write('ratio_1 + ratio_2 + ratio_3:', ratio_1 + ratio_2 + ratio_3)
        if not agree:
            st.error('Please click the agreement above.')
        elif ratio_1 + ratio_2 + ratio_3 != 100:
            st.error('The total ratio should be 100')
        elif ps_init_assets == 0:
            st.error('The initial funding cannot be 0')
        elif len(name) == 0:
            st.error('Please, what is your portfolio name ?')

        else:
            st.session_state['button1_click']=True
            response = requests.get(
                api_url,
                params=params
            )
            if response.status_code == 200:
                print("API call success")
                print("portfolio name:", response.json().get('portfolio_name',
                                                            'portfolio not found'))
                pf_status = response.json().get('portfolio_status',
                                                'portfolio status not found')
                if pf_status == 'ready':
                    pf= pd.read_json(response.json().get('portfolio',
                                                        'portfolio not found'))
                    st.session_state['pf']=pf

                    bh_perf = (pf['t_bh_val'].iloc[-1] \
                        - ps_init_assets)/ps_init_assets * 100
                    st.session_state['bh_perf']=bh_perf
                    ai_perf = (pf['t_ai_val'].iloc[-1] \
                        - ps_init_assets)/ps_init_assets * 100
                    st.session_state['ai_perf']=ai_perf

                    bh_val = pf['t_bh_val'].iloc[-1] - ps_init_assets
                    st.session_state['bh_val']=bh_val
                    ai_val = pf['t_ai_val'].iloc[-1] - ps_init_assets
                    st.session_state['ai_val']=ai_val

                else:
                    st.write(pf_status)
            else:
                st.write(f"API call error{response.status_code}")


    if st.session_state['button1_click'] or st.session_state['button2_click']:

        if "pf" in st.session_state:

            st.write('📈 Performance with Buy&Hold Strategy:')
            pf = st.session_state['pf']
            pf.rename(columns = {'t_bh_val':'Buy&Hold',
                                't_ai_val':'AI Reallocate',
                                't_ai_stable':'Stable',
                                't_bh_val':'Asset(USD)'},
                    inplace = True
                    )

            asset_df_init = pd.DataFrame({'coins':coins,'ratios':ratios})

            # pie chart of asset allocation
            pie_init = px.pie(asset_df_init,values='ratios',names='coins',
                            height=350,
                            color='coins',
                            color_discrete_map={coin_1:'#9ACD32',
                                        coin_2:'#228B22',
                                        coin_3:'#6B8E23',
                                        'Stable':'#ebaa00'
                                        },
                            hole=.6)

            # line chart of perfomance in past 20 days
            line_init = alt.Chart(pf).mark_line(color="#FFA500")\
                .encode(alt.X('date'),alt.Y('Asset(USD)', scale=alt.Scale(zero=False)))

            # plot charts
            st.altair_chart(line_init, use_container_width=True)

            bh_perf = st.session_state['bh_perf']
            bh_val = st.session_state['bh_val']

            st.metric("Buy&Hold Strategy",
                    f"${(round(bh_val, 2))}",
                    f"{(round(bh_perf, 3))}%")

            #################### init charts #########################


            ############## charts after reallocation #################
            ##########################################################

    col1, col2, col3 = st.columns((1,3,1))
    if col2.button('💸 Crypto Assistant, help to adjust my porflio, please! 💸'):
        st.session_state['button2_click']=True

        if "pf" not in st.session_state:
            st.error(("Please click 'Done' button before adjusting your portfolio."))
        else:
            # line charts of perfomance comparision in past 20 days
            st.write('📈 Performance with AI Reallocation Strategy:')

            pf = st.session_state['pf']
            pf_val = pf[['date','Asset(USD)','AI Reallocate']]
            pf_val.rename(columns = {'Asset(USD)':'Buy&Hold'}, inplace = True)
            pf_val = pd.melt(pf_val,id_vars =['date'],
                            value_vars =['Buy&Hold','AI Reallocate'])
            pf_val.rename(columns = {'value':'Asset(USD)',
                                    'variable':'Legend'},
                        inplace = True)

            line_new = alt.Chart(pf_val).mark_line().encode(
                                                    alt.X('date'),
                                                    alt.Y('Asset(USD)',
                                                    scale=alt.Scale(zero=False)),
                                                    color='Legend',
                                                    strokeDash='Legend').properties(
                                                        width=1300,
                                                        height=250)

            st.altair_chart(line_new,use_container_width=False)

            # bar charts of reallocation in past 20 days
            # prepare dataframe
            ratio_df = pf[['date',
                        f'{coin_1}_ai_alloc',
                        f'{coin_2}_ai_alloc',
                        f'{coin_3}_ai_alloc','Stable']]

            ratio_df.rename(columns = {
                                f'{coin_1}_ai_alloc':coin_1,
                                f'{coin_2}_ai_alloc':coin_2,
                                f'{coin_3}_ai_alloc':coin_3}, inplace = True)
            #exclude negtive ratios
            # ratio_df[coin_1]= ratio_df[coin_1].apply(lambda x: 0 if x<0 else x)
            # ratio_df[coin_2]= ratio_df[coin_2].apply(lambda x: 0 if x<0 else x)
            # ratio_df[coin_3]= ratio_df[coin_3].apply(lambda x: 0 if x<0 else x)
            # prepare the right format for plotting
            ratio_df = pd.melt(ratio_df,id_vars =['date'],
                            value_vars =[coin_1,coin_2,coin_3,'Stable'])

            ratio_df.rename(columns = {'value':'Ratios(%)',
                                    'variable':'Coins'},
                            inplace = True)

            bh_perf = st.session_state['bh_perf']
            ai_perf = st.session_state['ai_perf']
            bh_val = st.session_state['bh_val']
            ai_val = st.session_state['ai_val']
            st.metric("AI Reallocation Strategy (compare to B&H)",
                    f"${round((ai_val - bh_val), 2)}",
                    f"{round((ai_perf - bh_perf), 2)}%")

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
            asset_df_new = pd.DataFrame({'coins':coins,
                                        'init_ratio':ratios,
                                        'ratio_new':ratios_new})

            st.markdown("<h4 style='text-align: center;'>📈 Suggested Allocation "\
                        "For Tomorrow 📈</h4>", unsafe_allow_html=True)

            # asset_df_new
            pie_new = px.pie(asset_df_new,values='ratio_new',names='coins',
                            height=400,
                            color='coins',
                            color_discrete_map={coin_1:'#9ACD32',
                                                coin_2:'#228B22',
                                                coin_3:'#6B8E23',
                                                'Stable':'#ebaa00'
                                                },
                            hole=.6)
            col1, col2, col3 = st.columns((1,3,1))
            col2.plotly_chart(pie_new)

            st.session_state['button1_click']=False
            st.session_state['button2_click']=False
