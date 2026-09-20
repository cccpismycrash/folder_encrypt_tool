import argparse
import os
from pathlib import Path
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet, InvalidToken
import base64

class Encrypter:
           
    __instance = None
    __signature = b'AbramovEgor'

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance


    def cryptowalk(self, source: Path, password: str, encrypt_flag: bool):
        """
        Walks through the directory tree and encrypts or decrypts all files.
        """

        # extract files from the directory tree
        files = list()
        for root, _, filenames in source.walk():
            for filename in filenames:
                files.append(Path(root) / filename)

        skipped_files = list()

        # encrypt or decrypt files
        if encrypt_flag:
            for file in files:
                if file.is_symlink():
                    skipped_files.append((file, 'Symbolic links are not allowed'))
                    continue
                self.__encrypt(file, password, skipped_files)
        else:
            for file in files:
                if file.is_symlink():
                    skipped_files.append((file, 'Symbolic links are not allowed'))
                    continue
                self.__decrypt(file, password, skipped_files)

        # output
        processed = len(files) - len(skipped_files)
        operation = 'Encryption' if encrypt_flag else 'Decryption'

        print()

        if skipped_files:
            print(f'[+] {operation} completed.')
            print(f'    Processed: {processed}')
            print(f'    Skipped:   {len(skipped_files)}')

            print('\nSkipped files:')
            for file, reason in skipped_files:
                print('[!]', f'{reason}:', file)
        else:
            print(f'[+] {operation} completed successfully.')
            print(f'    Processed: {processed}')

        print()


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


    def __encrypt(self, source: Path, password: str, skipped_files: list):
        """
        Encrypts the file in place without changing its path.
        """

        try:
            with open(source, 'rb') as f:
                if f.read(len(self.__signature)) == self.__signature:
                    skipped_files.append((source, 'File is already encrypted'))
                    return
                f.seek(0)
                data = f.read()
        except PermissionError:
            skipped_files.append((source, 'No read permission'))
            return
        except Exception as e:
            skipped_files.append((source, f'Unknown error – {e}'))
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
        except PermissionError:
            skipped_files.append((source, 'No write permission'))
            return
        except Exception as e:
            skipped_files.append((source, f'Unknown error – {e}'))
            return


    def __decrypt(self, source: Path, password: str, skipped_files: list):
        """
        Decrypts the file in place.
        """

        try:
            with open(source, 'rb') as f:
                if f.read(len(self.__signature)) != self.__signature:
                    skipped_files.append((source, 'File is not encrypted or was encrypted by another utility'))
                    return
                salt = f.read(16)
                encrypted_data = f.read()
        except PermissionError:
            skipped_files.append((source, 'No read permission'))
            return
        except Exception as e:
            skipped_files.append((source, f'Unknown error – {e}'))
            return


        key = self.__generate_key(password, salt)
        f = Fernet(key)
        try:
            data = f.decrypt(encrypted_data)

            try:
                with open(source, 'wb') as f_out:
                    f_out.write(data)
            except PermissionError:
                skipped_files.append((source, 'No write permission'))
                return
            except Exception as e:
                skipped_files.append((source, f'Unknown error – {e}'))
                return

        except InvalidToken:
            skipped_files.append((source, 'Incorrect password or corrupted file'))
            return
        except Exception as e:
            skipped_files.append((source, f'Unknown error – {e}'))
            return


def main():
    parser = argparse.ArgumentParser('encrypt_folder_tool')
    parser.add_argument('-s', '--source', required=True, help='path to source directory')
    parser.add_argument('-p', '--password', required=True, help='password for encryption or decryption')
    parser.add_argument('-e', '--encrypt', action='store_true', help='encrypt files instead of decrypting')

    args = parser.parse_args()
    raw_source = Path(args.source)
    password = args.password
    encrypt_flag = args.encrypt 

    source = raw_source.resolve()
    home = Path.home().resolve()
    app_dir = Path(__file__).resolve().parent

    if not source.is_relative_to(home):
        parser.error("source must be inside the home directory")

    if app_dir.is_relative_to(source):
        parser.error("source must not contain the application directory")

    if raw_source.is_symlink():
        parser.error("source must not be a symbolic link")

    if not source.is_dir():
        parser.error("source must be an existing directory")

    encrypter = Encrypter()
    encrypter.cryptowalk(source, password, encrypt_flag)


if __name__ == '__main__':
    main()