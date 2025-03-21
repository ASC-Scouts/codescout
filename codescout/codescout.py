#!/usr/bin/env python3

"""
Cette librairie permet de créer une image au format png contenant un message codé
avec differents codes scouts:

Code soleil: Dans ce code, chaque lettre du message est représentée
par un soleil et le nombre de rayon de ce soleil correspond à l'ordre de la
lettre dans l'alphabet (de 1 à 26). Pour faciliter le décodage, les rayons
correspondant à des voyelles sont plus longs

Code musical: Dans ce code, chaque lettre du message est représentée
par une note de musique. Le A devient une blanche sur le DO central, et on
monte d'une note jusqu'au M qui est un LA. Ensuite on reprend au dos central
pour la lettre M mais avec des noires. On monte encore une fois jusqu'au LA
aigu pour Z.

Code alphabet: Dans ce code, chaque lettre du message est décalée par un
nombre de positions dans l'alphabet défini par le paramètre <decalage>

Code Avocat: équivalent au code alphabet avec un décalage de +8 (A vaut K)

Code Escalier: équivalent au code alphabet avec un décalage de -10 (S K liés)

La fonction principale de cette librairie se nomme codescout. Elle
prend deux parametres obligatoires et plusieurs parametres optionnels:
- message [requis]:       message a encoder
- code [requis]:          nom du code a utiliser pour encoder
- taille [defaut=8]:      taille des elements du message en pixels
- delimiteur [defaut=':'] caractere a utiliser dans le message pour indiquer
                          a la fonction de decouper le message sur plusieurs
                          lignes a l'aide de ce delimiteur
- interligne [defaut=1]:  permet d'ajouter de l'espace entre les lignes du
                          message afin par exemple de laisser de la place pour
                          decoder
- bordure [defaut=0]:     permet d'ajouter une bordure au message afin par
                          exemple de faciliter son decoupage (le parametre
                          correspond a la taille en pixels de la bordure
- legende [defaut='']:    permet d'ajouter une legende en bas a gauche
                          (par exemple une courte instruction, un numero...)
- decoder [defaut=False]  indique si oui ou nom on doit afficher le message
                          decode sous le code
- fonte [default='FreeMono.ttf'] nom de la fonte a utiliser pour la legende
                          et le texte decode

Cette fonction retourne une image, qui peut être affichée ou sauvegardée en
utilisant les méthodes image.draw() et image.save().

En mode ligne de commande, un paramètre optionnel supplémentaire permet de
spécifier le nom du fichier dans lequel sauvegarder l'image (au format PNG):
- sortie [optionnel]:     nom du fichier contenant l'image

Si ce paramètre n'est pas fourni, un nom de fichier est construit par le script
à partir du message.

Un autre paramètre permet d'afficher des informations utiles au déboguage:
- debug [defaut=False]

De plus, en mode de ligne de commande il y a des valeurs par défaut pour les
paramètres "message" et "code"
- message par défaut: "ABCDEFGHIJKLM:NOPQRSTUVWXYZ"
- code par défaut: "soleil"

Attention:
1) ne pas utiliser d'accents dans le texte a encoder
2) si le fichier de fonte n'est pas trouve, la fonte par defaut de la librairie
   PIL sera utilisee, et elle est assez petite
3) en mode ligne de commande, comme le script choisit le nom du fichier de sortie,
   il peut écraser un fichier existant. Le nom du fichier de sortie comprend tous
   les caractères entre a et z du message et a l'extension PNG. Si le script n'a
   pas le droit d'écrire dans le répertoire courant, une erreur se produira et
   l'image ne sera pas sauvegardée.

Exemple d'utilisation:
>>> from codescout import codescout
>>> image = codescout(message="La bonne humeur:est aussi contagieuse:que la rougeole",
                      "soleil",taille=15,bordure=2,legende="2024-05-12",decoder=True)
>>> image.save("code.png")

Equivalent en version ligne de commande:
./codescout.py -m "La bonne humeur:est aussi contagieuse:que la rougeole"\
                  -c soleil -t 15 -b 2 -l "2024-05-12" --decoder

Tapez ./codescout.py -h pour obtenir de l'aide sur l'utilisation en mode
ligne de commande.

Copyright 2024, Vincent Fortin (vincent.fortin@gmail.com)

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

"""

import math
import argparse
import re
from PIL import Image, ImageDraw, ImageFont
from unidecode import unidecode

# Codes reconnus par cette librairie
codes = ('SOLEIL', 'MUSICAL','AVOCAT','ESCALIER', 'ALPHABET')

def dessine_une_note(dessin, lettre, position, portee, rayon, bordure):
    """
    Cette fonction dessine une note de musique dans l'image "dessin".
    La note choisie est fonction de la lettre "lettre" et est placée à
    la position latérale "position" et la position verticale "portée".
    Le rayon de la note est "rayon", et l'on tien compte de la présence
    d'une bordure de "bordure" pixels.
    """

    # On met la lettre en majuscule et on enleve les accents
    lettre = unidecode(lettre.upper())

    # Si ce n'est pas une lettre on ne dessine rien
    if not lettre.isalpha():
        return

    # On calcule la position de la note sur la portée
    i = ord(lettre) - 65 # 65 est le code ASCII de la lettre A
    y = 14 * rayon - rayon * (i % 13) + portee + bordure
    x = 3 * rayon * position + bordure

    # On détermine la couleur (blanche ou noire de la note)
    # blanche pour A-M, noire pour N-Z
    fill = None if i <= 12 else 'black'

    # On dessine la note
    dessin.ellipse((x - rayon, y - rayon, x + rayon, y + rayon), outline='black', fill=fill)

    # Si la note est sous ou au-dessus de la portée on ajoute un trait
    if i in (0, 12, 13, 25):
        dessin.line((x - 2 * rayon, y, x + 2 * rayon, y))

    # On ajoute la hampe de la note
    if (i%13) < 5:
        dessin.line((x + rayon, y, x + rayon, y - 4 * rayon))
    else:
        dessin.line((x - rayon, y, x - rayon, y + 4 * rayon))

def creer_un_soleil(dessin,
                    lettre,
                    centre,
                    rayon=10,
                    longueur_trait_voyelle=20,
                    longueur_trait_consonne=10):

    """
    Cette fonction ajoute un soleil dans l'image "dessin". Le soleil encode
    la lettre "lettre" et est centré à la position "centre". Le rayon du
    cercle utilisé pour dessiner le soleil est de "rayon" pixels.
    Les rayons du soleil sont de longueur "longueur_voyelle" pour les
    voyelles et "longueur_consonne" pour les consonnes.
    """

    # On met la lettre en majuscule
    lettre = unidecode(lettre.upper())

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
        x_1 = centre[0] + rayon * math.cos(math.radians(angle))
        y_1 = centre[1] + rayon * math.sin(math.radians(angle))
        # Position de la fin du trait
        x_2 = centre[0] + (rayon + longueur_trait) * math.cos(math.radians(angle))
        y_2 = centre[1] + (rayon + longueur_trait) * math.sin(math.radians(angle))
        # On dessine le trait
        dessin.line((x_1, y_1, x_2, y_2), fill="black", width=1)

def decalage_alphabet(caractere, decalage):
    caractere = unidecode(caractere)
    if 'A' <= caractere <= 'Z':
        return chr((ord(caractere) - ord('A') + decalage) % 26 + ord('A'))
    elif 'a' <= caractere <= 'z':
        return chr((ord(caractere) - ord('a') + decalage) % 26 + ord('a'))
    else:
        return caractere

def code_alphabet(code, decalage, caractere):
    if code == 'AVOCAT':
        return decalage_alphabet(caractere, 10)
    elif code == 'ESCALIER':
        return decalage_alphabet(caractere, -8)
    else:
        return decalage_alphabet(caractere, decalage)

class Encodeur:
    """
    Classe générique définissant un encodeur.
    Chaque code scout reconnu par cette librairie hérite de cette classe
    """

    def __init__(self, message, delimiteur, taille_elements,
                 interligne, bordure, legende, fonte, decoder):
        """
        En plus d'initialiser les attributs de la classe a partir
        des options qui sont passees au constructeur, on divise le message
        en lignes en utilisant le separateur et on calcule la taille du message
        en nombre de caracteres par ligne. On etablit aussi une taille minimale
        pour l'image qui tient compte de la presence d'une legende et d'une bordure.
        """
        # Initialisation directe de certains attributs de classe
        # a partir des parametres du constructeur
        self.taille_elements = taille_elements
        self.interligne = interligne
        self.bordure = bordure
        self.legende = legende
        self.fonte = fonte
        self.decoder = decoder
        # Initialisation de la taille de l'image et du message
        self.taille_image = [0,0]
        self.taille_message = [0,0]
        # On sépare le message sur plusieurs lignes en utilisant le séparateur
        self.message_split = message.split(delimiteur)
        # Taille du message en nombre de caractères (considérant la ligne la plus longue)
        self.taille_message[0] = len(max(self.message_split, key=len))
        self.taille_message[1] = len(self.message_split)
        # On augmente la taille de l'image en fonction de la taille
        # de la bordure et de la presence d'une legende
        for i in range(2):
            self.taille_image[i] = bordure * 2
        if legende != '':
            self.taille_image[1] += taille_elements * 4

    def creer_image(self):
        """
        Creation de l'image et ajout des elements de base (bordure et legende)
        """
        # Création d'une image avec la bonne taille
        self.image = Image.new("1", self.taille_image, "white")
        # Creation de l'object permettant de dessiner l'image
        self.dessin = ImageDraw.Draw(self.image)
        # Ajout d'un cadre
        for i in range(0, self.bordure):
            self.dessin.rectangle([i, i,
                                   self.taille_image[0] - i,
                                   self.taille_image[1] - i])
        # Ajout d'une legende en bas a droite
        if self.legende != '':
            self.dessin.text([self.bordure + self.taille_elements * 2,
                              self.taille_image[1] -self.taille_elements * 6 - 1],
                              self.legende, font=self.fonte)

    def encoder_lettre(self, lettre, i, j):
        # A redefinir dans chaque classe heritee de celle-ci
        return

    def encoder_message(self):
        """
        Boucle sur les lignes et les caracteres de chaque ligne
        pour encoder chacun de ceux-ci a l'aide d'une methode
        redefinie dans chaque classe qui herite de celle-ci.
        """
        # Creation de l'image de base (cadre et elements de fond)
        self.creer_image()
        # On encode le message ligne par ligne
        for i in range(self.taille_message[1]):
            # Encodage de chaque lettre d'une ligne
            for j in range(len(self.message_split[i])):
                self.encoder_lettre(self.message_split[i][j], i, j)

class CodeSoleil(Encodeur):

    def __init__(self, message, delimiteur, taille_elements,
                 interligne, bordure, legende, fonte, decoder):
        """
        Definition d'attributs de classe qui permettront de positionner un element encodé
        sur l'image lors de l'appel à la méthode encoder_lettre.
        Il faut aussi ajuster la taille de l'image.
        """
        super().__init__(message, delimiteur, taille_elements,
                         interligne, bordure, legende, fonte, decoder)
        # Longueur des rayons pour les voyelles: 2 fois le rayon du soleil
        self.longueur_trait_voyelle = taille_elements * 2
        # Longueur des rayons pour les consonnes: meme que le rayon du soleil
        self.longueur_trait_consonne = taille_elements
        # Taille totale d'un soleil en pixel en incluant les rayons et de l'espace autour
        self.taille_soleil = taille_elements \
            + 2 * max(self.longueur_trait_consonne, self.longueur_trait_voyelle) \
            + taille_elements // 2
        self.taille_image[0] += self.taille_message[0] * self.taille_soleil
        self.taille_image[1] += self.taille_message[1] * self.taille_soleil * interligne

    def encoder_lettre(self, lettre, i, j):
        """
        Methode principale de la classe, qui permet d'encoder la lettre "lettre"
        a la position (i,j) de l'image.
        """
        creer_un_soleil(self.dessin,
            lettre,
            ((j + 0.5) * self.taille_soleil + self.bordure,
            (i * self.interligne + 0.5) * self.taille_soleil + self.bordure),
            self.taille_elements,
            self.longueur_trait_voyelle,
            self.longueur_trait_consonne)
        if self.decoder:
            self.dessin.text(((j + 0.3) * self.taille_soleil + self.bordure,
                              (i * self.interligne + 1) * self.taille_soleil + self.bordure),
                              lettre,
                              font=self.fonte)

class CodeMusical(Encodeur):

    def __init__(self, message, delimiteur, taille_elements,
                 interligne, bordure, legende, fonte, decoder):
        super().__init__(message, delimiteur, taille_elements,
                         interligne, bordure, legende, fonte, decoder)
        """
        Definition d'attributs de classe qui permettront de positionner un element encodé
        sur l'image lors de l'appel à la méthode encoder_lettre
        Il faut aussi ajuster la taille de l'image.
        """
        # Taille de l'image en pixel
        self.taille_portee = taille_elements * 16 + taille_elements * 4 * (interligne - 1)
        self.taille_image[0] += (self.taille_message[0] + 1) * taille_elements * 3
        self.taille_image[1] += self.taille_message[1] * self.taille_portee

    def creer_image(self):
        """
        Ajout d'elements de fond sur l'image (portee musicale)
        """
        super().creer_image()
        # On dessine les portées
        for i in range(self.taille_message[1]):
            for j in range(4 * self.taille_elements,
                           14 * self.taille_elements,
                           2 * self.taille_elements):
                pos_y = j + i * self.taille_portee + self.bordure
                self.dessin.line([(self.bordure, pos_y),
                                  (self.taille_image[0] - self.bordure, pos_y)])

    def encoder_lettre(self, lettre, i, j):
        """
        Methode principale de la classe, qui permet d'encoder la lettre "lettre"
        a la position (i,j) de l'image.
        """
        # On calcule la position de la note sur la portée
        x = 3 * self.taille_elements * (j + 0.75) + self.bordure
        dessine_une_note(self.dessin,
                         lettre,
                         j + 1,
                         i * self.taille_portee,
                         self.taille_elements,
                         self.bordure)
        if self.decoder:
            self.dessin.text((x, (i + 0.75) * self.taille_portee),
                             lettre, font=self.fonte, align='center')

class CodeAlphabet(Encodeur):

    def __init__(self, code, decalage, message, delimiteur, taille_elements,
                 interligne, bordure, legende, fonte, decoder):
        super().__init__(message, delimiteur, taille_elements,
                         interligne, bordure, legende, fonte, decoder)
        """
        Definition d'attributs de classe qui permettront de positionner un element encodé
        sur l'image lors de l'appel à la méthode encoder_lettre
        Il faut aussi ajuster la taille de l'image.
        """
        # Taille de l'image en pixel
        self.taille_image[0] += (self.taille_message[0] + 1) * taille_elements * 3
        self.taille_image[1] += self.taille_message[1] * taille_elements * 3 * (2 + interligne - 1)
        self.code = code
        self.decalage = decalage

    def encoder_lettre(self, lettre, i, j):
        """
        Methode principale de la classe, qui permet d'encoder la lettre "lettre"
        a la position (i,j) de l'image.
        """
        # On calcule la position de la note sur la portée
        x = 3 * self.taille_elements * (j + 0.5) + self.bordure
        y = (i * (1 + self.interligne)) * self.taille_elements * 3
        self.dessin.text((x, y), code_alphabet(self.code, self.decalage, lettre),
            font=self.fonte, align='center')
        if self.decoder:
            y = (i * (1 + self.interligne) + 1.5) * self.taille_elements * 3
            self.dessin.text((x, y), lettre, font=self.fonte, align='center')

def codescout(message, code,
              delimiteur = ':',
              taille = 8,
              interligne = 1,
              bordure = 0,
              legende = '',
              fonte = 'FreeMono.ttf',
              decoder = False,
              decalage = 0):
    """
    Fonction principale qui construit le code scout et retourne une image.
    Elle prend deux parametres obligatoires et plusieurs parametres optionnels:
    - message [requis]:       message a encoder
    - code [requis]:          nom du code a utiliser pour encoder
    - delimiteur [defaut=':'] caractere a utiliser dans le message pour indiquer
                              a la fonction de decouper le message sur plusieurs
                              lignes a l'aide de ce delimiteur
    - taille [defaut=8]:      taille des elements du message en pixels
    - interligne [defaut=1]:  permet d'ajouter de l'espace entre les lignes du
                              message afin par exemple de laisser de la place pour
                              decoder
    - bordure [defaut=0]:     permet d'ajouter une bordure au message afin par
                              exemple de faciliter son decoupage (le parametre
                              correspond a la taille en pixels de la bordure
    - legende [defaut='']:    permet d'ajouter une legende en bas a gauche
                              (par exemple une courte instruction, un numero...)
    - fonte [default='FreeMono.ttf'] nom de la fonte a utiliser pour la legende
                              et le texte decode
    - decoder [defaut=False]  indique si oui ou nom on doit afficher le message
                              decode sous le code
    - decalage [defaut=0]     indique le nombre de lettres de decalage pour les
                              codes de type "alphabet" (ex: AVOCAT = 8)
    """

    # Validation du nom du code
    code = code.upper()
    if code not in codes:
        print(f'Codes reconnus: {codes}')
        raise ValueError(f"code {code} inconnu")

    # On ajuste l'interligne a 2 au minimum si on doit ajouter le message decode
    if decoder:
        interligne = max(2, interligne)

    # On impose des valeurs minimales a la taille des elements, le nombre d'interlignes
    # et la taille de la bordure
    taille = max(1, taille)
    interligne = max(1, interligne)
    bordure = max(0, bordure)

    # Si on veut ecrire du texte (options legende ou decoder) il faut creer la fonte
    # Si le fichier de fonte n'existe pas on utilise la fonte par defaut
    try:
        fonte = ImageFont.truetype(fonte, taille*4)
    except IOError:
        fonte = ImageFont.load_default()

    if code == 'SOLEIL':
        encodeur = CodeSoleil(message, delimiteur, taille,
                              interligne, bordure, legende, fonte, decoder)
    elif code == 'MUSICAL':
        encodeur = CodeMusical(message, delimiteur, taille,
                               interligne, bordure, legende, fonte, decoder)
    else:
        encodeur = CodeAlphabet(code, decalage, message, delimiteur, taille,
                               interligne, bordure, legende, fonte, decoder)

    encodeur.encoder_message()

    return encodeur.image

def main():

    print("\n====================================================")
    print("Encodage d'un message à l'aide d'un code scout")
    print("Auteur: Goéland Astucieux (vincent.fortin@gmail.com)")
    print("Version du 16 mai 2024")
    print("====================================================\n")

    # Arguments du script
    parser = argparse.ArgumentParser(description='Encodeur en code scout')
    parser.add_argument('--message', '-m', type=str, required=False,
        default='ABCDEFGHIJKLM:NOPQRSTUVWXYZ',
        help='Message à encoder')
    parser.add_argument('--code', '-c', type=str, required=False,
        default='musical',
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
        help="Indique s'il faut afficher le message décodé")
    parser.add_argument('--decalage', type=int, required=False, default=0,
        help="Nombre de lettres de décalage pour le code alphabet")
    parser.add_argument('--debug', action='store_true', required=False, default=False,
        help="Indique si l'application est démarrée en mode de déboguage")
    args = parser.parse_args()

    debug = args.debug

    if debug:
        print("Message à encoder:")
        print(args.message)

    # Appel de la fonction principale en utilisant les arguments de la ligne de commande
    image_code = codescout(args.message,
                           args.code,
                           delimiteur = args.delimiteur,
                           taille = args.taille,
                           interligne = args.interligne,
                           bordure = args.bordure,
                           legende = args.legende,
                           fonte = args.fonte,
                           decoder = args.decoder,
                           decalage = args.decalage)

    # Si l'usager n'a pas fourni de nom de fichier on en construit un a partir du message
    if args.sortie == "":
        fichier_sortie = re.sub(r'[^a-zA-Z]', '', args.message.replace(" ", "_")) + '.png'
    else:
        fichier_sortie = args.sortie

    # On sauvegarde le résultat
    image_code.save(fichier_sortie)

    if debug:
        print("\nNom du fichier contenant l'image produite:")
        print(fichier_sortie)

if __name__ == '__main__':
    main()
