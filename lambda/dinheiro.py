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

class dinheiroIntentHandler(AbstractRequestHandler):
    
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("dinheiroIntent")(handler_input)
    
    def handle(self, handler_input):
        
        card_text = ""
        speak_output = ""
        session_attr = handler_input.attributes_manager.session_attributes
        
        slots = handler_input.request_envelope.request.intent.slots
        reais = str(slots['reais'].value)
        centavos = str(slots['centavos'].value)
        
        if centavos < 10:
            centavos = "0" + centavos
        
        
        #Primeiro preco
        if session_attr['estado'] == 210:
            session_attr['precoPrazo'] = "{0},{1}".format(reais, centavos)
            card_text = "Valor a prazo: {0},{1}".format(reais, centavos)
            speak_output = "O valor do produto a prazo vai ser de {0} reias e {1} centavos.\n posso cadastrar?".format(reais, centavos)
            session_attr['estado'] = 220
            
            
        
        
        
        return (
                handler_input.response_builder
                .speak(speak_output)
                .set_card(StandardCard("Valor", card_text, imagem_padrao))
                .ask("Posso ajudar em mais alguma coisa?")
                .response
        )
    
    
