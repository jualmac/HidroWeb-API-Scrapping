# Hidroweb-API
Scripts próprios produzidos para a coleta de dados através da REST API do HidroWeb e armazenamento em um banco de dados.

Extrai dados dos principais endpoints disponíveis em https://www.ana.gov.br/hidrowebservice/swagger-ui/index.html#/

Os scripts dividem as datas de coletas (nos endpoints na qual a mesma é relevante) em batches de 30 dias, para contornar a limitação de 30 dias de consulta na API;

# TODO
* Colocar todos os requests simples no mesmo -> Criar uma classe com um método base (oq está agora em endpoint_common);