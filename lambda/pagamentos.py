# -*- coding: utf-8 -*-

import logging
import ask_sdk_core.utils as ask_utils

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model.ui import SimpleCard
from ask_sdk_model.ui import StandardCard
from ask_sdk_model.ui.image import Image

from ask_sdk_model import Response

from datetime import date, timedelta
import requests
import json

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


chave_sistema = "1234"
codEmpresa = "716001"
codApp = "12"

url_base = "https://app.teste.virtuozo.com.br/api/v1/"


imagem_padrao = Image("https://i.imgur.com/L2N6x19.png", "https://i.imgur.com/L2N6x19.png")


class pagamentoNoPeriodoHandler(AbstractRequestHandler):
    
    def can_handle(self, handler_input):
        
        return ask_utils.is_intent_name("pagamentoNoPeriodoIntent")(handler_input)
    
    def handle(self, handler_input):
        
        
        periodo = 4
        data_ini = ""
        data_fim = date.today().strftime("%Y-%m-%d")
        
        slots = handler_input.request_envelope.request.intent.slots
        periodo = slots['momento'].value
        
        if periodo == "dia" or periodo == "hoje":
            
            data_ini = date.today().strftime("%Y-%m-%d")
           
        elif periodo == "semana":
            
            dia_da_semana = (date.today().weekday())+1
            data_ini = (date.today() + timedelta(days=-dia_da_semana)).strftime("%Y-%m-%d")
        
        elif periodo == "mês":
            
            data_ini = (date.today().replace(day=1)).strftime("%Y-%m-%d")
        
        elif periodo == "ano":
            
            data_ini = (date.today().replace(day=1, month=1)).strftime("%Y-%m-%d")
        
        
        header =  {
            "Content-Type": "application/json",
            "AuthToken": chave_sistema,
            "AuthEnterprise": codEmpresa
        }
        
        params = {
            "tipoFatura":1,
            "dataIni": data_ini,
            "dataFim": data_fim,
            "dtPesquisa": 2
        }
        
        img = imagem_padrao
        url = url_base + "pdvs/faturas/"
        resposta = requests.get(url, headers=header, params=params)
        
        speak_output = ""
        card_text = ""

        
        if resposta.status_code == 200:
            
            dados_json = resposta.json()
            qtd = len(dados_json['parcelas'])
            
            if qtd == 1: 
                speak_output ="Você pagou uma conta nesse período. " 
            else: 
                speak_output ="Você pagou {0} contas nesse período. ".format(qtd)
                
            card_text = "Contas pagas em - {0}\n\n".format(periodo)
            
            
            for parcela in dados_json['parcelas']:
                
                
                fornecedor = parcela['razaoSocial']
                valor = float(parcela['valorParcela'])
                    
                reais = round(int(valor))
                centavos = int((valor - reais) * 100)
                centavos = str(round(centavos))
                reais = str(reais)
                
                card_text = card_text + "\n\nValor: R${0}   Fornecedor: {1}".format(parcela['valorParcela'][:-1], parcela['razaoSocial'])
                
                
                if len(centavos) > 2:
                    centavos = centavos[:1]
                
                if int(centavos) > 0:
                    speak_output = speak_output + "{0} Reais e {1} centavos para {2}. ".format(reais, centavos, fornecedor)
                else:
                    speak_output = speak_output + "{0} Reais para {1}. ".format(reais, fornecedor)
                    
                
                for baixa in parcela['baixas']:
                    valor_bruto = baixa['valorBruto'][:-1]
                    
                    card_text = card_text +"\n\n * Data da Baixa: {0}    Valor Bruto: R${1}".format(baixa['dataBaixa'][:11], valor_bruto)
        
        else:
            
            speak_output = "Não consegui me comunicar com o sistema do virtuozo!"
                
        
        
        return (
                handler_input.response_builder
                .speak(speak_output)
                .set_card(StandardCard("Pagamentos ", card_text, img))
                .ask("Posso ajudar em mais alguma coisa?")
                .response
            )



    
    
class pagamentoHojeHandler(AbstractRequestHandler):
    
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("pagamentoHojeIntent")(handler_input)
    
    def handle(self, handler_input):
        
        hoje = date.today().strftime("%Y-%m-%d")
        
        header =  {
            "Content-Type": "application/json",
            "AuthToken": chave_sistema,
            "AuthEnterprise": codEmpresa
        }
        
        params = {
            "tipoFatura":1,
            "dataIni": hoje,
            "dataFim": hoje,
            "dtPesquisa": 1
        }
        
        total = 0.0
        
        card_text = "Contas a pagar.\n Data: {0}\n\n".format(date.today().strftime("%d/%m/%Y"))
        
        img = imagem_padrao
        url = url_base + "pdvs/faturas/"
        resposta = requests.get(url, headers=header, params=params)
        
        if resposta.status_code == 200:
            dados_json = resposta.json()
            qtd = len(dados_json['parcelas'])
            if qtd > 0:
                if qtd == 1:
                    speak_output = "Você tem {0} pagamento pra fazer hoje.".format(qtd)
                else:
                    speak_output = "Você tem {0} pagamentos pra fazer hoje.".format(qtd)
                
                for parcela in dados_json['parcelas']:
                    
                    fornecedor = parcela['razaoSocial']
                    valor = float(parcela['valorTotal'])
                    
                    
                    total += valor
                    reais = round(int(valor))
                    centavos = (valor - reais) * 100
                    centavos = str(round(centavos))
                    
                    if len(centavos) > 2:
                        centavos = centavos[:1]
                    
                    if int(centavos) > 0:
                        speak_output = speak_output + " {0} Reais e {1} centavos para {2}. ".format(str(reais), str(centavos), fornecedor)
                        card_text = card_text + "\nFornecedor: {0}  Valor: R${1},{2}".format(fornecedor, str(reais), str(centavos))
                    else:
                        speak_output = speak_output + " {0} Reais para {2}. ".format(str(reais), fornecedor)
                        card_text = card_text + "\nFornecedor: {0}  Valor: R${1},00".format(fornecedor, str(reais))
                
                card_text += "\n\nTotal: R${0}".format(total)
                
            else:
                speak_output = "Você não tem pagamentos pra fazer hoje."
                card_text = "Nada para pagar hoje."
                
        else:
            speak_output = "Não consegui me comunicar com o sistema do virtuozo!"
        
        return(
            handler_input.response_builder
            .speak(speak_output)
            .set_card(StandardCard("Pagamentos do dia.", card_text, img))
            .ask("Posso ajudar em mais alguma coisa?")
            .response
            )
            