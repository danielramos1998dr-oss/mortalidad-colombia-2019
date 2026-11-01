"""Transformación reproducible de los tres anexos; no elimina duplicados sin identificador."""
from pathlib import Path
import hashlib
import json
import pandas as pd
BASE = Path(__file__).resolve().parent

def prepare():
    raw = BASE / 'data/raw'
    df = pd.read_excel(raw/'Anexo1.NoFetal2019_CE_15-03-23.xlsx', sheet_name='No_Fetales_2019', dtype={'COD_DANE':str,'COD_DEPARTAMENTO':str,'COD_MUNICIPIO':str})
    assert df['AÑO'].eq(2019).all(), 'Se encontraron años diferentes de 2019'
    for col, width in [('COD_DANE',5),('COD_DEPARTAMENTO',2),('COD_MUNICIPIO',3)]:
        df[col] = df[col].str.strip().str.zfill(width)
    assert df.COD_DANE.eq(df.COD_DEPARTAMENTO + df.COD_MUNICIPIO).all()
    df['COD_MUERTE'] = df.COD_MUERTE.str.strip().str.upper().str.replace('.', '', regex=False)
    div = pd.read_excel(raw/'Divipola_CE_.xlsx',sheet_name='Hoja1',dtype=str)
    div['COD_DANE'] = div.COD_DANE.str.zfill(5)
    div['COD_DEPARTAMENTO'] = div.COD_DEPARTAMENTO.str.zfill(2)
    assert not div.COD_DANE.duplicated().any()
    df = df.merge(div[['COD_DANE','DEPARTAMENTO','MUNICIPIO']],on='COD_DANE',how='left',validate='many_to_one')
    dept = div.set_index('COD_DEPARTAMENTO').DEPARTAMENTO.to_dict()
    df['DEPARTAMENTO'] = df.DEPARTAMENTO.fillna(df.COD_DEPARTAMENTO.map(dept)).fillna('Sin homologar')
    df['MUNICIPIO'] = df.MUNICIPIO.fillna('Sin homologar')
    cols = ['COD_DANE','COD_DEPARTAMENTO','DEPARTAMENTO','MUNICIPIO','MES','SEXO','GRUPO_EDAD1','COD_MUERTE']
    df[cols].to_csv(BASE/'data/mortalidad.csv.gz',index=False,compression={'method':'gzip','mtime':0})
    causes = pd.read_excel(raw/'Anexo2.CodigosDeMuerte_CE_15-03-23.xlsx',sheet_name='Final',header=8)
    three = causes.iloc[:,[2,3]].dropna()
    three.columns = ['codigo','nombre']
    causes = causes.iloc[:,[4,5]].dropna()
    causes.columns = ['codigo','nombre']
    causes = pd.concat([causes,three],ignore_index=True)
    causes.codigo = causes.codigo.astype(str).str.strip().str.upper().str.replace('.', '', regex=False)
    causes = causes.drop_duplicates('codigo')
    causes.to_csv(BASE/'data/causas.csv',index=False)
    geo = pd.read_excel(raw/'Divipola_CE_.xlsx',sheet_name='Hoja3',header=1,dtype=str)
    geo = geo.iloc[:,[0,1,2,5,6]]
    geo.columns = ['codigo','nombre','municipio','lon','lat']
    geo = geo[geo.municipio.str.endswith('001',na=False)].copy()
    geo.codigo = geo.codigo.str.zfill(2)
    for c in ['lon','lat']: geo[c]=pd.to_numeric(geo[c].str.replace(',','.',regex=False),errors='coerce')
    assert geo.codigo.nunique()==33 and geo[['lon','lat']].notna().all().all()
    geo[['codigo','nombre','lon','lat']].to_csv(BASE/'data/departamentos.csv',index=False)
    audit = {'registros':len(df),'municipios_sin_homologar':int(df.MUNICIPIO.eq('Sin homologar').sum()),'causas_sin_catalogo':int((~df.COD_MUERTE.isin(causes.codigo)).sum()),'meses':df.MES.value_counts().sort_index().to_dict(),'sexo':df.SEXO.value_counts().sort_index().to_dict(),'fuentes_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in raw.glob('*.xlsx')}}
    (BASE/'data/auditoria.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(audit,ensure_ascii=False,indent=2))
if __name__=='__main__': prepare()
