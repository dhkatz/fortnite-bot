Fortnite-Bot
===================

[![forthebadge](http://forthebadge.com/images/badges/made-with-python.svg)](http://forthebadge.com)
[![forthebadge](http://forthebadge.com/images/badges/compatibility-club-penguin.svg)](http://forthebadge.com)


A Discord Bot built for use specifically in Fortnite related Discord servers. Made with hate and [discord.py](https://github.com/Rapptz/discord.py).
This bot is not designed to be setup by anyone else, but it's design intention is easy to understand.

Commands List (WIP)
-------------------
**Info:** Currently each command is prefixed with a period (.) Support for per-server prefixes coming within a couple days.

### PartyBus ###

Command and Aliases | Description | Usage
----------------|--------------|-------
`.duo` | Return duo stats for a player or yourself using Partybus.gg. | `.duo`, `.duo ImTheMyth`
`.solo` | Return solo  stats for a player or yourself using Partybus.gg. | `.solo`, `.solo ImTheMyth`
`.squad` | Return squad stats for a player or yourself using Partybus.gg. | `.squad`, `.squad ImTheMyth`
`.ign` |Tag your Fortnite IGN to your Discord account. Surround names with spaces in quotes. Empty to see current. | `.ign`, `.ign ImTheMyth`
`.stats` | Returns a player's stats from PartyBus.gg | `.stats DoctorJew`
`.lpg` | Get a player's last played game stats from PartyBus.gg | `.lpg DoctorJew`, `.lpg`

### General ###

Command and Aliases | Description | Usage
----------------|--------------|-------
`.info` | Returns information about the bot. | `.info`
`.lfg` | Are you looking for a game? | `.lfg`
`.bug` | Where to report a bug found in Fortnite. | `.bug`
`.support` | Do you need Epic Games support? | `.support`
`.prefix` | Get the command prefix of this server. | `.prefix`

### Reddit ###

Command and Aliases | Description | Usage
----------------|--------------|-------
`.reddit sticky` | Get the stickied posts from /r/Fortnite or /r/FortniteBR | `.reddit sticky fortnite`, `.reddit sticky fortnitebr`
`.reddit official` | Get official posts from Epic Games currently on the front page. | `.reddit official`

### Settings ###

WIP

General Requirements
------------

Please see the requirements.txt for more of the packages required.

* Python 3.6+
* discord.py[voice] 1.0.0a0+ (Rewrite)

Autorestarting on Linux
-----------------------

This guide assumes that your Linux distribution uses systemd (Example: Ubuntu 15.04 or newer). I am also assuming you have cloned the bot into /home/username/fortnite-bot (where username is some username you chose for the bot account).

Run this command in terminal:
`sudo nano /etc/systemd/system/fortnite.service`

Next, paste the following script, replace, `username` with your linux account name and `usergroup` with your user's group (usually the same as the username, but you can check with `groups username` in the terminal.)

```bash
[Unit]
Description=fortnite-bot
After=multi-user.target
[Service]
WorkingDirectory=/home/username/fortnite-bot
User=username
Group=usergroup
ExecStart=/usr/bin/python /home/username/fortnite-bot/bot.py
Type=idle
Restart=always
RestartSec=15

[Install]
WantedBy=multi-user.target
```

Save with CTRL+O.

You can now start the bot using
`sudo systemctl start fortnite.service`

If you want the bot to start automatically on boot, you can do `sudo systemctl enable fortnite.service`

If you need to view the bot's log, you can do `sudo journalctl -u fortnite.service`

Other available commands:
`sudo systemctl stop fortnite.service`
`sudo systemctl restart fortnite.service`