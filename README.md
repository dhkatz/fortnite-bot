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

General Requirements
------------

Please see the requirements.txt for more of the packages required.

* Python 3.6+
* discord.py[voice] 1.0.0a0+ (Rewrite)