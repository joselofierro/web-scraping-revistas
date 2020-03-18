import argparse
import logging
logging.basicConfig(level=logging.INFO)
from urllib.parse import urlparse
import hashlib
import pandas as pd

"""modulo nltk"""
import nltk
from nltk.corpus import stopwords
#nltk.download('punkt')
#nltk.download('stopwords')

logger = logging.getLogger(__name__)
stop_words = set(stopwords.words('spanish'))

# abstraccion del limpiado del dataframe(automatizacion
def main(filename):
	logger.info('Starting cleaning process')

	# vamos a leer los datos csv y crear un dataframe
	df = _read_data(filename)
	newspaper_uid = _extract_newspaper_uid(filename)
	df = _add_newspaper_uid_co(df, newspaper_uid)
	df = _extract_host(df)
	df =_generate_uids_for_rows(df)
	df = _tokenize_row(df, 'title')
	df = _tokenize_row(df, 'body')
	df = _drop_rows_missing_values(df)
	_save_data(df, filename)

	return df


def _read_data(filename):
	logger.info('Reading file {}'.format(filename))
	return pd.read_csv(filename)

def _extract_newspaper_uid(filename):
	logger.info('Extracting newspaper uid')

	#obtenemos el primer nombre del archivo
	newspaper_uid = filename.split('_')[0]
	logger.info('newspaper uid detected {}'.format(newspaper_uid))

	return newspaper_uid


# creacion de la columna de manera **abstracta**
def _add_newspaper_uid_co(df, newspaper_uid):
	logger.info('Agregando columna newspaper_uid with {}'.format(newspaper_uid))

	df['newspaper_uid'] = newspaper_uid

	return df


def _extract_host(df):
	logger.info('extract host from urls')

	df['host'] = df['url'].apply(lambda url: urlparse(url).netloc)

	return df

# genera un uids en formato md5 unico para cada noticia
def _generate_uids_for_rows(df):

	logger.info('Generating uids for each row')
	uids = (df.apply(lambda row: hashlib.md5(bytes(row['url'].encode())), axis=1).
			apply(lambda hash_object: hash_object.hexdigest())
		)

	# se lo asigna a una nueva columna
	df['uid'] = uids

	# establece la nueva columna como indice 
	return df.set_index('uid')

def _tokenize_row(df, column_name):
	global stop_words
	#funcion que elimina stopwords del title y body
	token_column = (
            df.apply(lambda row: nltk.word_tokenize(row[column_name]), axis=1)
              .apply(lambda tokens : list(filter(lambda token: token.isalpha(), tokens)))
              .apply(lambda tokens: list(map(lambda token: token.lower(), tokens)))
              .apply(lambda word_list: list(filter(lambda word: word not in stop_words, word_list)))
              .apply(lambda valid_word_list: len(valid_word_list))
	)

	logger.info('Token generated for {}'.format(column_name))

	df['n_tokens_{}'.format(column_name)] = token_column

	return df


def _drop_rows_missing_values(df):
	logger.info('eliminando rows donde no hay valores')
	return df.dropna()


def _save_data(df, filename):
	clean_filename = 'clean_{}'.format(filename)
	logger.info('save data at location: {}'.format(clean_filename))
	df.to_csv(clean_filename, encoding='utf-8-sig')

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('filename',
						help='The path to the dirty data',
						type=str)

	args = parser.parse_args()
	df = main(args.filename)

	print(df)