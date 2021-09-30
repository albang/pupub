# Idée:

Si on peut ajouter de la publicité automatiquement à un contenu audio c'est qu'on peut aussi l'enlever automatiquement.
# Kézaco:

Pupub permet  d'identifier un segment de audio dans un épisode de podcast et permet de l'enlever. 
Comment:

Il y a une première phase d'apprentissage où les segments de publicité sont indexés dans une base de donnée. Chaque épisode de podcast est ensuite analysé et comparé à cette base de publicité
   
  * Si il matche avec une publicité, on peut tronquer la publicité qui se trouve en début/et ou à la fin
   
  * Si il ne matche pas, soit il n'y a pas de publicité ou  soit on ne connait pas encore la publicité.

Une fois la publicité enlevée, on ajoute la durée réel de l'épisode en  métadonnée.  Cette information va être utile pour découvrir de nouvelles publicités. Effectivement les campagnes de publicité changent à travers le temps. Si on télécharge le même épisode une semaine plus tard, il y aura surement une nouvelle publicité. Pour découvrir une nouvelle publicité, il suffit de re-télécharger un épisode qu'on a déjà analysé ( dont on connait la longueur du contenu utile) et comparer la durée avec le nouvel épisode. Si il est plus long, on ne garde que le début du fichier en se basant sur:

    durée de la pub = temps total de l'épisode - temps du contenu *

* si la pub se trouve au début 

On indexe la nouvelle pub puis on passe les nouveau épisodes dans la moulinette. Normalement plus besoin, d'écouter de la pub
# Briques techniques 

    https://github.com/worldveil/dejavu

    python / feedparser / ffmpeg / sqlite




# How to :
## En amont:
  * avoir docker et démarré la base de donnée postgres
  * installé un environement de dev avec anaconda 3.6 + forge alternative pour pewee https://anaconda.org/conda-forge/peewee

## Le tuto 

1. configurer le podcast a télécharger dans le fichier ./podcast/config.json
2. Pour télécharger les épisodes ```cd podcast; python3 podcast.py```
3. une fois les épisodes téléchargé, on ouvre un épisode pour récuperer la pub avec audacity.
    * On séléctionne la publicité et dans le menu de audacity, fichier > Exporter l'audio sélectionné =>mp3 dans le répertoire pub
    * le nom du fichier sera le nom de la pub
4. décommenter certaines lignes selon ce que vous voulez faire et lancer le script detect_pub.py
5. Have fun


# Disclaimer:
Le code est livré "as is".