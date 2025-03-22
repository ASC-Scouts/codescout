
# A very simple Flask Hello World app for you to get started with...

import argparse
import configparser
from flask import Flask, send_file, request, render_template
from codescout import codescout

# Chemin absolu du fichier de configuration
config_file = '/home/scouts/codescout/codescout/codescout.ini'

# Chemin absolu des fichiers statiques
template_folder = '/var/www/templates'

# Création de l'objet dans lequel on lira la configuration
# En en faisant une variable globale on évite d'avoir à lire la config
# lors de chaque requête
config = configparser.ConfigParser()

# Démarrage de l'application flask
app = Flask(__name__, template_folder=template_folder)

# Appel de codescout via Flask
@app.route('/codescout')
def http_codescout():
    """
    Permet d'appeler la fonction codescout a l'aide d'une requete http
    """
    # Lecture de la config par defaut au démarrage
    if config.sections() == []:
        config.read(config_file)
        config['usager'] = {}
    # Lecture des parametres fournis par l'usager
    for k in config['defaut'].keys():
        param = request.args.get(k)
        if param:
            config['usager'][k] = param
        else:
            config['usager'][k] = config['defaut'][k]
    # Appeler codescout
    img = codescout(
            config['usager']['message'],
            config['usager']['code'],
            delimiteur = config['usager']['delimiteur'],
            taille = int(config['usager']['taille']),
            interligne = int(config['usager']['interligne']),
            bordure = int(config['usager']['bordure']),
            legende = config['usager']['legende'],
            fonte = config['usager']['fonte'],
            decoder = (config['usager']['decoder'] == '1'),
            decalage = int(config['usager']['decalage']),
            fontes = config['fontes'])
    img.save(config['sortie']['image'])
    # Renvoyer l'image générée au client
    return send_file(config['sortie']['image'], mimetype='image/png')

# Aide en ligne
@app.route('/')
def http_aide():
    return render_template('codescout.html')

# GUI
@app.route('/gui/')
def http_gui():
    return render_template('codescout_gui.html')

# Pour utilisation en mode ligne de commande avec le serveur de développement
def main():
    global config_file
    global debug

    parser = argparse.ArgumentParser(description='API RESTful pour codescout')
    parser.add_argument('--config', '-c', type=str, required=False,
        help='Nom du fichier de configuration')
    parser.add_argument('--debug', action='store_true', required=False, default=False,
        help="Indique si l'application est démarrée en mode de déboguage")
    args = parser.parse_args()

    debug = args.debug

    # On change le nom du fichier de config s'il est passe en parametre
    if args.config is not None:
        config_file = args.config

    # Lecture du fichier de configuration
    config.read(config_file)
    config['usager'] = {}

    app.run(debug=debug, host=config['serveur']['host'], port=int(config['serveur']['port']))

if __name__ == '__main__':
    main()