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

class cadastrarPessoaJuridicaIntentHandler(AbstractRequestHandler):
    #PESSOA JURIDICA
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("cadastrarPessoaJuridicaIntent")(handler_input)
    
    
    def handle(self, handler_input):
        header = {
                "Content-Type": "application/json",
                "AuthToken": chave_sistema,
                "AuthEnterprise": codEmpresa
        }
                        
        session_attr = handler_input.attributes_manager.session_attributes
        slots = handler_input.request_envelope.request.intent.slots
        
        cnpj_um = ""
        cnpj_dois = ""
        cnpj_tres = ""
        cnpj_quatro = ""
        cnpj_cinco = ""
        
        cnpj_quatro = str(slots['cnpj_quatro'].value)
        for i in range(4 - len(str(cnpj_quatro)) ):
            cnpj_quatro = "0" + cnpj_quatro
            
        cnpj_dois = str(slots['cnpj_dois'].value)
        for i in range(3 - len(str(cnpj_dois)) ):
            cnpj_dois = "0" + cnpj_dois
            
        cnpj_tres = str(slots['cnpj_tres'].value)
        for i in range(3 - len(str(cnpj_tres)) ):
            cnpj_tres = "0" + cnpj_tres
            
        if len(str(slots['cnpj_um'].value)) <= 1:
            cnpj_um = "0"+str(slots['cnpj_um'].value)
        else:
            cnpj_um = str(slots['cnpj_um'].value)
            
        if len(str(slots['cnpj_cinco'].value)) <= 1:
            cnpj_cinco= "0"+str(slots['cnpj_cinco'].value)
        else:
            cnpj_cinco = str(slots['cnpj_cinco'].value)
        
        documento = cnpj_um+cnpj_dois+cnpj_tres+cnpj_quatro+cnpj_cinco
        
        speak_output = ""
        card_text = ""
        
        
        card_text += "DOCUMENTO: {0}\n".format(documento)
        
        dados = {}
        
        dados['cnpj'] = documento
        
        body = {
            "Datasets": "basic_data, addresses_extended, emails_extended",
            "q": "doc{"+documento+"}",
            "AccessToken": "fbcaf2bd-9ab9-48d3-aaf2-ab60acb43540"
        }
        
        url = "https://bigboost.bigdatacorp.com.br/companies"
        resposta = requests.get(url, headers=header, params=body)
        
        if len(documento) == 14:
            
            if resposta.status_code == 200:
                #Filtro de dados
                dados_json = resposta.json()
                try:
                    dados['nome'] = dados_json['Result'][0]['BasicData']['OfficialName']
                    dados['email'] = dados_json['Result'][0][ 'ExtendedEmails']['Emails'][0]['EmailAddress']
                    dados['cep'] = dados_json['Result'][0]['ExtendedAddresses']['Addresses'][0]['ZipCode']
                    dados['endereco'] = dados_json['Result'][0]['ExtendedAddresses']['Addresses'][0]['AddressMain']
                    dados['cidade'] = dados_json['Result'][0]['ExtendedAddresses']['Addresses'][0]['City']
                    dados['numero'] = dados_json['Result'][0]['ExtendedAddresses']['Addresses'][0]['Number']
                    dados['complemento'] = dados_json['Result'][0]['ExtendedAddresses']['Addresses'][0]['Complement']
                    dados['bairro'] = dados_json['Result'][0]['ExtendedAddresses']['Addresses'][0]['Neighborhood']
                    
                except:
                    dados = {}  
                
            else:
                dados = {}
        else:
            dados = {}
        
        if not dados:
            card_text = card_text + "\nOs dados do documento informado não foram encontrados!"
            speak_output = "O documento não foi encontrado!"
        else:
            session_attr['estado'] = 101 # PESOA JURIDICA
            session_attr['dados'] = dados
            
            speak_output = "A pessoa {0} foi encontrada, deseja confirmar o cadastro?".format(dados['nome'])
            
            
            
        return (
                handler_input.response_builder
                .speak(speak_output)
                .set_card(StandardCard("Cadastro de pessoa", card_text, imagem_padrao))
                .ask("Posso ajudar em mais alguma coisa?")
                .response
                )


class cadastrarPessoaIntentHandler(AbstractRequestHandler):
    #PESSOA FISICA
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("cadastrarPessoaIntent")(handler_input)
        
    def handle(self, handler_input):
        
        header = {
                "Content-Type": "application/json",
                "AuthToken": chave_sistema,
                "AuthEnterprise": codEmpresa
        }
                        
        session_attr = handler_input.attributes_manager.session_attributes
        slots = handler_input.request_envelope.request.intent.slots
        documento = str(slots['cpf_um'].value)+str(slots['cpf_dois'].value)+str(slots['cpf_tres'].value)+str(slots['cpf_quatro'].value)
        
        
        speak_output = ""
        card_text = ""
        
        
        
        card_text += "DOCUMENTO: {0}\n".format(documento)
        
        dados = {}
        
        
        
        if len(documento) == 11:
            # Documento de 11 digitos = CPF
            
            dados['cpf'] = documento
            
            body = {
                "Datasets": "basic_data, addresses_extended, emails_extended",
                "q": "doc{" + documento + "}",
                "AccessToken": "fbcaf2bd-9ab9-48d3-aaf2-ab60acb43540"
            }
            
            url = "https://bigboost.bigdatacorp.com.br/peoplev2"
            resposta = requests.get(url, headers=header, params=body)
            
            if resposta.status_code == 200:
                
                dados_json = resposta.json()
                
                try:
                    
                    dados['nome'] = dados_json['Result'][0]['BasicData']['Name']
                    dados['email'] = dados_json['Result'][0]['ExtendedEmails']['Emails'][0]['EmailAddress']
                    card_text += "Nome: {0}\n".format(dados['nome'])
                    
                except:
                    dados = {}
                    
            else:
                dados = {}
                
                
        if not dados:
            card_text = card_text + "\nOs dados do documento informado não foram encontrados!"
            speak_output = "O documento não foi encontrado!"
        else:
            session_attr['estado'] = 100
            session_attr['dados'] = dados
            
            speak_output = "A pessoa {0} foi encontrada, deseja confirmar o cadastro?".format(dados['nome'])
            
            
            
        return (
                handler_input.response_builder
                .speak(speak_output)
                .set_card(StandardCard("Cadastro de pessoa", card_text, imagem_padrao))
                .ask("Posso ajudar em mais alguma coisa?")
                .response
            )