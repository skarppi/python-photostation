import requests
import time
import io
from requests_toolbelt.downloadutils import stream
from session import SynologyAuthSession
from utils import PhotoStationUtils
from error import SynologyException
from pprint import pprint, pformat

class PhotoStationService(object):

    session = None

    def __init__(self, url, root_album):
        PhotoStationService.session = SynologyAuthSession(url)

        self.root_album = PhotoStationAlbum(None, root_album)

    def __str__(self):
        return 'PhotoStationService root_album:' + str(self.root_album)

    def album(self, path, create):
        parent = self.root_album
        for folder in path.split('/'):
            album = parent.item(folder)
            if album:
                parent = album
            elif create:
                print('parent album {} is missing album {}'.format(parent.path, folder))
                parent = parent.create(folder)
            else:
                return None                

        return parent

    @staticmethod
    def query(api, params):
        return PhotoStationService.session.query(api, params)

class PhotoStationAlbum(object):

    def __init__(self, parent, name):
        self.parent = parent
        self.name = name
        self._items = None
        if self.parent:
            self.path =  parent.path + '/' + name
        else:
            self.path = name

    @classmethod
    def from_photostation(cls, parent, psalbum):
        album_path = PhotoStationUtils.album_path(psalbum['id'])
        name = album_path.replace(parent.path + '/', '')

        return cls(parent, name)

    def __str__(self):
        return '{path:' + self.path + ',name:' + self.name + '}'

    def item(self, name):
        return self.items.get(name)

    def add_item(self, name, item):
        if self._items is not None:
            self._items[name] = item 

    def remove_item(self, name):
        if self._items is not None:
            self._items.pop(name)

    @property
    def items(self):
        if not self._items:
            items = PhotoStationService.session.query('SYNO.PhotoStation.Album', {
                'method': 'list',
                'id': PhotoStationUtils.album_id(self.path),
                'type': 'album,photo,video',
                'offset': 0, 
                'limit': -1,
                'recursive': 'false'
                })

            self._items = {}
            for item in items['items']:
                if item['type'] == 'album':
                    album = PhotoStationAlbum.from_photostation(self, item)

                    self.add_item(album.name, album)
                else:
                    photo = PhotoStationPhoto.from_photostation(self, item)
                    self.add_item(photo.filename, photo)

        return self._items

    def create(self, name):
        PhotoStationService.session.query('SYNO.PhotoStation.Album', {
            'name': name,
            'title': '',
            'description': '',
            'id': PhotoStationUtils.album_id(self.path),
            'method': 'create',
            'ps_username': PhotoStationService.session.username
            })
        album = PhotoStationAlbum(self, name)
        self.add_item(name, album)
        return album

    def delete(self):
        PhotoStationService.session.query('SYNO.PhotoStation.Album', {
            'id': PhotoStationUtils.album_id(self.path),
            'method': 'delete',
            'ps_username': PhotoStationService.session.username
            })
        self.parent.remove_item(self.name)

    def create_item(self, filename, filetype, created, modified = None, filesize = None, title = None, description = None, rating = None, latitude = None, longitude = None):
        return PhotoStationPhoto(self, filename, filetype, created, modified, filesize, title, description, rating, latitude, longitude)

class PhotoStationPhoto(object):

    def __init__(self, album, filename, filetype, created, modified, filesize, title, description, rating, latitude, longitude):
        self.album = album
        self.filename = filename
        self.filetype = filetype
        self.created = created
        self.modified = modified
        self.filesize = filesize
        self.title = title
        self.description = description
        self.rating = rating
        self.latitude = latitude
        self.longitude = longitude

    @classmethod
    def from_photostation(cls, album, psphoto):
        info = psphoto['info']

        created = int(time.mktime(time.strptime(info['takendate'], '%Y-%m-%d %H:%M:%S'))) * 1000
        modified = int(time.mktime(time.strptime(info['createdate'], '%Y-%m-%d %H:%M:%S'))) * 1000
        filesize = int(info['size'])

        if info.get('gps') is not None:
            latitude = info['gps']['lat']
            longitude = info['gps']['lng']
        else:
            latitude = longitude = None

        return cls(album, 
            filename = PhotoStationUtils.photo_name(psphoto['id']),
            filetype = psphoto['type'],
            created = created,
            modified = modified,
            filesize = filesize,
            title = info['title'].encode('utf-8'),
            description = info['description'].encode('utf-8'),
            rating = info['rating'],
            latitude = latitude,
            longitude = longitude)

    def __str__(self):
        return '{filename:' + self.filename.decode('utf-8').encode('unicode-escape') + \
            ',filetype:' + self.filetype + \
            ',created:' + str(self.created) + \
            ',modified:' + str(self.modified) + \
            ',filesize:' + str(self.filesize) + \
            ',title:' + self.title.decode('utf-8').encode('unicode-escape') + \
            ',description:' + self.description.decode('utf-8').encode('unicode-escape') + \
            ',rating:' + str(self.rating) + \
            ',latitude:' + str(self.latitude) + \
            ',longitude:' + str(self.longitude) + '}'

    @property
    def fullpath(self):
        return self.album.path + '/' + self.filename 

    # Merge with remote if able.
    # Return false if rewrite is needed.
    def merge(self):

        remote = self.album.item(self.filename)
        if remote is None \
            or self.filename != remote.filename \
            or self.filetype != remote.filetype:

            # print(self.filetype + ' ' + self.fullpath + ' not found or cannot be merged with ' + str(remote))
            return False

        if self.modified is not None and self.modified / 1000 > remote.modified / 1000:
            print(self.filetype + ' ' + self.fullpath + ' timestamp differs, replacing existing ' + str(remote) + ' with ' + str(self))
            return False

        if self.filesize is not None and self.filesize != remote.filesize:
            print(self.filetype + ' ' + self.fullpath + ' filesize differs, replacing existing ' + str(remote) + ' with ' + str(self))
            return False

        changes = {}
        if self.title and self.title != remote.title:
            changes['title'] = self.title
        if self.description and self.description != remote.description:
            changes['description'] = self.description
        if self.rating is not None and self.rating != remote.rating:
            changes['rating'] = self.rating
        if not PhotoStationUtils.check_coordinates(self.latitude, remote.latitude):
            changes['gps_lat'] = self.latitude
        if not PhotoStationUtils.check_coordinates(self.longitude, remote.longitude):
            changes['gps_lng'] = self.longitude

        if len(changes) > 0:
            print(self.filetype + ' ' + self.fullpath +  ' has metadata changes ' + str(changes) + ', updating existing ' + str(remote))
            self.update(changes)

        return True

    def save_content(self, file):

        data = io.BytesIO()
        stream.stream_response_to_file(file, path=data)

        created = PhotoStationService.session.query('SYNO.PhotoStation.File', {
            'method': 'upload' + self.filetype,
            'version': '1',
            'dest_folder_path': self.album.path,
            'duplicate': 'overwrite', # rename, ignore
            'filename': self.filename,
            'mtime': str(self.created),
            'title': self.title,
            'description': self.description,
            'ps_username': PhotoStationService.session.username,
            'original': (self.filename, data)
            })
        
        if self.rating > 0 or (self.latitude and self.longitude):
            self.update({
                'rating': self.rating,
                'gps_lat': self.latitude,
                'gps_lng': self.longitude
            })

        self.album.add_item(self.filename, self)

    def update(self, changes):
        data = {
            'id': PhotoStationUtils.photo_id(self.filetype, self.album.path, self.filename),
            'method': 'edit',
            'ps_username': PhotoStationService.session.username
            }
        data.update(changes)
        PhotoStationService.session.query('SYNO.PhotoStation.Photo', data)
        
    def delete(self):
        PhotoStationService.session.query('SYNO.PhotoStation.Photo', {
            'id': PhotoStationUtils.photo_id(self.filetype, self.album.path, self.filename),
            'method': 'delete',
            'ps_username': PhotoStationService.session.username
            })
        self.album.remove_item(self.filename)
