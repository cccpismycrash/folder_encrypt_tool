from enum import StrEnum


class LoggerMessages(StrEnum):
    SYMLINK_NOT_ALLOWED = 'Symbolic links are not allowed'
    FILE_ALREADY_ENCRYPTED = 'File is already encrypted'
    NO_READ_PERMISSION = 'No read permission'
    UNKNOWN_ERROR = 'Unknown error - {error}'
    NO_WRITE_PERMISSION = 'No write permission'
    FILE_NOT_ENCRYPTED = 'File is not encrypted or was encrypted by another utility'
    BAD_PASSWORD = 'Incorrect password or corrupted file'