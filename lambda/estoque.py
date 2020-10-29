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



class estoqueIntentHandler(AbstractRequestHandler):
    
    def can_handle(self, handler_input):
        
        return ask_utils.is_intent_name("estoqueIntent")(handler_input)
    
    def handle(self, handler_input):
        
        speak_output = ""
        card_text = ""
        session_attr = handler_input.attributes_manager.session_attributes
        slots = handler_input.request_envelope.request.intent.slots
        codigo = slots['codigo'].value
        chave_sistema = session_attr['chave_sistema']
        codEmpresa = session_attr['cod_empresa'] 
        
        header =  {
            "Content-Type": "application/json",
            "AuthToken": chave_sistema,
            "AuthEnterprise": codEmpresa
        }
        
        params = { 
            
            'codProduto':codigo
            
        }
        
        
        
        url = session_attr['base_url'] + "/products/stockBalances"
        resposta = requests.get(url, headers=header, params=params)
        
        if resposta.status_code == 200:
            produtos = resposta.json()['list']
            
            qtd = len(produtos)
            speak_output = speak_output + "Eu encontrei {0} produtos com o código {1}.".format(qtd, codigo)
            
            for produto in produtos:
                
                speak_output = speak_output + " O produto {0} possui {1} unidades no estoque.".format(produto['descrProduto'], int(float(produto['saldo'])))
                card_text = card_text + "\nProduto: {0}\n".format(produto['descrProduto'])
                card_text = card_text + "Saldo do estoque: {0}\n".format(int(float(produto['saldo'])))
                
        else:
            speak_output = "Não consegui achar o produto com o código {0}".format(codigo)
            card_text = "Produto não encontrado."
            
        return (
            handler_input.response_builder
                .speak(speak_output)
                .set_card(StandardCard("Estoque ", card_text, session_attr['imagem_padrao']))
                .ask("Posso ajudar em mais alguma coisa?")
                .response
        )


class estoqueDoisIntentHandler(AbstractRequestHandler):
    
    def can_handle(self, handler_input):
        
        return ask_utils.is_intent_name("estoqueDoisIntent")(handler_input)
    
    def handle(self, handler_input):
        
        speak_output = ""
        card_text = ""
        
        session_attr = handler_input.attributes_manager.session_attributes
        slots = handler_input.request_envelope.request.intent.slots
        
        pesquisa = slots['nome_item'].value
        chave_sistema = session_attr['chave_sistema']
        codEmpresa = session_attr['cod_empresa'] 
        
        header =  {
            
            "Content-Type": "application/json",
            "AuthToken": chave_sistema,
            "AuthEnterprise": codEmpresa
            
        }
        
        params = { 
            
            'texto':pesquisa
            
        }
        
        url = session_attr['base_url'] + "/products/stockBalances"
        resposta = requests.get(url, headers=header, params=params)
        
        if resposta.status_code == 200:
            
            produtos = resposta.json()['list']
            
            qtd = len(produtos)
            speak_output = speak_output + "Eu encontrei {0} produtos com o nome {1}.".format(qtd, pesquisa)
            
            for produto in produtos:
                
                speak_output = speak_output + " O produto {0} possui {1} unidades no estoque.".format(produto['descrProduto'], int(float(produto['saldo'])))
                card_text = card_text + "\nProduto: {0}\n".format(produto['descrProduto'])
                card_text = card_text + "Saldo do estoque: {0}\n".format(int(float(produto['saldo'])))
                
        else:
            
            speak_output = "Não consegui achar o produto com o código {0}".format(codigo)
            card_text = "Produto não encontrado."
            
        return (
            handler_input.response_builder
                .speak(speak_output)
                .set_card(StandardCard("Estoque ", card_text, session_attr['imagem_padrao']))
                .ask("Posso ajudar em mais alguma coisa?")
                .response
        )
    
    