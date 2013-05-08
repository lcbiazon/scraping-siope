Scraping do SIOPE-FNDE
======================

Coleta de informações do Sistema de Informações sobre Orçamento Públicos
em Educação - SIOPE do Fundo Nacional de Desenvolvimento da Educação -
FNDE.

O script monta uma tabela com os gastos com educação fundamental dos municípios
brasileiros - previsão atualizada e receitas realizadas das "despesas custeadas
com a receita resultante de impostos e recursos do FUNDEB".

É necessário o uso do Python 3, com os pacotes
[BeautifulSoup4](https://pypi.python.org/pypi/beautifulsoup4),
[PDFMiner3k](https://pypi.python.org/pypi/pdfminer3k) e 
[lxml](https://pypi.python.org/pypi/lxml/)

pip install beautifulsoup4
pip install pdfminer3k
pip3 install lxml

ou

pip3 install beautifulsoup4
pip3 install pdfminer3k
pip3 install lxml

Outra dependência é o [slate](https://pypi.python.org/pypi/slate), que já está incluso com
modificações para rodar no Python3.
