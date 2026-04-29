from machine import Pin, ADC
import time

# Configuração das entradas analógicas
pino_acelerador = ADC(Pin(34))
pino_acelerador.atten(ADC.ATTN_11DB) 

pino_pressao_freio = ADC(Pin(35))
pino_pressao_freio.atten(ADC.ATTN_11DB)

# Configuração do pino do LED indicativo do ABS
LED_abs = Pin(33, Pin.OUT)

# Controle da temporização não-bloqueante do LED
ultimo_tempo_pisca = 0
intervalo_abs = 60 
estado_LED = 0

# Variáveis utilizadas na detecção da taxa de variação da frenagem
pressao_anterior = 0.0
abs_em_acao = False

velocidade_atual = 0.0

# Funções para converter o valor padrão do ADC (que possui valores de 0 a 4095) para porcentagem (0 a 100)
def ler_acelerador():
    return (pino_acelerador.read() / 4095) * 100

def ler_pressao_freio():
    return (pino_pressao_freio.read() / 4095) * 100

# Variável para marcar a primeira iteração do while
p_iteracao = True

while True:
    tempo_atual = time.ticks_ms()
    
    acelerador = ler_acelerador()
    pressao_atual = ler_pressao_freio()

    # Calcula o quão rápido o manete foi apertado neste ciclo
    variacao_pressao = pressao_atual - pressao_anterior

    # Avaliação dos estados do freio
    if pressao_atual < 5.0:
        # Manete solto: desativa freio e ABS
        abs_em_acao = False 
        LED_abs.value(0)
        estado_LED = 0
        status_terminal = "LIVRE" if acelerador > 5.0 else "SOLTO"
        
    else:
        # Detecção de PÂNICO: puxada brusca (mais de 25%), muita força (mais de 50%) em alta velocidade (mais de 20km/h)
        if variacao_pressao > 25.0 and pressao_atual > 50.0 and velocidade_atual > 20.0:
            abs_em_acao = True 
            
        if abs_em_acao and velocidade_atual > 0.0:
            # Temporização não-bloqueante para pulsar o LED do ABS
            if time.ticks_diff(tempo_atual, ultimo_tempo_pisca) > intervalo_abs:
                ultimo_tempo_pisca = tempo_atual
                estado_LED = not estado_LED 
                LED_abs.value(estado_LED)
            status_terminal = "PÂNICO (ABS)"
        else:
            # Frenagem normal (progressiva ou em baixa velocidade)
            LED_abs.value(1)
            status_terminal = "FRENAGEM NORMAL"

    # Física veicular
    if pressao_atual > 5.0:
        if abs_em_acao:
            # Desaceleração controlada pelo sistema ABS
            velocidade_atual -= 2.5 
        else:
            # Desaceleração proporcional à pressão exercida pelo piloto no manete
            desaceleracao = (pressao_atual / 100.0) * 2.0
            velocidade_atual -= desaceleracao
    else:
        if acelerador > 5.0:
            # Incremento de velocidade devido ao acelerador
            velocidade_atual += (acelerador / 100.0) * 1.5
        else:
            # Perda gradual de velocidade por atrito com o ambiente
            velocidade_atual -= 0.3

    # Travas de segurança
    if velocidade_atual < 0.0: velocidade_atual = 0.0
    if velocidade_atual > 140.0: velocidade_atual = 140.0

    print(f"Velocidade: {velocidade_atual:05.1f}km/h | Aceleração: {acelerador:05.1f}% | Freio: {pressao_atual:05.1f}% | {status_terminal}")
    
    # Atualiza a pressão para o cálculo do próximo ciclo
    pressao_anterior = pressao_atual

    #Palavra esperada pelo actions (Apenas no final da primeira iteração)
    if p_iteracao:
        print("Teste")
        p_iteracao = False
    
    # Atualização a cada 50ms
    time.sleep(0.05)