import yaml

# variable global no se modifica 
__config = None


#funcion que carga la configuracion por primera vez
def config():
	# acceso a la variable global dentro de nuestra funcion
	global __config
	if not __config:
		with open('config.yaml', mode='r') as f:
			__config = yaml.safe_load(f)

	return __config