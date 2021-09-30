import json
import time
import os
from dejavu import Dejavu
from dejavu.logic.recognizer.file_recognizer import FileRecognizer
from dejavu.logic.recognizer.microphone_recognizer import MicrophoneRecognizer
import pathlib
import matplotlib.pyplot as plt
# load config from a JSON file (or anything outputting a python dictionary)
# with open('rapport.json', 'r') as rapport:
#     stats=json.load( rapport)
# print([key] * len(stats[key]))
# plt.scatter(y=stats[key], x=[key] * len(stats[key]), c='coral', label=key)
# for key in stats:
#
# plt.title('Nuage de points avec Matplotlib')
# plt.savefig('Distribution de .png')
# plt.show()



with open('rapport.json', 'r') as rapport:
    stats=json.load( rapport)

cmap = plt.cm.get_cmap("hsv", len(stats)+1)
color_list=  [ cmap(x) for x in  range(0,len(stats))]

valeurs=[]
labels=[]

for podcast in stats:
    valeurs.append(stats[podcast])
    labels.append(podcast)

plt.hist(x=valeurs, range=(0, 1), bins = 10, color =color_list,label=labels,
            edgecolor = 'red', hatch = '/',
            histtype = 'bar') # bar est le defaut
plt.ylabel("nombre d'épisode" )
plt.xlabel('Confiance de détection')
plt.title("répartitions des pub sur le podcast Encore-une histoire S39")
plt.legend(labels)

plt.savefig('encore une histoire_apres_renforcement.png')
plt.show()
