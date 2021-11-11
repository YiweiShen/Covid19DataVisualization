# matplotlib.use('Agg'), is safe guarding, otherwise the error message will show:
# UserWarning: Starting a Matplotlib GUI outside of the main thread will likely fail.
import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
import requests
import base64
from io import BytesIO
import matplotlib.pyplot as plt
from datetime import date, timedelta, datetime


# Confirmed positive cases of COVID-19 in Ontario
# https://data.ontario.ca/dataset/confirmed-positive-cases-of-covid-19-in-ontario

# Status of COVID-19 cases in Ontario by Public Health Unit (PHU)
# https://data.ontario.ca/dataset/status-of-covid-19-cases-in-ontario-by-public-health-unit-phu


class Covid_Ontario_Active_Case:
    def __init__(self):
        j = self.fetch_data()
        self.df = self.create_dataframe(j)
        self.today = self.cal_today(self.df)

    def fetch_data(self):
        # use data API to figure out the dataset limit
        base_url = 'https://data.ontario.ca/api/3/action/datastore_search?resource_id=d1bfe1ad-6575-4352-8302-09ca81f7ddfc&limit='
        url = base_url + '1'
        r = requests.get(url)
        j = r.json()
        limit_cap = str(j['result']['total']+1)
        # fetch the full dataset of Covid-19 Ontario active cases
        url = base_url + limit_cap
        r = requests.get(url)
        j = r.json()
        return j

    def create_dataframe(self, j): 
        # store the cases into a list for pandas to process
        cases = []
        for i in j['result']['records']:
            cases.append(i)
        # load cases data into pandas dataframe
        df = pd.DataFrame(cases)
        # set FILE_DATE field to datetime format for easier query
        df['FILE_DATE'] = pd.to_datetime(df['FILE_DATE'])
        return df

    def cal_today(self, df):
        today = date.today().strftime("%Y""-""%m""-""%d")
        while df[(df['FILE_DATE'] == today)].empty:
            # if the data for today is not available, the today value will be adjust 
            # to the date of the data available most recently, possiblely it is yesterday
            today = (datetime.strptime(today, "%Y""-""%m""-""%d")- timedelta(1)).strftime("%Y""-""%m""-""%d")
        return today

    def display_info(self):
        print('-----------------------------------------------------')
        print('For the date of ' + self.today + ', details of Ontario active cases:\n')
        print(self.df[(self.df['FILE_DATE'] == self.today)][['PHU_NAME', 'ACTIVE_CASES']].to_string(index=False))
        print('-----------------------------------------------------')

    def cal_correlation(self):
        # show the correlation for the columns 'ACTIVE_CASES', 'RESOLVED_CASES', 'DEATHS'
        df_corr = pd.DataFrame(self.df, columns=['ACTIVE_CASES', 'RESOLVED_CASES', 'DEATHS']).corr()
        print('-----------------------------------------------------')
        print('Covid-19 data correlation calculated:\n')
        print(df_corr)
        print('-----------------------------------------------------')

    def get_heatmap(self):
        # Calculate a Heatmap that shows historical trend correlations between 
        # Ontario counties and create the heatmap plot using Seaborn
        df = self.df.copy(deep=True)
        df = df.pivot_table(index='FILE_DATE', columns='PHU_NAME', values='ACTIVE_CASES', aggfunc=np.mean)
        df_corr = pd.DataFrame(df, columns=df.columns).corr()
        mask = np.zeros_like(df_corr)
        mask[np.triu_indices_from(mask)] = True
        with sns.axes_style("white"):
            f, ax = plt.subplots(figsize=(14, 8))
            ax = sns.heatmap(df_corr, mask=mask, vmax=1, square=True)
        plt.suptitle('Heatmap of correlations')
        # Shrink the current axis's height by 10%, so that more words can fit into the figure
        box = ax.get_position()
        ax.set_position([box.x0, box.y0 + box.height * 0.1, box.width, box.height * 0.9])
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        graphic = base64.b64encode(image_png)
        graphic = graphic.decode('utf-8')
        return graphic

    def get_line_graph(self):
        # A line graph of the active cases for each of the Ontario counties over time
        df = self.df.copy(deep=True)
        df = df.pivot_table(index='FILE_DATE', columns='PHU_NAME', values='ACTIVE_CASES', aggfunc=np.mean)
        print('Creating the line graph...')
        ax = df.plot.line(title="Active cases for each of the Ontario counties over time", figsize=(14, 8))
        # Shrink the current axis's height by 10% on the bottom, so that the legend can be shown
        box = ax.get_position()
        ax.set_position([box.x0, box.y0 + box.height * 0.1, box.width, box.height * 0.9])
        # Put the legend below the current axis
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.12), ncol=7, prop={'size': 5})
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        graphic = base64.b64encode(image_png)
        graphic = graphic.decode('utf-8')
        return graphic