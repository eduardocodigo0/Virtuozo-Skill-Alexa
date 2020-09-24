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


chave_sistema = "xxx"
codEmpresa = "xxx"
codApp = "xxx"

url_base = "https://app.teste.virtuozo.com.br/api/v1/"


imagem_padrao = Image("https://i.imgur.com/L2N6x19.png", "https://i.imgur.com/L2N6x19.png")


def cadastrar_produto(descricao):
    header ={
    "Content-Type": "application/json",
    "AuthToken": chave_sistema,
    "AuthEnterprise": codEmpresa
    }
    
    params = '''
{
    "codProduto":"novo",
    "descrProduto":"%s",
    "flagAtivo": 1,
    "flagEstoque": 1,
    "margemLucro": 0,
    "grades": [
        {
            "codProdutoGrade": "novo",
            "codProduto": "novo",
            "codBarras": "novo",
            "flagAtivo": 1,
            "precoCusto": "1.000",
            "precoVista": "1.500",
            "precoPrazo": "2.500",
            "estoqueMinimo": "1.0000",
            "descMargemVista": "0.0",
            "codUnd": 9
        }
    ]
}'''%descricao
    
    url = "https://app.teste.virtuozo.com.br/api/v1/produto/novo"
    
    json_params = json.loads(params)
    resposta = requests.post(url, headers=header, json=json_params)
    
    result = ""
    
    if resposta.status_code == 200:
        result = "foi cadastrado com sucesso"
    else:
        result= "não foi cadastrado com sucesso"
        
    return result


class YesIntentHandler(AbstractRequestHandler):
    
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AMAZON.YesIntent")(handler_input)
        
    def handle(self, handler_input):
        session_attr = handler_input.attributes_manager.session_attributes
        card_text = ""
        
        if session_attr['estado'] != 0:
            
            
            if session_attr['estado'] == 200:
                session_attr['estado'] = 210
                speak_output = "Qual é o valor a prazo?"
                card_text = "Informe o valor do produto a prazo"
            
            if session_attr['estado'] == 220:
                session_attr['estado'] = 0
                desc = session_attr['dados-produto']
                if cadastrar_produto(desc):
                    speak_output = "O produto {0} foi encontrado e cadastrado com sucesso!".format(desc)
                    card_text = "Código: {0}\nNome: {1}\n\nCadastrado com sucesso".format(codigo, desc)
                else:
                    speak_output = "Não consegui cadastrar o produto {0}.".format(desc)
                    card_text = "Código: {0}\nNome: {1}\n\nErro ao cadastrar o produto".format(codigo, desc)
            
            header = {
                "Content-Type": "application/json",
                "AuthToken": chave_sistema,
                "AuthEnterprise": codEmpresa
            }
            
            
            if session_attr['estado'] == 100 or session_attr['estado'] == 101 : #100 = Estado de confirmacao de pessoa fisica #101 = Pessoa Juridica
                
                session_attr['estado'] = 0
                
                dados = session_attr['dados']
                if len(dados) <= 4:
                    params = '''
                    {
                        "cnpjCpf":"%s",
                        "razaoSocial":"%s",
                        "email":"%s"
                    }
                    '''%(dados['cpf'], dados['nome'], dados['email'])
                else:
                    params = '''
                    {
                            "cnpjCpf":"%s",
                            "razaoSocial":"%s",
                            "email":"%s",
                            "enderecos":{
                                "cep":"%s",
                                "endereco":"%s",
                                "cidade":"%s",
                                "numero":"%s",
                                "bairro":"%s",
                                "complemento":"%s"
                            }
                    }
                    '''%(dados['cnpj'], dados['nome'], dados['email'],dados['cep'], dados['endereco'], dados['cidade'], dados['numero'], dados['bairro'], dados['complemento'])
                
                
                url = "https://app.teste.virtuozo.com.br/api/v1/pessoa/nova"
                    
                json_params = json.loads(params)
                resposta = requests.post(url, headers=header, json=json_params)
                
                if resposta.status_code == 200:
                    
                    speak_output = "Pessoa encontrada e cadastrada com sucesso!"
                    card_text = card_text + "\nPessoa encontrada e cadastrada com sucesso!"
                    
                else:
                    
                    speak_output = "A pessoa foi encontrada mas ouve um erro no cadastro!"
                    card_text = card_text + "Erro no cadastro!"
            
            
        else:
            speak_output = "Eu ainda não pedi a confirmação de nada."
            card_text = ""

        return (
                handler_input.response_builder
                .speak(speak_output)
                .set_card(StandardCard("Confirmação", card_text, imagem_padrao))
                .ask("Posso ajudar em mais alguma coisa?")
                .response
        )


class NoIntentHandler(AbstractRequestHandler):
    
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AMAZON.NoIntent")(handler_input)
        
    def handle(self, handler_input):
        session_attr = handler_input.attributes_manager.session_attributes
        card_text = ""
        
        if session_attr['estado'] != 0:
            
            
            if session_attr['estado'] == 200 or session_attr['estado'] == 220:
                speak_output = "Cancelando o cadastro de produto."
                card_text = "Cadastro de produto cancelado."
                session_attr['estado'] = 0
                session_attr['dados-produto'] = {}
            
            if session_attr['estado'] == 100 or session_attr['estado'] == 101: #100 = Estado de confirmacao de pessoa
                speak_output = "Cancelando o cadastro."
                card_text = "Cadastro cancelado"
                session_attr['estado'] = 0
                session_attr['dados'] = {}
                
            
        else:
            speak_output = "Eu ainda não pedi a confirmação de nada."  
            
        
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .set_card(StandardCard("Confirmação", card_text, imagem_padrao))
                .ask("Posso ajudar em mais alguma coisa?")
                .response
        )
        
