import network
import utime
import urequests
import json
import ntptime
import machine
import time
from machine import DAC, Pin, freq


# Configuración WiFi
SSID = "*******"
PASSWORD = "********"

# Configurar frecuencia de CPU
freq(240000000)

pin25 = Pin(25, Pin.IN)

# Configuración del DAC (si lo estás usando para el audio)
dac = DAC(Pin(25, Pin.OUT))


# Configuración de los botones
boton13 = Pin(13, Pin.IN, Pin.PULL_UP)
boton34 = Pin(34, Pin.IN, Pin.PULL_UP)
boton21 = Pin(21, Pin.IN, Pin.PULL_UP)
boton1 = Pin(1, Pin.IN, Pin.PULL_UP)
boton36 = Pin(36, Pin.IN, Pin.PULL_UP)
boton35 = Pin(35, Pin.IN, Pin.PULL_UP)
boton19 = Pin(19, Pin.IN, Pin.PULL_UP)
boton3 = Pin(3, Pin.IN, Pin.PULL_UP)
boton39 = Pin(39, Pin.IN, Pin.PULL_UP)

# Configuración de los pines de la matriz
boton22 = Pin(22, Pin.IN, Pin.PULL_UP)
boton23 = Pin(23, Pin.IN, Pin.PULL_UP)
boton32 = Pin(32, Pin.IN, Pin.PULL_UP)
boton33 = Pin(33, Pin.IN, Pin.PULL_UP)
boton26 = Pin(26, Pin.IN, Pin.PULL_UP)
boton27 = Pin(27, Pin.IN, Pin.PULL_UP)

# Configuración de los botones de borrar y enviar
boton_borrar = Pin(14, Pin.IN, Pin.PULL_UP)
boton_enviar = Pin(12, Pin.IN, Pin.PULL_UP)

# Configuración del relé
rele = Pin(15, Pin.OUT)
rele3 = Pin(2, Pin.OUT)
rele4 = Pin(4, Pin.OUT)
rele5 = Pin(16, Pin.OUT)
rele6 = Pin(17, Pin.OUT)
rele7 = Pin(5, Pin.OUT)
releVenti = Pin(18, Pin.OUT)
rele.on()
rele3.on()
rele4.on()
rele5.on()
rele6.on()
rele7.on()
releVenti.on()




wifi = network.WLAN(network.STA_IF)

def conectar_wifi(ssid, password):
    global wifi
    wifi.active(True)
    if not wifi.isconnected():
        wifi.connect(ssid, password)
        timeout = 20 
        start_time = time.time()
        while not wifi.isconnected() and (time.time() - start_time) < timeout:
            time.sleep(1)
           
        if wifi.isconnected():
            print("Conexión establecida:", wifi.ifconfig())
        else:            
            wifi.active(False)  # Desactivar WiFi si no se conecta
    else:
        print("Ya está conectado a la red WiFi:", wifi.ifconfig())
    return wifi

conectar_wifi(SSID, PASSWORD)

def desconectar_wifi():
    if wifi.isconnected():
        wifi.disconnect()
    wifi.active(False)
    print("WiFi desconectado")


def pitido():
    frecuencia = 1000  # Frecuencia del pitido en Hz
    duracion = 0.1  # Duración del pitido en segundos
    muestra_tiempo = int(1000000 / frecuencia)

    for i in range(int(frecuencia * duracion)):
        dac.write(128)  # Valor medio para generar el tono
        time.sleep_us(muestra_tiempo)
        dac.write(0)
        time.sleep_us(muestra_tiempo)
    
import time

def pitido_suave(dac, frecuencia=1000, duracion=7):
    muestra_tiempo = int(1000000 / frecuencia)
    num_muestras = int(frecuencia * duracion)
    
    # Valores para el tono (amplitud inicial y final)
    amplitud_inicial = 0  # Comenzar con amplitud 0 para un inicio muy suave
    amplitud_final = 20
    
    # Reducir el paso para que el incremento sea más lento
    paso = (amplitud_final - amplitud_inicial) / (num_muestras * 2)  # El multiplicador 2 hace que el incremento sea más lento
    
    valor_dac = amplitud_inicial

    for i in range(num_muestras):
        dac.write(int(valor_dac))
        time.sleep_us(muestra_tiempo)
        
        # Alterna entre el valor actual y 0 para generar el tono
        dac.write(int(valor_dac))
        time.sleep_us(muestra_tiempo)
        dac.write(0)
        time.sleep_us(muestra_tiempo)
        
        # Incrementa el valor del DAC
        valor_dac += paso
        if valor_dac > amplitud_final:
            valor_dac = amplitud_final

# Asumiendo que tienes un objeto DAC configurado
pitido_suave(dac)


def reproducir_audio(carpeta, archivo):    
    api_url = f"http://192.168.1.9:4000/audio/{carpeta}/{archivo}/file"    
    try:
        response = urequests.get(api_url)        
        if response.status_code == 200:                        
            header_size = 44  
            chunk_size = 1024
            buffer = bytearray(chunk_size)
            response.raw.readinto(bytearray(header_size))
            sample_rate = 8000
            wait_time = int(1000000 / sample_rate)
            while True:
                chunk = response.raw.readinto(buffer)
                if chunk == 0:
                    break
                for i in range(chunk):
                    dac.write(buffer[i])
                    time.sleep_us(wait_time) 
        else:
            print(f"Error al obtener el audio desde la API: {response.status_code}")
    except Exception as e:
        print(f"Error de conexión: {e}")
    finally:
        if "response" in locals():
            response.close()        

reproducir_audio("Inicio", "tablero")


def enviar_datos(data, tipo):
    try:
        url = f"http://192.168.1.9:4000/{tipo}"
        headers = {"Content-Type": "application/json"}
        uz_json = json.dumps(data)

        response = urequests.post(url, data=uz_json, headers=headers)        
        if response.status_code == 200:
            reproducir_audio("Inicio", "finalevalacion")
        else:
            reproducir_audio("Inicio", "error")
    except Exception as e:
        reproducir_audio("Inicio", "error")
    finally:
        if response:
            response.close()

estado_botones = {
    "boton22": False,
    "boton23": False,
    "boton32": False,
    "boton33": False,
    "boton26": False,
    "boton27": False,
}


def manejar_boton(pin, boton_key):
    if pin.value() == 0:
        pitido()
        estado_botones[boton_key] = True
        time.sleep(0.3)                


def manejar_boton1(pin):   
    if pin.value() == 0:        
        pitido()
        reproducir_audio("Inicio", "explicacion_tablero")


def procesar_botones(valores_botones, intentos_maximos=3):
    intentos = 0
    estado = False
    while boton_enviar.value() == 1: 
        manejar_boton(boton22, "boton22")
        manejar_boton(boton23, "boton23")
        manejar_boton(boton32, "boton32")
        manejar_boton(boton33, "boton33")
        manejar_boton(boton26, "boton26")
        manejar_boton(boton27, "boton27")
        time.sleep(0.2)
        if boton_borrar.value() == 0:            
            pitido()
            reset_estado_botones()

        if boton_enviar.value() == 0:            
            pitido()            
            if (
                estado_botones["boton22"] == valores_botones[0]
                and estado_botones["boton23"] == valores_botones[1]
                and estado_botones["boton32"] == valores_botones[2]
                and estado_botones["boton33"] == valores_botones[3]
                and estado_botones["boton26"] == valores_botones[4]
                and estado_botones["boton27"] == valores_botones[5]
            ):               
                reproducir_audio("Inicio", "PracticaCorrecta")
                reset_estado_botones()
                estado = True
                break
            else:             
                reproducir_audio("Inicio", "PracticaIncorrecta")              
                reset_estado_botones()
                time.sleep(0.5)
                intentos += 1  # Incrementar el contador de intentos
                if intentos >= intentos_maximos:                    
                    estado = False
                    break

    return estado

contador_ciclos = 0

def reproducir_y_revisar_audio(
    carpeta, archivo, valores_esperados, relays_on, relays_off, delay=7
):
    global contador_ciclos
    reproducir_audio(carpeta, archivo)
    for relay in relays_off:
        relay.off()
    time.sleep(delay)
    for relay in relays_on:
        relay.on()
    reproducir_audio("Inicio", "Paracadaletracorto")

    time.sleep(0.5)
    if contador_ciclos == 0 or contador_ciclos % 3 == 0:
        reproducir_audio("Inicio", "borraryenviar")

    contador_ciclos += 1
    print(contador_ciclos)
    resultado = procesar_botones(valores_esperados)
    while not resultado:        
        reproducir_audio("Inicio", "AudioIntentos")
        for relay in relays_off:
            relay.off()
        time.sleep(5)
        for relay in relays_on:
            relay.on()

        time.sleep(0.5)
        resultado = procesar_botones(valores_esperados)

#Evaluacion
def procesar_botones_evaluacion(valores_botones):
    estado = False
    while boton_enviar.value() == 1:  # Mientras no se presione el botón de enviar
        try:
            # Actualizar el estado de los botones
            manejar_boton(boton22, "boton22")
            manejar_boton(boton23, "boton23")
            manejar_boton(boton32, "boton32")
            manejar_boton(boton33, "boton33")
            manejar_boton(boton26, "boton26")
            manejar_boton(boton27, "boton27")
            time.sleep(0.2)

            if boton_borrar.value() == 0:
                pitido()
                reset_estado_botones()

            if boton_enviar.value() == 0:
                pitido()
                # Verificar si el estado actual de los botones coincide con los valores esperados
                if (
                    estado_botones["boton22"] == valores_botones[0]
                    and estado_botones["boton23"] == valores_botones[1]
                    and estado_botones["boton32"] == valores_botones[2]
                    and estado_botones["boton33"] == valores_botones[3]
                    and estado_botones["boton26"] == valores_botones[4]
                    and estado_botones["boton27"] == valores_botones[5]
                ):
                    reset_estado_botones()
                    estado = True
                else:
                    reset_estado_botones()
                    estado = False
                break  # Salir del ciclo una vez se presiona el botón de enviar

        except Exception as e:
            reproducir_audio("Inicio", "error")
            time.sleep(1)  # Espera un segundo antes de reintentar en caso de error

    return estado



def reproducir_y_revisar_audio_evaluacion(
    carpeta, archivo, valores_esperados, relays_on, relays_off, delay=5
):
    global contador_ciclos
    reproducir_audio(carpeta, archivo)
    for relay in relays_off:
        relay.off()
    time.sleep(delay)
    for relay in relays_on:
        relay.on()    

    time.sleep(0.5)    
    resultado = procesar_botones_evaluacion(valores_esperados)
    return resultado





def manejar_boton2(pin):
    
    if pin.value() == 0:        
        pitido()
        reproducir_audio("Inicio", "espejo")
        reproducir_audio("PracticaAG", "CursoAaG")
        reproducir_audio("Inicio", "Recomendacion")
        reproducir_y_revisar_audio(
            "PracticaAG",
            "LetraA",
            [0, 1, 0, 0, 0, 0],
            [rele],
            [rele]
        )
        reproducir_y_revisar_audio(
            "PracticaAG",
            "LetraAescritura",
            [1, 0, 0, 0, 0, 0],
            [rele3],
            [rele3]
        )
        reproducir_y_revisar_audio(
            "PracticaAG",
            "LetraB",
            [0, 1, 1, 0, 0, 0],
            [rele, rele4, releVenti],
            [rele, rele4, releVenti],
        )
        reproducir_y_revisar_audio(
            "PracticaAG",
            "LetraBescritura",
            [1, 0, 0, 1, 0, 0],
            [rele3, rele5],
            [rele3, rele5],
        )
        reproducir_y_revisar_audio(
            "PracticaAG",
            "LetraC",
            [1, 1, 0, 0, 0, 0],
            [rele, rele3],
            [rele, rele3]
        )
        reproducir_y_revisar_audio(
            "PracticaAG",
            "LetraCescritura",
            [1, 1, 0, 0, 0, 0],
            [rele, rele3, releVenti],
            [rele, rele3, releVenti],
        )
        reproducir_y_revisar_audio(
            "PracticaAG",
            "LetraD",
            [1, 1, 0, 1, 0, 0],
            [rele, rele3, rele5],
            [rele, rele3, rele5],
        )
        reproducir_y_revisar_audio(
            "PracticaAG",
            "LetraDescritura",
            [1, 1, 1, 0, 0, 0],
            [rele, rele3, rele4],
            [rele, rele3, rele4],
        )
        reproducir_y_revisar_audio(
            "PracticaAG",
            "LetraE",
            [0, 1, 0, 1, 0, 0],
            [rele, rele5, releVenti],
            [rele, rele5, releVenti],
        )
        reproducir_y_revisar_audio(
            "PracticaAG",
            "LetraEescritura",
            [1, 0, 1, 0, 0, 0],
            [rele3, rele4],
            [rele3, rele4],
        )
        reproducir_y_revisar_audio(
            "PracticaAG",
            "LetraF",
            [1, 1, 1, 0, 0, 0],
            [rele, rele3, rele4],
            [rele, rele3, rele4],
        )
        reproducir_y_revisar_audio(
            "PracticaAG",
            "LetraFescritura",
            [1, 1, 0, 1, 0, 0],
            [rele, rele3, rele5, releVenti],
            [rele, rele3, rele5, releVenti],
        )
        reproducir_y_revisar_audio(
            "PracticaAG",
            "LetraG",
            [1, 1, 1, 1, 0, 0],
            [rele, rele3, rele4, rele5],
            [rele, rele3, rele4, rele5],
        )
        reproducir_y_revisar_audio(
            "PracticaAG",
            "LetraGescritura",
            [1, 1, 1, 1, 0, 0],
            [rele, rele3, rele4, rele5],
            [rele, rele3, rele4, rele5],
        )
        reproducir_audio("Inicio", "AudioRepetir")


def sincronizar_tiempo():
    try:
        ntptime.settime()  # Sincroniza el RTC del ESP32 con un servidor NTP
    except Exception as e:
        reproducir_audio("Inicio", "error")

def ajustar_zona_horaria(offset_horas):
    # Obtén el tiempo UTC actual en segundos desde epoch
    tiempo_utc = utime.time()
    # Ajusta el tiempo a tu zona horaria
    tiempo_local = tiempo_utc + offset_horas * 3600
    return utime.localtime(tiempo_local)   

def manejar_boton21(pin):
    try:        
        if pin.value() == 0:
            sincronizar_tiempo()                    
            tiempo_actual = ajustar_zona_horaria(-5)            
            fecha_actual = f"{tiempo_actual[0]:04d}-{tiempo_actual[1]:02d}-{tiempo_actual[2]:02d}"  # Año-Mes-Día
            hora_actual = f"{tiempo_actual[3]:02d}:{tiempo_actual[4]:02d}:{tiempo_actual[5]:02d}"  # Hora:Minuto:Segundo

            pitido()
            reproducir_audio("evaluacionAG", "evaluacionAG")
            reproducir_audio("Inicio", "recomentadionevaluacio")
            reproducir_audio("Inicio", "indicacionesevaluacion")        

            ag_data = generar_ag_data(fecha_actual, hora_actual)
            enviar_datos(ag_data,'ag')

    except Exception as e:
        reproducir_audio("Inicio", "error")
    
        

def generar_ag_data(fecha, hora):
    ag_data = {
        "ag_idestado": 2,
        "ag_fecha_inicio": fecha,
        "ag_hora_inicio": hora,
        "ag_unol": False,
        "ag_dosl": False,
        "ag_tresl": False,
        "ag_cuatrol": False,
        "ag_cincol": False,
        "ag_seisl": False,
        "ag_sietel": False,
        "ag_unos": False,
        "ag_doss": False,
        "ag_tress": False,
        "ag_cuatros": False,
        "ag_cincos": False,
        "ag_seiss": False,
        "ag_sietes": False,
        "ag_fecha_fin": "2024-08-27",
        "ag_hora_fin": "15:00:00"
    }

    try:
        # Reproducir y revisar audio para la evaluación y escritura
        ag_data["ag_unol"] = reproducir_y_revisar_audio_evaluacion("evaluacionAG", "letraAlectura", [0, 1, 0, 0, 0, 0], [rele3], [rele3])
        ag_data["ag_dosl"] = reproducir_y_revisar_audio_evaluacion("evaluacionAG", "letraBlectura", [0, 1, 1, 0, 0, 0], [rele3, rele5, releVenti], [rele3, rele5, releVenti])
        ag_data["ag_tresl"] = reproducir_y_revisar_audio_evaluacion("evaluacionAG", "letraClectura", [1, 1, 0, 0, 0, 0], [rele, rele3], [rele, rele3])
        ag_data["ag_cuatrol"] = reproducir_y_revisar_audio_evaluacion("evaluacionAG", "letraDlectura", [1, 1, 0, 1, 0, 0], [rele, rele3, rele4], [rele, rele3, rele4])
        ag_data["ag_cincol"] = reproducir_y_revisar_audio_evaluacion("evaluacionAG", "letraElectura", [0, 1, 0, 1, 0, 0], [rele3, rele4, releVenti], [rele3, rele4, releVenti])
        ag_data["ag_seisl"] = reproducir_y_revisar_audio_evaluacion("evaluacionAG", "letraFlectura", [1, 1, 1, 0, 0, 0], [rele, rele3, rele5], [rele, rele3, rele5])
        ag_data["ag_sietel"] = reproducir_y_revisar_audio_evaluacion("evaluacionAG", "letraGlectura", [1, 1, 1, 1, 0, 0], [rele, rele3, rele4, rele5], [rele, rele3, rele4, rele5])
        
        ag_data["ag_unos"] = reproducir_y_revisar_audio_evaluacion("evaluacionAG", "letraAescritura", [1, 0, 0, 0, 0, 0], [rele], [rele])
        ag_data["ag_doss"] = reproducir_y_revisar_audio_evaluacion("evaluacionAG", "letraBescritura", [1, 0, 0, 1, 0, 0], [rele, rele4], [rele, rele4])
        ag_data["ag_tress"] = reproducir_y_revisar_audio_evaluacion("evaluacionAG", "letraCescritura", [1, 1, 0, 0, 0, 0], [rele, rele3, releVenti], [rele, rele3, releVenti])
        ag_data["ag_cuatros"] = reproducir_y_revisar_audio_evaluacion("evaluacionAG", "letraDescritura", [1, 1, 1, 0, 0, 0], [rele, rele3, rele5], [rele, rele3, rele5])
        ag_data["ag_cincos"] = reproducir_y_revisar_audio_evaluacion("evaluacionAG", "letraEescritura", [1, 0, 1, 0, 0, 0], [rele, rele5], [rele, rele5])
        ag_data["ag_seiss"] = reproducir_y_revisar_audio_evaluacion("evaluacionAG", "letraFescritura", [1, 1, 0, 1, 0, 0], [rele, rele3, rele4, releVenti], [rele, rele3, rele4, releVenti])
        ag_data["ag_sietes"] = reproducir_y_revisar_audio_evaluacion("evaluacionAG", "letraGescritura", [1, 1, 1, 1, 0, 0], [rele, rele3, rele4, rele5], [rele, rele3, rele4, rele5])
    
    except Exception as e:
        reproducir_audio("Inicio", "error")
    
    return ag_data



def manejar_boton3(pin):
    
    if pin.value() == 0:
        pitido()
        reproducir_audio("Inicio", "espejo")
        reproducir_audio("PracticaHN", "CursoHaN")
        reproducir_audio("Inicio", "Recomendacion")
        reproducir_y_revisar_audio(
            "PracticaHN",
            "LetraH",
            [0, 1, 1, 1, 0, 0],
            [rele, rele4, rele5],
            [rele, rele4, rele5],
        )
        reproducir_y_revisar_audio(
            "PracticaHN",
            "LetraHescritura",
            [1, 0, 1, 1, 0, 0],
            [rele3, rele4, rele5],
            [rele3, rele4, rele5],
        )
        reproducir_y_revisar_audio(
            "PracticaHN",
            "LetraI",
            [1, 0, 1, 0, 0, 0],
            [rele3, rele4],
            [rele3, rele4]
        )
        reproducir_y_revisar_audio(
            "PracticaHN",
            "LetraIescritura",
            [0, 1, 0, 1, 0, 0],
            [rele, rele5, releVenti],
            [rele, rele5, releVenti],
        )
        reproducir_y_revisar_audio(
            "PracticaHN",
            "LetraJ",
            [1, 0, 1, 1, 0, 0],
            [rele3, rele4, rele5],
            [rele3, rele4, rele5],
        )
        reproducir_y_revisar_audio(
            "PracticaHN",
            "LetraJescritura",
            [0, 1, 1, 1, 0, 0],
            [rele, rele4, rele5],
            [rele, rele4, rele5],
        )
        reproducir_y_revisar_audio(
            "PracticaHN",
            "LetraK",
            [0, 1, 0, 0, 1, 0],
            [rele, rele6],
            [rele, rele6]
        )
        reproducir_y_revisar_audio(
            "PracticaHN",
            "LetraKescritura",
            [1, 0, 0, 0, 0, 1],
            [rele3, rele7, releVenti],
            [rele3, rele7, releVenti],
        )
        reproducir_y_revisar_audio(
            "PracticaHN",
            "LetraL",
            [0, 1, 1, 0, 1, 0],
            [rele, rele4, rele6],
            [rele, rele4, rele6],
        )
        reproducir_y_revisar_audio(
            "PracticaHN",
            "LetraLescritura",
            [1, 0, 0, 1, 0, 1],
            [rele3, rele5, rele7],
            [rele3, rele5, rele7],
        )
        reproducir_y_revisar_audio(
            "PracticaHN",
            "LetraM",
            [1, 1, 0, 0, 0, 0],
            [rele, rele3, rele6, releVenti],
            [rele, rele3, rele6, releVenti],
        )
        reproducir_y_revisar_audio(
            "PracticaHN",
            "LetraMescritura",
            [1, 1, 0, 1, 0, 0],
            [rele, rele3, rele7],
            [rele, rele3, rele7],
        )
        reproducir_y_revisar_audio(
            "PracticaHN",
            "LetraN",
            [1, 1, 0, 1, 1, 0],
            [rele, rele3, rele5, rele6],
            [rele, rele3, rele5, rele6],
        )
        reproducir_y_revisar_audio(
            "PracticaHN",
            "LetraNescritura",
            [1, 1, 1, 1, 0, 0],
            [rele, rele3, rele4, rele7],
            [rele, rele3, rele4, rele7],
        )
        reproducir_audio("Inicio", "AudioRepetir")        
        

def manejar_boton31(pin):
    try:        
        if pin.value() == 0:
            sincronizar_tiempo()                    
            tiempo_actual = ajustar_zona_horaria(-5)            
            fecha_actual = f"{tiempo_actual[0]:04d}-{tiempo_actual[1]:02d}-{tiempo_actual[2]:02d}"  # Año-Mes-Día
            hora_actual = f"{tiempo_actual[3]:02d}:{tiempo_actual[4]:02d}:{tiempo_actual[5]:02d}"  # Hora:Minuto:Segundo

            pitido()
            reproducir_audio("evaluacionHN", "evaluacionHN")
            reproducir_audio("Inicio", "recomentadionevaluacio")
            reproducir_audio("Inicio", "indicacionesevaluacion")            
            hn_data = generar_hn_data(fecha_actual, hora_actual)
            enviar_datos(hn_data,'hn')

    except Exception as e:
        reproducir_audio("Inicio", "error")
    

def generar_hn_data(fecha, hora):
    hn_data = {
        "hn_idestado": 2,
        "hn_fecha_inicio": fecha,
        "hn_hora_inicio": hora,
        "hn_unol": False,
        "hn_dosl": False,
        "hn_tresl": False,
        "hn_cuatrol": False,
        "hn_cincol": False,
        "hn_seisl": False,
        "hn_sietel": False,
        "hn_unos": False,
        "hn_doss": False,
        "hn_tress": False,
        "hn_cuatros": False,
        "hn_cincos": False,
        "hn_seiss": False,
        "hn_sietes": False,
        "hn_fecha_fin": "2024-08-27",
        "hn_hora_fin": "15:00:00"
    }

    try:
        # Reproducir y revisar audio para la evaluación y escritura
        hn_data["hn_unol"] = reproducir_y_revisar_audio_evaluacion("evaluacionHN", "letraHlectura", [0, 1, 1, 1, 0, 0],  [rele3, rele4, rele5],[rele3, rele4, rele5],)
        hn_data["hn_dosl"] = reproducir_y_revisar_audio_evaluacion("evaluacionHN", "letraIlectura", [1, 0, 1, 0, 0, 0], [rele, rele5, releVenti], [rele, rele5, releVenti])
        hn_data["hn_tresl"] = reproducir_y_revisar_audio_evaluacion("evaluacionHN", "letraJlectura",  [1, 0, 1, 1, 0, 0], [rele, rele4, rele5], [rele, rele4, rele5])
        hn_data["hn_cuatrol"] = reproducir_y_revisar_audio_evaluacion("evaluacionHN", "letraKlectura", [0, 1, 0, 0, 1, 0], [rele3, rele7, releVenti], [rele3, rele7, releVenti])
        hn_data["hn_cincol"] = reproducir_y_revisar_audio_evaluacion("evaluacionHN", "letraLlectura",  [0, 1, 1, 0, 1, 0], [rele3, rele5, rele7], [rele3, rele5, rele7])
        hn_data["hn_seisl"] = reproducir_y_revisar_audio_evaluacion("evaluacionHN", "letraMlectura", [1, 1, 0, 0, 1, 0], [rele, rele3, rele7], [rele, rele3, rele7])
        hn_data["hn_sietel"] = reproducir_y_revisar_audio_evaluacion("evaluacionHN", "letraNlectura", [1, 1, 0, 1, 1, 0], [rele, rele3, rele4, rele7], [rele, rele3, rele4, rele7])
        
        hn_data["hn_unos"] = reproducir_y_revisar_audio_evaluacion("evaluacionHN", "letraHescritura", [1, 0, 1, 1, 0, 0], [rele, rele4, rele5], [rele, rele4, rele5])
        hn_data["hn_doss"] = reproducir_y_revisar_audio_evaluacion("evaluacionHN", "letraIescritura",  [0, 1, 0, 1, 0, 0], [rele3, rele4], [rele3, rele4])
        hn_data["hn_tress"] = reproducir_y_revisar_audio_evaluacion("evaluacionHN", "letraJescritura", [0, 1, 1, 1, 0, 0], [rele3, rele4, rele5], [rele3, rele4, rele5])
        hn_data["hn_cuatros"] = reproducir_y_revisar_audio_evaluacion("evaluacionHN", "letraKescritura", [1, 0, 0, 0, 0, 1], [rele, rele6], [rele, rele6])
        hn_data["hn_cincos"] = reproducir_y_revisar_audio_evaluacion("evaluacionHN", "letraLescritura", [1, 0, 0, 1, 0, 1], [rele, rele4, rele6], [rele, rele4, rele6])
        hn_data["hn_seiss"] = reproducir_y_revisar_audio_evaluacion("evaluacionHN", "letraMescritura", [1, 1, 0, 0, 0, 1], [rele, rele3, rele6, releVenti], [rele, rele3, rele6, releVenti])
        hn_data["hn_sietes"] = reproducir_y_revisar_audio_evaluacion("evaluacionHN", "letraNescritura", [1, 1, 1, 0, 0, 1], [rele, rele3, rele5, rele6], [rele, rele3, rele5, rele6])
        
    except Exception as e:
        reproducir_audio("Inicio", "error")
    return hn_data




def manejar_boton4(pin):    
    if pin.value() == 0:        
        pitido()
        reproducir_audio("Inicio", "espejo")
        reproducir_audio("PracticaNT", "CursoNaT")
        reproducir_audio("Inicio", "Recomendacion")        
        reproducir_audio("PracticaNT", "LetraN")
        desconectar_wifi()
        rele.off()
        rele3.off()
        rele4.off()
        rele5.off()
        rele7.off()
        time.sleep(10)
        rele.on()
        rele3.on()
        rele4.on()
        rele5.on()
        rele7.on()
        conectar_wifi(SSID, PASSWORD)
        reproducir_audio("Inicio", "Paracadaletracorto")
        valores_esperados = [1, 1, 1, 1, 0, 1]
        resultadoN = procesar_botones(valores_esperados)

        while not resultadoN:           
            reproducir_audio("Inicio", "AudioIntentos")  # Cambiar audio si es necesario
            desconectar_wifi()
            rele.off()
            rele3.off()
            rele4.off()
            rele5.off()
            rele7.off()
            time.sleep(5)
            rele.on()
            rele3.on()
            rele4.on()
            rele5.on()
            rele7.on()
            conectar_wifi(SSID, PASSWORD)
            resultadoN = procesar_botones(valores_esperados)
        
        reproducir_audio("PracticaNT", "LetraNescritura")
        desconectar_wifi()        
        rele.off()
        rele3.off()
        rele4.off()
        rele5.off()
        rele6.off()
        time.sleep(10)
        rele.on()
        rele3.on()
        rele4.on()
        rele5.on()
        rele6.on()        
        conectar_wifi(SSID, PASSWORD)
        reproducir_audio("Inicio", "Paracadaletracorto")
        valores_esperados = [1, 1, 1, 1, 1, 0]
        resultadoNe = procesar_botones(valores_esperados)

        while not resultadoNe:          
            reproducir_audio("Inicio", "Paracadaletracorto")
            desconectar_wifi()            
            rele.off()
            rele3.off()
            rele4.off()
            rele5.off()
            rele6.off()
            time.sleep(5)
            rele.on()
            rele3.on()
            rele4.on()
            rele5.on()
            rele6.on()
            conectar_wifi(SSID, PASSWORD)
            resultadoNe = procesar_botones(valores_esperados)
        
        reproducir_y_revisar_audio(
            "PracticaNT",
            "LetraO",
            [0, 1, 0, 1, 1, 0],
            [rele, rele5, rele6, releVenti],
            [rele, rele5, rele6, releVenti],
        )
        reproducir_y_revisar_audio(
            "PracticaNT",
            "LetraOescritura",
            [1, 0, 1, 0, 0, 1],
            [rele3, rele4, rele7],
            [rele3, rele4, rele7],
        )
        reproducir_y_revisar_audio(
            "PracticaNT",
            "LetraP",
            [1, 1, 1, 0, 1, 0],
            [rele, rele3, rele4, rele6],
            [rele, rele3, rele4, rele6],
        )
        reproducir_y_revisar_audio(
            "PracticaNT",
            "LetraPescritura",
            [1, 1, 0, 1, 0, 1],
            [rele, rele3, rele5, rele7],
            [rele, rele3, rele5, rele7],
        )
        
        reproducir_audio("PracticaNT", "LetraQ")
        desconectar_wifi()
        rele.off()
        rele3.off()
        rele4.off()
        rele5.off()
        rele6.off()
        time.sleep(10)
        rele.on()
        rele3.on()
        rele4.on()
        rele5.on()
        rele6.on()
        conectar_wifi(SSID, PASSWORD)
        reproducir_audio("Inicio", "Paracadaletracorto")
        valores_esperados = [1, 1, 1, 1, 1, 0]
        resultadoQ = procesar_botones(valores_esperados)

        while not resultadoQ:          
            reproducir_audio("Inicio", "AudioIntentos")  # Cambiar audio si es necesario
            desconectar_wifi()
            rele.off()
            rele3.off()
            rele4.off()
            rele5.off()
            rele6.off()
            time.sleep(5)
            rele.on()
            rele4.on()
            rele5.on()
            rele6.on()
            conectar_wifi(SSID, PASSWORD)
            resultadoQ = procesar_botones(valores_esperados)        
        reproducir_audio("PracticaNT", "LetraQescritura")
        desconectar_wifi()        
        rele.off()
        rele3.off()
        rele4.off()
        rele5.off()
        rele7.off()
        time.sleep(10)
        rele.on()
        rele3.on()
        rele4.on()
        rele5.on()
        rele7.on()       
        conectar_wifi(SSID, PASSWORD)
        reproducir_audio("Inicio", "Paracadaletracorto")
        valores_esperados = [1, 1, 1, 1, 0, 1]
        resultadoQe = procesar_botones(valores_esperados)

        while not resultadoQe:            
            reproducir_audio("Inicio", "Paracadaletracorto")
            desconectar_wifi()            
            rele.off()
            rele3.off()
            rele4.off()
            rele5.off()
            rele7.off()
            time.sleep(5)
            rele.on()
            rele3.on()
            rele4.on()
            rele5.on()
            rele7.on()            
            conectar_wifi(SSID, PASSWORD)
            resultadoQe = procesar_botones(valores_esperados)
                    
        
        reproducir_y_revisar_audio(
            "PracticaNT",
            "LetraR",
            [0, 1, 1, 1, 1, 0],
            [rele, rele4, rele5, rele6],
            [rele, rele4, rele5, rele6],
        )
        reproducir_y_revisar_audio(
            "PracticaNT",
            "LetraRescritura",
            [1, 0, 1, 1, 0, 1],
            [rele3, rele4, rele5, rele7],
            [rele3, rele4, rele5, rele7],
        )
        reproducir_y_revisar_audio(
            "PracticaNT",
            "LetraS",
            [1, 0, 1, 0, 1, 0],
            [rele3, rele4, rele6],
            [rele3, rele4, rele6],
        )
        reproducir_y_revisar_audio(
            "PracticaNT",
            "LetraSescritura",
            [0, 1, 0, 1, 0, 1],
            [rele, rele5, rele7],
            [rele, rele5, rele7],
        )
        reproducir_y_revisar_audio(
            "PracticaNT",
            "LetraT",
            [1, 0, 1, 1, 1, 0],
            [rele3, rele4, rele5, rele6],
            [rele3, rele4, rele5, rele6],
        )
        reproducir_y_revisar_audio(
            "PracticaNT",
            "LetraTescritura",
            [0, 1, 1, 1, 0, 1],
            [rele, rele3, rele5, rele7],
            [rele, rele3, rele5, rele7],
        )
        reproducir_audio("Inicio", "AudioRepetir")
        

def manejar_boton41(pin):
    try:
        
        if pin.value() == 0:
            sincronizar_tiempo()                    
            tiempo_actual = ajustar_zona_horaria(-5)            
            fecha_actual = f"{tiempo_actual[0]:04d}-{tiempo_actual[1]:02d}-{tiempo_actual[2]:02d}"  # Año-Mes-Día
            hora_actual = f"{tiempo_actual[3]:02d}:{tiempo_actual[4]:02d}:{tiempo_actual[5]:02d}"  # Hora:Minuto:Segundo
            pitido()
            reproducir_audio("evaluacionNT", "evaluacionNT")
            reproducir_audio("Inicio", "recomentadionevaluacio")
            reproducir_audio("Inicio", "indicacionesevaluacion")            

            nt_data = generar_nt_data(fecha_actual, hora_actual)
            enviar_datos(nt_data, 'nt')

    except Exception as e:
        reproducir_audio("Inicio", "error")
    

def generar_nt_data(fecha, hora):
    nt_data = {
        "nt_idestado": 2,
        "nt_fecha_inicio": fecha,
        "nt_hora_inicio": hora,
        "nt_unol": False,
        "nt_dosl": False,
        "nt_tresl": False,
        "nt_cuatrol": False,
        "nt_cincol": False,
        "nt_seisl": False,
        "nt_sietel": False,
        "nt_unos": False,
        "nt_doss": False,
        "nt_tress": False,
        "nt_cuatros": False,
        "nt_cincos": False,
        "nt_seiss": False,
        "nt_sietes": False,
        "nt_fecha_fin": "2024-08-27",
        "nt_hora_fin": "15:00:00"
    }
    
    try:
        reproducir_audio("evaluacionNT", "letraNlectura")
        desconectar_wifi()
        rele.off()
        rele3.off()
        rele4.off()
        rele5.off()
        rele6.off()
        time.sleep(5)
        rele.on()
        rele3.on()
        rele4.on()
        rele5.on()
        rele6.on()
        conectar_wifi(SSID, PASSWORD)    
        valores_esperados = [1, 1, 1, 1, 0, 1]
        nt_data["nt_unol"] = procesar_botones_evaluacion(valores_esperados)
        nt_data["nt_dosl"] = reproducir_y_revisar_audio_evaluacion("evaluacionNT", "letraOlectura", [0, 1, 0, 1, 1, 0], [rele3, rele4, rele7], [rele3, rele4, rele7])
        nt_data["nt_tresl"] = reproducir_y_revisar_audio_evaluacion("evaluacionNT", "letraPlectura",  [1, 1, 1, 0, 1, 0], [rele, rele3, rele5, rele7], [rele, rele3, rele5, rele7])
        reproducir_audio("evaluacionNT", "letraQlectura")
        desconectar_wifi()
        rele.off()
        rele3.off()
        rele4.off()
        rele5.off()
        rele7.off()
        time.sleep(5)
        rele.on()
        rele3.on()
        rele4.on()
        rele5.on()
        rele7.on()
        conectar_wifi(SSID, PASSWORD)    
        valores_esperados = [1, 1, 1, 1, 1, 0]
        nt_data["nt_cuatrol"] = procesar_botones_evaluacion(valores_esperados)    
        nt_data["nt_cincol"] = reproducir_y_revisar_audio_evaluacion("evaluacionNT", "letraRlectura",  [0, 1, 1, 1, 1, 0], [rele3, rele4, rele5, rele7], [rele3, rele4, rele5, rele7])
        nt_data["nt_seisl"] = reproducir_y_revisar_audio_evaluacion("evaluacionNT", "letraSlectura", [1, 0, 1, 0, 1, 0], [rele, rele5, rele7], [rele, rele5, rele7])
        nt_data["nt_sietel"] = reproducir_y_revisar_audio_evaluacion("evaluacionNT", "letraTlectura", [1, 0, 1, 1, 1, 0], [rele, rele4, rele5, rele7], [rele, rele4, rele5, rele7])
        
        reproducir_audio("evaluacionNT", "letraNescritura")
        desconectar_wifi()        
        rele.off()
        rele3.off()
        rele4.off()
        rele5.off()
        rele7.off()
        time.sleep(5)
        rele.on()
        rele3.on()
        rele4.on()
        rele5.on()
        rele7.on()        
        conectar_wifi(SSID, PASSWORD)        
        valores_esperados = [1, 1, 1, 1, 1, 0]    
        nt_data["nt_unos"] = procesar_botones_evaluacion(valores_esperados)
        nt_data["nt_doss"] = reproducir_y_revisar_audio_evaluacion("evaluacionNT", "letraOescritura",  [1, 0, 1, 0, 0, 1], [rele, rele5, rele6, releVenti], [rele, rele5, rele6, releVenti])
        nt_data["nt_tress"] = reproducir_y_revisar_audio_evaluacion("evaluacionNT", "letraPescritura",  [1, 1, 0, 1, 0, 1], [rele, rele3, rele4, rele6], [rele, rele3, rele4, rele6])
        reproducir_audio("evaluacionNT", "letraQescritura")
        desconectar_wifi()
        rele.off()
        rele3.off()
        rele4.off()
        rele5.off()
        rele6.off()
        time.sleep(5)
        rele.on()
        rele3.on()
        rele4.on()
        rele5.on()
        rele6.on()
        conectar_wifi(SSID, PASSWORD)    
        valores_esperados = [1, 1, 1, 1, 0, 1]
        nt_data["nt_cuatros"] = procesar_botones_evaluacion(valores_esperados)
        nt_data["nt_cincos"] = reproducir_y_revisar_audio_evaluacion("evaluacionNT", "letraRescritura", [1, 0, 1, 1, 0, 1], [rele, rele4, rele5, rele6], [rele, rele4, rele5, rele6])
        nt_data["nt_seiss"] = reproducir_y_revisar_audio_evaluacion("evaluacionNT", "letraSescritura", [0, 1, 0, 1, 0, 1], [rele3, rele4, rele6], [rele3, rele4, rele6])
        nt_data["nt_sietes"] = reproducir_y_revisar_audio_evaluacion("evaluacionNT", "letraTescritura", [0, 1, 1, 1, 0, 1], [rele, rele4, rele5, rele6], [rele, rele4, rele5, rele6])
    
    except Exception as e:
        reproducir_audio("Inicio", "error")
    return nt_data
        


def manejar_boton5(pin):
    
    if pin.value() == 0:       
        pitido()
        reproducir_audio("Inicio", "espejo")
        reproducir_audio("PracticaUZ", "CursoUaZ")
        reproducir_audio("Inicio", "Recomendacion")
        reproducir_y_revisar_audio(
            "PracticaUZ",
            "LetraU",
            [0, 1, 0, 0, 1, 1],
            [rele, rele6, rele7],
            [rele, rele6, rele7],
        )
        reproducir_y_revisar_audio(
            "PracticaUZ",
            "LetraUescritura",
            [1, 0, 0, 0, 1, 1],
            [rele3, rele6, rele7],
            [rele3, rele6, rele7],
        )
        reproducir_y_revisar_audio(
            "PracticaUZ",
            "LetraV",
            [0, 1, 1, 0, 1, 1],
            [rele, rele4, rele6, rele7],
            [rele, rele4, rele6, rele7],
        )
        reproducir_y_revisar_audio(
            "PracticaUZ",
            "LetraVescritura",
            [1, 0, 0, 1, 1, 1],
            [rele3, rele5, rele6, rele7],
            [rele3, rele5, rele6, rele7],
        )
        reproducir_y_revisar_audio(
            "PracticaUZ",
            "LetraW",
            [1, 0, 1, 1, 0, 1],
            [rele3, rele4, rele5, rele7],
            [rele3, rele4, rele5, rele7],
        )
        reproducir_y_revisar_audio(
            "PracticaUZ",
            "LetraWescritura",
            [0, 1, 1, 1, 1, 0],
            [rele, rele4, rele5, rele6],
            [rele, rele4, rele5, rele6],
        )
        reproducir_y_revisar_audio(
            "PracticaUZ",
            "LetraX",
            [1, 1, 0, 0, 1, 1],
            [rele, rele3, rele6, rele7],
            [rele, rele3, rele6, rele7],
        )
        reproducir_y_revisar_audio(
            "PracticaUZ",
            "LetraXescritura",
            [1, 1, 0, 0, 1, 1],
            [rele, rele3, rele6, rele7],
            [rele, rele3, rele6, rele7],
        )
        releVenti.off()
        time.sleep(7)
        releVenti.on()
                
        reproducir_audio("PracticaUZ", "LetraY")
        desconectar_wifi()
        rele.off()
        rele3.off()        
        rele5.off()
        rele6.off()
        rele7.off()
        time.sleep(10)
        rele.on()
        rele3.on()        
        rele5.on()
        rele6.on()
        rele7.on()
        conectar_wifi(SSID, PASSWORD)
        reproducir_audio("Inicio", "Paracadaletracorto")
        valores_esperados = [1, 1, 0, 1, 1, 1]
        resultadoY = procesar_botones(valores_esperados)

        while not resultadoY:       
            reproducir_audio("Inicio", "AudioIntentos")  # Cambiar audio si es necesario
            desconectar_wifi()
            rele.off()
            rele3.off()        
            rele5.off()
            rele6.off()
            rele7.off()
            time.sleep(5)
            rele.on()
            rele3.on()        
            rele5.on()
            rele6.on()
            rele7.on()
            conectar_wifi(SSID, PASSWORD)
            resultadoY = procesar_botones(valores_esperados)        
        reproducir_audio("PracticaUZ", "LetraYescritura")
        desconectar_wifi()        
        rele.off()
        rele3.off()
        rele4.off()
        rele6.off()
        rele7.off()
        time.sleep(10)
        rele.on()
        rele3.on()
        rele4.on()
        rele6.on()
        rele7.on()        
        conectar_wifi(SSID, PASSWORD)
        reproducir_audio("Inicio", "Paracadaletracorto")
        valores_esperados = [1, 1, 1, 0, 1, 1]
        resultadoYe = procesar_botones(valores_esperados)

        while not resultadoYe:            
            reproducir_audio("Inicio", "Paracadaletracorto")
            desconectar_wifi()            
            rele.off()
            rele3.off()
            rele4.off()
            rele6.off()
            rele7.off()
            time.sleep(5)
            rele.on()
            rele3.on()
            rele4.on()
            rele6.on()
            rele7.on()            
            conectar_wifi(SSID, PASSWORD)
            resultadoYe = procesar_botones(valores_esperados)
        
        reproducir_y_revisar_audio(
            "PracticaUZ",
            "LetraZ",
            [0, 1, 0, 1, 1, 1],
            [rele, rele5, rele6, rele7],
            [rele, rele5, rele6, rele7],
        )
        reproducir_y_revisar_audio(
            "PracticaUZ",
            "LetraZescritura",
            [1, 0, 1, 0, 1, 1],
            [rele3, rele4, rele6, rele7],
            [rele3, rele4, rele6, rele7],
        )
        reproducir_audio("Inicio", "AudioRepetir")        

def manejar_boton51(pin):
    try:
        
        if pin.value() == 0:
            sincronizar_tiempo()                    
            tiempo_actual = ajustar_zona_horaria(-5)            
            fecha_actual = f"{tiempo_actual[0]:04d}-{tiempo_actual[1]:02d}-{tiempo_actual[2]:02d}"  # Año-Mes-Día
            hora_actual = f"{tiempo_actual[3]:02d}:{tiempo_actual[4]:02d}:{tiempo_actual[5]:02d}"  # Hora:Minuto:Segundo
            pitido()
            reproducir_audio("evaluacionUZ", "evaluacionUZ")
            reproducir_audio("Inicio", "recomeuzadionevaluacio")
            reproducir_audio("Inicio", "indicacionesevaluacion")            

            uz_data = generar_uz_data(fecha_actual, hora_actual)
            enviar_datos(uz_data, 'uz')

    except Exception as e:
        reproducir_audio("Inicio", "error")
    

def generar_uz_data(fecha, hora):
    uz_data = {
        "uz_idestado": 2,
        "uz_fecha_inicio": fecha,
        "uz_hora_inicio": hora,
        "uz_unol": False,
        "uz_dosl": False,
        "uz_tresl": False,
        "uz_cuatrol": False,
        "uz_cincol": False,
        "uz_seisl": False,        
        "uz_unos": False,
        "uz_doss": False,
        "uz_tress": False,
        "uz_cuatros": False,
        "uz_cincos": False,
        "uz_seiss": False,        
        "uz_fecha_fin": "2024-08-27",
        "uz_hora_fin": "15:00:00"
    }
    try:
        # Reproducir y revisar audio para la evaluación y escritura
        uz_data["uz_unol"] = reproducir_y_revisar_audio_evaluacion("evaluacionUZ", "letraUlectura", [0, 1, 0, 0, 1, 1],  [rele3, rele6, rele7],[rele3, rele6, rele7],)
        uz_data["uz_dosl"] = reproducir_y_revisar_audio_evaluacion("evaluacionUZ", "letraVlectura",  [0, 1, 1, 0, 1, 1], [rele3, rele5, rele6, rele7], [rele3, rele5, rele6, rele7])
        uz_data["uz_tresl"] = reproducir_y_revisar_audio_evaluacion("evaluacionUZ", "letraWlectura", [1, 0, 1, 1, 0, 1], [rele, rele4, rele5, rele6], [rele, rele4, rele5, rele6])
        uz_data["uz_cuatrol"] = reproducir_y_revisar_audio_evaluacion("evaluacionUZ", "letraXlectura", [1, 1, 0, 0, 1, 1], [rele, rele3, rele6, rele7], [rele, rele3, rele6, rele7])
        reproducir_audio("evaluacionUZ", "letraYlectura")
        desconectar_wifi()
        rele.off()
        rele3.off()        
        rele4.off()
        rele6.off()
        rele7.off()
        time.sleep(5)
        rele.on()
        rele3.on()        
        rele4.on()
        rele6.on()
        rele7.on()
        conectar_wifi(SSID, PASSWORD)    
        valores_esperados = [1, 1, 0, 1, 1, 1]
        uz_data["uz_cincol"] = procesar_botones_evaluacion(valores_esperados)     
        uz_data["uz_seisl"] = reproducir_y_revisar_audio_evaluacion("evaluacionUZ", "letraZlectura", [0, 1, 0, 1, 1, 1], [rele3, rele4, rele6, rele7], [rele3, rele4, rele6, rele7])        
        
        uz_data["uz_unos"] = reproducir_y_revisar_audio_evaluacion("evaluacionUZ", "letraUescritura", [1, 0, 0, 0, 1, 1], [rele, rele6, rele7], [rele, rele6, rele7])
        uz_data["uz_doss"] = reproducir_y_revisar_audio_evaluacion("evaluacionUZ", "letraVescritura",  [1, 0, 0, 1, 1, 1], [rele, rele4, rele6, rele7], [rele, rele4, rele6, rele7])
        uz_data["uz_tress"] = reproducir_y_revisar_audio_evaluacion("evaluacionUZ", "letraWescritura", [0, 1, 1, 1, 1, 0], [rele3, rele4, rele5, rele7], [rele3, rele4, rele5, rele7])
        uz_data["uz_cuatros"] = reproducir_y_revisar_audio_evaluacion("evaluacionUZ", "letraXescritura", [1, 1, 0, 0, 1, 1],  [rele, rele3, rele6, rele7],  [rele, rele3, rele6, rele7])
        reproducir_audio("evaluacionUZ", "letraYescritura")
        desconectar_wifi()        
        rele.off()
        rele3.off()
        rele5.off()
        rele6.off()
        rele7.off()
        time.sleep(5)
        rele.on()
        rele3.on()
        rele5.on()
        rele6.on()
        rele7.on()        
        conectar_wifi(SSID, PASSWORD)    
        valores_esperados = [1, 1, 1, 0, 1, 1]
        uz_data["uz_cincos"] = procesar_botones_evaluacion(valores_esperados)     
        uz_data["uz_seiss"] = reproducir_y_revisar_audio_evaluacion("evaluacionUZ", "letraZescritura", [1, 0, 1, 0, 1, 1], [rele, rele5, rele6, rele7], [rele, rele5, rele6, rele7])    
    
    except Exception as e:
        reproducir_audio("Inicio", "error")
    return uz_data

        


def reset_estado_botones():
    for key in estado_botones:
        estado_botones[key] = False    


# Configurar las interrupciones para los botones
boton13.irq(trigger=Pin.IRQ_FALLING, handler=manejar_boton1)
boton34.irq(trigger=Pin.IRQ_FALLING, handler=manejar_boton2)
boton21.irq(trigger=Pin.IRQ_FALLING, handler=manejar_boton3)
boton1.irq(trigger=Pin.IRQ_FALLING, handler=manejar_boton4)
boton36.irq(trigger=Pin.IRQ_FALLING, handler=manejar_boton5)
boton35.irq(trigger=Pin.IRQ_FALLING, handler=manejar_boton21)
boton19.irq(trigger=Pin.IRQ_FALLING, handler=manejar_boton31)
boton3.irq(trigger=Pin.IRQ_FALLING, handler=manejar_boton41)
boton39.irq(trigger=Pin.IRQ_FALLING, handler=manejar_boton51)



while True:
    time.sleep(1)
