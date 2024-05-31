import smtplib
from email.mime.text import MIMEText

# Diccionario de ejemplo (datos_combinados)
datos_combinados = [
    {'db_name': 'otra', 'user_id': 'uno', 'db_class': 'Low', 'user_state': 'uno@uno.com', 'user_manager': 'a@a.com'},
    {'db_name': 'men', 'user_id': 'tres', 'db_class': 'Low', 'user_state': 'tres@tres.com', 'user_manager': 'p@p.com'},
    {'db_name': 'boy', 'user_id': 'uno', 'db_class': 'High', 'user_state': 'uno@uno.com', 'user_manager': 'a@a.com'}
]

# Función para enviar correo electrónico
def enviar_correo(destinatario, mensaje):
    remitente = 'tu_correo@gmail.com'  # Coloca tu dirección de correo aquí
    asunto = 'Asunto del correo'
    
    mensaje = MIMEText(mensaje)
    mensaje['From'] = remitente
    mensaje['To'] = destinatario
    mensaje['Subject'] = asunto

    servidor_smtp = 'smtp.gmail.com'
    puerto_smtp = 587
    usuario_smtp = 'tu_correo@gmail.com'  # Coloca tu dirección de correo aquí
    password_smtp = 'tu_contraseña'  # Coloca tu contraseña aquí

    servidor = smtplib.SMTP(servidor_smtp, puerto_smtp)
    servidor.starttls()
    servidor.login(usuario_smtp, password_smtp)
    servidor.send_message(mensaje)
    servidor.quit()

# Validación de db_class y envío de correo electrónico
for dato in datos_combinados:
    if dato['db_class'] == 'High':
        mensaje_correo = f"Texto del correo para el usuario manager: {dato['user_manager']}"
        enviar_correo(dato['user_manager'], mensaje_correo)
