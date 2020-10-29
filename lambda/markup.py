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

from difflib import SequenceMatcher

from money_util import money_util

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class markupIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("markupIntent")(handler_input)

    def handle(self, handler_input):
        
        card_text = ""
        speak_output = ""
        
        session_attr = handler_input.attributes_manager.session_attributes
        slots = handler_input.request_envelope.request.intent.slots
        pesquisa = slots['produto'].value
        
        chave_sistema = session_attr['chave_sistema']
        codEmpresa = session_attr['cod_empresa'] 
        
        header = {
            "Content-Type": "application/json",
            "AuthToken": chave_sistema,
            "AuthEnterprise": codEmpresa
        }
        
        
        params = {
            "texto":pesquisa
        }
        url = session_attr['base_url']+"/produtos"
        resposta = requests.get(url, headers=header, params=params)
        
        
        if resposta.status_code == 200:
            
            menor = 0.0
            produto_atual = {}
            
            dados_json = resposta.json()
            produtos = dados_json['produtos']
            
            for produto in produtos:
                
                atual = SequenceMatcher(None, produto['descrProduto'], pesquisa).ratio()
                
                if menor < atual:
                    menor = atual
                    produto_atual = produto
            
            
            nome_produto = produto_atual['descrProduto']
            
            MU = money_util()
            
            preco_venda = MU.moneyToText(produto_atual['precoPrazo'])
            preco_custo = MU.moneyToText(produto_atual['precoCusto'])
            
            
            speak_preco_venda = MU.moneyToSpeak(produto_atual['precoPrazo'])
            speak_preco_custo = MU.moneyToSpeak(produto_atual['precoCusto'])
            
            margem_opb = float(produto_atual['margemLucro'])
            margem_opb = int(margem_opb) if margem_opb.is_integer else margem_opb
            
            card_text = "PRODUTO: {0}\n\nPREÇO: {1}\n\nPREÇO DE CUSTO: {2}\n\nMARGEM OPERACIONAL BRUTA: {3}%".format(nome_produto, preco_venda, preco_custo, margem_opb)
            speak_output = "O produto {0} tem a seguinte margem. {1} de preço de venda. {2} de preço de custo e {3} porcento de margem de lucro.".format(nome_produto, speak_preco_venda, speak_preco_custo, margem_opb)
        
        else:
            
            speak_output = "Desculpe, não consegui encontrar um produto com esse nome."
            card_text = "Nenhum produto com o nome {0} foi encontrado.".format(pesquisa)
            
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .set_card(StandardCard("Margem", card_text, session_attr['imagem_padrao']))
                .ask("Posso ajudar em mais alguma coisa?")
                .response
        )
