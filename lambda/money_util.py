class money_util:
#Transforma uma string com um float em texto do dinheiro para a Alexa falar
    def moneyToSpeak(self, dinheiro):
        
        speak = ""
        
        real, centavo = dinheiro.split(".")

        if len(centavo) > 2:
            centavo = centavo[:-1]

        int_real = int(real)
        int_centavo = int(centavo)

        if int_centavo < 10:
            centavo = centavo[1:]

        if real[0] =="0":
            real = real[1:]

        if int_real > 0:

            if int_real == 1:
                if int_centavo > 0:
                    if int_centavo == 1:
                        speak = "{0} real e {1} centavo".format(real, centavo)
                    else:
                        speak = "{0} real e {1} centavos".format(real, centavo)
                else:
                    speak = "{0} real".format(real)

            else:
                if int_centavo > 0:
                    if int_centavo == 1:
                        speak = "{0} reais e {1} centavo".format(real, centavo)
                    else:
                        speak = "{0} reais e {1} centavos".format(real, centavo)
                else:
                    speak = "{0} reais".format(real)
        else:
            if int_centavo > 0:
                if int_centavo == 1:
                    speak = "{0} centavo".format(centavo)
                else:
                    speak = "{0} centavos".format(centavo)
            else:
                speak = "0 reais e 0 centavos"
        
        return speak

#Transforma uma string com um float em texto do dinheiro para usar no card
    def moneyToText(self, dinheiro):
        
        text = ""
        real, centavo = dinheiro.split(".")
        
        if len(centavo) > 2:
            centavo = centavo[:-1]
                
        int_real = int(real)
        int_centavo = int(centavo)

        if int_real > 0:
            
            if int_real == 1:
                if int_centavo > 0:
                    if int_centavo == 1:
                        text = "R${0},{1}".format(real, centavo)
                    else:
                        text = "R${0},{1}".format(real, centavo)
                else:
                    text = "R${0},00".format(real)

            else:
                if int_centavo > 0:
                    if int_centavo == 1:
                        text = "R${0},{1}".format(real, centavo)
                    else:
                        text = "R${0},{1}".format(real, centavo)
                else:
                    text = "R${0},00".format(real)
        else:
            if int_centavo > 0:
                if int_centavo == 1:
                    text = "R$0,{0}".format(centavo)
                else:
                    text = "R$0,{0}".format(centavo)
            else:
                text = "R$0,00"
                
        return text
