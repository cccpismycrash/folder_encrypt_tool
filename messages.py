from enum import StrEnum


class ErrorMessages(StrEnum):
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
    PASSWORD_MISSING = 'password is missing'
    SOURCE_MISSING = 'source is missing'
    PASSWORD_AND_SOURCE_MISSING = 'password and source are missing'


class OutputMessages(StrEnum):
    SUMMARY_ENCRYPT = '[+] Encryption operation completed.'
    SUMMARY_DECRYPT = '[+] Decryption operations completed.'
    PROCESSED_COUNT = '[+] Processed: {count}.'
    SKIPPED_COUNT = '[!] Skipped: {count}.'
    SKIPPED_FILE = '[!] {reason}: {file_path}'
    SIGNATURE_UPDATED = '[+] New signature has been set.'
    UTILITY_NOT_EXECUTED = '[!] Utility was not executed.'


class HelpMessages(StrEnum):
    SOURCE_HINT = 'path to source directory'
    PASSWORD_HINT = 'password for encryption or decryption'
    ENCRYPT_HINT = 'encrypt files instead of decrypting'
    SET_SIGN_HINT = 'set a new file encryption signature stored in .sign file in app directory'
    DESCRIPTION = 'Utility for encrypting and decrypting all files in a directory and its subdirectories.'
    EPILOG = 'Before first use, set the file signature with --set-sign'