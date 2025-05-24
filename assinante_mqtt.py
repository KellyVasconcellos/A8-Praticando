# Import dos pacotes
import pandas as pd
import time
import paho.mqtt.client as mqtt

# Tópico para subscrever (mesmo que o publicador usa)
METRIC_TOPIC = "monitor/desempenho/cpu_uso"
BROKER_HOSTNAME = "mqtt.eclipseprojects.io"
OUTPUT_FILE = "dados_monitoramento_cpu.csv" # Nome do arquivo para persistir os dados
MESSAGES_TO_SAVE = 10 # Salva a cada 10 mensagens recebidas

# Criacao de um DataFrame para coleta de dados
# Adicionei uma coluna para o status/alerta
df_monitoramento = pd.DataFrame(columns = ['timestamp', 'cpu_uso', 'variacao_perc', 'status_alerta'])

# Variável global para armazenar o valor anterior da CPU para cálculo da variação
last_cpu_value = None
message_count = 0 # Contador para saber quando salvar

# Funcao ativada (callback) quando o client recebe a confirmacao de conexao
# com o broker (CONNACK).
def on_connect(client, userdata, flags, rc):
    print(f"Assinante conectado com resultado código: {str(rc)}")
    client.subscribe(METRIC_TOPIC)
    print(f"Assinando o tópico: {METRIC_TOPIC}")


# Funcao ativada (callback) quando uma mensagem publicada e recebida pelo
# cliente
def on_message(client, userdata, msg):
    global df_monitoramento
    global last_cpu_value
    global message_count

    try:
        # 1. Coletar o streaming de dados
        cpu_uso_atual = float(msg.payload.decode('utf-8')) # Decodifica e converte para float
        current_timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

        # 2. Realizar algum tipo de processamento
        variacao_perc = 0.0
        if last_cpu_value is not None and last_cpu_value != 0:
            variacao_perc = ((cpu_uso_atual - last_cpu_value) / last_cpu_value) * 100

        # Classificação/Status (processamento simples)
        status_alerta = "NORMAL"
        if cpu_uso_atual > 80:
            status_alerta = "CRÍTICO"
        elif cpu_uso_atual > 60:
            status_alerta = "ATENÇÃO"

        # 3. Armazenar um conjunto de dados em memória (no DataFrame)
        new_data = pd.DataFrame([{
            'timestamp': current_timestamp,
            'cpu_uso': cpu_uso_atual,
            'variacao_perc': round(variacao_perc, 2), # Arredonda para legibilidade
            'status_alerta': status_alerta
        }])

        df_monitoramento = pd.concat([df_monitoramento, new_data], ignore_index=True)

        print("\n--- Nova Métrica Recebida ---")
        print(f"Timestamp: {current_timestamp}")
        print(f"Uso de CPU: {cpu_uso_atual:.2f}%")
        print(f"Variação (último valor): {variacao_perc:.2f}%")
        print(f"Status: {status_alerta}")
        print("\nDataFrame Atual:")
        print(df_monitoramento.tail()) # Mostra as últimas entradas do DataFrame

        last_cpu_value = cpu_uso_atual # Atualiza o último valor
        message_count += 1

        # 4. Persistir os dados (quando atingir um certo número de mensagens)
        if message_count >= MESSAGES_TO_SAVE:
            print(f"\n--- Salvando {message_count} mensagens em '{OUTPUT_FILE}' ---")
            df_monitoramento.to_csv(OUTPUT_FILE, mode='a', header=not pd.io.common.file_exists(OUTPUT_FILE), index=False)
            df_monitoramento = pd.DataFrame(columns = ['timestamp', 'cpu_uso', 'variacao_perc', 'status_alerta']) # Limpa o DataFrame em memória após salvar
            message_count = 0 # Reseta o contador

    except ValueError as e:
        print(f"Erro ao converter payload para float: {msg.payload.decode('utf-8')}. Erro: {e}")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")


# Cricacao do objeto client do mqtt e definicao das funcoes de callback
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# Conexao com o broker
client.connect(BROKER_HOSTNAME)

# Metodo que gerencia a conexao com o broker
# Usamos loop_forever() para manter o assinante escutando.
# Uma alternativa seria loop_start() com um loop while True para outras operações.
try:
    client.loop_forever()
except KeyboardInterrupt:
    print("Assinante encerrado.")
    # Persistir quaisquer dados remanescentes antes de sair
    if not df_monitoramento.empty:
        print(f"\n--- Salvando dados remanescentes em '{OUTPUT_FILE}' ---")
        df_monitoramento.to_csv(OUTPUT_FILE, mode='a', header=not pd.io.common.file_exists(OUTPUT_FILE), index=False)
    client.disconnect()