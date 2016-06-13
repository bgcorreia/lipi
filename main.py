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
ALERTA_EMAIL = 3
ALERTA_SMS = ALERTA_EMAIL + 1

# CONTADOR DE ALERTAS
alertas=0

# PINOS LED
pinoLedVermelho = 16
pinoLedVerde = 19

# PINO BOTA
pinoBotao = 13

# PINOS DOS SENSORES
sensorEsquerdo = MotionSensor(20)
sensorDireito = MotionSensor(21)

# TEMPO DE ESPERA
delayTime = 10

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

# VARIAVEIS PINO
GPIO.setmode(GPIO.BCM)
#GPIO.setwarnings(False)

# PINO VERMELHO
GPIO.setup(pinoLedVermelho,GPIO.OUT)

# PINO VERDE
GPIO.setup(pinoLedVerde,GPIO.OUT)

# PINO BOTAO
GPIO.setup(pinoBotao,GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


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


# FUNCAO ENVIA NOTIFICACAO
def notifica(leito,tipo):
    global notificacao
    global direita
    global esquerda

    if(tipo == "email"):
        now = datetime.datetime.now()
        data = now.strftime("%H:%M:%S %d/%m/%Y")
        dataReversa = now.strftime("%Y%m%d%H%M%S")
        dataResumida = now.strftime("%m/%d %H:%M")
        mensagem="O(A) paciente do Leito " + leito + " encontra-se um pouco inquieto(a). Protocolo: " + str(leito) + str(dataReversa)
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

        # NOTIFICACAO ENVIADA
        #exec_audio("notificacao_enviada.wav",S)

        # LIMPAR VARIAVEIS
        #notificacao=0
        direita=0
        esquerda=0

    if(tipo == "sms"):
        now = datetime.datetime.now()
        data = now.strftime("%H:%M:%S %d/%m/%Y")
        dataReversa = now.strftime("%Y%m%d%H%M%S")
        dataResumida = now.strftime("%m/%d %H:%M")
        mensagem="O(A) paciente do Leito " + leito + " encontra-se um pouco inquieto(a). Protocolo: " + str(leito) + str(dataReversa)
        destino='998620224'

        if(DEBUG):
            print("----------DEBUG----------")
            print("Mensagem: " + mensagem)
            print("SMS para: " + destino)
            print('Valor da variavel notificacao: {}'.format(notificacao))
            print('Valor da variavel esquerda: {}'.format(esquerda))
            print('Valor da variavel direita: {}'.format(direita))
            print("----------DEBUG----------")

        print("Enviando sms...")
        # ENVIANDO EMAIL ATRAVES DO SISTEMA - SSMTP (FIZ UM SCRIPT PARA FACILITAR)
        os.system(scripts_dir + "enviar-sms " + "\"" + mensagem + "\"" + " " + destino)

        # NOTIFICACAO ENVIADA
        #exec_audio("notificacao_enviada.wav",S)

        # LIMPAR VARIAVEIS
        #notificacao=0
        direita=0
        esquerda=0
        

    return 0

# COLOCAR AUDIO
print("Sistema ligado!")
exec_audio("ligado.wav",2)

# LOOP "ETERNO" DO PROGRAMA
while True:

    if (GPIO.input(pinoBotao)):
        i+=1
        print(i,"Botao ativo, sensores ativos.")
        GPIO.output(pinoLedVerde,GPIO.HIGH)

        if (sensorDireito.motion_detected or sensorEsquerdo.motion_detected):

            if not (monitoramento):
                print("Movimento detectado!")

                if not (notificacao):
                    print("Entrou em notificacao")
                    exec_audio("movimento_detectado.wav",2)
                    exec_audio("modo_monitor_10s.wav",0)
            
                # COLOCAR AUDIO           
                #exec_audio("monitor_ativado.wav",0)

            
                monitoramento=1
                print("Modo de monitoramento ativado!")

                for cont in range (0, delayTime):
                    i+=1
                    print(i,"Aguardando botao DESLIGAR",cont,"s","de",delayTime)

                    # PISCAR LED NA DETECAO - ESPERA delayTime
                    if not (cont % 2):
                        print("Acendendo LED deteccao...")
                        GPIO.output(pinoLedVermelho,GPIO.HIGH)
                    else:
                        print("Apagando LED deteccao...")
                        GPIO.output(pinoLedVermelho,GPIO.LOW)
                
                    time.sleep(1)

                # QUANDO TEMPO FOR IMPAR, SERA NECESSARIO
                if (GPIO.input(pinoLedVermelho)):
                    print("Apagando LED de deteccao. Tempo de delay foi IMPAR.")
                    GPIO.output(pinoLedVermelho,GPIO.LOW)
            else:
                
                while(sensorEsquerdo.motion_detected or sensorDireito.motion_detected):

                    alertas+=1

                    print("Acendendo LED de deteccao - VERMELHO")
                    GPIO.output(pinoLedVermelho,GPIO.HIGH)

                    if(sensorEsquerdo.motion_detected):
                        esquerda+=1
                        notificacao+=1
                        print(i,"Movimento do lado ESQUERDO!",sensorEsquerdo.motion_detected)
                        exec_audio("mensagem_sra_camila.wav",14)
                
                    if(sensorDireito.motion_detected):
                        direita+=1
                        notificacao+=1
                        print(i,"Movimento do lado DIREITO!",sensorDireito.motion_detected)
                        exec_audio("mensagem_sra_camila.wav",14)
                    print("ENTROU")

                    i+=1
                    time.sleep(1)

                    #USAR SWITCH CASE! ABAIXO

                    if( notificacao == ALERTA_EMAIL ):
                        exec_audio("enviando_email.wav",1)
                        notifica("BC0013","email")
                        break

                    if( notificacao == ALERTA_SMS ):
                        exec_audio("enviando_sms.wav",1)
                        notifica("BC0013","sms")
                        break

                if(DEBUG):
                    print("----------DEBUG----------")
                    print('Valor da variavel notificacao: {}'.format(notificacao))
                    print('Valor da variavel esquerda: {}'.format(esquerda))
                    print('Valor da variavel direita: {}'.format(direita))
                    print("----------DEBUG----------")       
            
        else:
            i+=1
            if (GPIO.input(pinoLedVermelho)):
                print("Apagando LED de deteccao - VERMELHO")
                GPIO.output(pinoLedVermelho,GPIO.LOW)
            
            print(i,"Sem movimento")
        
            time.sleep(1)
    else:
        i+=1
        print(i,"Botao nao pressionado, sensores inativos.")
        GPIO.output(pinoLedVerde,GPIO.LOW)
        time.sleep(1)
