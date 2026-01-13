# 📡 Real-Time Data Pipeline com MQTT e Python

Este projeto implementa um sistema simplificado de coleta, processamento e persistência de dados em streaming utilizando o protocolo **MQTT**. O sistema simula o monitoramento de telemetria de CPU em tempo real, realizando o cálculo de variações e alertas antes de armazenar os dados para análise futura.

## 🎯 Objetivo
O objetivo é demonstrar uma arquitetura **Publisher/Subscriber (Pub/Sub)** onde:
1. Um **Publicador** simula a geração de métricas de hardware.
2. um **Assinante** consome esses dados em tempo real, aplica regras de negócio (cálculo de variação e classificação de status) e persiste os resultados em lotes (*batch*) em um arquivo CSV.



## 🛠️ Tecnologias Utilizadas
* **Python 3.x**
* **Paho-MQTT:** Biblioteca para comunicação via protocolo MQTT.
* **Pandas:** Processamento, manipulação de dados em memória e exportação para CSV.
* **MQTT Eclipse Broker:** Broker público utilizado para a troca de mensagens.

## 📂 Estrutura do Projeto
O sistema é dividido em dois scripts principais:

### 1. Publicador (`publisher.py`)
Simula um sensor de monitoramento de CPU. 
* Gera valores flutuantes aleatórios (0% a 100%).
* Publica as métricas no tópico `monitor/desempenho/cpu_uso` a cada 2 segundos.

### 2. Assinante/Consumidor (`subscriber.py`)
Atua como o motor de processamento:
* **Ingestão:** Escuta o tópico de métricas.
* **Processamento:** Calcula a variação percentual em relação à última leitura e classifica o status (NORMAL, ATENÇÃO, CRÍTICO).
* **Buffer em Memória:** Armazena os dados temporariamente em um DataFrame Pandas.
* **Persistência:** A cada 10 mensagens recebidas, os dados são descarregados (*flush*) em um arquivo `dados_monitoramento_cpu.csv`.

## 🚀 Como Executar

1. **Instale as dependências:**
   ```bash
   pip install paho-mqtt pandas
