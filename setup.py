try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'Aggiunti a pacchetto data anche candlestick e table, contenenti le classi per i relativi plot',  #singola linea descrivente il pacchetto. Per averla più lunga usare long_description
    'author': 'Valerio Bitetta', #The name of the package author
    'author_email': 'vabite@gmail.com', # 	The email address of the package author
    'version': '0.3', #The version number of the package
    'install_requires': ['nose'],
    'packages': ['data', 'candlestick', 'table', 'scatter', 'histogram', 'line'], #A list of Python packages that distutils will manipulate
    'scripts': [], #A list of standalone script files to be built and installed
    'name': 'charts' #The name of the package
}

setup(**config)
