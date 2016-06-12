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

pinoLed = 16
sensorEsquerdo = MotionSensor(20)
sensorDireito = MotionSensor(21)
delayTime = 15
notificacao=0
esquerda=0
direita=0
i=0

# DIRETORIOS
projeto_dir="/opt/lipi/"
scripts_dir="/opt/lipi/scripts/"
sounds_dir="/opt/lipi/sounds/"

pygame.mixer.init(48000, -16,1024)
soundA = pygame.mixer.Sound(sounds_dir + "Front_Center.wav")

soundChannelA = pygame.mixer.Channel(1)
soundChannelA.set_volume(50)


GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(pinoLed,GPIO.OUT)

while True:
    if (sensorDireito.motion_detected or sensorEsquerdo.motion_detected):

        print("Movimento detectado!")

        soundChannelA.play(soundA)

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
                
        while(sensorEsquerdo.motion_detected or sensorDireito.motion_detected):

            notificacao=1

            print("Acendendo LED de deteccao - VERMELHO")
            GPIO.output(pinoLed,GPIO.HIGH)

            if(sensorEsquerdo.motion_detected):
                esquerda+=1
                print(i,"Movimento do lado ESQUERDO!",sensorEsquerdo.motion_detected)
                
            if(sensorDireito.motion_detected):
                direita+=1
                print(i,"Movimento do lado DIREITO!",sensorDireito.motion_detected)

            i+=1
            time.sleep(1)

        if(DEBUG):
                print("----------DEBUG----------")
                print('Valor da variavel notificacao: {}'.format(notificacao))
                print('Valor da variavel esquerda: {}'.format(esquerda))
                print('Valor da variavel direita: {}'.format(direita))
                print("----------DEBUG----------")

        if(notificacao):
            print("LEMBRETE: COLOCAR BIP, E ALERTA POR VOZ")
            
            if(esquerda>12 or direita>12):
                # CHAMAR FUNCOES DE NOTIFICACAO AQUI
                now = datetime.datetime.now()
                data = now.strftime("%H:%M:%S %d/%m/%Y")
                dataReversa = now.strftime("%Y%m%d%H%M%S")
                dataResumida = now.strftime("%m/%d %H:%M")
                mensagem="A paciente do Leito BC-0013 encontra-se um pouco inquieta. Protocolo: BC0013" + str(dataReversa)
                assunto="LIPI - ALERTA - LEITO BC0013 - " + str(dataResumida)
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
                notificacao=0
                direita=0
                esquerda=0

    else:
        i+=1
        if (GPIO.input(pinoLed)):
            print("Apagando LED de deteccao - VERMELHO")
            GPIO.output(pinoLed,GPIO.LOW)
            
        print(i,"Sem movimento")
        
        time.sleep(1)
