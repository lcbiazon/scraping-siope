#!/usr/bin/env python3
from urllib import request, parse
from bs4 import BeautifulSoup, SoupStrainer
import shutil
import os
from slate import PDF

anos = ['2006','2007','2008','2009','2010','2011','2012']
periodo = '1'

#lista tirada de http://www.ibge.gov.br/home/geociencias/areaterritorial/principal.shtm
ufs = [
    ['11', 'Rondônia'],
    ['12', 'Acre'],
    ['13', 'Amazonas'],
    ['14', 'Roraima'],
    ['15', 'Pará'],
    ['16', 'Amapá'],
    ['17', 'Tocantins'],
    ['21', 'Maranhão'],
    ['22', 'Piauí'],
    ['23', 'Ceará'],
    ['24', 'Rio Grande do Norte'],
    ['25', 'Paraíba'],
    ['26', 'Pernambuco'],
    ['27', 'Alagoas'],
    ['28', 'Sergipe'],
    ['29', 'Bahia'],
    ['31', 'Minas Gerais'],
    ['32', 'Espírito Santo'],
    ['33', 'Rio de Janeiro'],
    ['35', 'São Paulo'],
    ['41', 'Paraná'],
    ['42', 'Santa Catarina'],
    ['43', 'Rio Grande do Sul'],
    ['50', 'Mato Grosso do Sul'],
    ['51', 'Mato Grosso'],
    ['52', 'Goiás'],
    ['53', 'Distrito Federal']
]

#O nome da linha referente ao ensino fundamental muda nos formulários dos diferentes anos
#O segundo parâmetro indica o termo de sucede a seção procurada (no caso de parsing do pdf)
termos_de_busca = {
    '2006': ['ENSINO FUNDAMENTAL'],
    '2007': ['18 - ENSINO FUNDAMENTAL'],
    '2008': ['18 - ENSINO FUNDAMENTAL'],
    '2009': ['24 - ENSINO FUNDAMENTAL'],
    '2010': ['24- ENSINO FUNDAMENTAL', '24.1- Despesas Custeadas'],
    '2011': ['24- ENSINO FUNDAMENTAL', '24.1- Despesas Custeadas'],
    '2012': ['24- ENSINO FUNDAMENTAL', '24.1- Despesas Custeadas']
}

siope_url = "https://www.fnde.gov.br/siope/relatorioRREOMunicipal2009.do"
pdf_url = "ftp://ftp.fnde.gov.br/web/siope/RREO/RREO_Municipal"

def monta_lista_cidades():
    # Busca a lista de municipios de cada estado e acrescenta na lista ufs
    for uf in ufs:
        municipios = []
        parametros = {'acao': 'pesquisar',
                    'pag': 'result',
                    'periodos': periodo,
                    'anos': '2012',
                    'cod_uf': uf[0]}

        with request.urlopen(siope_url, parse.urlencode(parametros).encode('utf-8')) as resposta:
            soup = BeautifulSoup(resposta.read(), 'lxml')
            a = soup.find('select', {'name': 'municipios'})

            for i in a.findAll('option'):
                municipios.append((i['value'], i.text.replace('\r\n', '').strip()))

            uf.append(municipios)

def analisa_siope_pdf(ano, uf, cod_uf, municipio, cod_municipio):
    arquivo = os.path.join('arquivos', ano, cod_uf, cod_municipio + '.pdf')

    if not os.path.exists(os.path.dirname(arquivo)):
        os.makedirs(os.path.dirname(arquivo))

    url = pdf_url + '_' + cod_municipio + '_' + periodo + '_' + ano + '.pdf'

    #Baixa o arquivo pdf correspondente e o armazena localmente
    try:
        with request.urlopen(url) as resposta, open(arquivo, 'wb') as destino:
            shutil.copyfileobj(resposta, destino)
    #Quando o arquivo correspondente ao municipio e ano não existe, o FTP devolve um erro de permissao de acesso
    #(um exemplo é São Paulo - SP - 2012)
    except TypeError:
        return('%s\t%s [%s]\t%s [%s]\n' % (ano, uf, cod_uf, municipio, cod_municipio))

    #Parsing do PDF. Um horror.
    with open(arquivo, mode="rb") as f:
        doc = PDF(f)
        #Os valores desejados estão sempre (acho) na página 4 do PDF, entre os termos listados em 'termos_de_busca'
        colunas = doc[3][doc[3].index(termos_de_busca[ano][0])+len(termos_de_busca[ano][0]):doc[3].index(termos_de_busca[ano][1])]

        valores = []

        while(colunas.find(",") != -1):
            prox_indice = colunas.index(",") + 3
            valores.append(colunas[:prox_indice])
            colunas = colunas[prox_indice:]

        atualizada = valores[1]
        realizada = valores[-2]

        return('%s\t%s [%s]\t%s [%s]\t%s\t%s\n' % (ano, uf, cod_uf, municipio, cod_municipio, atualizada, realizada))

def analisa_siope_html(ano, uf, cod_uf, municipio, cod_municipio):
    parametros = {'acao': 'pesquisar',
                  'pag': 'result',
                  'periodos': periodo,
                  'anos': ano,
                  'cod_uf': cod_uf,
                  'municipios': cod_municipio}

    #monta a url conforme os parâmetros especificados e estabelece a conexão com o servidor
    pagina = request.urlopen(siope_url, parse.urlencode(parametros).encode('utf-8'))

    #joga fora todos os elementos da página que não as linhas de uma tabela - tr (table row)
    linhas = BeautifulSoup(pagina.read(), parse_only=SoupStrainer('tr'))

    try:
        #realiza a busca pelo texto determinado
        linha_alvo = linhas.find(text=termos_de_busca[ano][0]).parent.parent

        #uma vez com a linha alvo, é só filtrar as colunas (td) certas
        colunas = linha_alvo.findAll('td')
        atualizada = colunas[2].findChild().text
        realizada = colunas[4].findChild().text

        return('%s\t%s [%s]\t%s [%s]\t%s\t%s\n' % (ano, uf, cod_uf, municipio, cod_municipio, atualizada, realizada))

    #Se a operação de busca da linha alvo falhar (porque o município não existe, por exemplo),
    #a condição abaixo é executada
    except AttributeError:
        return('%s\t%s [%s]\t%s [%s]\n' % (ano, uf, cod_uf, municipio, cod_municipio))

if __name__ == '__main__':
    monta_lista_cidades()

    for ano in anos:
        for cod_uf, uf, municipios in ufs:
            for cod_municipio, municipio in municipios:
                if ano in ['2006','2007','2008','2009']:
                    nova_entrada = analisa_siope_html(ano, uf, cod_uf, municipio, cod_municipio)
                else:
                    nova_entrada = analisa_siope_pdf(ano, uf, cod_uf, municipio, cod_municipio)

                with open('saida.txt', encoding='utf-8', mode='a') as saida:
                    saida.write(nova_entrada)
