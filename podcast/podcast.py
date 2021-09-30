from datetime import datetime,timedelta
import json
import logging
import os
import platform
import shutil

from pathlib import Path
from playhouse.sqlite_ext import *
from time import mktime
import feedparser
import requests
from mutagen.mp3 import MP3, HeaderNotFoundError
from mutagen.mp4 import MP4

from urllib.error import URLError

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if platform.system() in ["Linux", "Darwin"]:
    handler = logging.FileHandler('/var/log/arisa.log')
else:
    handler = logging.FileHandler(Path("c:/users/wyk/arisa-ng.log"))
logger.addHandler(handler)

dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, '../arisa_ng.db')
db = SqliteDatabase(filename)
class Mp3(object):
    def __init__(self, path):
        self.path = path
        audio = MP3(self.path)
        self.length = audio.info.length
        minute = int(audio.info.length / 60)
        seconde = int(audio.info.length % 60)
        self.length_str = f"{minute}m{seconde}s"

class Podcast(Model):
    name  = CharField(unique=True)
    url = CharField()
    title = CharField(null = True)
    data = JSONField(null=True)
    last_sync = DateTimeField(null=True)
    image = CharField(null=True)
    title = CharField(null=True)
    cache_path = Path("./cache")
    class Meta:
        database = db
        # This model uses the "people.db" database.
    #def __init__(self,url,name):
        #self.data = feedparser.parse(self.url)
        #self.episodes = {}

        #if self.data["feed"].get("summary",None) is None:
        #    self.summary = "Pouet"
        #else:
        #    self.summary = self.data['feed']["summary"]
        #self.get_podcast_image()
        #self.set_epispodes()
    def get_data(self):
        self.data=feedparser.parse(self.url)
        if self.data.get("bozo_exception") and  type(self.data["bozo_exception"]) is URLError:
            print("Erreur de maj ")
            return False
        else:

            self.last_sync = datetime.now()
            self.save()
            return True
    def get_podcast_info(self):
        if self.title is None:
            if self.data.get("feed"):
                self.title = self.data['feed']['title'].replace(' ', '').replace('?', '').replace("'", '')
            elif self.data.get("channel"):
                self.title = self.data['channel']['title'].replace(' ', '').replace('?', '').replace("'", '')
            else:
                self.title ="_default_"
        (self.cache_path / self.name).mkdir(exist_ok=True, parents=True)
        if self.image is None:
            self.image_extention = self.data['feed']["image"]["href"].split(".")[-1].split("?")[0]
            if not os.path.isfile(f"./cache/{self.name}/{self.title}.{self.image_extention}"):
                response = requests.get(self.data['feed']["image"]["href"], stream=True)
    #           print(response.headers)
                with open(f"./cache/{self.name}/{self.title}.{self.image_extention}", 'wb') as out_file:
                    shutil.copyfileobj(response.raw, out_file)
            self.image = f"./cache/{self.name}/{self.title}.{self.image_extention}"

    def set_episodes(self):
        logger.info(f"Récuperation des épisode pour {self.name}")
        for episode_data in self.data["entries"]:
            #print(episode_data)
            #exit(0)
            episode, created = Episode.get_or_create(podcast=self,title=episode_data["title"])
            episode.presque_init(podcast_name=self.name,data=episode_data)
            #episode.data=json.dumps(episode.data)
            episode.save()
            episode.download()


    def get_episodes(self,sort_by=None,reverse=False):
        cond={
            "name":{True:Episode.title.desc(),False:Episode.title},
            "length": {True: Episode.length.desc(), False: Episode.length},
            "publication_date": {True: Episode.publication_date.desc(), False: Episode.publication_date},
        }
        if sort_by is None:
            return [episode for episode in self.episodes.select().where(Episode.hidden == False).order_by(Episode.publication_date.desc())]
        else:
            return [episode for episode in self.episodes.select().where(Episode.hidden == False).order_by(cond[sort_by][reverse])]

    def download(self):
        for episode in self.episodes:
            episode.download()
class Episode(Model):

    name = CharField(null=True)
    podcast = ForeignKeyField(Podcast,backref='episodes')
    title = CharField(null=True)
    data = JSONField(null=True)
    audio_path = CharField(null=True)
    audio_extension = CharField(null=True)
    audio_url = CharField(null=True)
    image_path  = CharField(null=True)
    downloaded = BooleanField(default=False)
    hidden = BooleanField(default=False)
    publication_date = DateTimeField(null=True)
    length = FloatField(null=True)
    size = FloatField(null=True)

    class Meta:
        database = db  # This model uses the "people.db" database.

    def presque_init(self,podcast_name,data):
        self.data = data
        for link in dict(self.data)["links"]:
            if link["type"] in ["audio/mp3",'audio/mpeg','audio/x-m4a',"audio/x-wav"]:
                self.audio_type = link["type"]
                self.audio_url = link["href"]
                if self.audio_type in ["audio/mpeg","audio/mp3"]:
                    self.audio_extension = "mp3"
                elif self.audio_type == "audio/x-m4a":
                    self.audio_extension = "m4a"
                elif self.audio_type == "audio/x-wav":
                    self.audio_extension = "wav"
                self.size = link["length"]
        if "/" in self.data['id']:
            self.data['id']=self.data['id'].split("/")[-1]
        if "*" in self.data['id']:
            self.data['id'] = self.data['id'].split("*")[0]
        self.filename = f"{self.data['id'].replace('?','').replace('=','')}"
        #(self.filename)
        self.audio_filename =  f"{self.data['id']}.{self.audio_extension}"
        self.audio_path = f"./cache/{podcast_name}/{self.audio_filename}"
        self.image_path = f"./cache/{podcast_name}/{self.filename}"
        self.get_episode_image()
        self.image = None

        try:
            if self.length:
                self.length_old = self.length
        except:
            pass # pas beau

        if self.data.get("itunes_duration"):
            if ":" not  in self.data["itunes_duration"]:
                self.length =  self.data["itunes_duration"]
            else:
                if len(self.data["itunes_duration"])>=4 and len(self.data["itunes_duration"])<=5:
                    time_format = "%M:%S"
                else:
                    time_format= "%H:%M:%S"
                logger.info(f"{self.data['itunes_duration']}     => {time_format}")
                date_time = datetime.strptime(self.data["itunes_duration"],time_format)
                a_timedelta = date_time - datetime(1900, 1, 1)
                self.length = a_timedelta.total_seconds()

        else:
            self.length = None

        try:
            if self.length is not None:

                if float(self.length)-1 <= float(self.length_old) and float(self.length_old) <= float(self.length)+1:
                    pass
                else:
                    print(f"{self.podcast} {self.title}  {self.audio_filename} pas la meme longueur avant {self.length_old} après {self.length}")
        except:
            pass
        #print(json.dumps(self.data))


        #self.publication_date = "".join([str(x) for x in self.data.published_parsed])
        self.publication_date = datetime.fromtimestamp(mktime(self.data["published_parsed"]))

    def human_date(self):
        if self.length:
            minute = int(self.length / 60)
            seconde = int(self.length % 60)
            length_str = f"{minute}m{seconde}s"
            return length_str
        else:
            return None

    def download(self,button=None):
        logger.debug(f"Téléchargement de {self.title} ".encode('utf-8'))
        try:
            self.get_episode_image()
            self.get_episode_sound()
            if button:
                button.background_normal="./img/Download-green.png"
        except URLError as e:
            print("no internet")
    def get_episode_image(self):
        if self.data.get("image",None):

            if not os.path.isfile(self.image_path):
                response = requests.get(self.data["image"]["href"], stream=True)
                with open(self.image_path, 'wb') as out_file:
                    shutil.copyfileobj(response.raw, out_file)
        else:
            self.image_path = None

    def get_episode_sound(self):
        if not os.path.isfile(self.audio_path):
            response = requests.get(self.audio_url,  allow_redirects=True, stream=True,headers={"User-Agent":""})
            with open(self.audio_path, 'wb') as out_file:
                shutil.copyfileobj(response.raw, out_file)
                #Notification => antipub
        try:
            if self.audio_extension == "mp3":
                self.length = MP3(self.audio_path).info.length
            elif self.audio_extension == "m4a":
                self.length = MP4(self.audio_path).info.length
            # deal with wav
        except HeaderNotFoundError as e:
            print(f"{self.title} file {self.filename}.{self.filename} seems to be corrupted {e}")
        else:
            pass
            #logger.info(f"{self.title} {self.audio_extension}".encode('utf-8'))
    def  is_downloaded(self):
        if self.audio_path:
            #if _clean
            return os.path.isfile(self.audio_path)
        else:
            logger.error(f"{self.title} {self.audio_path} is none")

    def hide(self, component):
        #self.hidden = not self.hidden
        self.hidden = True
        self.save()

class Subscription(Model):
    user =  ForeignKeyField(Podcast,backref='user')
    podcast = ForeignKeyField(Podcast,backref='podcast')
    class Meta:
        database = db  # This model uses the "people.db" database.

if __name__ == '__main__':
    db.connect()
    db.create_tables([Podcast,Episode])
    with open('./config.json') as config_file:
        config=json.load(config_file)
    for podcast in config["podcasts"]:
        mon_podcast,created=Podcast.get_or_create(url=podcast["url"],name=podcast["name"])
        #if created or datetime.now()-mon_podcast.last_sync>timedelta(hours=1):
        mon_podcast.get_data()
        mon_podcast.get_podcast_info()
        mon_podcast.save()
        mon_podcast.set_episodes()

