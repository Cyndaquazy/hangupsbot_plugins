# Hangupsbot Plugins #

This repository contains the various [HangupsBot](https://github.com/hangoutsbot/hangoutsbot) plugins that I've written.

### Plugins ###

#### `timeme` ####

**Usage**: `/timeme TIMESTRING`, `/timer TIMESTRING`, or `/bot timeme TIMESTRING`.

A rudimentary time reporting plugin that adds the `timeme` command with aliases `/timer` and `/timeme`.  

`TIMESTRING` is any datetime string of the format `MM/DD/[YY]YY HH:MM[:SS] AM/PM +HHMM`.
The date, AM/PM, and timezone offset (+HHMM) are optional: the date and offset respectively default to the
current date and the bot's default timezone as given in the configuration file, whereas the time is assumed to
be in 24-hour format without the `AM/PM`. The plugin also accepts the ISO 8601-compliant format
`YYYY-MM-DD HH:MM:SS+HHMM` where all parts are required.

This plugin has one **configuration entry**: `timeme.default_tz`, which is a list of the `[hour_offset, minute_offset]`
of the default timezone. The initial values are `[0, 0]`, corresponding to the UTC/GMT offset, &pm;0000.

-----

### Installation ###

To install one of these plugins into your bot, copy the base Python file and any supporting files into the `plugins` directory of your bot's installation (usually `hangupsbot/plugins`), maintaining hierarchies, and add the plugin to the list of active plugins in the bot's configuration.
