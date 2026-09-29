import argparse
import os
from pathlib import Path
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet, InvalidToken
import base64

from messages import ErrorMessages, ParserMessages, OutputMessages, HelpMessages
from logger import logger


class Encrypter:
           
    __instance = None
    __signature = b'AbramovEgor'


    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance


    def __init__(self):
        self.__skipped_count = 0
        self.__processed_count = 0
        self.__skipped_files = list()


    def __skipped_inc(self):
        self.__skipped_count += 1


    def __processed_inc(self):
        self.__processed_count += 1


    def cryptowalk(self, source: Path, password: str, encrypt_flag: bool):
        """
        Walks through the directory tree and encrypts or decrypts all files.
        """

        # extract files from the directory tree
        files = list()
        for root, _, filenames in source.walk():
            for filename in filenames:
                files.append(Path(root) / filename)

        # encrypt or decrypt files
        if encrypt_flag:
            for file in files:
                self.__encrypt(file, password)
        else:
            for file in files:
                self.__decrypt(file, password)
                

    def summary(self, encrypt_flag: bool):
        """
        Displays the results of the utility’s operation.
        """

        if self.__skipped_count == 0 and self.__processed_count == 0:
            logger.warning(ErrorMessages.UTILITY_NOT_EXECUTED)          

        if encrypt_flag:
            logger.info(OutputMessages.SUMMARY_ENCRYPT)
            logger.info(OutputMessages.PROCESSED_COUNT.format(
                count=self.__processed_count
            ))
        else:
            logger.info(OutputMessages.SUMMARY_DECRYPT)
            logger.info(OutputMessages.PROCESSED_COUNT.format(
                count=self.__processed_count
            ))

        if self.__skipped_count:
            logger.warning(OutputMessages.SKIPPED_COUNT.format(
                count=self.__skipped_count
            ))
            for file_path, reason in self.__skipped_files:
                logger.warning(OutputMessages.SKIPPED_FILE.format(
                    reason=reason,
                    file_path=file_path
                ))


    def __generate_key(self, password: str, salt: bytes) -> bytes:
        """
        Generates a 32-byte key from the password and salt using PBKDF2-HMAC-SHA256.
        """
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,  # key length in bytes
            salt=salt,
            iterations=100000,
        )
        # encode the key using URL-safe Base64 for Fernet compatibility
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))


    def __encrypt(self, source: Path, password: str):
        """
        Encrypts the file in place without changing its path.
        """

        if source.is_symlink():
            self.__skipped_files.append((source, ErrorMessages.SYMLINK_NOT_ALLOWED)) 
            self.__skipped_inc()
            return

        try:
            with open(source, 'rb') as f:
                if f.read(len(self.__signature)) == self.__signature:
                    self.__skipped_files.append((source, ErrorMessages.FILE_ALREADY_ENCRYPTED))
                    self.__skipped_inc()
                    return
                f.seek(0)
                data = f.read()
        except PermissionError:
            self.__skipped_files.append((source, ErrorMessages.NO_READ_PERMISSION))
            self.__skipped_inc()
            return
        except Exception as e:
            self.__skipped_files.append((source, 
                                         ErrorMessages.UNKNOWN_ERROR.format(
                                             error=e
                                         )))
            self.__skipped_inc()
            return

        salt = os.urandom(16)
        key = self.__generate_key(password, salt)
        f = Fernet(key)
        encrypted_data = f.encrypt(data)

        try:
            with open(source, 'wb') as f_out:
                f_out.write(self.__signature)
                f_out.write(salt)
                f_out.write(encrypted_data)
                self.__processed_inc()
        except PermissionError:
            self.__skipped_files.append((source, ErrorMessages.NO_WRITE_PERMISSION))
            self.__skipped_inc()
            return
        except Exception as e:
            self.__skipped_files.append((source, 
                                         ErrorMessages.UNKNOWN_ERROR.format(
                                             error=e
                                         )))
            self.__skipped_inc()
            return


    def __decrypt(self, source: Path, password: str):
        """
        Decrypts the file in place.
        """

        if source.is_symlink():
            self.__skipped_files.append((source, ErrorMessages.SYMLINK_NOT_ALLOWED))
            self.__skipped_inc()
            return

        try:
            with open(source, 'rb') as f:
                if f.read(len(self.__signature)) != self.__signature:
                    self.__skipped_files.append((source, ErrorMessages.FILE_NOT_ENCRYPTED))
                    self.__skipped_inc()
                    return
                salt = f.read(16)
                encrypted_data = f.read()
        except PermissionError:
            self.__skipped_files.append((source, ErrorMessages.NO_READ_PERMISSION))
            self.__skipped_inc()
            return
        except Exception as e:
            self.__skipped_files.append((source, 
                                         ErrorMessages.UNKNOWN_ERROR.format(
                                             error=e
                                         )))
            self.__skipped_inc()
            return


        key = self.__generate_key(password, salt)
        f = Fernet(key)
        try:
            data = f.decrypt(encrypted_data)

            try:
                with open(source, 'wb') as f_out:
                    f_out.write(data)
                    self.__processed_inc()
            except PermissionError:
                self.__skipped_files.append((source, ErrorMessages.NO_WRITE_PERMISSION))
                self.__skipped_inc()
                return
            except Exception as e:
                self.__skipped_files.append((source, 
                                            ErrorMessages.UNKNOWN_ERROR.format(
                                                error=e
                                            )))
                self.__skipped_inc()
                return

        except InvalidToken:
            self.__skipped_files.append((source, ErrorMessages.BAD_PASSWORD))
            self.__skipped_inc()
            return
        except Exception as e:
            self.__skipped_files.append((source, 
                                         ErrorMessages.UNKNOWN_ERROR.format(
                                             error=e
                                         )))
            self.__skipped_inc()
            return


def main():

    util_name = Path(__file__).parent.name

    parser = argparse.ArgumentParser(util_name)
    parser.add_argument('-s', '--source', required=True, help=HelpMessages.SOURCE_HINT)
    parser.add_argument('-p', '--password', required=True, help=HelpMessages.PASSWORD_HINT)
    parser.add_argument('-e', '--encrypt', action='store_true', help=HelpMessages.ENCRYPT_HINT)

    args = parser.parse_args()
    raw_source = Path(args.source)
    password = args.password
    encrypt_flag = args.encrypt 

    source = raw_source.resolve()
    home = Path.home().resolve()
    app_dir = Path(__file__).resolve().parent

    if not source.is_relative_to(home):
        parser.error(ParserMessages.PATH_NOT_HOME_DIR)

    if app_dir.is_relative_to(source):
        parser.error(ParserMessages.PATH_TO_APP_DIR)

    if raw_source.is_symlink():
        parser.error(ParserMessages.SYMLICK_PATH)

    if not source.is_dir():
        parser.error(ParserMessages.PATH_NOT_EXISTING)

    encrypter = Encrypter()
    encrypter.cryptowalk(source, password, encrypt_flag)
    encrypter.summary(encrypt_flag)


if __name__ == '__main__':
    main()