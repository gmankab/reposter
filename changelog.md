# changelog

## future plans

- restreaming

- recording streams

- chunk by chunk downloading and uploading very big files without saving them on disk

- the ability to specify which messages will not be reposted using pyrogram filters

## known bugs

- hyperlinks not supported
- forwarded messages are reposted without author

## 22.4.13

- fixed architecture issue caused crash

## 22.4.12

- fixed app updating

## 22.4.10

- fixed crash

## 22.4.7

- fixed error when get wrong chat after /repost command

## 22.4.4

- fixed bug with config path

## 22.4.3

- fixed app updating

## 22.4.2

- added /repost_single command
- added ability to pass config path as command line argument

## 22.4.1

removed extra logs

## 22.4.0

- added /repost command, it will repost all messages starting from specified one

## 22.3.7

- fixed app updating

## 22.3.0

- updated readme
- changed download links, old links disabled
- now when you updating app windows launchers updates too
- python version updated to 3.10.8

## 22.2.3

- added "notifications_delay" parameter in config

## 22.2.2

- fixed bug with reposting wrong message

## 22.2.1

- now notifications will be sent every 3 seconds instead of 5

## 22.2.0

- added support for webk links
- added notifications for streams

## 22.1.22

- fixed crash in termux

## 22.1.21

- fixed script version checking

## 22.1.20

- fixed bug with app updating

## 22.1.17

- now updating all libs with apps

## 22.1.16

- now using [curses](https://docs.python.org/3/howto/curses.html) instead of [pynput](https://pypi.org/project/pynput/) for terminal interactive input, now gnome-terminal supported

- fixed some typos

## 22.1.15

- fixed crash when session expired

## 22.1.14

- fixed reposting polls

## 22.1.13

- updated easyselect lib

## 22.1.12

- another time fixed error when message deleted but was not reposter and was not saved in `msg_history.yml`

## 22.1.11

- now instead of text of a message reposter saving text hash in `msg_history.yml`

- fixed error when message deleted but was not reposter and was not saved in `msg_history.yml`

## 22.1.10

- fixed typo

## 22.1.9

- fixed forwarding posts with long captions

## 22.1.8

- fixed printing and logging errors

## 22.1.7

- now all console logs sending in logs chat after restart

## 22.1.6

- link to changelog sends in logs chat if update found

## 22.1.5

- now shows link to changelog if update found

- links in logs are cleaner, just t.me instead of https://t.me

## 22.1.4

- updated wide logo on pypi and github

## 22.1.3

- added ability to disable saving edited messages history

## 22.1.2

- typo fix

## 22.1.1

- now can edit and mark as deleted 100 latest messages instead 5

## 22.1.0

- deleted massages now marked as deleted but not deleting

- added message editing history but when source chat is not restricted and target chat is a chanel and has linked chat

- added ability to check updates on start and ability to update app using pip

- reposter no longer reacts to a message about a person joining a chat, changing the name of the chat, etc

- default config path and cache path changed so that files are not deleted during app update

- now all errors writing to error.txt file and sending to logs chat

- fixed error FloodWait: Telegram says: [420 FLOOD_WAIT_X] - A wait of X seconds is required (caused by "messages.CheckChatInvite")

- fixed looped start with non-english folder names in windows launcher

- fixed app restart method in windows launcher

- python version updated from 3.10.6 to 3.10.7 in windows launcher

- removed useless prints in chat

## 22.0.3

- fixed crash when logs chan not specified and you trying to kick any member from any chat

## 22.0.2

- fixed start on windows

- fixed tgcrypto missing error

## 22.0.0

- [backupper](https://github.com/gmankab/backupper) - legacy version of this script, no longer supported

- name changed from backupper to reposter

- all code fully rewritten

- all settings can be changed directly in telegram, no need to edit `config.yml` manually anymore

- logs are readable now

- logs are only in telegram now, not in terminal

- progress of file downloading/uploading now printed in logs

- added support of in memory downloading/uploading for files up to 100 mb

- telegram session data now stored in config.yml

- added support of messages with links, locations, stickers, venues

- added support of messages with captions longer than 1024 symbols

- now reposter on pypi.org

- fixed bug with square videos on ios client

- recursive reposts support: source -> target1 -> target2 -> target3
