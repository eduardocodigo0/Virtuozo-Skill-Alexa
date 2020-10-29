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

from money_util import money_util

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)



class faturasHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("faturaIntent")(handler_input)

    def handle(self, handler_input):
        
        session_attr = handler_input.attributes_manager.session_attributes
        
        chave_sistema = session_attr['chave_sistema']
        codEmpresa = session_attr['cod_empresa'] 
        
        header =  {
            "Content-Type": "application/json",
            "AuthToken": chave_sistema,
            "AuthEnterprise": codEmpresa
        }
        
        params = {
            "tipoFatura":1,
            "tipoFat": "0"
        }
        
        
        card_text = ""
        url = session_attr['base_url']+ "/pdvs/faturas/"
        resposta = requests.get(url, headers=header, params=params)
        
        MU = money_util()
            
        
        if resposta.status_code == 200:
            speak_output = "Aqui estão suas faturas a pagar. "
            
            dados_json = resposta.json()
            if len(dados_json['parcelas']) > 0:
                
                for parcela in dados_json['parcelas']:
                    
                    fornecedor = parcela['razaoSocial']
                    
                    valor_texto = MU.moneyToText(parcela['valorTotal'])
                    valor_fala = MU.moneyToSpeak(parcela['valorTotal'])
                    
                    speak_output = speak_output + "{0} para {1}. ".format(valor_fala, fornecedor)
                    card_text = card_text +"Valor: {0}        Vencimento: {1}     Fornecedor: {2}\n\n".format(valor_texto, parcela['dataVencimento'], parcela['razaoSocial'])
                    
            else:
                speak_output = "Não achei nenhuma fatura a pagar."
            
        else:
            speak_output = "Não consegui acessar o sistema!"
            
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .set_card(StandardCard("Faturas", card_text, session_attr['imagem_padrao']))
                .ask("Posso ajudar em mais alguma coisa?")
                .response
        )
