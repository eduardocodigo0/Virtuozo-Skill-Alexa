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


class tenhoParaReceberHojeIntentHandler(AbstractRequestHandler):
    
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("tenhoParaReceberHojeIntent")(handler_input)
    
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
            "tipoFatura":0,
            "dataIni": hoje,
            "dataFim": hoje,
            "dtPesquisa": 1
        }
        
        total = 0.0
        
        card_text = "Contas a receber.\n Data: {0}\n\n".format(date.today().strftime("%d/%m/%Y"))
        
        
        url = session_attr['base_url'] + "/pdvs/faturas/"
        resposta = requests.get(url, headers=header, params=params)
        
        if resposta.status_code == 200:
            dados_json = resposta.json()
            qtd = len(dados_json['parcelas'])
            if qtd > 0:
                if qtd == 1:
                    speak_output = "Você vai receber {0} pagamento hoje.".format(qtd)
                else:
                    speak_output = "Você vai receber {0} pagamentos hoje.".format(qtd)
                
                for parcela in dados_json['parcelas']:
                    
                    fornecedor = parcela['razaoSocial']
                    
                    valor_texto = MU.moneyToText(parcela['valorTotal'])
                    valor_fala = MU.moneyToSpeak(parcela['valorTotal'])
                    
                    
                    total += float(parcela['valorTotal'])
                    
                    
                    
                    speak_output = speak_output + " {0} de {1}. ".format(valor_fala, fornecedor)
                    card_text = card_text + "\nCliente: {0}  Valor: {1}".format(fornecedor, valor_texto)
                
                total_texto = MU.moneyToText(str(total))
                
                card_text += "\n\nTotal: {0}".format(total_texto)
                
            else:
                speak_output = "Você não tem nada para receber hoje."
                card_text = "Nada para receber hoje."
                
        else:
            speak_output = "Não consegui me comunicar com o sistema do virtuozo!"
        
        return(
            handler_input.response_builder
            .speak(speak_output)
            .set_card(StandardCard("Recebimentos do dia.", card_text, session_attr['imagem_padrao']))
            .ask("Posso ajudar em mais alguma coisa?")
            .response
            )