# contents

- [2.1](#21)
- [2.0](#20)

## 2.1

- Added multiconfig support. Just specify path to your config file after `backupper` executable in your terminal command or `.bat` or `.sh` script. Example: `python backupper.py my_new_config.yml` or `python backupper.bat my_new_config.yml`
- added automatic sending bugreports to "saved messages" so then you can forward it to developer
- added much more comments to config file
- fixed backupping messages with multiple media
- now the media is not separated from the caption
- fixed remembering the last message
- added option for don't close program after backupping messages and wait for new messages
- most of the code has been rewritten, cleaned up and optimized
- you can [compare this code with previous version 2.0](https://github.com/gmankab/backupper/compare/5400581431cd98b55fe4c1ab359857b418db3724...55de634ac3ddea494c24bc550213e67e37b53556#diff-686181f4d0f8e0a0d2b779c9a242a53d0794f3b9d1cb1513255a8930b8ab0372)

## 2.0

- initial release
