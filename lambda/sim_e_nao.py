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
from re import sub

from money_util import money_util

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)




def criar_fatura_com_uma_parcela(chave_sistema, codEmpresa, url_base, codContaBancaria, valor, numDocumento, descricao, codPlanoContas, dataVencimento, idApiExterno, codPessoa, nomeFantasia):
    header = {
        "Content-Type": "application/json",
        "AuthToken": chave_sistema,
        "AuthEnterprise": codEmpresa
    }

    params = {
            "dadosPessoa":{
            "codPessoa": codPessoa,
            "nomeFantasia":nomeFantasia,
            "cnpjCpf":""
       },
       "dadosFatura":{

            "codFatura": "novo",
            "tipoFatura":"1",
            "codContaBancaria": codContaBancaria ,
            "valor":valor,
            "numDocumento":numDocumento,
            "descricao": descricao,
            "codPlanoContas": codPlanoContas,
            "dataVencimento": dataVencimento,
            "gerarBaixa":"false",
            "idApiExterno": idApiExterno

       }
   }

    url = url_base + "/fatura/novo"
    resposta = requests.post(url, headers=header, json=params)

    return (resposta.status_code == 200)




def email_pedido(codPedido, chave_sistema, codEmpresa, url_base):

    header =  {
        "Content-Type": "application/json",
        "AuthToken": chave_sistema,
        "AuthEnterprise": codEmpresa
    }

    params = {
        "email": "eduardo_his@hotmail.com",
        "tipoAnexo": 1
    }

    url = url_base + "/pedido/email/{0}".format(codPedido)
    resposta = requests.post(url, headers=header, json=params)

    return (resposta.status_code == 200)



def emitir_nota(codPedido, chave_sistema, codEmpresa, url_base):

    sucesso = False

    header =  {
        "Content-Type": "application/json",
        "AuthToken": chave_sistema,
        "AuthEnterprise": codEmpresa
    }

    params = {
        "codPedido": codPedido,
        "natOp": "Venda",
        "mod": 65,
        "numeroCaixa": "000"
    }

    url = url_base +  "/nfce"
    resposta = requests.post(url, headers=header, json=params)

    if resposta.status_code == 200:

        sucesso = True
        
    return sucesso



def realizar_venda(itens, qtd_lista, pagamento, chave_sistema, codEmpresa, url_base):
    
    #TROCAR CODPESSOA POR CODIGO PEGO NO SISTEMA 
    json_data = '''{
            "idApiExtPed": "1234567890",
            "tipoPedido":"0",
            "vistaPrazo":"1",
            "codPessoa":2,      
            "cnpjCpfPed":null,
            "numDoc":"1234567890",
            "obsPedido":"Feito via Alexa",
            "itens":[
            ''' 

    n = 0
    valor_bruto = 0.00
    valor_serv_liquido = 0.00

    for item in itens:
        
        qtd = int(qtd_lista[n])
        
        if item["flagTipoProduto"] == 0:
            valor_bruto += (float(item["precoPrazo"]) * qtd)
            
        else:
            valor_serv_liquido += (float(item["precoPrazo"]) * qtd)
            
        
        n += 1
        json_data += '''{
        "codPedItem":"novo",
        "numItem": %s,
        "flagTipoProduto": %s,
        "codProdutoGrade": %s,
        "quantItem": %s,        
        "vrUnit": %s,
        "vrTot": %s,
        "percDesc":0.000000,
        "vrDesc":0.00,
        "percAcr":0.000000,
        "vrAcr":0.00,
        "vrOutDesp":0.00,
        "vrFrete":0.00,
        "vrSeg":0.00,
        "vrItem": %s
                                    
        },'''%(n, item["flagTipoProduto"], item["codProdutoGrade"], qtd, item["precoPrazo"], (qtd * float(sub(r'[^\d.]', '', item["precoPrazo"]))),(qtd * float(sub(r'[^\d.]', '', item["precoPrazo"]))) ) 
                
                
                
        

    json_data = json_data[:-1]
    json_data += '''
            ],
            "vrProdSeg": 0,
            "vrProdOutDesp":0,
            "vrProdBruto": %s,        
            "percProdDesc":"0.000000",
            "vrProdDesc":0.00,
            "percProdAcr":"0.000000",
            "vrProdAcr":0.00,
            "vrProdFrete":0.00,
            "vrProdLiq": %s,     
            "vrServBruto": %s,       
            "percServDesc":0.00,
            "vrServDesc":0.00,
            "percServAcr": "0.000000",
            "vrServAcr":0.00,
            "vrServLiq": %s,         
            "vrLiquido": %s,        
            "vrTroco":0.00,
            "codVendedor":2,
            "pagtos":[
                {
                    "codFaturaParcela":"0",
                    "codPedFP":null,
                    "meioPagto": %s,
                    "valorPagto": %s    
                
                }
                
            ],
            "codUsuario": null
        }'''%(valor_bruto, valor_bruto, valor_serv_liquido, valor_serv_liquido , (valor_bruto + valor_serv_liquido), pagamento, (valor_bruto + valor_serv_liquido))
    

    header = {
        "Content-Type": "application/json",
        "AuthToken": chave_sistema,
        "AuthEnterprise": codEmpresa
        }



    json_params = json.loads(json_data)
    
    url = url_base +  "/pedido/novo"

    resposta = requests.post(url, headers=header, json=json_params)
                    
    if resposta.status_code == 200:
        dados_json = resposta.json()             
        return True, dados_json


    return False, []





def cadastrar_produto(descricao, chave_sistema, codEmpresa, url_base):
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
    
    url = url_base +  "/produto/novo"
    
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
        
        
        chave_sistema = session_attr['chave_sistema']
        codEmpresa = session_attr['cod_empresa'] 
        url_base = session_attr['base_url']
        
        card_text = ""
        
        if session_attr['estado'] != 0:
            
            if session_attr['estado'] == 555: #Criar nova conta a pagar
                
                if not session_attr['parcelado']:
                    
                    
                    #Trocar "1" no codContaBancaria e "1023" no codPlano de contas quando API estiver pronta
                    
                    codContaBancaria = 1
                    valor = float(session_attr["valor_fatura"].replace(",", "."))
                    numDocumento = int(session_attr['numero_documento'])
                    descricao = session_attr['descricao_fatura']
                    codPlanoContas = 1023
                    dataVencimento = session_attr['vencimentos']
                    idApiExterno = session_attr['alexa_id']
                    
                    codPessoa = str(session_attr['fornecedor_atual']['codPessoa']) 
                    nomeFantasia = session_attr['fornecedor_atual']['nomeFantasia'] 
                    
                    
                    
                    
                    
                    
                    #if criar_fatura_com_uma_parcela(chave_sistema, codEmpresa, url_base, 1, float(session_attr["valor_fatura"].replace(",", ".")), int(session_attr['numero_documento']), session_attr['descricao_fatura'], 1023, session_attr['vencimentos'], user_id, session_attr['fornecedores']['codPessoa'] ,session_attr['fornecedores']['codPessoa']  ):        
                    if criar_fatura_com_uma_parcela(chave_sistema, codEmpresa, url_base, codContaBancaria, valor, numDocumento, descricao, codPlanoContas, dataVencimento, idApiExterno, codPessoa, nomeFantasia):
                        speak_output = "Sua nova conta a pagar foi criada com sucesso!"
                        card_text = "Conta a pagar criada com sucesso!"
                        session_attr['estado'] = 0
                    
                    else:
                        
                        speak_output = "Ouve um erro. Não conseguir criar sua nova conta a pagar"
                        card_text = "Erro ao criar nova conta a pagar!"
                        session_attr['estado'] = 0
                    
                
                else:#implementar quando multiplas parcelas forem liberadas
                    pass
                    
                
                session_attr['estado'] = 0
            
            if session_attr['estado'] == 512:
                speak_output = "Qual a data de vencimento?"
                card_text = "Informe a data de vencimento."
                session_attr['estado'] = 510
            
            if session_attr['estado'] == 506: #Alterar para permitir multiplas parcelas
                #session_attr['parcelado'] = True
                #session_attr['parcelas'] = []
                #session_attr['vencimentos'] = []
                #speak_output = "Qual o a data de vencimento da parcela?"
                #card_text = "Qual o a data de vencimento da parcela?"
                #session_attr['estado'] = 510
                
                speak_output = "Desculpe, no momento apenas à vista"
                card_text = "Criação de faturas com mais de uma parcela em breve!"
                session_attr['estado'] = 0
                
            
            if session_attr['estado'] == 503:
                speak_output = "Você escolheu adicionar uma descrição, qual vai ser a descrição?"
                card_text = "Informe a descrição!"
                session_attr['estado'] = 504
            
            if session_attr['estado'] == 460:
                
                sucesso = email_pedido(int(session_attr['codigo_ultimo_pedido']), chave_sistema, codEmpresa, url_base)
                #sucesso = True
                
                if sucesso:
                    
                    speak_output = "A nota fiscal foi enviada para o seu e-mail"
                    card_text = "NFC-e enviada ao e-mail"
                    session_attr['estado'] = 0
                    
                else:
                    
                    speak_output = "Ouve um erro ao enviar sua nota fiscal por e-mail"
                    card_text = "Erro ao enviar NFC-E por e-mail"
                    session_attr['estado'] = 0
            
            if session_attr['estado'] == 450:
                
                sucesso = emitir_nota(int(session_attr['codigo_ultimo_pedido']), chave_sistema, codEmpresa, url_base)
                #sucesso = True
                
                if sucesso:
                    
                    speak_output = "A nota foi emitida, deseja que ela seja enviada para o seu e-mail?"
                    card_text = "NFC-e emitida com sucesso!"
                    session_attr['estado'] = 460
                    
                else:
                    
                    speak_output = "Ouve um erro ao emitir sua nota fiscal"
                    card_text = "Erro ao emitir NFC-E"
                    session_attr['estado'] = 0
                    
            
            if session_attr['estado'] == 440:
                carrinho = session_attr['carrinho']
                quantidade = session_attr['qtd_compra']
                pagamento = session_attr['forma_pagamento']
                
                compra_ok, dados = realizar_venda(carrinho, quantidade, pagamento, chave_sistema, codEmpresa, url_base)
                
                session_attr['codigo_ultimo_pedido'] = dados["pedido"]["codPedido"]
                
                if compra_ok:
                    session_attr['estado'] = 0
                    speak_output = "Sua venda foi realizada com sucesso! Deseja emitir nota fiscal?"
                    card_text = "Sua venda foi realizada com sucesso!"
                    session_attr['estado'] = 450
                else:
                    session_attr['estado'] = 0
                    speak_output = "Ouve um erro ao realizar sua venda, por favor verifique os dados dos seus produtos no sistema"
                    card_text = "Não foi possivel concluir a venda"
                
            
            if session_attr['estado'] == 200:
                session_attr['estado'] = 210
                speak_output = "Qual é o valor a prazo?"
                card_text = "Informe o valor do produto a prazo"
            
            if session_attr['estado'] == 220:
                session_attr['estado'] = 0
                desc = session_attr['dados-produto']
                if cadastrar_produto(desc, chave_sistema, codEmpresa, url_base):
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
            
            
            if session_attr['estado'] == 105: #105 = Estado de confirmação FORNECEDOR
                
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
                            "categoriaPessoa":1,
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
                
                
                url = url_base + "/pessoa/nova"
                    
                json_params = json.loads(params)
                resposta = requests.post(url, headers=header, json=json_params)
                
                if resposta.status_code == 200:
                    
                    speak_output = "Fornecedor encontrado e cadastrado com sucesso!"
                    card_text = card_text + "\nFornecedor encontrado e cadastrado com sucesso!"
                    
                else:
                    
                    speak_output = "O fornecedor foi encontrado mas ouve um erro no cadastro!"
                    card_text = card_text + "Erro no cadastro!"
            
            
            
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
                
                
                url = url_base + "/pessoa/nova"
                    
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
                .set_card(StandardCard("Confirmação", card_text, session_attr['imagem_padrao'] ))
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
            
            if session_attr['estado'] == 100 or session_attr['estado'] == 101 or session_attr['estado'] == 105: #100 = Estado de confirmacao de pessoa
                speak_output = "Cancelando o cadastro."
                card_text = "Cadastro cancelado"
                session_attr['estado'] = 0
                session_attr['dados'] = {}
                
            if session_attr['estado'] == 440:
                speak_output = "Cancelando a compra."
                card_text = "Compra cancelada"
                session_attr['estado'] = 0
                
            if session_attr['estado'] == 450:
                speak_output = "Ok, não vou emitir agora"
                card_text = "Não emitir NFC-E"
                session_attr['estado'] = 0
                
            if session_attr['estado'] == 506:
                speak_output = "Então vai ter apenas uma parcela, Qual é a data de vencimento?"
                card_text = "Pagamento a vista.\n\nQual é a data de vencimento?"
                session_attr['parcelado'] = False
                session_attr['estado'] = 510
            
            if session_attr['estado'] == 503:
                speak_output = "Ok, vai ter mais de uma parcela?"
                card_text = "Terá mais de uma parcela?."
                session_attr['descricao_fatura'] = "Sem descrição"
                session_attr['estado'] = 506
            
            if session_attr['estado'] == 512:
                
                total = 0.0
                numero_de_parcelas = 0
                
                MU = money_util()
                
                for parcela in session_attr['parcelas']:
                    numero_de_parcelas += 1
                    total += float(parcela.replace(",","."))
                
                
                total_texto = MU.moneyToText(total)
                total_fala = MU.moneyToSpeak(total)
                
                speak_output = "Você tem {0} parcelas, totalizando {1}. Você confirma a criação dessa nova conta a pagar?".format(numero_de_parcelas, total_fala)
                card_text = "Parcelas: {0}\n\nTOTAL: {1}".format(numero_de_parcelas, total_texto)
                
                
                session_attr['estado'] = 555
                
            if session_attr['estado'] == 555:
                speak_output = "A criação da nova conta a pagar foi cancelada!"
                card_text = "A criação da nova conta a pagar foi cancelada!"
                session_attr['estado'] = 0
                
                
        else:
            speak_output = "Eu ainda não pedi a confirmação de nada."  
            
        
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .set_card(StandardCard("Confirmação", card_text, session_attr['imagem_padrao'] ))
                .ask("Posso ajudar em mais alguma coisa?")
                .response
        )
        