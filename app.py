import pandas as pd
# import altair as alt
import streamlit as st
from PIL import Image
# import numpy as np
# import matplotlib.pyplot as plt
import datetime
# import seaborn as sns

image = Image.open('covid19.png')
st.image(image, use_column_width=True)

@st.cache(allow_output_mutation=True)
def data_loader():
    url = 'https://toyokeizai.net/sp/visual/tko/covid19/csv/prefectures.csv'
    df = pd.read_csv(url)
    return df

st.title('Japanese Covid-19 Dashboard')

#データの整形
def to_date(d):
    # '{.formatの添え字:指定したい書式の型}' 02は最小幅は二桁という意味
    return pd.to_datetime('{0:02}/{1:02}/{2:02}'.format(d['year'], d['month'], d['date']), format='%Y/%m/%d')

def data_visualize():
    try:
        df = data_loader()
        # 日付に直す
        df['days'] = df.apply(to_date, axis=1)
        # Null値の補完
        df = df.fillna(0)

        # 型変換
        df['deaths'] = df['deaths'].astype(int)
        df['serious'] = df['serious'].astype(int)
        df['peopleTested'] = df['peopleTested'].astype(int)
        df['hospitalized'] = df['hospitalized'].astype(int)
        df['discharged'] = df['discharged'].astype(int)

        #カラム名の変更
        df = df.rename(columns={'days':'年月日', 'prefectureNameJ': '都道府県', 'peopleTested': '検査数','testedPositive':'陽性者数','discharged':'回復者数',\
                                'hospitalized':'療養者数','serious':'重症者数','deaths':'死者数'})
        # 必要なカラムのみに絞る
        df = df[['年月日', '都道府県', '検査数', '陽性者数', '回復者数', '療養者数', '重症者数', '死者数']]

        _df = df.groupby('都道府県').max().sort_values('陽性者数',ascending=False)

        st.header('都道府県別の累計')
        st.dataframe(_df)
        st.bar_chart(_df['陽性者数'])

        st.header('全国陽性者数グラフ/日')
        df_days_all = df.loc[:, ["年月日", "都道府県", '陽性者数']]
        df_days_all = df_days_all.loc[:, ["年月日", "都道府県", '陽性者数']]
        df_days_all = df_days_all.set_index("年月日")
        df_days_all = df_days_all.groupby('年月日').sum()
        df_days_all['陽性者数/日'] = df_days_all["陽性者数"].diff()
        st.bar_chart(df_days_all['陽性者数/日'])

        #都道府県インプット
        _prefectureNameJ = st.sidebar.text_input("都道府県を入力してください", "東京都")

        st.header(f'{_prefectureNameJ}・陽性者数グラフ/日')
        df_prefecture = df.groupby('都道府県').get_group(_prefectureNameJ)
        df_days = df_prefecture.loc[:, ["年月日", "都道府県", '陽性者数']]
        #年月日の差分
        df_days['陽性者数/日'] = df_days["陽性者数"].diff()
        df_days = df_days.set_index("年月日")
        # st.write(df_days)
        st.bar_chart(df_days["陽性者数/日"])
        # st.line_chart(df_days["陽性者数/日"])

        df['陽性率'] = df['陽性者数'] / df['検査数'] * 100
        df['復帰率'] = df['回復者数'] / df['陽性者数'] * 100
        df['療養率'] = df['療養者数'] / df['陽性者数'] * 100
        df['重症化率'] = df['重症者数'] / df['陽性者数'] * 100
        df['死亡率'] = df['死者数'] / df['陽性者数'] * 100

        # days = '2021-08-19'
        days = datetime.datetime.now() - datetime.timedelta(days=2)
        days = datetime.datetime.strftime(days, '%Y-%m-%d')

        df2 = df[['都道府県', '検査数', '陽性者数', '回復者数', '療養者数', '重症者数','死者数', '陽性率', '復帰率', '療養率', '重症化率', '死亡率']][df['年月日'] == days]

        df3 = pd.DataFrame(
            data=df2[['検査数', '陽性者数', '回復者数', '療養者数', '重症者数', '死者数']].sum())
        df3 = df3.T
        df3['陽性率'] = df3['陽性者数'] / df3['検査数'] * 100
        df3['復帰率'] = df3['回復者数'] / df3['陽性者数'] * 100
        df3['療養率'] = df3['療養者数'] / df3['陽性者数'] * 100
        df3['重症化率'] = df3['重症者数'] / df3['陽性者数'] * 100
        df3['死亡率'] = df3['死者数'] / df3['陽性者数'] * 100

        st.header('全国累計')
        df3 = df3.reset_index(drop=True)
        st.dataframe(df3)

        st.header('都道府県別・PCR検査陽性率（降順）')
        _df2 = df2[['都道府県','検査数','陽性者数','陽性率']].sort_values('陽性率',ascending=False)
        # _df2 = df2.set_index('都道府県')

        _df2 = _df2.set_index("都道府県")

        st.dataframe(_df2,1000)
        st.bar_chart(_df2['陽性率'], use_container_width=True)

        st.header('都道府県別・感染から復帰率（降順）')
        __df2 = df2[['都道府県', '陽性者数', '回復者数', '復帰率']].sort_values('復帰率', ascending=False)
        __df2 = __df2.set_index("都道府県")
        st.dataframe(__df2)

        st.header(f'{_prefectureNameJ}・回復者数/日')
        # df_prefecture = df.groupby('都道府県').get_group(_prefectureNameJ)
        df_days = df_prefecture.loc[:, ["年月日", "都道府県", '回復者数']]
        #年月日の差分
        df_days['回復者数/日'] = df_days["回復者数"] + df_days["回復者数"].diff()
        df_days = df_days.set_index("年月日")
        # st.write(df_days)
        st.bar_chart(df_days["回復者数/日"], use_container_width=True)


        st.header('都道府県別・療養率（降順）')
        __df2 = df2[['都道府県', '陽性者数', '療養者数', '療養率']].sort_values('療養率', ascending=False)
        __df2 = __df2.set_index("都道府県")
        st.dataframe(__df2, width=1000)
        st.bar_chart(__df2['療養率'])

        st.header(f'{_prefectureNameJ}・療養者数/日')
        # df_prefecture = df.groupby('都道府県').get_group(_prefectureNameJ)
        df_days = df_prefecture.loc[:, ["年月日", "都道府県", '療養者数']]
        #年月日の差分
        df_days['療養者数/日'] = df_days["療養者数"] + df_days["療養者数"].diff()
        df_days = df_days.set_index("年月日")
        # st.write(df_days)
        st.bar_chart(df_days["療養者数/日"], use_container_width=True)


        st.header('都道府県別・重症化率（降順）')
        __df2 = df2[['都道府県', '陽性者数', '重症者数', '重症化率']].sort_values('重症化率', ascending=False)
        __df2 = __df2.set_index("都道府県")
        st.dataframe(__df2, width=1000)
        st.bar_chart(__df2['重症化率'], use_container_width=True)

        st.header(f'{_prefectureNameJ}・重症者数/日')
        # df_prefecture = df.groupby('都道府県').get_group(_prefectureNameJ)
        df_days = df_prefecture.loc[:, ["年月日", "都道府県", '重症者数']]
        #年月日の差分
        df_days['重症者数/日'] = df_days["重症者数"] + df_days["重症者数"].diff()
        df_days = df_days.set_index("年月日")
        # st.write(df_days)
        st.bar_chart(df_days["重症者数/日"], use_container_width=True)


        st.header('都道府県別・死亡率（降順）')
        __df2 = df2[['都道府県', '陽性者数', '死者数', '死亡率']].sort_values('死亡率', ascending=False)
        __df2 = __df2.set_index("都道府県")
        st.dataframe(__df2)
        st.bar_chart(__df2['死亡率'], use_container_width=True)

        st.header(f'{_prefectureNameJ}・死者数/日')
        # df_prefecture = df.groupby('都道府県').get_group(_prefectureNameJ)
        df_days = df_prefecture.loc[:, ["年月日", "都道府県", '死者数']]
        #年月日の差分
        df_days['死者数/日'] = df_days["死者数"].diff()
        df_days = df_days.set_index("年月日")
        # st.write(df_days)
        st.bar_chart(df_days["死者数/日"], use_container_width=True)
    except:
        st.error(
            "エラーがおきているようです。都道府県名を漢字で入力してください。"
        )

data_visualize()

st.write('Copyright © 2021 Tomoyuki Yoshikawa. All Rights Reserved.')
