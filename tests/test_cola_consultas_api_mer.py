import datetime as dt,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from cola_consultas_api_mer import build,checkpoint
H=["codigo","fecha_publicacion","categoria"]
D=dt.date(2026,10,28)
class QueueTests(unittest.TestCase):
 def test_priority_and_no_duplicates(self):
  p=[H,["1-1-COT26","2026-10-28","Compra Ágil"],
    ["1-1-COT26","2026-10-28","Compra Ágil"],
    ["2-2-COT26","2026-10-26","Compra Ágil"],
    ["3-3-COT26","2026-10-20","Compra Ágil"],
    ["4-4-COT26","2026-10-20","Compra Ágil"],
    ["5-5-LE26","2026-10-28","Licitaciones"]]
  states={"2-2-COT26":{"estado":"ERROR","proximo_intento":"2026-10-27"},
          "3-3-COT26":{"estado":"EN_SEGUIMIENTO","proxima_revision":"2026-10-28"},
          "4-4-COT26":{"estado":"COMPLETO"}}
  x=build(p,states,D,budget=3)
  self.assertEqual([c["codigo"] for c in x["consultas"]],["1-1-COT26","2-2-COT26","3-3-COT26"])
  self.assertEqual(len({c["codigo"] for c in x["consultas"]}),3)
 def test_failed_etl_blocks_new(self):
  p=[H,["1-1-COT26","2026-10-28","Compra Ágil"],["2-2-COT26","2026-10-28","Compra Ágil"]]
  s={"2-2-COT26":{"estado":"ERROR","proximo_intento":"2026-10-28"}}
  self.assertEqual([x["codigo"] for x in build(p,s,D,etlp_ok=False)["consultas"]],["2-2-COT26"])
 def test_checkpoint(self):
  x=checkpoint({},"1-1-COT26","error",D,error="HTTP 429")
  self.assertEqual(x["1-1-COT26"]["proximo_intento"],"2026-10-29")
  y=checkpoint(x,"1-1-COT26","ok_pendiente",D,sha="sha")
  self.assertEqual(y["1-1-COT26"]["proxima_revision"],"2026-10-30")
  z=checkpoint(y,"1-1-COT26","ok_completo",D)
  self.assertEqual(z["1-1-COT26"]["estado"],"COMPLETO")
 def test_old_not_initially_queried(self):
  p=[H,["1-1-COT26","2026-07-21","Compra Ágil"]]
  self.assertEqual(build(p,{},D)["consultas"],[])
if __name__=="__main__":unittest.main()
