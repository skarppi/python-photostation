Synology PhotoStation Python API
================================

A Python API to communicate with `Photo Station <https://www.synology.com/en-global/dsm/6.1/packages/PhotoStation>`_ running on Synology NAS. Photos and videos are uploaded directly to PhotoStation through its Web API with various metadata including ratings, title, description, and GPS coordinates.

This module uploads only original files and lets Synology to process the required thumbnail versions. This works fine with Synology DS916+ but might be too slow with models having slower processors.

Supported features:

* Login to your shared or personal Photo Station
* List album contents
* Create missing albums automatically
* Add new photos
* Update metadata of existing photos
* Update photo binaries based if either timestamp or filesize differs
* Delete photos

Tested with Synology DS916+ running DSM 6.1 and Photo Station 6.7.1. Should work with older versions too but you mileage may vary.

Installation
------------

::

    pip install photostation

Usage
-----

::

    from photostation import PhotoStationService, SynologyException
    import requests

    try:
        # login to Photo Station and set up root album
        service = PhotoStationService('https://USERNAME:PASSWORD@xyz.synology.me/photo/webapi/', 'root-album')

        # get reference to album and create it if missing
        album = service.album('2017/05/13', create=True)

        # list album content (subalbums, photos, videos)
        print(album.items)

        # add photo reference inside album
        photo = album.create_item(
            filename = 'testimage.jpg', # original filename
            filetype = 'photo',         # photo or video 
            created = 1494603121336,    # timestamp of photo capture
            modified = 1494603121336    # optional timestamp to compare if existing binary has changed
            filesize = 1000,            # optional filesize to compare if existing binary has changed
            title = '',                 # optional title
            description = '',           # optional description
            rating = 0,                 # optional starts from 0 to 5
            latitude = 60,              # optional coordinates for videos
            longitude = 20)             # optional coordinates for videos

        # update metadata of existing photos
        merged = photo.merge()

        if merged:
            print('metadata was updated or already up to date, deleting photo')

            photo.delete()
        else:
            # upload new file
            stream = requests.get('https://dummyimage.com/600x400/000/fff', stream=True)
            photo.save_content(stream)

    except SynologyException as se:
        print se.value
