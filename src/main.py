from machine import Pin, ADC
import time

print("Teste")

pino_acelerador = ADC(Pin(34))
pino_acelerador.atten(ADC.ATTN_11DB) 

pino_pressao_freio = ADC(Pin(35))
pino_pressao_freio.atten(ADC.ATTN_11DB)

LED_abs = Pin(33, Pin.OUT)

ultimo_tempo_pisca = 0
intervalo_abs = 60 
estado_LED = 0

pressao_anterior = 0.0
abs_em_acao = False

velocidade_atual = 0.0

def ler_acelerador():
    return (pino_acelerador.read() / 4095) * 100

def ler_pressao_freio():
    return (pino_pressao_freio.read() / 4095) * 100

while True:
    tempo_atual = time.ticks_ms()
    
    acelerador = ler_acelerador()
    pressao_atual = ler_pressao_freio()
    variacao_pressao = pressao_atual - pressao_anterior

    if pressao_atual < 5.0:
        abs_em_acao = False 
        LED_abs.value(0)
        estado_LED = 0
        status_terminal = "LIVRE" if acelerador > 5.0 else "SOLTO"
        
    else:
        if variacao_pressao > 25.0 and pressao_atual > 50.0 and velocidade_atual > 20.0:
            abs_em_acao = True 
            
        if abs_em_acao and velocidade_atual > 0.0:
            if time.ticks_diff(tempo_atual, ultimo_tempo_pisca) > intervalo_abs:
                ultimo_tempo_pisca = tempo_atual
                estado_LED = not estado_LED 
                LED_abs.value(estado_LED)
            status_terminal = "PÂNICO (ABS)"
        else:
            LED_abs.value(1)
            status_terminal = "FRENAGEM NORMAL"

    if pressao_atual > 5.0:
        if abs_em_acao:
            velocidade_atual -= 2.5 
        else:
            desaceleracao = (pressao_atual / 100.0) * 2.0
            velocidade_atual -= desaceleracao
    else:
        if acelerador > 5.0:
            velocidade_atual += (acelerador / 100.0) * 1.5
        else:
            velocidade_atual -= 0.3

    if velocidade_atual < 0.0: velocidade_atual = 0.0
    if velocidade_atual > 140.0: velocidade_atual = 140.0

    print(f"Velocidade: {velocidade_atual:05.1f}km/h | Aceleração: {acelerador:05.1f}% | Freio: {pressao_atual:05.1f}% | {status_terminal}")
    
    pressao_anterior = pressao_atual
    
    time.sleep(0.05)