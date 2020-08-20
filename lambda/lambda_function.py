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

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


chave_sistema = "000"#alterar para sua chave
codEmpresa = "000"#alterar para seu codigo
codApp = "12"

url_base = "https://app.teste.virtuozo.com.br/api/v1/"#Alterar para URL oficial


imagem_padrao = Image("https://i.imgur.com/L2N6x19.png", "https://i.imgur.com/L2N6x19.png")



class Utilitarios:
    
    def teste():
        pass



class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Bem vindo ao virtuoso gestão empresarial!"
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )



class faturasHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("faturaIntent")(handler_input)

    def handle(self, handler_input):
        
        header =  {
            "Content-Type": "application/json",
            "AuthToken": chave_sistema,
            "AuthEnterprise": codEmpresa
        }
        
        params = {
            "tipoFatura":1
        }
        
        
        card_text = ""
        img = imagem_padrao
        url = url_base + "pdvs/faturas/"
        resposta = requests.get(url, headers=header, params=params)
        
        if resposta.status_code == 200:
            speak_output = "Aqui estão suas faturas a pagar"
            
            dados_json = resposta.json()
            for parcela in dados_json['parcelas']:
                card_text = card_text +"Valor: {0}        Vencimento: {1}     Fornecedor: {2}\n\n".format(parcela['valorTotal'], parcela['dataVencimento'], parcela['razaoSocial'])
            
        else:
            speak_output = "Não achei nenhuma fatura!"
            
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .set_card(StandardCard("Faturas", card_text, img))
                .ask("Posso ajudar em mais alguma coisa?")
                .response
        )




class pagamentoNoPeriodoHandler(AbstractRequestHandler):
    
    def can_handle(self, handler_input):
        
        return ask_utils.is_intent_name("pagamentoNoPeriodoIntent")(handler_input)
    
    def handle(self, handler_input):
        
        
        periodo = 4
        data_ini = ""
        data_fim = date.today().strftime("%Y-%m-%d")
        
        slots = handler_input.request_envelope.request.intent.slots
        periodo = slots['momento'].value
        
        if periodo == "dia" or periodo == "hoje":
            
            data_ini = date.today().strftime("%Y-%m-%d")
           
        elif periodo == "semana":
            
            dia_da_semana = (date.today().weekday())+1
            data_ini = (date.today() + timedelta(days=-dia_da_semana)).strftime("%Y-%m-%d")
        
        elif periodo == "mês":
            
            data_ini = (date.today().replace(day=1)).strftime("%Y-%m-%d")
        
        elif periodo == "ano":
            
            data_ini = (date.today().replace(day=1, month=1)).strftime("%Y-%m-%d")
        
        
        header =  {
            "Content-Type": "application/json",
            "AuthToken": chave_sistema,
            "AuthEnterprise": codEmpresa
        }
        
        params = {
            "tipoFatura":1,
            "dataIni": data_ini,
            "dataFim": data_fim,
            "dtPesquisa": 2
        }
        
        img = imagem_padrao
        url = url_base + "pdvs/faturas/"
        resposta = requests.get(url, headers=header, params=params)
        
        speak_output = ""
        card_text = ""

        
        if resposta.status_code == 200:
            
            dados_json = resposta.json()
            qtd = len(dados_json['parcelas'])
            
            if qtd == 1: 
                speak_output ="Você pagou uma conta nesse período." 
            else: 
                speak_output ="Você pagou {0} contas nesse período.".format(qtd)
                
            card_text = "Contas pagas em - {0}\n\n".format(periodo)
            
            
            for parcela in dados_json['parcelas']:
                
                
                fornecedor = parcela['razaoSocial']
                valor = float(parcela['valorParcela'])
                    
                reais = round(int(valor))
                centavos = int((valor - reais) * 100)
                centavos = str(centavos)
                reais = str(reais)
                
                card_text = card_text + "\n\nValor: R${0}   Fornecedor: {1}".format(parcela['valorParcela'][:-1], parcela['razaoSocial'])
                
                
                if len(centavos) > 2:
                    centavos = centavos[:1]
                
                if int(centavos) > 0:
                    speak_output = speak_output + "{0} Reais e {1} centavos para {2}. ".format(reais, centavos, fornecedor)
                else:
                    speak_output = speak_output + "{0} Reais para {1}. ".format(reais, fornecedor)
                    
                
                for baixa in parcela['baixas']:
                    valor_bruto = baixa['valorBruto'][:-1]
                    
                    card_text = card_text +"\n\n * Data da Baixa: {0}    Valor Bruto: R${1}".format(baixa['dataBaixa'][:11], valor_bruto)
        
        else:
            
            speak_output = "Não consegui me comunicar com o sistema do virtuozo!"
                
        
        
        return (
                handler_input.response_builder
                .speak(speak_output)
                .set_card(StandardCard("Pagamentos ", card_text, img))
                .ask("Posso ajudar em mais alguma coisa?")
                .response
            )


class pagamentoHojeHandler(AbstractRequestHandler):
    
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("pagamentoHojeIntent")(handler_input)
    
    def handle(self, handler_input):
        
        hoje = date.today().strftime("%Y-%m-%d")
        
        header =  {
            "Content-Type": "application/json",
            "AuthToken": chave_sistema,
            "AuthEnterprise": codEmpresa
        }
        
        params = {
            "tipoFatura":1,
            "dataIni": hoje,
            "dataFim": hoje,
            "dtPesquisa": 1
        }
        
        total = 0.0
        
        card_text = "Contas a pagar.\n Data: {0}\n\n".format(date.today().strftime("%d/%m/%Y"))
        
        img = imagem_padrao
        url = url_base + "pdvs/faturas/"
        resposta = requests.get(url, headers=header, params=params)
        
        if resposta.status_code == 200:
            dados_json = resposta.json()
            qtd = len(dados_json['parcelas'])
            if qtd > 0:
                if qtd == 1:
                    speak_output = "Você tem {0} pagamento pra fazer hoje.".format(qtd)
                else:
                    speak_output = "Você tem {0} pagamentos pra fazer hoje.".format(qtd)
                
                for parcela in dados_json['parcelas']:
                    
                    fornecedor = parcela['razaoSocial']
                    valor = float(parcela['valorTotal'])
                    
                    card_text = card_text + "\nFornecedor: {1}  Valor: R${0}".format(valor, fornecedor)
                    total += valor
                    reais = round(int(valor))
                    centavos = int((valor - reais) * 100)
                    centavos = str(centavos)
                    
                    if len(centavos) > 2:
                        centavos = centavos[:1]
                    
                    if int(centavos) > 0:
                        speak_output = speak_output + " {0} Reais e {1} centavos para {2}. ".format(str(reais), str(centavos), fornecedor)
                    else:
                        speak_output = speak_output + " {0} Reais para {2}. ".format(str(reais), fornecedor)
                
                card_text += "\n\nTotal: R${0}".format(total)
                
            else:
                speak_output = "Você não tem pagamentos pra fazer hoje."
                card_text = "Nada para pagar hoje."
                
        else:
            speak_output = "Não consegui me comunicar com o sistema do virtuozo!"
        
        return(
            handler_input.response_builder
            .speak(speak_output)
            .set_card(StandardCard("Pagamentos do dia.", card_text, img))
            .ask("Posso ajudar em mais alguma coisa?")
            .response
            )
        
    


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





class listarClientesHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("listarClientesIntent")(handler_input)

    def handle(self, handler_input):
        
        header =  {
            "Content-Type": "application/json",
            "AuthToken": chave_sistema,
            "AuthEnterprise": codEmpresa
        }
        
        
        card_text = ""
        img = imagem_padrao
        url = url_base + "pessoas/0"
        resposta = requests.get(url, headers=header)
        
        if resposta.status_code == 200:
            speak_output = "Vou escrever o nome dos clientes na tela."
            
            dados_json = resposta.json()
            for pessoa in dados_json['pessoas']:
                card_text = card_text + "\n{0}".format(pessoa['razaoSocial'])
            
        else:
            speak_output = "Não achei nenhum cliente!"
            
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .set_card(StandardCard("Clientes", card_text, img))
                .ask("Posso ajudar em mais alguma coisa?")
                .response
        )

class precoHandler(AbstractRequestHandler):
    
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("precoIntent")(handler_input)

    def handle(self, handler_input):
        
        slots = handler_input.request_envelope.request.intent.slots
        produto = slots['produto']
        
        header =  {
            "Content-Type": "application/json",
            "AuthToken": chave_sistema,
            "AuthEnterprise": codEmpresa
        }
        
        params = {
            'texto': produto.value
        }
        
        card_text = ""
        url = url_base + "\produtos"
        resposta = requests.get(url, headers=header, params=params)
        if resposta.status_code == 200:
            
            dados_json = resposta.json()
            
            if not dados_json['produtos']:
                speak_output = "produto {0} nao encontrado".format(produto.value)
            else:
                valor = dados_json['produtos'][0]["precoVista"]
                speak_output = "O produto {0} custa {1}".format(produto.value, valor)
                card_text = "{0} custa apenas: {1}. Aproveite!".format(produto.value, valor)
            
            
                
        else:
            speak_output =  "Erro {0}".format(resposta.status_code)
            
        return (
            handler_input.response_builder
                .speak(speak_output)
                .set_card(SimpleCard("Valor", card_text))
                .ask("Posso ajudar em mais alguma coisa?")
                .response
        )


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Você pode me perguntar o que pagou nessa semana, me perguntar das parcelas que precisa pargar hoje ou pedir para que eu mostre os clientes."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Tchau!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "Você acabou de ativar" + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Desculpe, não entendi o que eu deveria fazer!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.


sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(estoqueIntentHandler())
sb.add_request_handler(precoHandler())
sb.add_request_handler(listarClientesHandler())
sb.add_request_handler(faturasHandler())
sb.add_request_handler(pagamentoHojeHandler())
sb.add_request_handler(pagamentoNoPeriodoHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler()) # Precisa ser por ultimo para nao sobreescrever os outros handlers

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()