# -*- coding: UTF-8 -*-
import urllib
from BeautifulSoup import BeautifulSoup, SoupStrainer
from time import time

anos = ['2006','2007','2008','2009']

#lista tirada de http://www.ibge.gov.br/home/geociencias/areaterritorial/principal.shtm
ufs = [
    '11', #Rondônia
    '12', #Acre
    '13', #Amazonas
    '14', #Roraima
    '15', #Pará
    '16', #Amapá
    '17', #Tocantins
    '21', #Maranhão
    '22', #Piauí
    '23', #Ceará
    '24', #Rio Grande do Norte
    '25', #Paraíba
    '26', #Pernambuco
    '27', #Alagoas
    '28', #Sergipe
    '29', #Bahia
    '31', #Minas Gerais
    '32', #Espírito Santo
    '33', #Rio de Janeiro
    '35', #São Paulo
    '41', #Paraná
    '42', #Santa Catarina
    '43', #Rio Grande do Sul
    '50', #Mato Grosso do Sul
    '51', #Mato Grosso
    '52', #Goiás
    '53', #Distrito Federal
]

#O nome da linha buscada muda nos formulários dos diferentes anos
termos_de_busca = {
    '2006': 'ENSINO FUNDAMENTAL',
    '2007': '18 - ENSINO FUNDAMENTAL',
    '2008': '18 - ENSINO FUNDAMENTAL',
    '2009': '24 - ENSINO FUNDAMENTAL'
}

url = "https://www.fnde.gov.br/siope/relatorioRREOMunicipal2009.do"

#cronômetro
t0 = time()

saida = open('saida.txt', 'w')

def lista_municipios(uf):
    municipios = []
    url = "https://www.fnde.gov.br/siope/relatorioRREOMunicipal2009.do"
    page = urllib.urlopen(url, urllib.urlencode({'cod_uf': uf}))
    soup = BeautifulSoup(page.read())
    a = soup.find('select', {"name": 'municipios'})

    for i in a.findAll('option'):
        municipios.append(i['value'])

    return municipios

for uf in ufs:
    municipios = lista_municipios(uf)

    for ano in anos:
        for municipio in municipios:
            parametros = {'acao': 'pesquisar',
                          'pag': 'result',
                          'periodos': 1,
                          'anos': ano,
                          'cod_uf': uf,
                          'municipios': municipio}

            #monta a url conforme os parâmetros especificados e estabelece a conexão com o servidor
            pagina = urllib.urlopen(url, urllib.urlencode(parametros))

            #joga fora todos os elementos da página que não as linhas de uma tabela - tr (table row)
            linhas = BeautifulSoup(pagina.read(), parseOnlyThese=SoupStrainer('tr'))

            try:
                #realiza a busca pelo texto determinado
                linha_alvo = linhas.find(text=termos_de_busca[ano]).parent.parent

                #uma vez com a linha alvo, é só filtrar as colunas (td) certas
                colunas = linha_alvo.findAll('td')
                atualizada = colunas[2].findChild().text
                realizada = colunas[4].findChild().text

                saida.write("%s\t%s\t%s\t%s\t%s\n" % (ano, uf, municipio, atualizada, realizada))
            #Se a operação de busca da linha alvo falhar (porque o município não existe, por exemplo),
            #a condição abaixo é executada
            except AttributeError:
                saida.write("%s\t%s\t%s\t---\n" % (ano, uf, municipio))

            saida.flush()

t1 = time()

saida.write('\n\nTempo de execução: %.1fs' %(t1-t0))
saida.close()
