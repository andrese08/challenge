#!/usr/bin/env python
# -*- coding: utf-8 -*-

import smtplib
from email.mime.text import MIMEText

# Diccionario de ejemplo (datos_combinados)


# Función para enviar correo electrónico
def enviar_correo(destinatario, mensaje):
    asunto = 'Reválidas anuales del proceso de clasificación de la información--MELI'
    
    mensaje = MIMEText(mensaje)
    #mensaje['From'] = remitente
    mensaje['To'] = destinatario
    mensaje['Subject'] = asunto

    servidor_smtp = 'smtp.gmail.com'
    puerto_smtp = 587
    usuario_smtp = 'challengemeliedison@gmail.com'  # Coloca tu dirección de correo aquí
    password_smtp = 'gmphjebdlsnzyrst'  # Coloca tu contraseña aquí
    

    servidor = smtplib.SMTP(servidor_smtp, puerto_smtp)
    servidor.starttls()
    servidor.login(usuario_smtp, password_smtp)
    servidor.send_message(mensaje)
    servidor.quit()



