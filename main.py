#!/usr/bin/env python3

# BIBLIOTECAS
from gpiozero import MotionSensor
import datetime
import RPi.GPIO as GPIO
import pygame.mixer
import os
import time

# ATIVAR PARA MAIS DETALHES NA EXECUCAO. DEBUG=1 -> ATIVO , DEBUG=0 -> INATIVO
DEBUG=1

# LIMITE ALERTAS
MAX_ALERTAS=2

# CONTADOR DE ALERTAS
alertas=0

# PINO DO LED VERMELHO - PINO DE ALERTA
pinoLed = 16

# PINOS DOS SENSORES
sensorEsquerdo = MotionSensor(20)
sensorDireito = MotionSensor(21)

# TEMPO DE ESPERA
delayTime = 20

# NOTIFICACAO
notificacao=0

# CONTADOR DE ALERTAS DOS SENSORES
esquerda=0
direita=0

# CONTADOR
i=0

# CANAL DE AUDIO
canal=0

# VARIAVEL QUE GUARDA MODO DE FUNCIONAMENTO DOS SENSORES
monitoramento=0

# VARIAVEIS PINOS GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(pinoLed,GPIO.OUT)

# DIRETORIOS
projeto_dir="/opt/lipi/"
scripts_dir=projeto_dir + "scripts/"
sounds_dir=projeto_dir + "sounds/"


# FUNCAO EXECUTA AUDIO
def exec_audio(nome_audio,tempo_espera):
    global canal

    if(canal==8):
        canal=0

    if(DEBUG):
        print('Canal: {}'.format(canal))
    
    pygame.mixer.init(48000, -16,1024)
    soundCanal = pygame.mixer.Channel(canal)

    sound = pygame.mixer.Sound(sounds_dir + nome_audio)
    print("Tocando audio...")
    soundCanal.play(sound)
        
    canal+=1

    time.sleep(tempo_espera)
    
    return 0


# FUNCAO ENVIA EMAIL
def env_email(leito):
    global notificacao
    global direita
    global esquerda

    now = datetime.datetime.now()
    data = now.strftime("%H:%M:%S %d/%m/%Y")
    dataReversa = now.strftime("%Y%m%d%H%M%S")
    dataResumida = now.strftime("%m/%d %H:%M")
    mensagem="A(O) paciente do Leito " + leito + " encontra-se um pouco inquieta. Protocolo: " + str(leito) + str(dataReversa)
    assunto="LIPI - ALERTA - LEITO " + leito + " - " + str(dataResumida)
    destino='brunogomescorreia@gmail.com'

    if(DEBUG):
        print("----------DEBUG----------")
        print("Mensagem: " + mensagem)
        print("Assunto: " + assunto)
        print("Email para: " + destino)
        print('Valor da variavel notificacao: {}'.format(notificacao))
        print('Valor da variavel esquerda: {}'.format(esquerda))
        print('Valor da variavel direita: {}'.format(direita))
        print("----------DEBUG----------")

    print("Enviando email...")
    # ENVIANDO EMAIL ATRAVES DO SISTEMA - SSMTP (FIZ UM SCRIPT PARA FACILITAR)
    os.system(scripts_dir + "enviar-email " + "\"" + mensagem + "\"" + " " + "\"" + assunto + "\"" + " " + destino)

    # LIMPAR VARIAVEIS
    #notificacao=0
    direita=0
    esquerda=0

    return 0


# LOOP "ETERNO" DO PROGRAMA
while True:
    if (sensorDireito.motion_detected or sensorEsquerdo.motion_detected):

        if not (monitoramento):
            print("Movimento detectado!")

            exec_audio("movimento_detectado.wav",2)
            exec_audio("em_X_segundos.wav",0)
            print("Modo de monitoramento ativado!")
            monitoramento=1

            for cont in range (0, delayTime):
                i+=1
                print(i,"Aguardando botao DESLIGAR",cont,"s","de",delayTime)

                # PISCAR LED NA DETECAO - ESPERA delayTime
                if not (cont % 2):
                    print("Acendendo LED deteccao...")
                    GPIO.output(pinoLed,GPIO.HIGH)
                else:
                    print("Apagando LED deteccao...")
                    GPIO.output(pinoLed,GPIO.LOW)
                
                time.sleep(1)

            # QUANDO TEMPO FOR IMPAR, SERA NECESSARIO
            if (GPIO.input(pinoLed)):
                print("Apagando LED de deteccao. Tempo de delay foi IMPAR.")
                GPIO.output(pinoLed,GPIO.LOW)
        else:
                
            while(sensorEsquerdo.motion_detected or sensorDireito.motion_detected):

                alertas+=1
                notificacao+=1
                
                print("Acendendo LED de deteccao - VERMELHO")
                GPIO.output(pinoLed,GPIO.HIGH)

                if(sensorEsquerdo.motion_detected):
                    esquerda+=1
                    print(i,"Movimento do lado ESQUERDO!",sensorEsquerdo.motion_detected)
                    exec_audio("mensagem_sra_camila.wav",14)
                
                if(sensorDireito.motion_detected):
                    direita+=1
                    print(i,"Movimento do lado DIREITO!",sensorDireito.motion_detected)
                    exec_audio("mensagem_sra_camila.wav",14)

                i+=1
                time.sleep(1)

                #USAR SWITCH CASE! ABAIXO

                #if( esquerda > MAX_ALERTAS or direita > MAX_ALERTAS ):
                if( notificacao > MAX_ALERTAS ):
                    # CHAMAR FUNCOES DE NOTIFICACAO AQUI
                    exec_audio("mensagem_sra_camila_notificacao.wav",8)
                    env_email("BC-0013")
                    break

            if(DEBUG):
                print("----------DEBUG----------")
                print('Valor da variavel notificacao: {}'.format(notificacao))
                print('Valor da variavel esquerda: {}'.format(esquerda))
                print('Valor da variavel direita: {}'.format(direita))
                print("----------DEBUG----------")       
            
    else:
        i+=1
        if (GPIO.input(pinoLed)):
            print("Apagando LED de deteccao - VERMELHO")
            GPIO.output(pinoLed,GPIO.LOW)
            
        print(i,"Sem movimento")
        
        time.sleep(1)
