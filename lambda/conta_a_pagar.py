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

#====== FUNCOES ========================================

def get_fornecedor(query, chave_sistema, codEmpresa, url_base):
    
    pessoas = []

    header = {
        "Content-Type": "application/json",
        "AuthToken": chave_sistema,
        "AuthEnterprise": codEmpresa
    }

    params = {
        'query': query
    }

    url = url_base + "/pessoas/1"
    resposta = requests.get(url, headers=header, params=params)

    if resposta.status_code == 200:

        dados_json = resposta.json()
        pessoas = dados_json['pessoas']


    return pessoas



#======= PONTO DE ENTRADA ===============================

class contaAPagarIntentIntentHandler(AbstractRequestHandler):
    
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("contaAPagarIntent")(handler_input)
    
    def handle(self, handler_input):
        
        card_text = "Nova conta a pagar."
        speak_output = "Ok. Vamos lançar uma nova conta a pagar. Quem é o fornecedor?"
        session_attr = handler_input.attributes_manager.session_attributes
        
        session_attr['estado'] = 500
         
        return (
                handler_input.response_builder
                .speak(speak_output)
                .set_card(StandardCard("Nova conta a pagar", card_text, session_attr['imagem_padrao']))
                .ask(speak_output)
                .response
        )

#======= INTENTS ========================================

class listarFornecedorIntentHandler(AbstractRequestHandler):
    
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("listarFornecedorIntent")(handler_input)
    
    def handle(self, handler_input):
        card_text = ""
        speak_output = ""
        session_attr = handler_input.attributes_manager.session_attributes
        slots = handler_input.request_envelope.request.intent.slots
        fornecedor = slots['fornecedor'].value
        if session_attr['estado'] == 500:
            if fornecedor == "novo":
                
                speak_output = "Vamos implementar a criação de um novo fornecedor em breve"
                card_text = "Em breve"
            
            else:
                
                fornecedores = get_fornecedor(fornecedor, session_attr['chave_sistema'], session_attr['cod_empresa'],  session_attr['base_url'])
                
                if fornecedores:
                    
                    session_attr["fornecedores"] = fornecedores
                    speak_output = "Eu encontrei os seguintes fornecedores com esse nome."
                    
                    contador = 0
                    for fornecedor in fornecedores:
                        contador += 1
                        speak_output += " {0}. {1}.".format(contador, fornecedor['razaoSocial'])
                        card_text += "\n{0} - Fornecedor: {1}\n".format(contador, fornecedor['razaoSocial'])
                    
                    speak_output += " Qual deles eu deveria usar?" 
                    session_attr['estado'] = 501
                else:
                    
                    speak_output = "Nenhum fornecedor com o nome {0} foi encontrado!"
                    card_text = "Fornecedor não encontrado"
        else:
            
            speak_output = "Agora não é o momento pra isso"
            card_text = ""
         
        return (
                handler_input.response_builder
                .speak(speak_output)
                .set_card(StandardCard("Fornecedor.", card_text, session_attr['imagem_padrao']))
                .ask(speak_output)
                .response
        )



class escolheFornecedorIntentHandler(AbstractRequestHandler):
    
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("escolheFornecedorIntent")(handler_input)
    
    def handle(self, handler_input):
        
        card_text = ""
        speak_output = ""
        session_attr = handler_input.attributes_manager.session_attributes
        slots = handler_input.request_envelope.request.intent.slots
        numero = int(slots['numero_fornecedor'].value)
        
        if session_attr['estado'] == 501:
            if (numero > 0) and (numero <= (len(session_attr["fornecedores"]) + 1)):
                
                session_attr["fornecedor_atual"] = session_attr["fornecedores"][numero - 1]
                speak_output += " Fornecedor {0} foi encontrado. Agora informe o número do documento.".format(session_attr["fornecedor_atual"]["razaoSocial"] )
                card_text += "Fornecedor: {0}\nInforme o número do documento.".format(session_attr["fornecedor_atual"]["razaoSocial"] )
                session_attr['estado'] = 502
            
            elif numero > len(session_attr["fornecedores"]) + 1:
                
                speak_output = "O número {0} não corresponde a nenhum fornecedor da lista".format(numero)
                card_text = "Não foi possivel selecionar o fornecedor informado!"
            
        else:
            speak_output = "Agora não é o momento pra isso"
            card_text = ""
            
        return (
                handler_input.response_builder
                .speak(speak_output)
                .set_card(StandardCard("Escolha de fornecedor", card_text, session_attr['imagem_padrao']))
                .ask(speak_output)
                .response
        )


class numeroDocumentoFaturaIntentHandler(AbstractRequestHandler):
    
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("numeroDocumentoFaturaIntent")(handler_input)
    
    def handle(self, handler_input):
        
        card_text = ""
        speak_output = ""
        session_attr = handler_input.attributes_manager.session_attributes
        slots = handler_input.request_envelope.request.intent.slots
        slot_names = ['num_um','num_dois', 'num_tres']
        numero = ""
        
        for nome in slot_names:
            numero += str(slots[nome].value) if slots[nome].value else ""
            
        if session_attr['estado'] == 502:
            
            if len(numero) > 0:
                
                card_text += "Número do documento: {0}".format(numero)
                speak_output += "O número do documento é {0}. Deseja adicionar uma descrição?".format(numero)
                session_attr['estado'] = 503
                session_attr['numero_documento'] = numero
                
            else:
                
                card_text += "Por favor, informe o número do documento!"
                speak_output += "Por favor, informe o número do documento!"
                
        else:
            speak_output = "Agora não é o momento pra isso"
            card_text = ""
            
        return (
                handler_input.response_builder
                .speak(speak_output)
                .set_card(StandardCard("Número do documento.", card_text, session_attr['imagem_padrao']))
                .ask(speak_output)
                .response
        )


class descricaoFaturaIntentHandler(AbstractRequestHandler):
    
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("descricaoFaturaIntent")(handler_input)
    
    def handle(self, handler_input):
        
        card_text = ""
        speak_output = ""
        session_attr = handler_input.attributes_manager.session_attributes
        slots = handler_input.request_envelope.request.intent.slots
        descricao = slots['descricao'].value
            
        if session_attr['estado'] == 504:
            #Escolha do plano de contas precisa ser feita AQUI com estado 505 apos a criacao da API
            card_text += "Descrição da fatura: {0}".format(descricao)
            speak_output += "A sua descrição será: {0}. vai ter mais de uma parcela?.".format(descricao)
            session_attr['descricao_fatura'] = descricao
            session_attr['estado'] = 506
            
        else:
            speak_output = "Agora não é o momento pra isso"
            card_text = ""
            
        return (
                handler_input.response_builder
                .speak(speak_output)
                .set_card(StandardCard("Descrição da fatura", card_text, session_attr['imagem_padrao']))
                .ask(speak_output)
                .response
        )

class vencimentoParcelaIntentHandler(AbstractRequestHandler):
    
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("vencimentoParcelaIntent")(handler_input)
    
    def handle(self, handler_input):
        
        card_text = ""
        speak_output = ""
        session_attr = handler_input.attributes_manager.session_attributes
        slots = handler_input.request_envelope.request.intent.slots
        data = slots['data'].value
            
        if session_attr['estado'] == 510:
            
            if session_attr['parcelado']:
                card_text += "Vencimento da fatura: {0}".format(data)
                speak_output += "O vencimento da fatura será em {0}. qual vai ser o valor?.".format(data)
                session_attr['vencimentos'].append(data)
                session_attr['estado'] = 508
            else:
                card_text += "Vencimento da fatura: {0}".format(data)
                speak_output += "O vencimento da fatura será em {0}. qual vai ser o valor?.".format(data)
                session_attr['vencimentos'] = data
                session_attr['estado'] = 508
            
        else:
            speak_output = "Agora não é o momento pra isso"
            card_text = ""
            
        return (
                handler_input.response_builder
                .speak(speak_output)
                .set_card(StandardCard("Vencimento", card_text, session_attr['imagem_padrao']))
                .ask(speak_output)
                .response
        )


