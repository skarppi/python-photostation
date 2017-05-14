class SynologyException(Exception):
    API_ERROR = {
        0  : 'No error',
        100: 'Unknown error',
        101: 'Invalid parameter',
        102: 'The requested API does not exist',
        103: 'The requested method does not exist',
        104: 'The requested version does not support the functionality',
        105: 'The logged in session does not have permission',
        106: 'Session timeout',
        107: 'Session interrupted by duplicate login',
        400: 'Invalid parameter',
        401: 'Unknown error of file operation',
        402: 'System is too busy',
        403: 'Invalid user does this file operation',
        404: 'Invalid group does this file operation',
        405: 'Invalid user and group does this file operation',
        406: 'Can\'t get user/group information from the account server',
        407: 'Operation not permitted',
        408: 'No such file or directory',
        409: 'Non-supported file system',
        410: 'Failed to connect internet-based file system (ex: CIFS)',
        411: 'Read-only file system',
        412: 'Filename too long in the non-encrypted file system',
        413: 'Filename too long in the encrypted file system',
        414: 'File already exists',
        415: 'Disk quota exceeded',
        416: 'No space left on device',
        417: 'Input/output error',
        418: 'Illegal name or path',
        419: 'Illegal file name',
        420: 'Illegal file name on FAT filesystem',
        421: 'Device or resource busy',
        467: 'No such tag',
        468: 'Duplicate tag',
        470: 'No such file',
        555: 'No such shared album',
        599: 'No such task of the file operation',
        1001 : 'Http error: no response body, no response header',
        1002 : 'Http error: no response data, no errorcode in response header',
        1003 : 'Http error: No JSON response data',
        12007: 'Http error: cannotFindHost',
        12029: 'Http error: cannotConnectToHost',
        12038: 'Http error: serverCertificateHasUnknownRoot'
    }


    def __init__(self, code):
        if code in self.API_ERROR:
            self.value = self.API_ERROR[code]
        else:
            self.value = 'Unknown error from API (%d)' % code