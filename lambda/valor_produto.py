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


chave_sistema = "XXXX"
codEmpresa = "XXXXXX"
codApp = "XX"

url_base = "https://app.teste.virtuozo.com.br/api/v1/"


imagem_padrao = Image("https://i.imgur.com/L2N6x19.png", "https://i.imgur.com/L2N6x19.png")


class custoProdutoIntentHandler(AbstractRequestHandler):
    
    def can_handle(self, handler_input):
        
        return ask_utils.is_intent_name("custoProdutoIntent")(handler_input)
    
    def handle(self, handler_input):
        
        speak_output = ""
        card_text = ""
        slots = handler_input.request_envelope.request.intent.slots
        produto = slots['produto'].value
        
        header =  {

            "Content-Type": "application/json",
            "AuthToken": chave_sistema,
            "AuthEnterprise": codEmpresa
        
        }
        
        params = {
        
            'texto': produto

        }
        
        url = "http://app.teste.virtuozo.com.br/api/v1/produtos"
        resposta = requests.get(url, headers=header, params=params)
        
        if resposta.status_code == 200:

            dados_json = resposta.json()
            
            if not dados_json['produtos']:
                
                speak_output = "Não encontrei nenhum produto com esse nome!"
                card_text = "Nenhum produto foi encontrado"
                
            else:
                
                speak_output = "Eu encontrei os seguintes produtos com essa descrição. "
                
                for produto in dados_json['produtos']:
                    
                    nome = produto['descrProduto']
                    
                    valor = float(produto['precoPrazo'][:-1])
                    reais = int(valor)
                    centavos = produto['precoPrazo'][:-1].split(".", 1)[1]
                    centavos_num = int(centavos)
                    
                    reais_num = reais
                    reais = str(reais)
                    
                    
                    if reais_num <= 1:
                        if reais_num != 0:
                            
                            if centavos_num > 1:
                                if centavos_num < 10:
                                    speak_output = speak_output + "{0} com o preço de {1} real e {2} centavos. ".format(nome, reais, centavos[1:])
                                else:
                                    speak_output = speak_output + "{0} com o preço de {1} real e {2} centavos. ".format(nome, reais, centavos)
                            elif centavos_num == 1:
                                speak_output = speak_output + "{0} com o preço de {1} real e {2} centavo. ".format(nome, reais, centavos)
                            else:
                                speak_output = speak_output + "{0} com o preço de {1} real. ".format(nome, reais)
                        
                        else:
                            speak_output = speak_output + "{0} com o preço de {1} centavos. ".format(nome, centavos)   
                    else:
                        
                        
                        if centavos_num > 1:
                            if centavos_num < 10:
                                speak_output = speak_output + "{0} com o preço de {1} reais e {2} centavos. ".format(nome, reais, centavos[1:])
                            else:
                                speak_output = speak_output + "{0} com o preço de {1} reais e {2} centavos. ".format(nome, reais, centavos)
                        elif centavos_num == 1:
                            speak_output = speak_output + "{0} com o preço de {1} reais e {2} centavo. ".format(nome, reais, centavos)
                        else:
                            speak_output = speak_output + "{0} com o preço de {1} reais. ".format(nome, reais)
                    
                    card_text += "PRODUTO: {0}\n".format(produto['descrProduto'])
                    card_text += "VALOR: {0}\n\n".format(produto['precoPrazo'][:-1])
                    
        else:
            
            speak_output = "Ouve um erro ao acessar o servidor."
            card_text = "Erro ao acessar o servidor!"
        
        
        return (
                handler_input.response_builder
                .speak(speak_output)
                .set_card(StandardCard("Produtos", card_text, imagem_padrao))
                .ask("Posso ajudar em mais alguma coisa?")
                .response
            )
