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


class NovoProdutoIntentHandler(AbstractRequestHandler):
    
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("NovoProdutoIntent")(handler_input)

    def handle(self, handler_input):
        
        speak_output = "feito"
        card_text = ""
        slots = handler_input.request_envelope.request.intent.slots
        codigo = str(slots['a'].value) + str(slots['b'].value) +str(slots['c'].value) +str(slots['d'].value) +str(slots['e'].value) +str(slots['f'].value) +str(slots['g'].value) +str(slots['h'].value) +str(slots['i'].value) +str(slots['j'].value) +str(slots['k'].value) +str(slots['l'].value) +str(slots['m'].value)
        
        
        session_attr = handler_input.attributes_manager.session_attributes
        session_attr['estado'] = 200
        session_attr['codigo_produto'] = codigo
        
        card_text = codigo
        
        header = {
            "Content-Type": "application/json"
        }
            
        body = {
            "Datasets": "basic_data",
            "q": "ean{"+codigo+"}",
            "AccessToken": "fbcaf2bd-9ab9-48d3-aaf2-ab60acb43540"
        }
            
        url = "https://bigboost.bigdatacorp.com.br/products"
        
        resposta = {}
        
        try:
            resposta = requests.get(url, headers=header, params=body)
            if resposta.status_code == 200:
                
                dados_json = resposta.json()
                        
                        
                desc = dados_json['Result'][0]['BasicData']['Title']
                
                session_attr['dados-produto'] = desc
                
                speak_output = "O produto {0} foi encontrado. deseja informar o preço a prazo agora?".format(desc)
                card_text = "Código: {0}\nNome: {1}\n\nDeseja informar o valor a prazo?".format(codigo, desc)
            
            else:
                
                speak_output = "Não consegui encontrar o produto."
                card_text = "Código: {0}\nProduto não encontrado!".format(codigo)
                session_attr['estado'] = 0
                
        except:
            card_text = "Erro no request"


            
        return (
            handler_input.response_builder
                .speak(speak_output)
                .set_card(SimpleCard("Novo Produto", card_text))
                .ask(speak_output)
                .response
        )