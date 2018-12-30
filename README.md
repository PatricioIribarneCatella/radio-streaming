# TP-Radio-Streaming

Radio Streaming (Sistemas Distribuidos I)

## Ejecutar

- Dependencias: [_ZeroMQ_](http://zeromq.org/) (en particular el _binding_ para [_Python_](https://pyzmq.readthedocs.io/en/latest/))

Se debe generar el archivo de configuración mediante el siguiente comando:

```bash
 $ ./config-generator.py --antennas="[ISO_COUNTRY:NUM_NODES ...]" --routers=NUM_NODES
 							[--output=FILE(config.json)]
 			- FILE: nombre del archivo de configuración (con extensión .json)
```

#### Backend

Se corren todas la antenas que figuran en el archivo de configuración, como así también los _routers_.

```bash
 $ ./run-backend.py [--config=FILE(config.json)]

	- FILE: en formato JSON
```

- Si se quiere lanzar una _antena_ en particular:

```bash
 $ ./run-antenna.py --country=ISO-PAIS --aid=ANTENNA-ID [--config=FILE(config.json)]
 
 	- FILE: en formato JSON
```

- Si se quiere lanzar un _router_ en particular:

```bash
 $ ./run-router.py --rid=RUTER-ID [--config=FILE(config.json)]
 
 	- FILE: en formato JSON
```

#### Estaciones

- Transmisión:
```bash
 $ python3 src/nodes/sender.py --freq=FREQ-CODE --input=WAV [--config=FILE(config.json)]

	- FREQ-CODE: en el formato <ISO-PAIS>-<FREQ>
	- WAV: música a reproducir en formato .wav
	- FILE: en formato JSON
```

- Recepción:

```bash
 $ python3 src/nodes/receiver.py --freq=FREQ-CODE --country=CODE
 													[--config=FILE(config.json)]

	- FREQ-CODE: en el formato <ISO-PAIS>-<FREQ>
	- CODE: el ISO del país donde se va a conectar
	- FILE: en formato JSON
```

## Terminar

- Para finalizar la ejecución de todas las _antenas_ y los _routers_  se debe realizar lo siguiente:

```bash
 $ ./stop-backend.py
```

- Para finalizar la ejecución de una sóla _antena_:

```bash
 $ ./stop-antenna.py --country=ISO-PAIS --aid=ANTENNA-ID
```

- Para finalizar la ejecución de un _router_

```bash
 $ ./stop-router.py --rid=ROUTER-ID
```

- Para finalizar la ejecución de alguna de las estaciones (_transmisora_ o _receptora_), teclear **Ctrl-C**.