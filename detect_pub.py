import json
import os
from dejavu import Dejavu
from dejavu.logic.recognizer.file_recognizer import FileRecognizer
from dejavu.logic.recognizer.microphone_recognizer import MicrophoneRecognizer
from  pathlib import  Path
import matplotlib.pyplot as plt
import time
# load config from a JSON file (or anything outputting a python dictionary)
from shutil import copyfile
import subprocess
import sys
from podcast.podcast import Podcast
from peewee import *
import time
class Conf_File(object):
    def load(self,path):
        with open(path, "r") as conf_file:
            data = json.load(conf_file)
        return data

class Pupub(object):
    def __init__(self):
        self.pub_path = Path("./pub")
        self.no_pub_path = Path("./no_pub")
        self.no_pub_list = os.listdir(self.no_pub_path)
        self.pub_config_path = Path("./config/pub.json")
        self.pub_config=Conf_File().load(self.pub_config_path)
        self.output_path = Path("./output")
        self.sample_path = Path("samples_mp3")
        self.cache_path = Path("podcast/cache")
        self.seuil=0.1
        self.stats={}
        self.dejavu_config_path = Path("./config/dejavu.json")
        self.dejavu_config=Conf_File().load(self.dejavu_config_path)
        self.pupub_config_path = Path("./config/pupub.json")
        self.pupub_config=Conf_File().load(self.pupub_config_path)
        self.djv = Dejavu(self.dejavu_config)

    def fingerprint(self):
        self.djv.fingerprint_directory(str(self.pub_path), [".mp3"], 5)

    def scan(self):
        pass

    def add_stats_entry(self,results):
        song_name=results['results'][0]['song_name'].decode('utf-8')
        confidence=results['results'][0]['fingerprinted_confidence']
        if confidence < self.seuil:
            if file in self.no_pub_list:
                song_name = "no_pub"
            else:
                song_name="undefined"
        else:
            print(f"Cet épisode {file} est a une pub de : {results['results'][0]['song_name']}\n")
        if self.stats.get(song_name):
            self.stats[song_name].append(confidence)
        else:
            self.stats[song_name]= [confidence ]

    def re_cut_pub(self,file_path,song_name,output_path):
        for ad in self.pub_config["pub"]:
            if song_name == ad["name"]:
                subprocess.call(
                    [self.pupub_config["ffmpeg_path"], '-ss', "0", '-t', str(ad["length"]), '-i', f"{file_path}", '-acodec', 'copy', '-y',
                     str(output_path)])

    def remove_ad(self,file_path,song_name,output_path):
        for ad in self.pub_config["pub"]:
            if song_name == ad["name"]:

                subprocess.call(
                    [self.pupub_config["ffmpeg_path"], '-ss', str(ad["length"]) , '-i', f"{file_path}", '-acodec', 'copy', '-y',
                     str(output_path)])

    def categorize(self,file,results):
        song_name=results['results'][0]['song_name'].decode('utf-8')
        confidence=results['results'][0]['fingerprinted_confidence']
        (self.output_path/"uncategorized").mkdir(exist_ok=True)
        if confidence < self.seuil:
            if file in self.no_pub_list:
                pass
            else:
                copyfile(self.sample_path/file,
                         self.output_path/"uncategorized"/file)

        elif confidence > self.seuil and confidence < 0.5:
            (self.pub_path / song_name).mkdir(exist_ok=True,parents=True)
            #self.re_cut_pub(file_path=self.sample_path/file,song_name=song_name,output_path=self.pub_path / song_name / f"{song_name}_{file}")
            #self.remove_ad(file_path=self.sample_path/file,song_name=song_name,output_path=self.output_path / song_name / f"{song_name}_{file}_clean.mp3")
            #copyfile(self.sample_path / file,
            #         self.pub_path / song_name / f"{song_name}_{file}")

        else:
            (self.output_path/song_name).mkdir(exist_ok=True)
            #copyfile(self.sample_path/file,
            #         self.output_path/song_name/f"{confidence}_{file}")
            #self.remove_ad(file_path=self.sample_path / file, song_name=song_name,
            #               output_path=self.output_path / song_name / f"{song_name}_{file}_clean.mp3")
            pass

    def write_report(self):
        with open('rapport.json', 'w') as rapport:
            json.dump(self.stats, rapport)




if __name__ == '__main__':

    db = SqliteDatabase('arisa_ng.db')
    db.connect()

    # create a Dejavu instance
    detector=Pupub()
    # Fingerprint all the mp3's in the directory we give it
    debut = time.time()
    detector.fingerprint()
    for podcast in Podcast.select():
        print(podcast.name)
        detector.sample_path=detector.cache_path/podcast.name
        for epi in podcast.episodes.select():
            file = Path(epi.audio_path).name
            print(file)
            if Path(detector.sample_path/file).exists():
                results = detector.djv.recognize(FileRecognizer, detector.sample_path/file)
                detector.categorize(file,results)
                #pour les stats
                detector.add_stats_entry(results)
    detector.write_report()


    print(time.time()-debut)

    #detector.write_report()