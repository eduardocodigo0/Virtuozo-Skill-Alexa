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


chave_sistema = "xxx"
codEmpresa = "xxx"
codApp = "xxx"

url_base = "https://app.teste.virtuozo.com.br/api/v1/"


imagem_padrao = Image("https://i.imgur.com/L2N6x19.png", "https://i.imgur.com/L2N6x19.png")

class faturasHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("faturaIntent")(handler_input)

    def handle(self, handler_input):
        
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
        img = imagem_padrao
        url = url_base + "pdvs/faturas/"
        resposta = requests.get(url, headers=header, params=params)
        
        if resposta.status_code == 200:
            speak_output = "Aqui estão suas faturas a pagar. "
            
            dados_json = resposta.json()
            if len(dados_json['parcelas']) > 0:
                
                for parcela in dados_json['parcelas']:
                    
                    fornecedor = parcela['razaoSocial']
                    valor = float(parcela['valorTotal'])
                    
                    reais = round(int(valor))
                    centavos = (valor - reais) * 100
                    centavos = str(round(centavos))
                    reais = str(reais)
                    
                    if len(centavos) > 2:
                        centavos = centavos[:1]
                        
                    if int(centavos) > 0:
                        speak_output = speak_output + "{0} Reais e {1} centavos para {2}. ".format(reais, str(centavos), fornecedor)
                        card_text = card_text +"Valor: R${0},{1}        Vencimento: {2}     Fornecedor: {3}\n\n".format(reais, centavos, parcela['dataVencimento'], parcela['razaoSocial'])
                    else:
                        speak_output = speak_output + "{0} Reais para {1}. ".format(reais, fornecedor)   
                        card_text = card_text +"Valor: R${0},00        Vencimento: {1}     Fornecedor: {2}\n\n".format(reais, parcela['dataVencimento'], parcela['razaoSocial'])
                    
                    
            else:
                speak_output = "Não achei nenhuma fatura a pagar."
            
        else:
            speak_output = "Não consegui acessar o sistema!"
            
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .set_card(StandardCard("Faturas", card_text, img))
                .ask("Posso ajudar em mais alguma coisa?")
                .response
        )
