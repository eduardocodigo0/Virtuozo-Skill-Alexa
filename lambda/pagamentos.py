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

from money_util import money_util

from datetime import date, timedelta
import requests
import json

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)




class pagamentoNoPeriodoHandler(AbstractRequestHandler):
    
    def can_handle(self, handler_input):
        
        return ask_utils.is_intent_name("pagamentoNoPeriodoIntent")(handler_input)
    
    def handle(self, handler_input):
        session_attr = handler_input.attributes_manager.session_attributes
        
        MU = money_util()
        
        chave_sistema = session_attr['chave_sistema']
        codEmpresa = session_attr['cod_empresa'] 
        
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
        
        
        url = session_attr['base_url'] + "/pdvs/faturas/"
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
                    
                valor_texto = MU.moneyToText(parcela['valorParcela'])
                valor_fala = MU.moneyToSpeak(parcela['valorParcela'])
                
                card_text = card_text + "\n\nValor: {0}   Fornecedor: {1}".format(valor_texto, fornecedor)
                
                
                speak_output = speak_output + "{0} para {1}. ".format(valor_fala, fornecedor)
                
                for baixa in parcela['baixas']:
                    valor_bruto = MU.moneyToText(baixa['valorBruto'])
                    
                    card_text = card_text +"\n\n * Data da Baixa: {0}    Valor Bruto: R${1}".format(baixa['dataBaixa'][:11], valor_bruto)
        
        else:
            
            speak_output = "Não consegui me comunicar com o sistema do virtuozo!"
                
        
        
        return (
                handler_input.response_builder
                .speak(speak_output)
                .set_card(StandardCard("Pagamentos ", card_text, session_attr['imagem_padrao']))
                .ask("Posso ajudar em mais alguma coisa?")
                .response
            )



    
    
class pagamentoHojeHandler(AbstractRequestHandler):
    
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("pagamentoHojeIntent")(handler_input)
    
    def handle(self, handler_input):
        
        session_attr = handler_input.attributes_manager.session_attributes
        
        MU = money_util()
        
        chave_sistema = session_attr['chave_sistema']
        codEmpresa = session_attr['cod_empresa'] 
        
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
        
        
        url = session_attr['base_url'] + "/pdvs/faturas/"
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
                    
                    valor_texto = MU.moneyToText(parcela['valorTotal'])
                    valor_fala = MU.moneyToSpeak(parcela['valorTotal'])
                    
                    
                    total += float(parcela['valorTotal'])
                    
                    
                    
                    speak_output = speak_output + " {0} para {1}. ".format(valor_fala, fornecedor)
                    card_text = card_text + "\nFornecedor: {0}  Valor: {1}".format(fornecedor, valor_texto)
                
                total_texto = MU.moneyToText(str(total))
                
                card_text += "\n\nTotal: {0}".format(total_texto)
                
            else:
                speak_output = "Você não tem pagamentos pra fazer hoje."
                card_text = "Nada para pagar hoje."
                
        else:
            speak_output = "Não consegui me comunicar com o sistema do virtuozo!"
        
        return(
            handler_input.response_builder
            .speak(speak_output)
            .set_card(StandardCard("Pagamentos do dia.", card_text, session_attr['imagem_padrao']))
            .ask("Posso ajudar em mais alguma coisa?")
            .response
            )
            