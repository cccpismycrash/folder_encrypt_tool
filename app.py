import argparse
from pathlib import Path

from encrypter import Encrypter

from messages import ParserMessages, HelpMessages


def main():

    util_name = Path(__file__).parent.name

    parser = argparse.ArgumentParser(
        prog=util_name,
        description=HelpMessages.DESCRIPTION,
        epilog=HelpMessages.EPILOG                             
    )

    parser.add_argument('-s', '--source', help=HelpMessages.SOURCE_HINT)
    parser.add_argument('-p', '--password', help=HelpMessages.PASSWORD_HINT)
    parser.add_argument('-e', '--encrypt', action='store_true', help=HelpMessages.ENCRYPT_HINT)
    parser.add_argument('--set-sign', help=HelpMessages.SET_SIGN_HINT)

    args = parser.parse_args()
    
    signature = args.set_sign

    if signature:
        Encrypter.update_signature(signature)
        return

    if args.source is not None:
        raw_source = Path(args.source)
    else:
        raw_source = None
    
    password = args.password
    encrypt_flag = args.encrypt 

    if password is None and raw_source is None:
        parser.error(ParserMessages.PASSWORD_AND_SOURCE_MISSING)
    elif password is None:
        parser.error(ParserMessages.PASSWORD_MISSING)
    elif raw_source is None:
        parser.error(ParserMessages.SOURCE_MISSING)

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
    encrypter.set_signature()
    encrypter.cryptowalk(source, password, encrypt_flag)
    encrypter.summary(encrypt_flag)


if __name__ == '__main__':
    main()