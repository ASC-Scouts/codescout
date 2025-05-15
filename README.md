# codescout
Librairie python permettant d'encoder des messages à l'aide de codes utilisés par les scouts
Copyright 2024, Vincent Fortin (vincent.fortin@gmail.com)

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

Code alphabet: Dans ce code, chaque lettre du message est décalée d'un
certain nombres de positions dans l'alphabet, en fonction d'un paramètre
nommé "decalage". Par exemple, si decalage=2 alors un A devient un C, un
B devient un D, un Y de vient un A et ainsi de suite.

Code avocat (A vaut K): équivalent au code alphabet avec un décalage de 8:
un A devient un K, un B devient un L et ainsi de suite.

Code escalier (S-K liés): équivalent au code alphabet avec un décalage de
-10: un S devient un K, un T devient un L et ainsi de suite.

Code semaphore: le message est encodé selon le code maritime du
sémaphore qui permet d'épeler un mot avec la position des bras.

Code braille: le message est encodé en alphabet braille.

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
- fonte [defaul='FreeMono.ttf'] nom de la fonte a utiliser pour la legende
                          et le texte decode
- decalage [defaul=0]     decalage a utiliser pour le code alphabet
- fontes [defaut={}]      dictionnaire definissant le nom des codes et la
                          localisation des fontes sur disque pour les codes
                          qui sont definis par une fonte

Cette fonction retourne une image, qui peut être affichée ou sauvegardée en
utilisant les méthodes image.draw() et image.save().

En mode ligne de commande, un paramètre optionnel supplémentaire permet de
spécifier le nom du fichier dans lequel sauvegarder l'image (au format PNG):
- sortie [optionnel]:     nom du fichier contenant l'image

Si ce paramètre n'est pas fourni, un nom de fichier est construit par le script
à partir du message.

Attention:
1) si le fichier de fonte n'est pas trouve, la fonte par defaut de la librairie
   PIL sera utilisee, et elle est assez petite
2) en mode ligne de commande, lorsque le script choisit le nom du fichier de sortie,
   il peut écraser un fichier existant. Le nom du fichier de sortie comprend tous
   les caractères entre a et z du message et a l'extension PNG. Si le script n'a
   pas le droit d'écrire dans le répertoire courant, une erreur se produira et
   l'image ne sera pas sauvegardée.

Exemple d'utilisation:

````
from codescout import codescout
image = codescout(message="La bonne humeur:est aussi contagieuse:que la rougeole",
                      "soleil",taille=15,bordure=2,legende="2024-05-12",decoder=True)
image.save("code.png")
````

Equivalent en version ligne de commande:

````
./codescout.py -m "La bonne humeur:est aussi contagieuse:que la rougeole"\
                  -c soleil -t 15 -b 2 -l "2024-05-12" --decoder
````

Tapez ``./codescout.py -h`` pour obtenir de l'aide sur l'utilisation en mode
ligne de commande.

Une application flask a été ajoutée afin de produire des codes à l'aide de requêtes http.
On peut y accéder ainsi:

````
from codescout import app
````

Pour démarrer un serveur de développement, on utilisera la méthode app.run().

Le serveur de développement peut aussi être démarré à partir du script flask_codescout.py.

Ce script lit un fichier de configuration pour déterminer les valeurs par défaut lors de
l'appel à la fonction codescout() et aussi lors du démarrage du serveur de développement.

Le nom du fichier de configuration peut être spécifié à l'aide de l'option --config.

On peut aussi lancer le serveur de développement en mode de déboguage avec l'option --debug.

