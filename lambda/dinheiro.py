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




class dinheiroIntentHandler(AbstractRequestHandler):
    
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("dinheiroIntent")(handler_input)
    
    def handle(self, handler_input):
        
        card_text = ""
        speak_output = ""
        session_attr = handler_input.attributes_manager.session_attributes
        
        slots = handler_input.request_envelope.request.intent.slots
        reais = str(slots['reais'].value)
        
        MU = money_util()
        
        
        
        if slots['centavos'].value:
            
            centavos = str(slots['centavos'].value)
        else:
            
            centavos = "0"
        
        
        if int(centavos) < 10:
            centavos = "0" + centavos
            
            
        if session_attr['estado'] == 210:
            session_attr['precoPrazo'] = "{0},{1}".format(reais, centavos)
            card_text = "Valor a prazo: {0},{1}".format(reais, centavos)
            speak_output = "O valor do produto a prazo vai ser de {0} reais e {1} centavos.\n posso cadastrar?".format(reais, centavos)
            session_attr['estado'] = 220
            
        #Valor da fatura a pagar
        if session_attr['estado'] == 508:
            
            if  not session_attr['parcelado']:
                session_attr['valor_fatura'] = "{0},{1}".format(reais, centavos)
                card_text = "Valor da fatura: {0},{1}".format(reais, centavos)
                speak_output = "O valor da fatura vai ser de {0} reais e {1} centavos. Você confirma a criação dessa nova conta a pagar?".format(reais, centavos)
                session_attr['estado'] = 555
            
            else:
                session_attr['parcelas'].append("{0},{1}".format(reais, centavos))
                card_text = "Valor da parcela: {0},{1}".format(reais, centavos)
                speak_output = "Uma parcela de {0} reais e {1} centavos foi adicionada. Deseja adicionar mais uma parcela?".format(reais, centavos)
                session_attr['estado'] = 512
                
        
        
        return (
                handler_input.response_builder
                .speak(speak_output)
                .set_card(StandardCard("Valor", card_text, session_attr['imagem_padrao']))
                .ask("Posso ajudar em mais alguma coisa?")
                .response
        )



#========= Mostra a soma do saldo de todas as contas bancarias =========

class dinheiroDisponivelIntentHandler(AbstractRequestHandler):
    
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("dinheiroDisponivelIntent")(handler_input)
    
    def handle(self, handler_input):

        card_text = ""
        speak_output = ""
        session_attr = handler_input.attributes_manager.session_attributes
        
        chave_sistema = session_attr['chave_sistema']
        codEmpresa = session_attr['cod_empresa'] 

        header = {
            "Content-Type": "application/json",
            "AuthToken": chave_sistema,
            "AuthEnterprise": codEmpresa
        }

        
        url =  session_attr['base_url']+"/accountsBalances"
        resposta = requests.get(url, headers=header)

        if resposta.status_code == 200:

            dados_json = resposta.json()
            txt = str(dados_json['totalBalance'])
            real, centavo = txt.split(".")

            if int(centavo) > 0:
                speak_output = "Você tem {0} reais e {1} centavos de dinheiro disponível".format(real, centavo)
                card_text = "Dinheiro disponível: R${0},{1}".format(real, centavo)
            else:
                speak_output = "Você tem {0} reais de dinheiro disponível".format(real)
                card_text = "Dinheiro disponível: R${0},00".format(real)

        else:
            speak_output = "Ouve um erro, Não consegui ver o seu Saldo."
            card_text = "Erro ao consultar saldo."

        return (
                handler_input.response_builder
                .speak(speak_output)
                .set_card(StandardCard("Saldo total disponível", card_text, session_attr['imagem_padrao']))
                .ask("Posso ajudar em mais alguma coisa?")
                .response
        )
#========= Mostra o saldo de uma conta bancaria escolhida ou de todas uma por uma ==============

class mostraSaldoIntentHandler(AbstractRequestHandler):
    
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("mostraSaldoIntent")(handler_input)
    
    def handle(self, handler_input):

        card_text = ""
        speak_output = ""
        session_attr = handler_input.attributes_manager.session_attributes
        slots = handler_input.request_envelope.request.intent.slots
        pesquisa = slots['banco'].value
        
        chave_sistema = session_attr['chave_sistema']
        codEmpresa = session_attr['cod_empresa'] 

        header = {
            "Content-Type": "application/json",
            "AuthToken": chave_sistema,
            "AuthEnterprise": codEmpresa
        }

        url =  session_attr['base_url']+"/accountsBalances"
        resposta = requests.get(url, headers=header)

        if resposta.status_code == 200:

            dados_json = resposta.json()
            contas = dados_json['accountBalances']

            if SequenceMatcher(None, "todos", pesquisa).ratio() <= 0.6:
                
                menor = 0.0
                conta_escolhida = {}
                
                for conta in contas:
                    
                    atual = SequenceMatcher(None, conta['razaoSocial'], pesquisa).ratio()
                    if atual >= menor:
                        
                        menor, conta_escolhida = atual, conta
                        
                txt = str(conta_escolhida['saldoPosterior'])
                real, centavo = txt.split(".")

                if int(centavo) > 0:
                    if len(centavo) >= 3: centavo = centavo[:-1]
                    speak_output = "Você tem {0} reais e {1} centavos de saldo em {2}".format(real, centavo, conta_escolhida['razaoSocial'])
                    card_text = "{2}: R${0},{1}".format(real, centavo, conta_escolhida['razaoSocial'])
                else:
                    speak_output = "Você tem {0} reais de saldo em {1}".format(real, conta_escolhida['razaoSocial'])
                    card_text = "{1}: R${0},00".format(real, conta_escolhida['razaoSocial'])
                
                
            else:
                
                speak_output = "Aqui estão os seus saldos em cada uma de suas contas. "
                
                for conta in contas:
                    
                    txt = str(conta['saldoPosterior'])
                    
                    real, centavo = txt.split(".")
                    
                    
                    if int(centavo) > 0:
                        if len(centavo) >= 3: centavo = centavo[:-1]
                        speak_output += "{0} reais e {1} centavos de saldo em {2}. ".format(real, centavo, conta['razaoSocial'])
                        card_text += "\n\n{2}: R${0},{1}".format(real, centavo, conta['razaoSocial'])
                        
                    else:
                        speak_output += "{0} reais de saldo em {1}. ".format(real, conta['razaoSocial'])
                        card_text += "\n\n{1}: R${0},00".format(real, conta['razaoSocial'])
                        

        else:
            speak_output = "Ouve um erro, Não consegui ver o seu Saldo."
            card_text = "Erro ao consultar saldo."

        return (
                handler_input.response_builder
                .speak(speak_output)
                .set_card(StandardCard("Saldo", card_text, session_attr['imagem_padrao']))
                .ask("Posso ajudar em mais alguma coisa?")
                .response
        )





    