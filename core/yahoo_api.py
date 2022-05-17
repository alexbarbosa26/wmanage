import requests
from bs4 import BeautifulSoup
from .models import Cotacao, Nota
from django.db.models import Sum
from datetime import datetime
from pytz import timezone

# cotação do yahoo
def get_yahoo_cotacao():
   
    result_compra = Nota.objects.values('ativo').annotate(qt=Sum('quantidade'), preco_f=Sum('total_compra'), custos=Sum('total_custo'), preco_m=Sum('preco'), v_mercado=Sum('preco'), lucro=Sum('preco')).filter(tipo='C')
    result_venda = Nota.objects.values('ativo').annotate(qt=Sum('quantidade'), preco_f=Sum('total_compra'), custos=Sum('total_custo')).filter(tipo='V')
        
    for venda in result_venda:
        for compra in result_compra:
        #compra.quantidade = compra.quantidade - venda.quantidade
            if compra['ativo'] == venda['ativo']:
                compra['qt'] = compra['qt'] - venda['qt']
                compra['preco_f'] = compra['preco_f'] - venda['preco_f']
                compra['custos'] = compra['custos'] - venda['custos']
    
    for compra in result_compra:
        data_e_hora_atuais = datetime.now()
        fuso_horario = timezone('America/Sao_Paulo')
        if compra['qt'] != 0:
            url = 'https://br.financas.yahoo.com/quote/'+compra['ativo']+'.SA'
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.64'}
            #pegando cotação no yahoo            
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, 'lxml')
            # preco_mercado = soup.find_all('div', {'class':'D(ib) Mend(20px)'})[0].find('span').text
            preco_mercado = soup.find_all('div', {'class':'D(ib) Mend(20px)'})[0].find('fin-streamer').text
            try:
                variacao_mercado = []
                variacao_mercado.append(soup.find_all('fin-streamer', {'class':'Fw(500) Pstart(8px) Fz(24px)'})[0].text)
                variacao_mercado.append(soup.find_all('fin-streamer', {'class':'Fw(500) Pstart(8px) Fz(24px)'})[1].text)
            except IndexError:
                # variacao_mercado = soup.find_all('span', {'class':'Trsdu(0.3s) Fw(500) Pstart(10px) Fz(24px) C($negativeColor)'})[0].text
                variacao_mercado = []
                variacao_mercado.append(soup.find_all('fin-streamer', {'class':'Fw(500) Pstart(8px) Fz(24px)'})[0].text)
                variacao_mercado.append(soup.find_all('fin-streamer', {'class':'Fw(500) Pstart(8px) Fz(24px)'})[1].text)
                mercado_aberto_fechado = soup.find('span', {'data-id':'mk-msg'}).text
            # variacao_mercado = variacao_mercado.split(' ')

            Cotacao.objects.filter(ativo=compra['ativo']).update(ativo=compra['ativo'], fechamento_ajustado = preco_mercado, variacao_1 = variacao_mercado[0], variacao_2 = variacao_mercado[1], status_fechado_aberto = mercado_aberto_fechado, data_instante = data_e_hora_atuais.astimezone(fuso_horario))
        else:
            pass            