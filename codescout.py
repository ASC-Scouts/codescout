#!/usr/bin/env python3

# Cette librairie permet de créer une image au format png contenant un message codé
# avec differents codes scouts:
#
# Code soleil: Dans ce code, chaque lettre du message est représentée
# par un soleil et le nombre de rayon de ce soleil correspond à l'ordre de la
# lettre dans l'alphabet (de 1 à 26). Pour faciliter le décodage, les rayons
# correspondant à des voyelles sont plus longs
#
# Code musical: Dans ce code, chaque lettre du message est représentée
# par une note de musique. Le A devient une blanche sur le DO central, et on
# monte d'une note jusqu'au M qui est un LA. Ensuite on reprend au dos central
# pour la lettre M mais avec des noires. On monte encore une fois jusqu'au LA
# aigu pour Z.
#
# La fonction principale de cette librairie se nomme codescout. Elle
# prend deux parametres obligatoires et plusieurs parametres optionnels:
# - message [requis]:       message a encoder
# - code [requis]:          nom du code a utiliser pour encoder
# - taille [defaut=8]:      taille des elements du message en pixels
# - delimiteur [defaut=':'] caractere a utiliser dans le message pour indiquer
#                           a la fonction de decouper le message sur plusieurs
#                           lignes a l'aide de ce delimiteur
# - interligne [defaut=1]:  permet d'ajouter de l'espace entre les lignes du
#                           message afin par exemple de laisser de la place pour
#                           decoder
# - bordure [defaut=0]:     permet d'ajouter une bordure au message afin par
#                           exemple de faciliter son decoupage (le parametre
#                           correspond a la taille en pixels de la bordure
# - legende [defaut='']:    permet d'ajouter une legende en bas a gauche
#                           (par exemple une courte instruction, un numero...)
# - decoder [defaut=False]  indique si oui ou nom on doit afficher le message
#                           decode sous le code
# - fonte [default='FreeMono.ttf'] nom de la fonte a utiliser pour la legende
#                           et le texte decode
#
# Attention:
# 1) ne pas utiliser d'accents dans le texte a encoder
# 2) si le fichier de fonte n'est pas trouve, la fonte par defaut de la librairie
#    PIL sera utilisee, et elle est assez petite
#
# Exemple d'utilisation:
# >>> from codescout import codescout
# >>> image = codescout(message="La bonne humeur:est aussi contagieuse:que la rougeole",
#                       "soleil",taille=15,bordure=2,legende="2024-05-12",decoder=True)
# >>> image.save("code.png")
#
# Equivalent en version ligne de commande:
# ./codescout.py -m "La bonne humeur:est aussi contagieuse:que la rougeole"\
#                   -c soleil -t 15 -b 2 -l "2024-05-12" --decoder
#
# Tapez ./codescout.py -h pour obtenir de l'aide sur l'utilisation en mode
# ligne de commande.
#
# Copyright 2024, Vincent Fortin (vincent.fortin@gmail.com)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from PIL import Image, ImageDraw, ImageFont
import math
import argparse
import re

def creer_un_soleil(dessin, 
                    lettre, 
                    centre, 
                    rayon=10,
                    longueur_trait_voyelle=20,
                    longueur_trait_consonne=10):

    # Cette fonction ajoute un soleil dans l'image "dessin". Le soleil encode
    # la lettre "lettre" et est centré à la position "centre". Le rayon du
    # cercle utilisé pour dessiner le soleil est de "rayon" pixels.
    # Les rayons du soleil sont de longueur "longueur_voyelle" pour les
    # voyelles et "longueur_consonne" pour les consonnes.

    # On met la lettre en majuscule
    lettre = lettre.upper()

    # Si ce n'est pas une lettre on ne dessine rien
    if not lettre.isalpha():
        return

    # Le nombre de rayons dépend de la position de la lettre dans l'alphabet
    position_dans_alphabet = ord(lettre) - 65 + 1  # ASCII value of 'A' is 65
    num_rayons = position_dans_alphabet

    # On dessine d'abord le soleil
    dessin.ellipse((centre[0] - rayon, centre[1] - rayon,
                  centre[0] + rayon, centre[1] + rayon), outline="black")

    # On dessine ensuite chaque rayon
    for i in range(num_rayons):
        # Angle du rayon (zero a l'est)
        angle = i * (360 / 26) - 90
        # On utilise le code ASCII pour determiner si c'est une voyelle et la longueur du trait
        lettre = chr(65 + i)
        longueur_trait = longueur_trait_voyelle if lettre in 'AEIOUY' else longueur_trait_consonne
        # Position du debut du trait au bord du soleil
        x1 = centre[0] + rayon * math.cos(math.radians(angle))
        y1 = centre[1] + rayon * math.sin(math.radians(angle))
        # Position de la fin du trait
        x2 = centre[0] + (rayon + longueur_trait) * math.cos(math.radians(angle))
        y2 = centre[1] + (rayon + longueur_trait) * math.sin(math.radians(angle))
        # On dessine le trait
        dessin.line((x1, y1, x2, y2), fill="black", width=1)

def dessine_une_note(dessin,lettre,position,portee,rayon,bordure):
   # On met la lettre en majuscule
   lettre = lettre.upper()

   # Si ce n'est pas une lettre on ne dessine rien
   if not lettre.isalpha():
       return

   # On calcule la position de la note sur la portée
   i = ord(lettre) - 65 # 65 est le code ASCII de la lettre A
   y = 14*rayon - rayon*(i%13) + portee + bordure
   x = 3*rayon*position + bordure

   # On détermine la couleur (blanche ou noire de la note)
   # blanche pour A-M, noire pour N-Z
   fill = None if i <= 12 else 'black'

   # On dessine la note
   dessin.ellipse((x-rayon,y-rayon,x+rayon,y+rayon), outline='black', fill=fill)

   # Si la note est sous ou au-dessus de la portée on ajoute un trait
   if i in (0,12,13,25):
       dessin.line((x-2*rayon,y,x+2*rayon,y))

   # On ajoute la hampe de la note
   if (i%13) < 5:
       dessin.line((x+rayon,y,x+rayon,y-4*rayon))
   else:
       dessin.line((x-rayon,y,x-rayon,y+4*rayon))

# Fonction principale qui construit le code scout et retourne une image
def codescout(message,
              code,
              delimiteur = ':',
              taille = 8,
              interligne = 1,
              bordure = 0,
              legende = '',
              fonte = 'FreeMono.ttf',
              decoder = False):

    # Validation du nom du code
    code = code.upper()
    codes = ('SOLEIL','MUSICAL')
    if code not in codes:
        print(f'Codes reconnus: {codes}')
        raise ValueError(f"code {code} inconnu")

    # On ajuste l'interligne a 2 au minimum si on doit ajouter le message decode
    if decoder:
        interligne = max(2, interligne)

    # Si on veut ecrire du texte (options legende ou decoder) il faut creer la fonte
    # Si le fichier de fonte n'existe pas on utilise la fonte par defaut
    if decoder or legende != '':
        try:
            fonte = ImageFont.truetype(fonte, taille*4)
        except:
            fonte = ImageFont.load_default()

    # On sépare le message sur plusieurs lignes en utilisant le séparateur
    message_split = message.split(delimiteur)

    # Taille du message en nombre de caractères (considérant la ligne la plus longue)
    taille_message_x = len(max(message_split, key=len))
    taille_message_y = len(message_split)

    if code == 'SOLEIL':
        # Longueur des rayons pour les voyelles: 2 fois le rayon du soleil
        longueur_trait_voyelle = taille * 2
        # Longueur des rayons pour les consonnes: meme que le rayon du soleil
        longueur_trait_consonne = taille
        # Taille totale d'un soleil en pixel en incluant les rayons et de l'espace autour
        taille_soleil = taille + 2 * max(longueur_trait_consonne, longueur_trait_voyelle) + taille // 2
        taille_image = [taille_message_x * taille_soleil, taille_message_y * taille_soleil * interligne]
    elif code == 'MUSICAL':
        # Taille de l'image en pixel
        taille_portee = taille * 16 + taille * 4 * (interligne - 1)
        taille_image = [(taille_message_x+1)*taille*3, taille_message_y*taille_portee]

    # Ajout d'espace pour le cadre et la légende
    for i in range(2):
        taille_image[i] = taille_image[i] + bordure * 2
    if legende != '':
        taille_image[1] = taille_image[1] + taille * 4

    # Création d'une image avec la bonne taille
    image = Image.new("1", taille_image, "white")

    # Creation de l'object permettant de dessiner l'image
    dessin = ImageDraw.Draw(image)

    # Ajout d'un cadre
    for i in range(0,bordure):
        dessin.rectangle([i,i,taille_image[0]-i,taille_image[1]-i])

    # Ajout d'une legende en bas a droite
    if legende != '':
        dessin.text([bordure+taille*2,taille_image[1]-taille*6-1], legende, font=fonte)
    
    if code == 'MUSICAL':
        # On dessine les portées
        for i in range(taille_message_y):
            for j in range(4*taille,14*taille,2*taille):
                pos_y = j + i * taille_portee + bordure
                dessin.line([(bordure,pos_y),(taille_image[0]-bordure,pos_y)])

    # On encode le message ligne par ligne
    for i in range(taille_message_y):
        # Encodage de chaque lettre d'une ligne
        for j in range(len(message_split[i])):
            if code == 'SOLEIL':
                creer_un_soleil(dessin, 
                    message_split[i][j], 
                    ((j+0.5)*taille_soleil+bordure, (i*interligne+0.5)*taille_soleil+bordure),
                    taille,
                    longueur_trait_voyelle,
                    longueur_trait_consonne)
                if decoder:
                    dessin.text(((j+0.3)*taille_soleil+bordure, (i*interligne+1)*taille_soleil+bordure),
                                message_split[i][j], font=fonte)
            elif code == 'MUSICAL':
                # On calcule la position de la note sur la portée
                x = 3*taille*(j+0.75) + bordure
                dessine_une_note(dessin, message_split[i][j], j+1, i*taille_portee, taille, bordure)
                if decoder:
                    dessin.text((x,(i+0.75)*taille_portee),
                                 message_split[i][j], font=fonte, align='center')

    return image

if __name__ == '__main__':

    print("\n====================================================")
    print("Encodage d'un message à l'aide d'un code scout")
    print("Auteur: Goéland Astucieux (vincent.fortin@gmail.com)")
    print("Version du 12 mai 2024")
    print("====================================================\n")

    # Arguments du script
    parser = argparse.ArgumentParser(description='Encodeur en code scout')
    parser.add_argument('--message', '-m', type=str, required=True,
                        help='Message à encoder')
    parser.add_argument('--code', '-c', type=str, required=True,
                        help='Nom du code à utiliser (soleil ou musical)')
    parser.add_argument('--sortie', '-s', type=str, required=False, default="",
                        help='Nom du fichier qui contiendra le message codé')
    parser.add_argument('--delimiteur', '-d', type=str, required=False, default=':',
                        help='Délimiteur utilisé pour diviser le message sur plusieurs lignes')
    parser.add_argument('--taille', '-t', type=int, required=False, default=8,
                        help="Taille des éléments (en pixels)")
    parser.add_argument('--interligne', '-i', type=int, required=False, default=1,
                        help="Permet d'ajouter de l'espace vide entre chaque ligne de code pour decoder")
    parser.add_argument('--bordure', '-b', type=int, required=False, default=0,
                        help='Nombre de pixels du cadre (pas de cadre si egal a zero)')
    parser.add_argument('--legende', '-l', type=str, required=False, default="",
                        help="Légende ajoutée en bas à gauche de l'image")
    parser.add_argument('--fonte', '-f', type=str, required=False, default='FreeMono.ttf',
                        help="Fonte à utiliser pour la légende")
    parser.add_argument('--decoder', action='store_true', required=False, default=False,
                        help="Indique s'il faut afficher le messgae décodé")
    args = parser.parse_args()

    message = args.message
    sortie = args.sortie
    code = args.code.upper()
    delimiteur = args.delimiteur
    taille = max(1,args.taille)
    interligne = max(1, args.interligne)
    bordure = max(0, args.bordure)
    legende = args.legende
    fonte = args.fonte
    decoder = args.decoder

    print("Message à encoder:")
    print(args.message)

    # Appel de la fonction principale en utilisant les arguments de la ligne de commande
    image = codescout(message, code, delimiteur, taille, interligne, bordure, legende, fonte, decoder)

    # Si l'usager n'a pas fourni de nom de fichier on en construit un a partir du message
    if sortie == "":
        # Pas de nom de fichier fourni, on utilise le message pour en construire un
        sortie = message.replace(" ", "_")
        sortie = re.sub(r'[^a-zA-Z]', '', sortie)
        sortie = sortie + '.png'

    # On sauvegarde le résultat
    image.save(sortie)

    print("\nNom du fichier contenant l'image produite:")
    print(sortie)
