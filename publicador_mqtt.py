# Import dos pacotes
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import time
import random

# Tópico para publicar a métrica
METRIC_TOPIC = "monitor/desempenho/cpu_uso"
BROKER_HOSTNAME = "mqtt.eclipseprojects.io"

# Valor inicial da métrica (simulação)
current_metric_value = 50.0

# Funcao ativada (callback) quando o client recebe a confirmacao de conexao
# com o broker (CONNACK).
def on_connect(client, userdata, flags, rc):
    print(f"Publicador conectado com resultado código: {rc}")
    # Não precisa subscrever a nada aqui, apenas publicar.


# Funcao principal para enviar a métrica
def send_metric():
    global current_metric_value
    # Simula flutuações na métrica
    # Adiciona ou subtrai um valor aleatório entre -2 e +2
    change = random.uniform(-2.0, 2.0)
    current_metric_value += change

    # Garante que a métrica fique entre 0 e 100
    current_metric_value = max(0.0, min(100.0, current_metric_value))

    # Arredonda para 2 casas decimais para manter a simplicidade
    metric_to_send = round(current_metric_value, 2)

    print(f"Publicando métrica de CPU: {metric_to_send:.2f}% no tópico '{METRIC_TOPIC}'")
    # Publica a métrica. Convertemos para string porque o MQTT lida com bytes/strings.
    publish.single(METRIC_TOPIC, str(metric_to_send), hostname=BROKER_HOSTNAME)


# Cricacao do objeto client do mqtt e definicao das funcoes de callback
client = mqtt.Client()
client.on_connect = on_connect

# Conexao com o broker
client.connect(BROKER_HOSTNAME)

client.loop_start()

try:
    while True:
        send_metric()
        time.sleep(2) # Envia uma métrica a cada 2 segundos
except KeyboardInterrupt:
    print("Publicador encerrado.")
    client.loop_stop()

    client.disconnect()
