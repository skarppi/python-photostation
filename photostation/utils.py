
class PhotoStationUtils(object):
    @staticmethod
    def ascii2hex(str):
        return ''.join(x.encode('hex') for x in str)

    @staticmethod
    def hex2ascii(hex):
        return bytearray.fromhex(hex).decode()

    @staticmethod
    def album_id(path):
        if not path:
            return ''
        else:
            return 'album_' + PhotoStationUtils.ascii2hex(path)

    @staticmethod
    def album_path(album_id):
        return PhotoStationUtils.hex2ascii(album_id.split('_')[1])

    @staticmethod
    def photo_id(filetype, path, filename):
        return '_'.join((filetype, PhotoStationUtils.ascii2hex(path), PhotoStationUtils.ascii2hex(filename)))

    @staticmethod
    def photo_name(photo_id):
        return PhotoStationUtils.hex2ascii(photo_id.split('_')[2])
