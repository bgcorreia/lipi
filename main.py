#!/usr/bin/env python3

# BIBLIOTECAS
import datetime
import RPi.GPIO as GPIO
import pygame.mixer
import os
import time

## VARIAVEIS

## ATIVAR PARA MAIS DETALHES NA EXECUCAO. DEBUG=1 -> ATIVO , DEBUG=0 -> INATIVO
DEBUG=1

## LIMITE ALERTAS
ALERTA_EMAIL = 3
ALERTA_SMS = ALERTA_EMAIL + 1

## VARIAVEIS P/ DEFINICAO DOS PINOS
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

## LED VERMELHO
pinoLedVermelho = 26
GPIO.setup(pinoLedVermelho,GPIO.OUT)

## LED VERDE
pinoLedVerde = 19
GPIO.setup(pinoLedVerde,GPIO.OUT)

## BOTAO
pinoBotao = 13
GPIO.setup(pinoBotao,GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

## SENSOR ULTRASSONICO - GATILHO
pinoGatilho = 20
GPIO.setup(pinoGatilho,GPIO.OUT)

## SENSOR ULTRASSONICO - ECHO
pinoEcho = 21
GPIO.setup(pinoEcho,GPIO.IN)

## TEMPO DE ESPERA
tempoEspera = 5

## NOTIFICACAO
notificacao=0

## CONTADOR
contador=0

## CANAL DE AUDIO
canalAudio=0

## VARIAVEL QUE GUARDA MODO DE FUNCIONAMENTO DOS SENSORES
monitoramento=0

## DIRETORIOS
projeto_dir="/opt/lipi/"
scripts_dir=projeto_dir + "scripts/"
sounds_dir=projeto_dir + "sounds/"

### FUNCOES

### CALCULA DISTANCIA
def calcDistancia(pino_Gatilho,pino_Echo):

    global contador

    GPIO.output(pino_Gatilho, True)
    time.sleep(0.00001)
    GPIO.output(pino_Gatilho, False)

    # ENQUANTO FALSO
    while not (GPIO.input(pino_Echo)):
            pulsoInicio = time.time()

    # ENQUANTO VERDADEIRO
    while (GPIO.input(pino_Echo)):
            pulsoFim = time.time()
     
    pulsoDuracao = pulsoFim - pulsoInicio
     
    distancia = pulsoDuracao * 17150
     
    distancia = round(distancia, 2)

    print ("{} A distancia e: {} cm".format(contador,distancia))

    contador+=1

    return distancia


### EXECUTA AUDIO
def execAudio(nome_Audio,tempo_Espera):
    global canalAudio
    global contador

    if(canalAudio==8):
        canalAudio=0

    if(DEBUG):
        print('Canal do Audio: {}'.format(canalAudio))
    
    pygame.mixer.init(48000, -16,1024)
    somCanal = pygame.mixer.Channel(canalAudio)

    som = pygame.mixer.Sound(sounds_dir + nome_Audio)
    print('Tocando audio: {} Tempo Espera: {}'.format(nome_Audio,tempo_Espera))
    somCanal.play(som)
        
    canalAudio+=1

    time.sleep(tempo_Espera)
    
    return 0


### ENVIA NOTIFICACAO
def notifica(leito, tipo, destino, nome_Paciente, nome_Parente):
    global notificacao

    if(tipo == "email"):
        now = datetime.datetime.now()
        data = now.strftime("%H:%M:%S %d/%m/%Y")
        dataReversa = now.strftime("%Y%m%d%H%M%S")
        dataResumida = now.strftime("%m/%d %H:%M")
        mensagem="Sr(a) " + nome_Parente + ", o(a) paciente " + nome_Paciente + " do Leito " + leito + " encontra-se um pouco inquieto(a). Protocolo: " + str(leito) + str(dataReversa)
        assunto="LIPI - ALERTA - LEITO " + leito + " - " + str(dataResumida)

        if(DEBUG):
            print("----------DEBUG----------")
            print("Mensagem: " + mensagem)
            print("Assunto: " + assunto)
            print("Email para: " + destino)
            print('Valor da variavel notificacao: {}'.format(notificacao))
            print("----------DEBUG----------")

        print("Enviando email...")
        # ENVIANDO EMAIL ATRAVES DO SISTEMA - SSMTP (FIZ UM SCRIPT PARA FACILITAR)
        os.system(scripts_dir + "enviar-email " + "\"" + mensagem + "\"" + " " + "\"" + assunto + "\"" + " " + destino)

        # NOTIFICACAO ENVIADA
        #execAudio("notificacao_enviada.wav",S)

        # LIMPAR VARIAVEIS

    if(tipo == "sms"):
        now = datetime.datetime.now()
        data = now.strftime("%H:%M:%S %d/%m/%Y")
        dataReversa = now.strftime("%Y%m%d%H%M%S")
        dataResumida = now.strftime("%m/%d %H:%M")
        mensagem="Sr(a) " + nome_Parente + ", o(a) paciente " + nome_Paciente + " do Leito " + leito + " encontra-se um pouco inquieto(a). Protocolo: " + str(leito) + str(dataReversa)

        if(DEBUG):
            print("----------DEBUG----------")
            print("Mensagem: " + mensagem)
            print("SMS para: " + destino)
            print('Valor da variavel notificacao: {}'.format(notificacao))
            print("----------DEBUG----------")

        print("Enviando sms...")
        # ENVIANDO EMAIL ATRAVES DO SISTEMA - SSMTP (FIZ UM SCRIPT PARA FACILITAR)
        os.system(scripts_dir + "enviar-sms " + "\"" + mensagem + "\"" + " " + destino)

        # NOTIFICACAO ENVIADA
        #execAudio("notificacao_enviada.wav",S)

        # LIMPAR VARIAVEIS 

    return 0


## PISCA LED
def piscaLed(tempo_Espera,pino_Led):

    global contador

    for cont in range (tempo_Espera):
        contador+=1
        print(contador,"Aguardando botao DESLIGAR",cont,"s","de",tempo_Espera)

        # PISCAR LED NA DETECAO - ESPERA delayTime
        if not (cont % 2):
            print("Acendendo LED")
            GPIO.output(pino_Led,GPIO.HIGH)
        else:
            print("Apagando LED")
            GPIO.output(pino_Led,GPIO.LOW)

        time.sleep(1)

    return 0


# INCOFRMACOES DO PACIENTE E PARENTE
nomePaciente="Margarete"
leitoPaciente="BC0013"
nomeParente="Bruno"
numTelefoneParente="988122235"
emailParente="brunogomescorreia@gmail.com"


# ESPERANDO SENSOR ESTABILIZAR
GPIO.output(pinoGatilho,False)
print ("Aguardando o Sensor Estabilizar")
while (contador <=3):
    distancia = calcDistancia(pinoGatilho, pinoEcho)
    time.sleep(1)
    contador+=1

# INFORMANDO QUE SISTEMA ESTA LIGADO
print("Sistema ligado!")
execAudio("ligado.wav",2)

# LOOP "ETERNO" DO PROGRAMA
while (True):

    # APAGA LED VERMELHO - CASO ESTEJA ACESO
    if(GPIO.input(pinoLedVermelho)):
        GPIO.output(pinoLedVermelho,GPIO.LOW)

    if(DEBUG):
        print("Valor statusBotao: ",GPIO.input(pinoBotao))

    # SE BOTAO PRESSIONADO
    if (GPIO.input(pinoBotao)): # IF ID 1

        contador+=1
        print(contador,"Botao ativo, sensores ativos.")
        GPIO.output(pinoLedVerde,GPIO.HIGH)

        distancia = calcDistancia(pinoGatilho, pinoEcho)
        time.sleep(1)

        if(distancia < 17):
            if(DEBUG):
                print("Entrou em distancia < 16")
            # COLOCAR AUDIO
            #execAudio("algum_objeto.wav",2)
            piscaLed(5,pinoLedVermelho)

            if(distancia < 16 and GPIO.input(pinoBotao)):
                print("NOTIFICACAO: ALGUM OBJETO ESTA OBSTRUINDO OS SENSORES!")

        elif(distancia > 18 and distancia < 21.50):
            if(DEBUG):
                print("Entrou em 18 < distancia < 21")
            # COLOCAR AUDIO
            #execAudio("cuidado_sra.wav",2)
            piscaLed(5,pinoLedVermelho)

            if((distancia > 18 and distancia < 21.50) and GPIO.input(pinoBotao)):
                print("AVISO: PACIENTE COM RISCO DE QUEDA!")

        elif(distancia > 26):
            print("Entrou em distancia > 26")
            piscaLed(5,pinoLedVermelho)

            if(distancia > 26 and GPIO.input(pinoBotao)):
                print("AVISO: PACIENTE NAO ESTA NO LEITO!")
                #notifica(leitoPaciente, "email", emailParente, nomePaciente, nomeParente)
                #notifica(leitoPaciente, "sms", numTelefoneParente, nomePaciente, nomeParente)
                
            
                 
    else: # ELSE IF ID 1
        contador+=1
        print(contador,"Botao nao pressionado, alertas inativos.")
        GPIO.output(pinoLedVerde,GPIO.LOW)
        distancia = calcDistancia(pinoGatilho, pinoEcho)
        time.sleep(1)
        
# INICIANDO ESTABILIZACAO DO SENSOR
#GPIO.output(pinoGatilho,False)
#print ("Aguardando o Sensor Estabilizar")
#time.sleep(3)
    
