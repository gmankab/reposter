# changelog

## known bugs

- looped start with non-english folder names on windows

- edited or deleted messages are ignored

## future plans

- restreaming

- recording streams

- support of editing and deleting messages

- chunk by chunk downloading and uploading very big files without saving them on disk

- the ability to specify which messages will not be reposted using pyrogram filters

## 22.0.3

- fixed crash when logs chan not specified and you trying to kick any member from any chat

## 22.0.2

- fixed start on windows

- fixed tgcrypto missing error

## 22.0

- [backupper](https://github.com/gmankab/backupper) - legacy version of this script, no longer supported

- name changed from backupper to reposter

- all code fully rewritten

- all settings can be changed directly in telegram, no need to edit `config.yml` manually anymore

- logs are readable now

- logs are only in telegram now, not in terminal

- downloading or uploading progress now printing in logs

- telegram session data now stored in config.yml

- added support of messages with links, locations, stickers, venues

- added support of messages with captions longer than 1024 symbols

- now reposter on pypi.org

- fixed bug with square videos on ios client

- recursive reposts support: source -> target1 -> target2 -> target3
