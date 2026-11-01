import unittest
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from analysis import *
class AnalysisTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls): cls.d=load_data()
 def test_totals(self):
  self.assertEqual(len(self.d),244355)
  for keys in [['MES'],['Sexo'],['Edad'],['COD_DEPARTAMENTO']]: self.assertEqual(counts(self.d,keys).Muertes.sum(),244355)
  self.assertEqual(self.d.Sexo.value_counts().to_dict(),{'Masculino':134573,'Femenino':109689,'Indeterminado':93})
 def test_age_boundaries(self):
  self.assertTrue(self.d.loc[self.d.GRUPO_EDAD1.eq(4),'Edad'].eq('Mortalidad neonatal').all())
  self.assertTrue(self.d.loc[self.d.GRUPO_EDAD1.eq(5),'Edad'].eq('Mortalidad infantil').all())
  self.assertEqual(self.d.Edad.eq('Edad desconocida').sum(),23)
  self.assertFalse(self.d.Edad.eq('Sin clasificación').any())
 def test_filters(self):
  q=filter_data(self.d,'52',[1,3],'Femenino')
  self.assertGreater(len(q),0)
  self.assertTrue(q.COD_DEPARTAMENTO.eq('52').all() and q.MES.between(1,3).all() and q.Sexo.eq('Femenino').all())
  self.assertEqual(len(filter_data(self.d,'52',[1,12])),7837)
 def test_ranking(self):
  c=top_causes(self.d)
  self.assertEqual(c.iloc[0]['Código'],'I219');self.assertEqual(c.iloc[0].Muertes,35088)
  self.assertFalse(c.Causa.str.startswith('Código sin').any())
  self.assertTrue(c.Muertes.is_monotonic_decreasing)
  low=cities(self.d,ascending=True,n=10)
  self.assertEqual(len(low),10);self.assertTrue(low.Muertes.gt(0).all())
  for row in cities(self.d,x95=True).itertuples():
   self.assertEqual(row.Muertes,len(self.d[self.d.COD_DANE.eq(row.COD_DANE)&self.d.COD_MUERTE.str.startswith('X95')]))
 def test_app_callback(self):
  from app import app,update,reset
  client=app.server.test_client()
  for url in ['/','/_dash-layout','/_dash-dependencies','/health']: self.assertEqual(client.get(url).status_code,200)
  for args in [('ALL',[1,12],'ALL'),('52',[3,8],'Femenino'),('97',[1,1],'Indeterminado')]:
   r=update(*args);self.assertEqual(len(r),9)
   for i in [2,3,4,5,7,8]: r[i].to_json()
  self.assertEqual(reset(1),('ALL','ALL',[1,12]))
if __name__=='__main__': unittest.main()
