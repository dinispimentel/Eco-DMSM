# Eco-DMSM
Eco-DMSM é um servidor http-python que analisa o mercado DMarket sob uma série de filtros e compara os preços com os do Mercado Steam. Devolve, principalmente, as entradas que tiverem menor preço (médio, único) no DMarket.

## Pontos-chave
  - Multi-threaded (python multithreaded, global locked)
  - Compatível com Redis cache
  - Compatível com uso de proxies para remover restrições de throtling.
  - Flexivél (Muitos filtros diferentes)
  - Baseado em API reliable do DMarket
  - Barra de progresso Websocket realtime \*broken\*

 # Disclaimer

Todo o uso dado a este programa é ético e aceitável sob os termos de serviço da Steam e DMarket.

Este projeto ([EcoGaming](https://github.com/dinispimentel/EcoGaming/) e associados) são um proof-of-concept antigo, pouco eficazes e possivelmente não funcionais. 
Não é dado suporte para nada relacionado a estes módulos/projeto.
