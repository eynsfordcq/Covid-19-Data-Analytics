# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

#importing packages
import dash
from dash.dcc.Dropdown import Dropdown
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
#from ipywidgets import widgets

app = dash.Dash(__name__)

def clean_data(df, status):
  df = df.fillna("") #replace NaN value 
  df = df.drop(["Province/State", "Lat", "Long"], axis = 1) #drop unecessary columns
  df = df.rename(columns = {"Country/Region": "Country"}) #rename column name to just country
  df = df.groupby(["Country"], sort = True).sum() #merge countries together (previously seperated by province/state)
  df.insert(0, "Status", status, allow_duplicates = True) #add a Status column
  df = df.reset_index().set_index(["Country", "Status"]) #make country and status column a pair index
  return df

#World timeseries confirmed, death, recovered cases
df_confirmed = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv")
df_deaths = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv")
df_recovered = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv")
df_confirmed = clean_data(df_confirmed, "Confirmed")
df_deaths = clean_data(df_deaths, "Deaths")
df_recovered = clean_data(df_recovered, "Recovered")
df_confirmed = df_confirmed.append(df_confirmed.sum(numeric_only=True).rename(('World', 'Confirmed'))) 
df_deaths = df_deaths.append(df_deaths.sum(numeric_only=True).rename(('World', 'Deaths'))) 
df_recovered = df_recovered.append(df_recovered.sum(numeric_only=True).rename(('World', 'Recovered'))) 
df_combined = pd.concat([df_confirmed,df_deaths,df_recovered]).sort_values(by=["Country", "Status"])
df_combined.columns = pd.to_datetime(df_combined.columns)
country_list = df_combined.index.get_level_values(0).unique().tolist()

#Malaysia Daily Confirmed Cases in Timeseries
url_cases_malaysia = "https://raw.githubusercontent.com/MoH-Malaysia/covid19-public/main/epidemic/cases_malaysia.csv"
df_daily_cases = pd.read_csv(url_cases_malaysia, usecols=['date','cases_new', 'cases_import', 'cases_active', 'cases_unvax', 'cases_pvax', 'cases_child', 'cases_adult', 'cases_elderly'])
df_daily_cases['date'] = pd.to_datetime(df_daily_cases['date'])
df_daily_cases = df_daily_cases.groupby(['date']).sum()
fig_daily_cases = go.FigureWidget(data = [
                              go.Scatter(name = "New Cases", y=df_daily_cases['cases_new'], x=df_daily_cases.index),
                              ],
                              layout = go.Layout(plot_bgcolor = "#EEEEEE"))
fig_daily_cases.update_layout(title='Malaysia Daily Confirmed Cases', title_x=0.5)
fig_daily_cases.update_yaxes(title='Cases')

#Malaysia Daily Death Cases in Timeseries
url_death_malaysia = "https://raw.githubusercontent.com/MoH-Malaysia/covid19-public/main/epidemic/deaths_malaysia.csv"
df_daily_death = pd.read_csv(url_death_malaysia, usecols=['date','deaths_new'])
df_daily_death['date'] = pd.to_datetime(df_daily_death['date'])
df_daily_death = df_daily_death.groupby(['date']).sum()
fig_daily_death = go.FigureWidget(data = [
                              go.Scatter(name = "Deaths", y=df_daily_death['deaths_new'], x=df_daily_death.index),
                              ],
                              layout = go.Layout(plot_bgcolor = "#EEEEEE"))
fig_daily_death.update_layout(title='Malaysia Daily Death Cases', title_x=0.5)
fig_daily_death.update_yaxes(title='Cases')

#Malaysia Daily Vaccinations in timeseries
url_vax_malaysia= "https://raw.githubusercontent.com/CITF-Malaysia/citf-public/main/vaccination/vax_malaysia.csv"
df_vax = pd.read_csv(url_vax_malaysia)
df_vax['date'] = pd.to_datetime(df_vax['date'])
df_vax = df_vax.groupby(['date']).sum()
fig_vax = go.Figure(
    data=[
          go.Bar(name="Partially Vaccinated",x=df_vax.index, y=df_vax['daily_partial']),
          go.Bar(name="Fully Vaccinated",x=df_vax.index, y=df_vax['daily_full']),
          go.Bar(name="Booster",x=df_vax.index, y=df_vax['daily_booster'])
    ]
)
fig_vax.update_layout(
    barmode='stack',
    title="Daily Covid-19 Vaccinations in Malaysia",
    xaxis_title="Date",
    yaxis_title="Count")

#Malaysia Daily Confirmed Cases by State
url_cases_states = "https://raw.githubusercontent.com/MoH-Malaysia/covid19-public/main/epidemic/cases_state.csv"
df_cases_states = pd.read_csv(url_cases_states)
df_cases_states['date'] =pd.to_datetime(df_cases_states['date'])
df_cases_states = df_cases_states.set_index('date')
df_cases_states = df_cases_states.pivot_table(index='date', columns='state', values='cases_new')

#Malaysia Daily Death Cases by State
url_death_states = "https://raw.githubusercontent.com/MoH-Malaysia/covid19-public/main/epidemic/deaths_state.csv"
df_death_states = pd.read_csv(url_death_states)
df_death_states['date'] = pd.to_datetime(df_death_states['date'])
df_death_states = df_death_states.set_index('date')
df_death_states = df_death_states.pivot_table(index='date', columns='state', values='deaths_new')

#Malaysia Daily Hospital Admission Rate by State
url_hosp_states = "https://raw.githubusercontent.com/MoH-Malaysia/covid19-public/main/epidemic/hospital.csv"
df_hosp_states = pd.read_csv(url_hosp_states, usecols=['date','state', 'beds_covid', 'hosp_covid'])
df_hosp_states['date'] = pd.to_datetime(df_hosp_states['date'])
df_hosp_states = df_hosp_states.set_index('date')
df_hosp_states['hosp_admission_rate'] = df_hosp_states['hosp_covid']/df_hosp_states['beds_covid']*100
df_hosp_states=df_hosp_states.pivot_table(index='date', columns='state', values='hosp_admission_rate')

app.layout = html.Div(
    style={'margin': '0px auto', 'width': '75%'},
    children=[
    html.H1(children='Covid-19 Dashboard'),

    html.Br(),
    
    #World cases
    html.Div(
        className='cardBackground', 
        children = [
        html.H2(children='Worldwide Cumulative Confirmed and Death Cases'),

        dcc.Dropdown(
                id="DropDownManager",
                options=[{
                    'label': i,
                    'value': i
                } for i in country_list],
                value='World'
        ),

        html.Br(),

        dcc.Graph(
            id='ww-graph'
        )
    ]), 

    html.Br(),

    #Asean cases
    html.Div(
        className='cardBackground', 
        children = [
        html.H2(children='ASEAN Confirmed, Deaths, and Recovered Cases'),

        dcc.Dropdown(
                id="DropDownManager2",
                options=[
                    {'label': 'Confirmed', 'value': 'Confirmed'},
                    {'label': 'Deaths', 'value': 'Deaths'},
                    {'label': 'Recovered', 'value': 'Recovered'}
                    ],
                value='Confirmed'
        ),

        html.Br(),

        dcc.Graph(
            id='ww2-graph'
        ) 
    ]),

    html.Br(),

    #Malaysia cases (total)
    html.Div(
        className='cardBackground',
        children=[
            html.H2("Trend of Malaysia Daily New Confirmed & Death Cases"),

            html.Div(
                children=[
                    html.Div(
                        className='flex-container',
                        children=[
                            html.Div(
                                className='flex-item',
                                children=[
                                    html.Div(
                                        className='flex-fig',
                                        children=[dcc.Graph(figure=fig_daily_cases)])
                                ]
                            ),
                            html.Div(
                                className='flex-item',
                                children=[
                                    html.Div(
                                        className='flex-fig',
                                        children=[dcc.Graph(figure=fig_daily_death)]
                                    )
                                ]
                            )
                        ]
                ),
            ]),
        ]
    ),
             
    html.Br(),

    #Malaysia cases (by state)
    html.Div(
        className='cardBackground', 
        children = [
        html.H2(children='Malaysia Cases, Deaths and Hospital Admission Rate per State'),

        dcc.Tabs([
            dcc.Tab(label='Cases', children=[
                dcc.Graph(
                    figure={
                        'data': [
                            go.Bar(name = "Hospital Admission Rate", y=df_cases_states.columns, x=df_cases_states.iloc[-1], orientation = 'h')
                        ],
                        'layout': {
                            'title': "Daily Confirmed Cases Updated on " + str(df_cases_states.iloc[-1].name)
                        }
                    }
                )
            ]),
            dcc.Tab(label='Death', children=[
                dcc.Graph(
                    figure={
                        'data': [
                            go.Bar(name = "Hospital Admission Rate", y=df_death_states.columns, x=df_death_states.iloc[-1], orientation = 'h')
                        ],
                        'layout': {
                            'title': "Daily Death Cases Updated on " + str(df_cases_states.iloc[-1].name)
                        }
                    }
                )
            ]),
            dcc.Tab(label='Hospital Admission Rate', children=[
                dcc.Graph(
                    figure={
                        'data': [
                            go.Bar(name = "Hospital Admission Rate", y=df_hosp_states.columns, x=df_hosp_states.iloc[-1], orientation = 'h')
                        ],
                        'layout': {
                            'title': "Daily Hospital Admission Rate Updated on " + str(df_hosp_states.iloc[-1].name)
                        }
                    }
                )
            ])
        ])
    ]),

    html.Br(),

    #Malaysia Vaccine
    html.Div(
        className='cardBackground', 
        children = [
        html.H2(children='Malaysia Daily Vaccinations'),

        dcc.Graph(
            figure=fig_vax
        )
    ])
])

@app.callback(
    dash.dependencies.Output('ww-graph', 'figure'),
    dash.dependencies.Input('DropDownManager', 'value'))

def update_graph(value):
    country = value 

    fig = make_subplots(specs=[[{"secondary_y" : True}]])
    fig.add_trace(go.Bar(x = df_combined.columns, y = df_combined.loc[country, "Confirmed"], name = "Confirmed"), secondary_y = False)
    fig.add_trace(go.Line(x = df_combined.columns, y = df_combined.loc[country, "Deaths"], name = "Deaths"), secondary_y = True)
    fig.update_yaxes(title_text="Confirmed Cases", secondary_y=False)
    fig.update_yaxes(title_text="Death Cases", secondary_y=True)
    fig.update_layout(title_text = country + " Confirmed Cases vs Death Cases")
    return fig

@app.callback(
    dash.dependencies.Output('ww2-graph', 'figure'),
    dash.dependencies.Input('DropDownManager2', 'value'))

def update_graph(value):
    input = value 
    fig = go.FigureWidget(data = [
                              go.Scatter(name = "Malaysia", x = df_combined.columns, y = df_combined.loc["Malaysia", input]),
                              go.Scatter(name = "Singapore", x = df_combined.columns, y = df_combined.loc["Singapore", input]),
                              go.Scatter(name = "Thailand", x = df_combined.columns, y = df_combined.loc["Thailand", input]),
                              go.Scatter(name = "Indonesia", x = df_combined.columns, y = df_combined.loc["Indonesia", input]),
                              go.Scatter(name = "Philippines", x = df_combined.columns, y = df_combined.loc["Philippines", input]),
                              go.Scatter(name = "Laos", x = df_combined.columns, y = df_combined.loc["Laos", input]),
                              go.Scatter(name = "Cambodia", x = df_combined.columns, y = df_combined.loc["Cambodia", input]),
                              go.Scatter(name = "Brunei", x = df_combined.columns, y = df_combined.loc["Brunei", input]),
                              go.Scatter(name = "Vietnam", x = df_combined.columns, y = df_combined.loc["Vietnam", input]),
                              go.Scatter(name = "Burma", x = df_combined.columns, y = df_combined.loc["Burma", input])
                              ],
                              layout = go.Layout(plot_bgcolor = "#EEEEEE"))
    fig.update_layout(title_text = input + " Cases among ASEAN countries")
    fig.update_yaxes(title_text="Cases")
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)

