# Encrypt Folder Tool

Консольная утилита для шифрования и дешифрования файлов внутри указанной директории.

Для шифрования используется **Fernet**, а ключ формируется из пользовательского пароля с помощью **PBKDF2-HMAC-SHA256** и случайно сгенерированной соли.

Файлы шифруются и расшифровываются **на месте**, без изменения их имени и расположения.

## Постановка задачи
Реализовать защиту данных пользовательских папок и файлов, находящихся в
папке, а также подпапках путем шифрования. Для доступа к данным исходной
папке необходимо выполнить дешифрование.

## Используемый инструментарий

- **Python 3.12** – язык реализации утилиты.
- **cryptography** – библиотека для реализации криптографических операций.
- **Fernet** – симметричное аутентифицированное шифрование файлов.
- **PBKDF2-HMAC-SHA256** – получение ключа шифрования из пользовательского пароля.
- **pathlib** – работа с путями и рекурсивный обход файловой системы.
- **argparse** – обработка аргументов командной строки.
- **os** – генерация криптографически стойкой случайной соли.
- **base64** – кодирование ключа в URL-safe Base64.

## Требования

* Python 3.12+
* библиотека `cryptography`

Установка:
```bash
git clone <URL репозитория>
cd <имя репозитория>
pip install -r requirements.txt
```

## Использование

```bash
python -m app [-h] [-s SOURCE] [-p PASSWORD] [-e] [--set-sign SET_SIGN]
```

### Аргументы

```text
  -h, --help            show this help message and exit
  -s, --source SOURCE   path to source directory
  -p, --password PASSWORD
                        password for encryption or decryption
  -e, --encrypt         encrypt files instead of decrypting
  --set-sign SET_SIGN   set a new file encryption signature stored in .sign file in app directory
```

Если флаг `-e` не указан, программа работает в режиме дешифрования.

## Примеры использования

1. Для шифрования всех файлов внутри директории и его поддиректорий:

    ```bash
    python -m app -s ./data -p password123 -e
    ```

    Ответ:
    ```bash
    2026-10-01 01:49:45 INFO        folder_encrypt_tool: [+] Encryption operation completed.
    2026-10-01 01:49:45 INFO        folder_encrypt_tool: [+] Processed: 3.
    ```

2. Для дешифрования файлов:

    ```bash
    python -m app -s ./data -p password123
    ```

    Ответ:
    ```bash
    2026-10-01 01:50:24 INFO        folder_encrypt_tool: [+] Decryption operations completed.
    2026-10-01 01:50:24 INFO        folder_encrypt_tool: [+] Processed: 3.
    ```


## Формат зашифрованного файла:

```text
+----------------+----------------+-------------------------+
| Signature      | Salt           | Fernet encrypted data   |
+----------------+----------------+-------------------------+
| ? bytes        | 16 bytes       | variable                |
+----------------+----------------+-------------------------+
```

Сигнатура не определена по умолчанию, перед первым использованием необходимо установить собственную сигнатуру через `--set-sign`.


## Генерация ключа

Ключ шифрования генерируется из пользовательского пароля с помощью алгоритма PBKDF2-HMAC-SHA256.

Параметры генерации ключа:

```text
Algorithm:   SHA-256
Key length:  32 bytes
Salt length: 16 bytes
Iterations:  100000
```

После генерации 32-байтный ключ кодируется с помощью URL-safe Base64.

## Ограничения

Утилита может работать только с директориями, расположенными внутри домашней директории пользователя.

Нельзя использовать:

* директории за пределами домашней директории;
* директорию, содержащую саму утилиту;
* символическую ссылку в качестве исходной директории.

Символические ссылки на файлы внутри обрабатываемой директории также пропускаются.

## Структура проекта

```text
project/
├── app.py
├── encrypter.py
├── logger.py
├── messages.py
├── README.md
└── requirements.txt
```

Логика шифрования находится в классе `Encrypter`, при его реализации использовался паттерн **Singleton**.

Логика приложения находится в модуле `app.py`.


## Тестирование

Тесты проводились в Windows 11 Pro 25H2. Тесты также можно адаптировать для UNIX-подобных ОС.

Все указанные команды необходимо передавать приложению через CLI (`python -m app ...`), если командам явно не указано другое.

Перед тестами необходимо:
1. Создать тестовую директорию (например, `/test_dir`) и, опционально, поддиректории.
2. Наполнить тестовую директорию и её поддиректории любыми файлами.
3. Задать собственную сигнатуру для зашифрованных файлов через `--set-sign qwerty`

После каждого теста необходимо:
1. Расшифровать все файлы.

Описание тест-кейсов по группам:
1. Блок UC-1.x состоит из позитивных тестов, направлен на проверку штатной работы утилиты.
2. Блок UC-2.x проверяет класс Encryption и его логику обработки нештатных ситуаций.
3. Блок UC-3.x проверяет логику консольного приложения и его логику обработки некорректных аргументов.
4. Блок UC-4.x проверяет два сценария: (1) попытка расшифровать файл при новой сигнатуре, когда шифрование происходило при старой сигнатуре; (2) попытка шифрования уже "зашифрованной" директории, куда добавили новый незашифрованный файл. 


|id| Test case | Test steps | Ожидаемый результат |
|---|---|---|---|
|UC-1.1| Зашифровать содержимые файлы в директории | 1. `-p password123 -s ./test_dir -e` | `INFO        folder_encrypt_tool: [+] Encryption operation completed.`<br>`INFO        folder_encrypt_tool: [+] Processed: 3.` |
|UC-1.2| Расшифровать содержимые файлы в директории | 1. `-p password123 -s ./test_dir` | `INFO        folder_encrypt_tool: [+] Decryption operations completed.`<br>`INFO        folder_encrypt_tool: [+] Processed: 3.`  |
|UC-1.3| Установить новую сигнатуру | 1. `--set-sign qwerty` | `INFO        folder_encrypt_tool: [+] New signature has been set.` |
|UC-2.1| Файл уже зашифрован | 1. `-p password123 -s ./test_dir -e`<br>2. `-p password123 -s ./test_dir -e` | `INFO        folder_encrypt_tool: [+] Encryption operation completed.`<br>`INFO        folder_encrypt_tool: [+] Processed: 0.`<br>`WARNING     folder_encrypt_tool: [!] Skipped: 3.`<br>`WARNING     folder_encrypt_tool: [!] File is already encrypted: ...\test_dir\dfsafs.txt`<br>`WARNING     folder_encrypt_tool: [!] File is already encrypted: ...\test_dir\1asd\3421f.xlsx`<br>`WARNING     folder_encrypt_tool: [!] File is already encrypted: ...\test_dir\1asd\fasdfasd.txt` |
|UC-2.2| Файл не зашифрован | 1. `-p password123 -s ./test_dir`<br>2. `-p password123 -s ./test_dir` | `INFO        folder_encrypt_tool: [+] Decryption operations completed.`<br>`INFO        folder_encrypt_tool: [+] Processed: 0.`<br>`WARNING     folder_encrypt_tool: [!] Skipped: 3.`<br>`WARNING     folder_encrypt_tool: [!] File is not encrypted or was encrypted by another utility: ...\test_dir\dfsafs.txt`<br>`WARNING     folder_encrypt_tool: [!] File is not encrypted or was encrypted by another utility: ...\test_dir\1asd\3421f.xlsx`<br>`WARNING     folder_encrypt_tool: [!] File is not encrypted or was encrypted by another utility: ...\test_dir\1asd\fasdfasd.txt`<br> |
|UC-2.3| Неправильный пароль | 1. `-p password123 -s ./test_dir -e`<br>2. `-p qwerty123 -s ./test_dir` | `INFO        folder_encrypt_tool: [+] Decryption operations completed.`<br>`INFO        folder_encrypt_tool: [+] Processed: 0.`<br>`WARNING     folder_encrypt_tool: [!] Skipped: 3.`<br>`WARNING     folder_encrypt_tool: [!] Incorrect password or corrupted file: ...\test_dir\dfsafs.txt`<br>`WARNING     folder_encrypt_tool: [!] Incorrect password or corrupted file: ...\test_dir\1asd\3421f.xlsx`<br>`WARNING     folder_encrypt_tool: [!] Incorrect password or corrupted file: ...\test_dir\1asd\fasdfasd.txt` |
|UC-2.4| Нет прав на запись | 1. Открыть любой файл в `/test_dir` (кроме `.txt`)<br>2. `-p password123 -s ./test_dir -e`   | `INFO        folder_encrypt_tool: [+] Encryption operation completed.`<br>`INFO        folder_encrypt_tool: [+] Processed: 2.`<br>`WARNING     folder_encrypt_tool: [!] Skipped: 2.`<br>`WARNING     folder_encrypt_tool: [!] No write permission: ...\test_dir\1asd\3421f.xlsx`<br>`WARNING     folder_encrypt_tool: [!] No read permission: ...\test_dir\1asd\~$3421f.xlsx` |
|UC-2.5| Нет прав на чтение | 1. Создать в `/test_dir` файл MS Office<br>2. Открыть этот файл<br>3. `-p password123 -s ./test_dir -e`| `INFO        folder_encrypt_tool: [+] Encryption operation completed.`<br>`INFO        folder_encrypt_tool: [+] Processed: 2.`<br>`WARNING     folder_encrypt_tool: [!] Skipped: 2.`<br>`WARNING     folder_encrypt_tool: [!] No write permission: ...\test_dir\1asd\3421f.xlsx`<br>`WARNING     folder_encrypt_tool: [!] No read permission: ...\test_dir\1asd\~$3421f.xlsx` |
|UC-2.6| Ничего не было зашифровано/дешифровано | 1. Удалить все файлы и директории в `/test_dir`<br>2. `-p password123 -s ./test_dir -e`<br>*После теста:*<br> - *Вернуть удаленные файлы и директории в `/test_dir`*| `WARNING     folder_encrypt_tool: [!] Utility was not executed.` |
|UC-3.1| Получен симлинк | 1. Открыть консоль с правами администратора.<br>2. Перейти в консоли в `/test_dir`<br>3. `mklink /D "test_link" ".../folder_encrypt_tool/test_dir"`<br>4. `-p password123 -s ./test_dir/test_link -e`| `folder_encrypt_tool: error: source must not be a symbolic link` |
|UC-3.2| Получен путь за пределами домашней директории | 1. `-p password123 -s 'C:/Program Files' -e`| `folder_encrypt_tool: error: source must be inside the home directory` |
|UC-3.3| Получен путь с директорией проекта | 1. `-p password123 -s ./ -e`<br>или<br>2. `-p password123 -s ../ -e`<br>или<br>3. `-p password123 -s ../../ -e`| `folder_encrypt_tool: error: source must not contain the application directory` |
|UC-3.4| Получен несуществующий путь | 1. `-p password123 -s ./123test_dir123 -e` | `folder_encrypt_tool: error: source must be an existing directory` |
|UC-3.5| Нет пароля | 1. `-s ./test_dir -e` | `folder_encrypt_tool: error: password is missing` |
|UC-3.6| Нет пути | 1. `-p password123 -e` | `folder_encrypt_tool: error: source is missing` |
|UC-3.7| Нет пароли и пути | 1. `-e` | `folder_encrypt_tool: error: password and source are missing` |
|UC-4.1| Смена сигнатуры после шифрования | 1. `-p password123 -s ./test_dir -e`<br>2. `--set-sign ytrewq`<br>3. `-p password123 -s ./test_dir` | `INFO        folder_encrypt_tool: [+] Decryption operations completed.`<br>`INFO        folder_encrypt_tool: [+] Processed: 0.`<br>`WARNING     folder_encrypt_tool: [!] Skipped: 3.`<br>`WARNING     folder_encrypt_tool: [!] File is not encrypted or was encrypted by another utility: ...\test_dir\dfsafs.txt`<br>`WARNING     folder_encrypt_tool: [!] File is not encrypted or was encrypted by another utility: ...\test_dir\1asd\3421f.xlsx`<br>`WARNING     folder_encrypt_tool: [!] File is not encrypted or was encrypted by another utility: ...\test_dir\1asd\fasdfasd.txt` |
|UC-4.2| Шифрование новых файлов в директории после шифрования старых | 1. `-p password123 -s ./test_dir -e`<br>2. Добавляем в `/test_dir` новый файл `new_file.txt`<br>3. `-p password123 -s ./test_dir -e` | `INFO        folder_encrypt_tool: [+] Encryption operation completed.`<br>`INFO        folder_encrypt_tool: [+] Processed: 1.`<br>`WARNING     folder_encrypt_tool: [!] Skipped: 3.`<br>`WARNING     folder_encrypt_tool: [!] File is already encrypted: ...\test_dir\dfsafs.txt`<br>`WARNING     folder_encrypt_tool: [!] File is already encrypted: ...\test_dir\1asd\3421f.xlsx`<br>`WARNING     folder_encrypt_tool: [!] File is already encrypted: ...\test_dir\1asd\fasdfasd.txt` |

## Рекомендации
1. Не меняйте сигнатуру после шифрования файла. Чтобы расшифровать файлы с старой сигнатурой после смены сигнатуры, необходимо установить старую сигнатуру.
2. Можно добавять новые файлы в "зашифрованные" директории, после чего снова шифровать эти директории. Можно также шифровать новые файлы с другим паролем. Расшифровывать такие директории придется в несколько запусков утилиты (сколько паролей, столько и запусков). При каждом запуске будут расшифровываться файлы с валидным паролем, а остальные останутся нетронутыми.