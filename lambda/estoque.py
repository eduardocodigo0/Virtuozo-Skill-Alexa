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


class estoqueIntentHandler(AbstractRequestHandler):
    
    def can_handle(self, handler_input):
        
        return ask_utils.is_intent_name("estoqueIntent")(handler_input)
    
    def handle(self, handler_input):
        
        speak_output = ""
        card_text = ""
        
        slots = handler_input.request_envelope.request.intent.slots
        codigo = slots['codigo'].value
        
        header =  {
            "Content-Type": "application/json",
            "AuthToken": chave_sistema,
            "AuthEnterprise": codEmpresa
        }
        
        params = { 
            
            'codProduto':codigo
            
        }
        
        
        
        url = url_base + "produtos"
        resposta = requests.get(url, headers=header, params=params)
        
        if resposta.status_code == 200:
            produtos = resposta.json()['produtos']
            
            speak_output = speak_output + "Esse é o estoque do produto de código {0}".format(codigo)
            
            for produto in produtos:
                
                speak_output = speak_output + ""
                card_text = card_text + "Produto: {0}\n".format(produto['descrProduto'])
                card_text = card_text + "Estoque minimo: {0}\n".format(produto['estoqueMinimo'])
                
        else:
            speak_output = "Não consegui achar o produto com o código {0}".format(codigo)
            card_text = "Produto não encontrado."
            
        return (
            handler_input.response_builder
                .speak(speak_output)
                .set_card(StandardCard("Estoque ", card_text, imagem_padrao))
                .ask("Posso ajudar em mais alguma coisa?")
                .response
        )
        
    
    
