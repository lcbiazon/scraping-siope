#!/usr/bin/env python3
from urllib import request, parse
from bs4 import BeautifulSoup, SoupStrainer

anos = ['2006','2007','2008','2009']

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
termos_de_busca = {
    '2006': 'ENSINO FUNDAMENTAL',
    '2007': '18 - ENSINO FUNDAMENTAL',
    '2008': '18 - ENSINO FUNDAMENTAL',
    '2009': '24 - ENSINO FUNDAMENTAL'
}

url = "https://www.fnde.gov.br/siope/relatorioRREOMunicipal2009.do"

if __name__ == "__main__":
    # Busca a lista de municipios de cada estado e acrescenta na lista ufs
    for uf in ufs:
        municipios = []
        url = "https://www.fnde.gov.br/siope/relatorioRREOMunicipal2009.do"
        data = parse.urlencode({'cod_uf': uf[0]})
        binary_data = data.encode('utf-8')
        page = request.urlopen(url, binary_data)
        soup = BeautifulSoup(page.read())
        a = soup.find('select', {"name": 'municipios'})

        for i in a.findAll('option'):
            municipios.append((i['value'], i.text.replace('\r\n', "").strip()))

        uf.append(municipios)

    for ano in anos:
        for cod_uf, uf, municipios in ufs:
            for cod_municipio, municipio in municipios:
                parametros = {'acao': 'pesquisar',
                              'pag': 'result',
                              'periodos': 1,
                              'anos': ano,
                              'cod_uf': cod_uf,
                              'municipios': cod_municipio}

                #monta a url conforme os parâmetros especificados e estabelece a conexão com o servidor
                data = parse.urlencode(parametros)
                binary_data = data.encode('utf-8')
                pagina = request.urlopen(url, binary_data)

                #joga fora todos os elementos da página que não as linhas de uma tabela - tr (table row)
                linhas = BeautifulSoup(pagina.read(), parse_only=SoupStrainer('tr'))

                try:
                    #realiza a busca pelo texto determinado
                    linha_alvo = linhas.find(text=termos_de_busca[ano]).parent.parent

                    #uma vez com a linha alvo, é só filtrar as colunas (td) certas
                    colunas = linha_alvo.findAll('td')
                    atualizada = colunas[2].findChild().text
                    realizada = colunas[4].findChild().text

                    with open("saida.txt", encoding='utf-8', mode="a") as saida:
                        saida.write("%s\t%s [%s]\t%s [%s]\t%s\t%s\n" % (ano, uf, cod_uf, municipio, cod_municipio, atualizada, realizada))

                #Se a operação de busca da linha alvo falhar (porque o município não existe, por exemplo),
                #a condição abaixo é executada
                except AttributeError:
                    with open("saida.txt", encoding='utf-8', mode="a") as saida:
                        saida.write("%s\t%s [%s]\t%s [%s]\n" % (ano, uf, cod_uf, municipio, cod_municipio))
