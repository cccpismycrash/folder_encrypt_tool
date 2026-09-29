from enum import StrEnum


class LoggerMessages(StrEnum):
    SYMLINK_NOT_ALLOWED = 'Symbolic links are not allowed'
    FILE_ALREADY_ENCRYPTED = 'File is already encrypted'
    NO_READ_PERMISSION = 'No read permission'
    UNKNOWN_ERROR = 'Unknown error - {error}'
    NO_WRITE_PERMISSION = 'No write permission'
    FILE_NOT_ENCRYPTED = 'File is not encrypted or was encrypted by another utility'
    BAD_PASSWORD = 'Incorrect password or corrupted file'


class ParserMessages(StrEnum):
    PATH_NOT_HOME_DIR = 'source must be inside the home directory'
    PATH_TO_APP_DIR = 'source must not contain the application directory'
    SYMLICK_PATH = 'source must not be a symbolic link'
    PATH_NOT_EXISTING = 'source must be an existing directory'


class OutputMessages(StrEnum):
    SUMMARY = '[+] {count} operations completed.\n'
    PROCESSED_COUNT = '\tProcessed: {count}.\n'
    SKIPPED_COUNT = '\tSkipped: {count}.'
    SKIPPED_FILE = '[!] {reason}: {file_path}'


class HelpMessages(StrEnum):
    SOURCE_HINT = 'path to source directory'
    PASSWORD_HINT = 'password for encryption or decryption'
    ENCRYPT_HINT = 'encrypt files instead of decrypting'