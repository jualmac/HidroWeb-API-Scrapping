# Hidroweb-API
Scripts próprios produzidos para a coleta de dados através da REST API do HidroWeb e armazenamento em um banco de dados.

Extrai dados dos principais endpoints disponíveis em https://www.ana.gov.br/hidrowebservice/swagger-ui/index.html#/

Os scripts dividem as datas de coletas (nos endpoints na qual a mesma é relevante) em batches de 30 dias, para contornar a limitação de 30 dias de consulta na API;

# Utilização do scrapper

## 1) Endpoints comuns (sem station code)

Executa todos os endpoints comuns:

`python3 endpoint_common.py --endpoints all`

Executa apenas endpoints específicos:

`python3 endpoint_common.py --endpoints HidroUF HidroBacia`

Controle do modo de escrita no banco:

- `--inplace`: sobrescreve a tabela de destino (padrão);
- `--no-inplace`: faz append na tabela de destino;

Exemplo com append:

`python3 endpoint_common.py --endpoints HidroUF --no-inplace`

## 2) Endpoints chunkados (com station code e janela de datas)

Executa todos os endpoints chunkados para uma estação:

`python3 endpoint_chunk.py --endpoints all --stationcode 87450004`

Executa endpoint específico para múltiplas estações (lista por espaço):

`python3 endpoint_chunk.py --endpoints HidroinfoanaSerieTelemetricaDetalhada_v1 --stationcode 87450004 87444000 87399000`

Também aceita lista separada por vírgula:

`python3 endpoint_chunk.py --endpoints HidroinfoanaSerieTelemetricaAdotada_v2 --stationcode 87450004,87444000,87399000`

Executa com janela de datas customizada:

`python3 endpoint_chunk.py --endpoints all --stationcode 87450004 87444000 --start-date 2020-01-01 --end-date 2020-12-31`

Controle do modo de escrita no banco:

- `--inplace`: sobrescreve a tabela de destino (padrão);
- `--no-inplace`: faz append na tabela de destino;

# Mapeamento dos Endpoints:
* "/EstacoesTelemetricas/HidrosatSerieDados/v1": Séries das estações virtuais (HidroSat). Deve ser informado o código de estação (consulta HidroSatInventarioEstacoes) e período (limitado a 366 dias por requisição).
* "/EstacoesTelemetricas/HidrosatInventarioEstacoes/v1": Inventário de estações virtuais (estimação por satélite) cadastradas na base HidroSat. Não há limitação de busca por requisição.
* "/EstacoesTelemetricas/HidroinfoanaSerieTelemetricaDetalhada/v1": Séries das estações telemétricas. Além dos dados adotados, são retornados também os dados brutos disponíveis. Deve ser informado o código da estação e período (limitado a 30 dias por requisição).
* "/EstacoesTelemetricas/HidroinfoanaSerieTelemetricaDetalhada/v2": Séries das estações telemétricas. Além dos dados adotados, são retornados também os dados brutos disponíveis. Deve ser informado o código da estação (separadas por vírgula - MÁXIMO 10) e período (limitado a 30 dias por requisição).
* "/EstacoesTelemetricas/HidroinfoanaSerieTelemetricaAdotada/v1": Séries das estações telemétricas. Retorna os dados adotados de chuva, nível e vazão. Deve ser informado o código da estação e período (limitado a 30 dias por requisição).
* "/EstacoesTelemetricas/HidroinfoanaSerieTelemetricaAdotada/v2": Séries das estações telemétricas. Retorna os dados adotados de chuva, nível e vazão. Deve ser informado o código da estação (separadas por vírgula - MÁXIMO 10) e período (limitado a 30 dias por requisição).
* "/EstacoesTelemetricas/HidroUF/v1": Lista de unidades federativas cadastradas na base HIDRO. Não há limitação de busca por requisição.
* "/EstacoesTelemetricas/HidroSubBacia/v1": Lista de sub-bacias hidrográficas cadastradas na base HIDRO. Não há limitação de busca por requisição.
* "/EstacoesTelemetricas/HidroSerieVazao/v1": Séries de vazão das estações convencionais (coleta manual). Deve ser informado o código de estação e período (limitado a 366 dias por requisição).
* "/EstacoesTelemetricas/HidroSerieSedimentos/v1": Séries de sedimento das estações convencionais (coleta manual). Deve ser informado o código de e período (limitado a 366 dias por requisição).
* "/EstacoesTelemetricas/HidroSerieResumoDescarga/v1": Séries de medições de descarga líquida das estações. Deve ser informado o código de estação (consulta HidroInventarioEstacoes) e período (limitado a 366 dias por requisição).
* "/EstacoesTelemetricas/HidroSerieQA/v1": Séries de qualidade de água das estações convencionais (coleta manual). Deve ser informado o código de estação e período (limitado a 366 dias por requisição).
* "/EstacoesTelemetricas/HidroSeriePerfilTransversal/v1": Séries de medições do perfil transversal das estações. Deve ser informado o código de estação e período (limitado a 366 dias por requisição).
* "/EstacoesTelemetricas/HidroSerieGranulometria/v1": Série de Granulometria para as estações. Deve ser informado o código de estação e período (limitado a 366 dias por requisição).
* "/EstacoesTelemetricas/HidroSerieCurvaDescarga/v1": Série de curvas de descarga líquida traçadas para as estações. Deve ser informado o código de estação período (limitado a 366 dias por requisição).
* "/EstacoesTelemetricas/HidroSerieCotas/v1": Séries de cota das estações convencionais (coleta manual). Deve ser informado o código de estação e período (limitado a 366 dias por requisição).
* "/EstacoesTelemetricas/HidroSerieChuva/v1": Séries de chuva das estações convencionais (coleta manual). Deve ser informado o código de estação e período (limitado a 366 dias por requisição).
* "/EstacoesTelemetricas/HidroRio/v1": Lista de corpos hídricos cadastrados na base HIDRO. Não há limitação de busca por requisição.
* "/EstacoesTelemetricas/HidroMunicipio/v1": Lista de municípios cadastrados na base HIDRO. Ressalta-se que a base Hidro usa um código diferente do IBGE. Não há limitação de busca por requisição.
* "/EstacoesTelemetricas/HidroInventarioEstacoes/v1": Inventário completo de estações cadastradas na base Hidro. Deve ser informado, ao menos, um dos seguintes filtros: Cód. Estação, Cód. Bacia ou UF.
* "/EstacoesTelemetricas/HidroEntidade/v1": Lista de entidades cadastradas na base Hidro. As entidades são utilizadas para caracterizar o responsável e operador das estações. Não há limitação de busca por requisição.
* "/EstacoesTelemetricas/HidroBacia/v1": Lista de bacias hidrográficas cadastradas na base Hidro. Não há limitação de busca por requisição.

# TODO:
* Testar todos endpoints;
* Corrigir HEADERS;