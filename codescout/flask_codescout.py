#!/usr/bin/env python3

"""
Ce module permet d'appeler la fonction codescout a l'aide d'une requete http
en faisant appel a la librairie flask pour offrir un API RESTful
"""

import argparse
from flask import Flask, send_file, request
from codescout import codescout

# Serveur http
app = Flask(__name__)

# Nom par defaut du fichier dans lequel l'image est produite par le serveur http
outfile_http = 'codescout.png'

@app.route('/codescout')
def http_codescout():
    """
    Permet d'appeler la fonction codescout a l'aide d'une requete http
    """
    # Parametres de la requete http
    params_str = {
        'code' : 'musical',
        'message' : 'ABCDEFGHIJKLM:NOPQRSTUVWXYZ',
        'delimiteur' : ':',
        'legende' : '',
        'fonte' : 'FreeMono.ttf'}
    params_int = {
        'taille' : 8,
        'interligne' : 1,
        'bordure' : 0}
    params_bool = {
        'decoder' : True}
    # Récupérer les arguments de la requête HTTP
    for k in params_str.keys():
        param = request.args.get(k)
        if param:
            params_str[k] = param
    for k in params_int.keys():
        param = request.args.get(k)
        if param:
            params_int[k] = int(param)
    for k in params_bool.keys():
        param = request.args.get(k)
        if param:
            params_bool[k] = request.args.get(k) == '1'
    # Appeler codecoutvotre script Python pour générer l'image
    img = codescout(
            params_str['message'],
            params_str['code'],
            delimiteur = params_str['delimiteur'],
            taille = params_int['taille'],
            interligne = params_int['interligne'],
            bordure = params_int['bordure'],
            legende = params_str['legende'],
            fonte = params_str['fonte'],
            decoder = params_bool['decoder'])
    img.save(outfile_http)
    # Renvoyer l'image générée au client
    return send_file(outfile_http, mimetype='image/png')

def main():
    parser = argparse.ArgumentParser(description='API RESTful pour codescout')
    parser.add_argument('--sortie', '-s', type=str, required=False, default="",
        help='Nom du fichier qui contiendra le message codé')
    parser.add_argument('--debug', action='store_true', required=False, default=False,
        help="Indique si l'application est démarrée en mode de déboguage")
    args = parser.parse_args()

    debug = args.debug
    
    if debug:
        print("Démarrage du serveur http")
    if args.sortie != '':
        outfile_http = args.sortie
    app.run(debug=debug)

if __name__ == '__main__':
    main()