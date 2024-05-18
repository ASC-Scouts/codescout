#!/usr/bin/env python3

"""
Ce module permet d'appeler la fonction codescout a l'aide d'une requete http
en faisant appel a la librairie flask pour offrir un API RESTful
"""

import argparse
import configparser
from flask import Flask, send_file, request
from codescout import codescout

# Configuration par defaut
config = configparser.ConfigParser()
config_file = 'codescout.ini'

# Indique si on est en mode debug
debug = False

# Serveur http
app = Flask(__name__)

@app.route('/codescout')
def http_codescout():
    """
    Permet d'appeler la fonction codescout a l'aide d'une requete http
    """
    # Lecture de la config par defaut la premiere fois
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
    # Affichage de la configuration
    if debug:
        print("Démarrage du serveur http")
        print("Configuration par défaut:")
        for s in config.sections():
            print(f"[{s}]")
            for k in config[s].keys():
                print(f"{k}={config[s][k]}")
            print("")
    # Appeler codecoutvotre script Python pour générer l'image
    img = codescout(
            config['usager']['message'],
            config['usager']['code'],
            delimiteur = config['usager']['delimiteur'],
            taille = int(config['usager']['taille']),
            interligne = int(config['usager']['interligne']),
            bordure = int(config['usager']['bordure']),
            legende = config['usager']['legende'],
            fonte = config['usager']['fonte'],
            decoder = (config['usager']['decoder'] == '1'))
    img.save(config['sortie']['image'])
    # Renvoyer l'image générée au client
    return send_file(config['sortie']['image'], mimetype='image/png')

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