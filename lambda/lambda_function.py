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



'''
    Alexa vai poder interagir com o usuario de forma complexa por meio de estados.
    
=== ESTADOS ===
    
Estado 0 = Estado Inicial.
Estado 100 = Estado de confirmacao de cadastro de pessoa.
Estado 200 = Estado de confirmacao de cadastro de produto.
Estado 300 = Estado de conformacao de cobranca
Estado 400 = Estado de confirmacao de compra
estado 500 = Estado de criação conta a pagar

'''

#=========INTENTS============================================================
#Ponto de entrada
class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        
        speak_output = "Bem vindo ao virtuoso gestão empresarial!"
        session_attr = handler_input.attributes_manager.session_attributes
        # session_attr['chave_sistema'] = "1234"
        # session_attr['cod_empresa'] = "716001"
        session_attr['alexa_id'] = "beta@alexa_skill@2020"
        
        session_attr['chave_sistema'] = "INSERIR AUTHTOKEN"
        session_attr['cod_empresa'] = "INSERIR AUTHENTERPRISE"
        
        session_attr['cod_app'] = "INSERIR CODIGO DO APP"
        
        session_attr['base_url'] = "INSERIR URL BASE"
        session_attr['imagem_padrao'] = Image("https://i.imgur.com/L2N6x19.png", "https://i.imgur.com/L2N6x19.png")
        
        session_attr['big_boost_key'] = "INSERIR KEY DA API BIGBOOST"
        session_attr['big_boost_url'] = "https://bigboost.bigdatacorp.com.br"
        
        
        
        session_attr['estado'] = 0
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


#=== Classes Personalizadas ===
from cadastro_de_pessoas import cadastrarPessoaIntentHandler, cadastrarPessoaJuridicaIntentHandler, cadastraFornecedorIntentHandler

from estoque import estoqueIntentHandler
from estoque import estoqueDoisIntentHandler

from faturas import faturasHandler

from pagamentos import pagamentoHojeHandler
from pagamentos import pagamentoNoPeriodoHandler

from sim_e_nao import NoIntentHandler
from sim_e_nao import YesIntentHandler

from cadastro_de_produto import NovoProdutoIntentHandler

from dinheiro import dinheiroIntentHandler
from dinheiro import dinheiroDisponivelIntentHandler
from dinheiro import mostraSaldoIntentHandler

from valor_produto import custoProdutoIntentHandler

from cobranca import cobrancaIntentHandler
from cobranca import meioIntentHandler

from compra import compraIntentHandler
from compra import cancelarCompraIntentHandler
from compra import addProdutoIntentHandler
from compra import escolheProdutoIntentHandler
from compra import qtdProdutoCompraIntentHandler
from compra import finalizarCompraIntentHandler
from compra import metodoPagamentoIntentHandler

from conta_a_pagar import contaAPagarIntentIntentHandler
from conta_a_pagar import listarFornecedorIntentHandler
from conta_a_pagar import escolheFornecedorIntentHandler
from conta_a_pagar import numeroDocumentoFaturaIntentHandler
from conta_a_pagar import descricaoFaturaIntentHandler
from conta_a_pagar import vencimentoParcelaIntentHandler

from markup import markupIntentHandler

from recebimentos import tenhoParaReceberHojeIntentHandler

#=== Classes Padrao===
from classes_padrao import HelpIntentHandler
from classes_padrao import IntentReflectorHandler
from classes_padrao import SessionEndedRequestHandler
from classes_padrao import CancelOrStopIntentHandler
from classes_padrao import CatchAllExceptionHandler


#============SkillBuilder==================================================

sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(YesIntentHandler())
sb.add_request_handler(NoIntentHandler())
sb.add_request_handler(custoProdutoIntentHandler())
sb.add_request_handler(NovoProdutoIntentHandler())
sb.add_request_handler(numeroDocumentoFaturaIntentHandler())
sb.add_request_handler(escolheFornecedorIntentHandler())
sb.add_request_handler(descricaoFaturaIntentHandler())
sb.add_request_handler(compraIntentHandler())
sb.add_request_handler(contaAPagarIntentIntentHandler())
sb.add_request_handler(vencimentoParcelaIntentHandler())
sb.add_request_handler(listarFornecedorIntentHandler())
sb.add_request_handler(cancelarCompraIntentHandler())
sb.add_request_handler(metodoPagamentoIntentHandler())
sb.add_request_handler(addProdutoIntentHandler())
sb.add_request_handler(estoqueIntentHandler())
sb.add_request_handler(estoqueDoisIntentHandler())
sb.add_request_handler(escolheProdutoIntentHandler())
sb.add_request_handler(qtdProdutoCompraIntentHandler())
sb.add_request_handler(finalizarCompraIntentHandler())
sb.add_request_handler(dinheiroIntentHandler())
sb.add_request_handler(dinheiroDisponivelIntentHandler())
sb.add_request_handler(mostraSaldoIntentHandler())
sb.add_request_handler(cadastrarPessoaIntentHandler())
sb.add_request_handler(cadastrarPessoaJuridicaIntentHandler())
sb.add_request_handler(cadastraFornecedorIntentHandler())
sb.add_request_handler(tenhoParaReceberHojeIntentHandler())
sb.add_request_handler(markupIntentHandler())
sb.add_request_handler(faturasHandler())
sb.add_request_handler(pagamentoHojeHandler())
sb.add_request_handler(pagamentoNoPeriodoHandler())
sb.add_request_handler(cobrancaIntentHandler())
sb.add_request_handler(meioIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler()) # Precisa ser por ultimo para nao sobreescrever os outros handlers

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()