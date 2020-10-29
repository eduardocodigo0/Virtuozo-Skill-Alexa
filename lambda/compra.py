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




#======= PONTO DE ENTRADA ===============================

class compraIntentHandler(AbstractRequestHandler):
    
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("compraIntent")(handler_input)
    
    def handle(self, handler_input):
        
        
        
        card_text = "Iniciando nova venda."
        speak_output = "Iniciando uma nova venda. Quais produtos você quer vender?"
        session_attr = handler_input.attributes_manager.session_attributes
        session_attr['estado'] = 400
        session_attr['carrinho'] = []
        session_attr['qtd_compra'] = []
         
        return (
                handler_input.response_builder
                .speak(speak_output)
                .set_card(StandardCard("Nova compra", card_text, session_attr['imagem_padrao']))
                .ask(speak_output)
                .response
        )

#======= CANCELAR COMPRA ===============================

class cancelarCompraIntentHandler(AbstractRequestHandler):
    
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("cancelaCompraIntent")(handler_input)
    
    def handle(self, handler_input):
        
        session_attr = handler_input.attributes_manager.session_attributes
        
        if session_attr['estado'] >= 400 and session_attr['estado'] <= 499:
            session_attr['estado'] = 0
            session_attr['carrinho'] = []
            card_text = "Venda cancelada."
            speak_output = "Sua venda foi cancelada."
        
        else:
            card_text = "Nenhuma venda em progresso."
            speak_output = "Você não tem nenhuma venda em progresso."
         
        return (
                handler_input.response_builder
                .speak(speak_output)
                .set_card(StandardCard("Desistiu da venda", card_text, session_attr['imagem_padrao']))
                .ask(speak_output)
                .response
        )


#==== INSERIR PRODUTO =========================================

class addProdutoIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("addProdutoIntent")(handler_input)
    
    def handle(self, handler_input):
        
        session_attr = handler_input.attributes_manager.session_attributes
        
        
        chave_sistema = session_attr['chave_sistema']
        codEmpresa = session_attr['cod_empresa'] 
        
        if session_attr['estado'] == 400:
            
            speak_output = ""
            card_text = ""
            slots = handler_input.request_envelope.request.intent.slots
            produto = slots['produto'].value
            
            header =  {
    
                "Content-Type": "application/json",
                "AuthToken": chave_sistema,
                "AuthEnterprise": codEmpresa
            
            }
            
            params = {
            
                'texto': produto
    
            }
            
            url = session_attr['base_url'] + "/produtos"
            resposta = requests.get(url, headers=header, params=params)
            
            if resposta.status_code == 200:
                
                dados_json = resposta.json()
                
                if not dados_json['produtos']:
                    
                    speak_output = "Não encontrei nenhum produto com esse nome!"
                    card_text = "Nenhum produto foi encontrado"
                    
                else:
                    
                    speak_output = "Eu encontrei os seguintes produtos com essa descrição. "
                    
                    
                    count = 0
                    session_attr['produtos_encontrados'] = []
                    
                    for produto in dados_json['produtos']:
                        count += 1
                        
                        MU = money_util()
                        
                        
                        session_attr['produtos_encontrados'].append({"num":count, "dados":produto})
                        
                        nome = produto['descrProduto']
                        MU = money_util()
                        
                        valor_fala = MU.moneyToSpeak(produto['precoPrazo'])
                        valor_texto = MU.moneyToText(produto['precoPrazo'])
                        
                        
                        speak_output = speak_output + "{0}. {1} com o preço de {2}. ".format(count, nome, valor_fala)
                            
                            
                        card_text += "{0} - PRODUTO: {1}\n".format(count,produto['descrProduto'])
                        card_text += "VALOR: {0}\n\n".format(valor_texto)
                        
                    speak_output = speak_output + " Qual deles você gostaria de adicionar a venda?"
                    session_attr['estado'] = 410
            else:
                
                speak_output = "Ouve um erro ao acessar o servidor."
                card_text = "Erro ao acessar o servidor!"
        
        else:
            card_text = "Nenhuma venda em progresso."
            speak_output = "Você não tem nenhuma venda em progresso."
         
        return (
                handler_input.response_builder
                .speak(speak_output)
                .set_card(StandardCard("Adicionar produto na venda", card_text, session_attr['imagem_padrao']))
                .ask(speak_output)
                .response
        )
#============= ECOLHER PRODUTO ===================================================

class escolheProdutoIntentHandler(AbstractRequestHandler):
    
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("escolheProdutoIntent")(handler_input)
    
    def handle(self, handler_input):
        card_text = ""
        speak_output = ""
        session_attr = handler_input.attributes_manager.session_attributes
        slots = handler_input.request_envelope.request.intent.slots
        item = slots['item'].value
        
        session_attr['produto_temp'] = {}
        
        if session_attr['estado'] == 410:
            
            
            
            try:
                card_text = "Produto adicionado."
                desc = session_attr['produtos_encontrados'][int(item) - 1]['dados']['descrProduto']
                session_attr['produto_temp'] = session_attr['produtos_encontrados'][int(item) - 1]['dados']
                speak_output = "Produto {0} foi selecionado, por favor informe a quantidade.".format(desc)
                session_attr['estado'] = 420
                session_attr['produtos_encontrados'] = []
                
                
            except:
                speak_output = "Nenhum produto da lista foi adicionado a venda"
                card_text = "Produto fora da lista."
                session_attr['estado'] = 400
                session_attr['produtos_encontrados'] = []
        else:
            card_text = "Primeiro peça para adicionar um item a venda."
            speak_output = "Primeiro peça para adicionar um item a venda."
         
        return (
                handler_input.response_builder
                .speak(speak_output)
                .set_card(StandardCard("Escolhendo produto", card_text, session_attr['imagem_padrao']))
                .ask(speak_output)
                .response
        )

#============== QTD =============================================

class qtdProdutoCompraIntentHandler(AbstractRequestHandler):
    
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("qtdProdutoCompraIntent")(handler_input)
    
    def handle(self, handler_input):
        card_text = ""
        speak_output = ""
        session_attr = handler_input.attributes_manager.session_attributes
        slots = handler_input.request_envelope.request.intent.slots
        qtd = slots['qtd'].value
        
        if session_attr['estado'] == 420:
            
            
            nome = session_attr['produto_temp']["descrProduto"]
            
            if int(qtd) > 0:
                if qtd == 1:
                    speak_output = " {0} unidade do produto {1}, foram adicionadas na sua venda! Gostaria de adicionar mais alguma coisa?".format(qtd, nome)
                else:
                    speak_output = " {0} unidades do produto {1}, foram adicionadas na sua venda! Gostaria de adicionar mais alguma coisa?".format(qtd, nome)
                
                card_text = " {0} unidades do produto {1}, foram adicionadas na sua venda!".format(qtd, nome)
                session_attr['carrinho'].append(session_attr['produto_temp'])
                session_attr['qtd_compra'].append(qtd)
                
                session_attr['estado'] = 400
                
            else:
                speak_output = "A quantidade precisa ser um número maior que zero"
         
        return (
                handler_input.response_builder
                .speak(speak_output)
                .set_card(StandardCard("Quantidade do produto", card_text, session_attr['imagem_padrao']))
                .ask(speak_output)
                .response
        )        

#=========== Finalizar Compra ======================================


class finalizarCompraIntentHandler(AbstractRequestHandler):
    
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("finalizarCompraIntent")(handler_input)
    
    def handle(self, handler_input):
        card_text = ""
        speak_output = ""
        session_attr = handler_input.attributes_manager.session_attributes
        
        
        if session_attr['estado'] == 400:
            
            qtd =  session_attr['qtd_compra']
            carrinho = session_attr['carrinho']
            cont = 0
            total = 0.000
            
            MU = money_util()
            
            
            for produto in carrinho:
                        
                total += float(produto["precoPrazo"]) * int(qtd[cont])
                
                valor_texto = MU.moneyToText(produto["precoPrazo"])
                
                card_text = card_text +"\n\nProduto: {0} Valor:{1} Quantidade: {2}".format(produto['descrProduto'], valor_texto, qtd[cont])
                cont += 1
            
            
            
            valor_fala = MU.moneyToSpeak(str(total))
            valor_texto = MU.moneyToText(str(total))
            
            
            speak_output = speak_output + "O valor total de sua venda é de {0}. ".format(valor_fala)
            card_text = card_text + "\nTOTAL: {0}".format(valor_texto)
            
            session_attr['estado'] = 430
            speak_output = speak_output + " Qual método de pagamento eu deveria usar? Dinheiro. Cartão de débito ou cartão de crédito?"
        
        else:
            
            speak_output = "Agora não é o momento certo para isso"
        
        
        
        return (
                handler_input.response_builder
                .speak(speak_output)
                .set_card(StandardCard("Finalizando", card_text, session_attr['imagem_padrao']))
                .ask(speak_output)
                .response
        )        

#=========== Forma de Pagamento ====================================

class metodoPagamentoIntentHandler(AbstractRequestHandler):
    
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("metodoPagamentoIntent")(handler_input)
    
    def handle(self, handler_input):
        card_text = ""
        speak_output = ""
        session_attr = handler_input.attributes_manager.session_attributes
        slots = handler_input.request_envelope.request.intent.slots
        forma_de_pagamento = slots['pagamento'].value
        
        if session_attr['estado'] == 430:
            
            if len(forma_de_pagamento) == 8:
                session_attr['forma_pagamento'] = 0
            elif len(forma_de_pagamento) == 16:
                session_attr['forma_pagamento'] = 1
            elif len(forma_de_pagamento) == 17:
                session_attr['forma_pagamento'] = 10
                
            
            speak_output = "Você escolheu o método {0}. Deseja confirmar o pedido?".format(forma_de_pagamento)
            session_attr['estado'] = 440
            card_text = "Método de pagamento: {0}".format(forma_de_pagamento)
            
            
        else:
            speak_output = "Diga. finalizar venda. antes de escolher o método de pagamento"
            
         
        return (
                handler_input.response_builder
                .speak(speak_output)
                .set_card(StandardCard("Forma de pagamento", card_text, session_attr['imagem_padrao']))
                .ask(speak_output)
                .response
        )  



