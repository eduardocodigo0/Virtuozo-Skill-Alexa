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



class cobrancaIntentHandler(AbstractRequestHandler):
    
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("cobrancaIntent")(handler_input)
    
    def handle(self, handler_input):
        
        session_attr = handler_input.attributes_manager.session_attributes
        
        
        chave_sistema = session_attr['chave_sistema']
        codEmpresa = session_attr['cod_empresa'] 
        
        card_text = ""
        speak_output = ""
        session_attr = handler_input.attributes_manager.session_attributes
        slots = handler_input.request_envelope.request.intent.slots
        periodo = slots['periodo'].resolutions.resolutions_per_authority[0].values[0].value.id
        
        MU = money_util()
        
        header = {
            "Content-Type": "application/json",
            "AuthToken": chave_sistema,
            "AuthEnterprise": codEmpresa
        }
                
        params = {}
        
        if int(periodo) == 0:
            
            params = {
                "tipoFatura": "0",
                "tipoFat": "0",
                "dataIni": (date.today().replace(day=1)).strftime("%Y-%m-%d"),
                "dataFim": date.today().strftime("%Y-%m-%d"),
                "dtPesquisa": 1
            }
                        
        elif int(periodo) == 1:
            params = {
                "tipoFatura": "0",
                "tipoFat": "0",
                "dataIni": (date.today().replace(day=1, month=(mes_anterior-1) )).strftime("%Y-%m-%d"),
                "dataFim": date.today().strftime("%Y-%m-%d"),
                "dtPesquisa": 1
            }
        elif int(periodo) == 2:
            params = {
                "tipoFatura": "0",
                "tipoFat": "0",
                "dataIni": (date.today().replace(day=1, month=1 )).strftime("%Y-%m-%d"),
                "dataFim": date.today().strftime("%Y-%m-%d"),
                "dtPesquisa": 1
            }
        
        url = session_attr['base_url']+"pdvs/faturas/"
        
        lista_devedores = []
        
        if params != {}:
            speak_output = "Periodo reconhecido"
            
            
            resposta = requests.get(url, headers=header, params=params)
            if resposta.status_code == 200:
                
                
                dados_json = resposta.json()
                
                if dados_json['parcelas']:
                    
                    for parcela in dados_json['parcelas']:
                        
                        card_text += card_text + "\nNome: {0} Valor: {1} Vencimento: {2}\n".format(parcela['razaoSocial'], MU.moneyToText(parcela['valorTotal']), parcela['dataVencimento'])
                        lista_devedores.append({ "nome":parcela['razaoSocial'], "vencimento":parcela['dataVencimento'], "valor":parcela['valorTotal'], "codigo": parcela['codPessoaRef'] })
                    
                    session_attr['devedores'] = lista_devedores
                    session_attr['estado'] = 300
                    
                    speak_output = "Encontrei {0} cobranças para fazer. A cobrança deve ser feita por e-mail? ou whatsapp?".format(len(lista_devedores))
                    
                else:
                    speak_output = "Ouve um erro na conexão"
                
            else:
                
                speak_output = "Não achei nenhuma cobrança pra fazer feita."
            
            
            
            
        else:
            speak_output = "Não foi possivel reconhecer o período informado."
        
        
        return (
                handler_input.response_builder
                .speak(speak_output)
                .set_card(StandardCard("Cobrança", card_text, session_attr['imagem_padrao']))
                .ask("Posso ajudar em mais alguma coisa?")
                .response
        )

###### MEIO da MSG INTENT HANDLER ###############################################################################################

def manda_msg(num, msg):
    
    resultado = "Erro ao enviar mensagem"
    token = "INSERIR TOKEN DA API DIGISAC"
    service_id = "INSERIR SERVICE ID DA API DIGISAC"

    header = {
        "Content-Type": "application/json",
        "Authorization": "Bearer {0}".format(token)
    }

    json_data = {

        "text": msg,
        "number": "55{0}".format(num),
        "serviceId": service_id
    }

    url = "INSERIR URL DA API DIGISAC"
    resposta = requests.post(url, headers=header, json=json_data)

    if resposta.status_code == 200:

        resultado = "A mensagem de cobrança foi enviada com sucesso"

    else:

        resultado = "Ouve um erro ao enviar a mensagem"

    return resultado


class meioIntentHandler(AbstractRequestHandler):
    
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("meioIntent")(handler_input)
    
    def handle(self, handler_input):
        
        card_text = ""
        speak_output = ""
        session_attr = handler_input.attributes_manager.session_attributes
        slots = handler_input.request_envelope.request.intent.slots
        
        meio = slots['meio'].value
        
        header = {
            "Content-Type": "application/json",
            "AuthToken": chave_sistema,
            "AuthEnterprise": codEmpresa
        }
        
        if session_attr['estado'] == 300:
            if meio == "whatsapp":
                
                devedores = session_attr['devedores']
                for devedor in devedores:
                    
                    params = { "query":devedor["codigo"]}
                    url =  session_attr['base_url'] + "/pessoas/0"
                    resposta = requests.get(url, headers=header, params=params)

                    if resposta.status_code == 200:
                        
                        dados_json = resposta.json()
                        for pessoa in dados_json['pessoas']:
                            
                            if pessoa['numTelefone']:
                                
                                res = manda_msg(pessoa['numTelefone'], "[TESTE ESTAGIARIO ]Oi, lembre-se de pagar sua conta") 
                                speak_output = speak_output + "{0} para {1}. ".format(res, devedor["nome"])
                                card_text = card_text + "{0} para {1}. \n".format(res, devedor["nome"])
                                
                            else:
                                
                                speak_output = speak_output + "{0} não tem um tefelone cadastrado. ".format(devedor["nome"])
                                card_text = card_text + "{0} não tem um tefelone cadastrado. \n".format(devedor["nome"])
                
                
                
            else:
                
                speak_output = "Por enquanto apenas via whatsapp"
                card_text = "Por enquanto apenas via whatsapp"
                
            
        session_attr['estado'] = 0
         
        return (
                handler_input.response_builder
                .speak(speak_output)
                .set_card(StandardCard("Cobrança", card_text, session_attr['imagem_padrao']))
                .ask("Posso ajudar em mais alguma coisa?")
                .response
        )
        
        
        
        
        