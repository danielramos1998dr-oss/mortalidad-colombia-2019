"""Dashboard de mortalidad no fetal: Colombia, 2019."""
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, Input, Output, State, dcc, html, dash_table
from analysis import BASE, AGE_GROUPS, SEX, MONTHS, load_data, filter_data, counts, cities, top_causes
DATA=load_data()
GEO=pd.read_csv(BASE/'data/departamentos.csv',dtype={'codigo':str})
BLUE='#176b91'
TEAL='#12a89d'
COLORS={'Masculino':BLUE,'Femenino':TEAL,'Indeterminado':'#b58430','Sin información':'#8594a2'}
app=Dash(__name__,title='Mortalidad Colombia · 2019',update_title='Actualizando…')
server=app.server

@server.get('/health')
def health(): return {'status':'ok','registros':len(DATA)}


def panel(title, note, id, wide=False):

    graph_frame = 'chart-frame'

    if id == 'sex-chart':
        graph_frame += ' chart-frame--tall'
    elif id == 'age':
        graph_frame += ' chart-frame--age'

    return html.Section([
        html.H2(title),
        html.P(note, className='note'),

        html.Div(
            dcc.Graph(
                id=id,
                responsive=True,
                style={
                    'width': '100%',
                    'height': '100%',
                    'minWidth': 0,
                    'minHeight': 0
                },
                config={
                    'topojsonURL': '/assets/',
                    'displaylogo': False,
                    'toImageButtonOptions': {
                        'format': 'png',
                        'scale': 2
                    }
                }
            ),
            className=graph_frame
        )
    ], className='panel wide' if wide else 'panel')


def polish(fig,height=390):
    fig.update_layout(template='plotly_white',font={'family':'Arial','color':'#173448','size':12},margin={'l':30,'r':25,'t':24,'b':55},height=height,paper_bgcolor='white',colorway=[BLUE,TEAL,'#eaac4c'],legend_title_text='',hoverlabel={'bgcolor':'white'},separators=',.')
    return fig

def empty():
    f=go.Figure(); f.add_annotation(text='No hay registros para esta selección',showarrow=False,x=.5,y=.5,xref='paper',yref='paper');f.update_xaxes(visible=False);f.update_yaxes(visible=False)
    return polish(f)

app.layout=html.Div([
    html.Header([html.Div('ANÁLISIS DE DATOS  /  ESTADÍSTICAS VITALES',className='eyebrow'),html.Div([html.Div([html.H1(['Mortalidad en Colombia',html.Span('2019',className='year')]),html.P('Una mirada territorial, temporal y demográfica a las defunciones no fetales.')]),html.Div('PYTHON + DASH',className='badge')],className='hero-row')]),
    html.Main([
        html.Div([html.Div([html.Label('Departamento / Bogotá D. C.',htmlFor='department'),dcc.Dropdown(id='department',options=[{'label':'Colombia · todos','value':'ALL'}]+[{'label':r.DEPARTAMENTO,'value':r.COD_DEPARTAMENTO} for r in DATA[['COD_DEPARTAMENTO','DEPARTAMENTO']].drop_duplicates().sort_values('DEPARTAMENTO').itertuples()],value='ALL',clearable=False)]),html.Div([html.Label('Sexo',htmlFor='sex'),dcc.Dropdown(id='sex',options=[{'label':'Todos','value':'ALL'}]+[{'label':v,'value':v} for v in SEX.values()],value='ALL',clearable=False)]),html.Div([html.Label('Meses del año'),dcc.RangeSlider(id='months',min=1,max=12,step=1,value=[1,12],marks={i+1:m for i,m in enumerate(MONTHS)},allowCross=False)]),html.Button('Restablecer',id='reset',n_clicks=0)],className='filters'),
        html.Div(id='scope',className='scope'),html.Div(id='kpis',className='kpis'),
        html.Div([
            panel('01 / Distribución territorial','Total por departamento y Bogotá D. C. Burbujas ubicadas en sus capitales; no representan el lugar exacto de cada muerte.','map'),
            panel('02 / Evolución mensual','Conteos mensuales. Las diferencias no están ajustadas por el número de días de cada mes.','line'),
            panel('03 / Cinco municipios con más casos X95','Agresión con disparo de otras armas de fuego y las no especificadas. No incluye todos los homicidios ni mide riesgo por habitante.','violent'),
            panel('04 / Diez municipios con menos muertes','Solo municipios con al menos un registro. Porcentaje dentro de los diez seleccionados; no es una tasa poblacional. Empates: código DANE.','pie'),
            html.Section([html.H2('05 / Diez principales causas de muerte'),html.P('Código completo de la causa básica; descripción del catálogo adjunto. Orden descendente por casos.',className='note'),dash_table.DataTable(id='causes',columns=[{'name':x,'id':x} for x in ['Código','Causa','Muertes']],data=[],sort_action='native',style_table={'overflowX':'auto'},style_cell={'fontFamily':'Arial','fontSize':14,'padding':'12px','textAlign':'left','whiteSpace':'normal','height':'auto'},style_header={'backgroundColor':'#edf4f8','fontWeight':'bold'},style_cell_conditional=[{'if':{'column_id':'Muertes'},'textAlign':'right'},{'if':{'column_id':'Código'},'width':'90px'}],style_data_conditional=[{'if':{'row_index':'odd'},'backgroundColor':'#f8fbfd'}]),html.Button('Descargar tabla CSV',id='download-button'),dcc.Download(id='download')],className='panel wide'),
            panel('06 / Muertes por sexo y departamento','Barras apiladas en números absolutos. Incluye la categoría indeterminado.','sex-chart',True),
            panel('07 / Distribución por ciclo de vida','Histograma de frecuencias agrupadas según la tabla de la actividad. Rangos de amplitud desigual: se muestran casos, no densidades.','age',True)
        ],className='grid'),
        html.Details([html.Summary('Metodología y límites de interpretación'),html.P('Cada fila del anexo NoFetal2019 corresponde a una defunción registrada. No se eliminan filas iguales: no hay identificador único que permita concluir que sean duplicados. El cruce municipal usa cinco dígitos DANE y la causa se cruza por su código completo.'),html.P('Se interpreta la geografía del anexo como ocurrencia de la defunción, según la estructura de EEVV; no contiene residencia ni localización específica del hecho violento. Los conteos no permiten comparar riesgo sin denominadores poblacionales. La ausencia de registros no se considera prueba de cero defunciones.'),html.P('Se respeta la agrupación de edades de la consigna: neonatal 0–4 incluye 28–29 días; infantil 5–6 corresponde solo a 1–11 meses. Estas etiquetas académicas no sustituyen las definiciones de indicadores epidemiológicos. Edad desconocida (29) se conserva.'),html.P('El mapa utiliza un fondo geográfico general de Natural Earth distribuido por Plotly, incluido en assets. Las burbujas representan agregados departamentales y no sus límites administrativos. Los datos se cargan desde archivos locales.'),html.A('Consultar diccionario DANE EEVV 2019',href='https://microdatos.dane.gov.co/index.php/catalog/696',target='_blank')],className='method'),
        html.Footer('Fuente: anexos académicos suministrados · EEVV 2019 / DANE · Aplicación educativa')
    ])
])

@app.callback(Output('department','value'),Output('sex','value'),Output('months','value'),Input('reset','n_clicks'),prevent_initial_call=True)
def reset(_): return 'ALL','ALL',[1,12]

@app.callback(Output('kpis','children'),Output('scope','children'),Output('map','figure'),Output('line','figure'),Output('violent','figure'),Output('pie','figure'),Output('causes','data'),Output('sex-chart','figure'),Output('age','figure'),Input('department','value'),Input('months','value'),Input('sex','value'))
def update(department,months,sex):
    q=filter_data(DATA,department,months,sex)
    n=len(q); x95=int(q.COD_MUERTE.str.startswith('X95').sum())
    def card(label,value,detail): return html.Div([html.Small(label),html.Strong(f'{value:,}'.replace(',','.')),html.Span(detail)],className='kpi')
    kpis=[card('DEFUNCIONES',n,'registros en la selección'),card('MUNICIPIOS',q.loc[q.MUNICIPIO.ne('Sin homologar'),'COD_DANE'].nunique(),'con registros homologados'),card('AGRESIONES X95',x95,'subconjunto de causas externas'),card('EDAD DESCONOCIDA',int(q.GRUPO_EDAD1.eq(29).sum()),'registros conservados')]
    region='Colombia' if department=='ALL' else DATA.loc[DATA.COD_DEPARTAMENTO.eq(department),'DEPARTAMENTO'].iloc[0]
    scope=f'{region} · {MONTHS[months[0]-1]}–{MONTHS[months[1]-1]} 2019 · {"Todos los sexos" if sex=="ALL" else sex} · Todos los gráficos responden a estos filtros'
    if not n: return kpis,scope,empty(),empty(),empty(),empty(),[],empty(),empty()
    dep=counts(q,['COD_DEPARTAMENTO','DEPARTAMENTO'])
    mapped=dep.merge(GEO,left_on='COD_DEPARTAMENTO',right_on='codigo',validate='one_to_one')
    mp=px.scatter_geo(mapped,lat='lat',lon='lon',size='Muertes',color='Muertes',hover_name='DEPARTAMENTO',hover_data={'lat':False,'lon':False,'Muertes':True},size_max=48,color_continuous_scale='Teal',projection='mercator')
    mp.update_geos(lataxis_range=[-5,14],lonaxis_range=[-83,-66],showcountries=True,showland=True,landcolor='#edf3f5',countrycolor='#aabdc9',showocean=True,oceancolor='#f8fbfd',showframe=False)
    mp=polish(mp);mp.update_layout(margin={'l':0,'r':0,'t':0,'b':0},coloraxis_colorbar={'title':'Muertes','thickness':10,'len':.6})
    monthly=q.groupby('MES').size().reindex(range(months[0],months[1]+1),fill_value=0)
    line=px.line(x=[MONTHS[i-1] for i in monthly.index],y=monthly.values,markers=True,labels={'x':'Mes','y':'Muertes'})
    line.update_traces(line_color=BLUE,fill='tozeroy',fillcolor='rgba(23,107,145,.07)');line.update_yaxes(rangemode='tozero')
    v=cities(q,x95=True)
    violent=px.bar(v.sort_values('Muertes'),x='Muertes',y='Ciudad',orientation='h',text='Muertes') if len(v) else empty()
    violent.update_layout(yaxis_title=None);violent.update_traces(cliponaxis=False)
    low=cities(q,ascending=True,n=10)
    pie=px.pie(low,names='Ciudad',values='Muertes',hole=.48,color_discrete_sequence=px.colors.qualitative.Safe) if len(low) else empty()
    pie.update_traces(textinfo='percent',hovertemplate='%{label}<br>%{value} muertes<br>%{percent} de los diez<extra></extra>')
    stack=px.bar(counts(q,['DEPARTAMENTO','Sexo']),x='DEPARTAMENTO',y='Muertes',color='Sexo',color_discrete_map=COLORS,category_orders={'DEPARTAMENTO':dep.sort_values('Muertes',ascending=False).DEPARTAMENTO.tolist(),'Sexo':list(SEX.values())})
    stack.update_layout(barmode='stack',xaxis_title=None,xaxis_tickangle=-45)
    ages=counts(q,['Edad']).set_index('Edad').reindex([x[0] for x in AGE_GROUPS],fill_value=0).reset_index()
    ages['Rango']=[x[3] for x in AGE_GROUPS]
    age=px.bar(ages,x='Edad',y='Muertes',text='Muertes',hover_data=['Rango']);age.update_layout(bargap=.08,xaxis_title=None,xaxis_tickangle=-25)
    return kpis,scope,mp,polish(line),polish(violent),polish(pie),top_causes(q).to_dict('records'),polish(stack,470),polish(age,440)

@app.callback(Output('download','data'),Input('download-button','n_clicks'),State('department','value'),State('months','value'),State('sex','value'),prevent_initial_call=True)
def download(_,department,months,sex):
    return dcc.send_data_frame(top_causes(filter_data(DATA,department,months,sex)).to_csv,'principales_causas_2019.csv',index=False)

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('--port',type=int,default=int(os.environ.get('PORT',8050)))
    args,_=parser.parse_known_args()
    app.run(host='0.0.0.0',port=args.port,debug=False)
