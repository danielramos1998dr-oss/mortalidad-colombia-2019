"""Agregaciones compartidas por el dashboard y las pruebas."""
from pathlib import Path
import pandas as pd
BASE=Path(__file__).resolve().parent
AGE_GROUPS=[('Mortalidad neonatal',0,4,'Menor de 1 mes'),('Mortalidad infantil',5,6,'1–11 meses'),('Primera infancia',7,8,'1–4 años'),('Niñez',9,10,'5–14 años'),('Adolescencia',11,11,'15–19 años'),('Juventud',12,13,'20–29 años'),('Adultez temprana',14,16,'30–44 años'),('Adultez intermedia',17,19,'45–59 años'),('Vejez',20,24,'60–84 años'),('Longevidad / Centenarios',25,28,'85–100+ años'),('Edad desconocida',29,29,'Sin información')]
SEX={1:'Masculino',2:'Femenino',3:'Indeterminado'}
MONTHS=['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic']

def load_data():
    d=pd.read_csv(BASE/'data/mortalidad.csv.gz',dtype={'COD_DANE':str,'COD_DEPARTAMENTO':str})
    d['Sexo']=d.SEXO.map(SEX).fillna('Sin información')
    ages={i:name for name,a,b,_ in AGE_GROUPS for i in range(a,b+1)}
    d['Edad']=d.GRUPO_EDAD1.map(ages).fillna('Sin clasificación')
    return d

def filter_data(d,department='ALL',months=None,sex='ALL'):
    q=d
    if department!='ALL': q=q[q.COD_DEPARTAMENTO.eq(department)]
    if months: q=q[q.MES.between(*months)]
    if sex!='ALL': q=q[q.Sexo.eq(sex)]
    return q

def counts(d,keys):
    return d.groupby(keys,dropna=False).size().reset_index(name='Muertes')

def cities(d,ascending=False,n=5,x95=False):
    q=d[d.COD_MUERTE.str.startswith('X95',na=False)] if x95 else d
    q=q[q.MUNICIPIO.ne('Sin homologar')]
    c=counts(q,['COD_DANE','MUNICIPIO','DEPARTAMENTO'])
    c=c.sort_values(['Muertes','COD_DANE'],ascending=[ascending,True]).head(n)
    c['Ciudad']=c.MUNICIPIO+' · '+c.DEPARTAMENTO
    return c

def top_causes(d):
    c=counts(d,['COD_MUERTE']).sort_values(['Muertes','COD_MUERTE'],ascending=[False,True]).head(10)
    catalog=pd.read_csv(BASE/'data/causas.csv').set_index('codigo').nombre
    c['Causa']=c.COD_MUERTE.map(catalog).fillna('Código sin descripción en el catálogo suministrado')
    return c.rename(columns={'COD_MUERTE':'Código'})[['Código','Causa','Muertes']]
