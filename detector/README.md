# Person detection and recognition using OpenCV


## Setup and running

Install [pyenv win](https://github.com/pyenv-win/pyenv-win)

```cmd
pyenv install 3.12.3
pyenv local 3.12.3
```

to setup virtual environment use the commands below

```cmd
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```


before running set the following environment variables
get the api_hash and app_id from https://my.telegram.org, under API Development
create channel and set the channel id (usually negative number)

```cmd
set TELEGRAM_APP_ID=?
set TELEGRAM_API_HASH=?
set TELEGRAM_CHANNEL_ID=?
```

to run the code use the command below
```cmd
venv\Scripts\python app.py
```

