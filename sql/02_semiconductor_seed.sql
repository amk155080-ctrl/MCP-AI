INSERT INTO mcp4.semiconductor_universe
(stock_code, stock_name, hbm_flag, hbf_flag, cxl_flag, pim_flag, ai_server_flag, packaging_flag, osat_flag, foundry_flag, weight_score)
VALUES
('000660','SK하이닉스',true,true,true,false,true,false,false,false,25),
('005930','삼성전자',true,true,true,true,true,true,false,true,22),
('042700','한미반도체',true,true,false,false,true,true,false,false,23),
('089030','테크윙',true,false,false,false,true,false,false,false,18),
('095340','ISC',true,false,true,false,true,false,false,false,18),
('039030','이오테크닉스',true,false,false,false,true,true,false,false,17),
('058470','리노공업',false,false,true,false,true,false,false,false,16),
('240810','원익IPS',false,false,false,false,false,true,false,false,14),
('036930','주성엔지니어링',false,false,false,false,false,true,false,false,14),
('319660','피에스케이',false,false,false,false,false,true,false,false,13),
('084370','유진테크',false,false,false,false,false,true,false,false,13),
('403870','HPSP',false,false,false,false,true,true,false,false,16),
('067310','하나마이크론',false,false,false,false,true,false,true,false,14),
('222800','심텍',false,false,false,false,true,false,false,false,12)
ON CONFLICT (stock_code) DO UPDATE SET
stock_name=EXCLUDED.stock_name, hbm_flag=EXCLUDED.hbm_flag, hbf_flag=EXCLUDED.hbf_flag,
cxl_flag=EXCLUDED.cxl_flag, ai_server_flag=EXCLUDED.ai_server_flag,
packaging_flag=EXCLUDED.packaging_flag, osat_flag=EXCLUDED.osat_flag,
foundry_flag=EXCLUDED.foundry_flag, weight_score=EXCLUDED.weight_score;
