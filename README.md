# simple-kms-app
Simple KMS app written using Python for testing TDE feature on EnterpriseDB database platform.

## Prerequisite
- Python 3.x
- Python 3.x-venv
- sqlite3

## Installation
Install some required packages. If using RHEL operating system, use the following command.
```bash
yum -y install python3 sqlite wget unzip netcat
```

Create Python virtual environments using `venv`.
```bash
python3 -m venv /PATH/TO/simple-kms-app
```

Download as `.zip` and extract it inside Python virtual environments directory.
```bash
wget https://github.com/abdulazizm41/simple-kms-app/archive/refs/heads/main.zip
unzip ./main.zip
mv simple-kms-app-main/* /PATH/TO/simple-kms-app
```

Activate Python virtual environments, upgrade `pip`, then install `requirements.txt`.
```bash
cd /PATH/TO/simple-kms-app
source ./bin/activate
pip install --upgrade pip
pip install -r ./requirements.txt
```

Run the app. By default, it listens to all addresses on the machine (`0.0.0.0`) and port `8000`.
```bash
python3 ./simple-kms-app.py
```

Or run the app in the background.
```bash
python3 ./simple-kms-app.py > /PATH/TO/simple-kms-app.log 2>&1 &
```

## API Reference
#### Encrypt plaintext
```bash
POST /encrypt
```
| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `payload` | `string` | **Required**. Plaintext to be encrypted. |

#### Decrypt encrypted text
```bash
POST /decrypt
```
| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `payload` | `string` | **Required**. Encrypted text to be decrypted. |

## Usage (Basic)
#### Encrypt
```bash
curl -XPOST "http://127.0.0.1:8000/encrypt" \
-H "Content-Type: application/json" \
-d'{"payload": "Hello World!"}'
```

#### Decrypt
Adjust the `payload` with the previously obtained encryption results.
```bash
curl -XPOST "http://127.0.0.1:8000/decrypt" \
-H "Content-Type: application/json" \
-d'{"payload": "EDB20241007014857AeMgNHzVsy/cgF3U3ZrM8A=="}'
```

## Usage (Advanced)
The scripts for encryption and decryption are provided in the `scripts` directory, named `encrypt.sh` and `decrypt.sh` respectively. By default, it points to the ip `127.0.0.1` and port `8000`. Sample data is also provided in the `samples` directory. The `key.bin` file is a sample of encryption key in plain form, utilized by the TDE feature on the EnterpriseDB platform database.

#### Encrypt
```bash
# raw.txt
cat ./samples/raw.txt | base64 | /usr/bin/sh ./scripts/encrypt.sh > ./samples/raw.txt.enc
  
# key.bin
cat ./samples/key.bin | base64 | /usr/bin/sh ./scripts/encrypt.sh > ./samples/key.bin.enc
```

#### Decrypt
```bash
# raw.txt.enc
/usr/bin/sh ./scripts/decrypt.sh $(cat ./samples/raw.txt.enc) | base64 -di

# key.bin.enc
/usr/bin/sh ./scripts/decrypt.sh $(cat ./samples/key.bin.enc) | base64 -di
```

## Usage (EnterpriseDB TDE)
TDE features are available starting from EDB version 15 and up. To use this `simple-kms-app` together with EDB, pass the command into `--key-wrap-command` and `--key-unwrap-command` when initializing database for the first time. Below command is tested using EDB version 16.

#### Initialize the database
```bash
initdb -A scram-sha-256 -D $PGDATA -k -U enterprisedb -W --data-encryption \
--key-wrap-command='base64 | /usr/bin/sh /PATH/TO/scripts/encrypt.sh > %p' \
--key-unwrap-command='/usr/bin/sh /PATH/TO/scripts/decrypt.sh $(cat %p) | base64 -di'
```

#### How is data stored on disk with TDE?
In this example, the data in the `tbfoo` table is encrypted. `The pg_relation_filepath` function locates the data file corresponding to the `tbfoo` table.
```
insert into tbfoo values ('abc','123');
INSERT 0 1

select pg_relation_filepath('tbfoo');

 pg_relation_filepath
----------------------
 base/5/16416
```

Grepping the data looking for characters doesn't return anything. Viewing the last five lines returns the encrypted data.
```
$ hexdump -C 16416 | grep abc
$

$ hexdump -C 16416 | tail -5
00001fc0  c8 0f 1d c8 9a 63 3d dc  7d 4e 68 98 b8 f2 5e 0a  |.....c=.}Nh...^.|
00001fd0  9a eb 20 1d 59 ad be 94  6e fd d5 6e ed 0a 72 8c  |.. .Y...n..n..r.|
00001fe0  7b 14 7f de 5b 63 e3 84  ba 6c e7 b0 a3 86 aa b9  |{...[c...l......|
00001ff0  fe 4f 07 50 06 b7 ef 6a  cd f9 84 96 b2 4b 25 12  |.O.P...j.....K%.|
00002000
```

## Disclaimer
This script is made for testing purposes only. I do not guarantee its security features. SSL is not supported yet. It is not related to and does not cooperating with EnterpriseDB. For KMS that is officially supported by EnterpriseDB, you can see the official EDB documentation.
 - [EDB Docs - Transparent Data Encryption](https://www.enterprisedb.com/docs/tde/latest/)
 - [EDB Docs - Securing the data encryption key](https://www.enterprisedb.com/docs/tde/latest/key_stores/)

## Authors
- [@abdulazizm41](https://www.github.com/abdulazizm41)
