# TP-Radio-Streaming

Radio Streaming (Sistemas Distribuidos I)

## Ejecutar

- Dependencias: [_ZeroMQ_](http://zeromq.org/) (en particular el _binding_ para [_Python_](https://pyzmq.readthedocs.io/en/latest/))

#### Backend

Se corren todas la antenas que figuran en el archivo de configuración, como así también los _routers_.

```bash
 $ ./run-backend.py [--config=FILE]

	FILE: en formato JSON
```

Si se quiere lanzar una antena en particular:

```bash
 $ ./run-antenna.py --country=ISO-PAIS --aid=ANTENNA-ID
```

#### Estaciones

- Transmisión:
```bash
 $ python3 src/nodes/sender.py --freq=FREQ-CODE --input=WAV --config=FILE

	- FREQ-CODE: en el formato <ISO-PAIS>-<FREQ>
	- WAV: música a reproducir en formato .wav
	- FILE: en el formato JSON
```

- Recepción:

```bash
 $ python3 src/nodes/receiver.py --freq=FREQ-CODE --country=CODE --config=FILE

	- FREQ-CODE: en el formato <ISO-PAIS>-<FREQ>
	- CODE: el ISO del país donde se va a conectar
	- FILE: en el formato JSON
```

## Terminar

Para finalizar la ejecución de todas las antenas y los routers  se debe realizar lo siguiente:

```bash
 $ ./stop-backend.py
```

Para finalizar la ejecución de una sóla antena:

```bash
 $ ./stop-antenna.py --country=ISO-PAIS --aid=ANTENNA-ID
```

Para finalizar la ejecución de alguna de las estaciones (_transmisora_ o _receptora_), teclear **Ctrl-C**.