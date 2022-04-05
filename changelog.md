# contents

- [2.1](#21)
- [2.0](#20)

## 2.2

- removed ability to input data in config.yml directly from script because it was difficult and took up most of the code, now you can only do it yourself in a text editor
- removed ability to backup old messages
- fixed some typos
- fixed a bug due to which if you passed an argument with the path for the config to a bat file, it was lost and not passed to the python script
- fixed bug due to which files with the same name overwrite each other
- fixed bug with duplicate messages
- config become more detailed
- added ability to backup multiple chats
<!-- - added ability to just forward message instead of downloading it to the storage -->
- added update checker
- added ability to turn on automatic updates
- most of the code has been rewritten, cleaned up and optimized

## 2.1

- fixed remembering the last message
- fixed backupping messages with multiple media
- now the media is not separated from the caption
- now script automatically restarts if crashes
- Added multiconfig support. Just specify path to your config file after `backupper` executable in your terminal command or `.bat` or `.sh` script. Example: `backupper.py my_new_config.yml` or `python backupper.bat my_new_config.yml`
- added automatic sending bugreports to "saved messages" so then you can forward it to developer
- added much more comments to config file
- added option for don't close program after backupping messages and wait for new messages
- added ability to just run batch file on windows without installing python
- most of the code has been rewritten, cleaned up and optimized
- you can [compare this code with previous version 2.0](https://github.com/gmankab/backupper/compare/5400581431cd98b55fe4c1ab359857b418db3724...55de634ac3ddea494c24bc550213e67e37b53556#diff-686181f4d0f8e0a0d2b779c9a242a53d0794f3b9d1cb1513255a8930b8ab0372)

## 2.0

- initial release
