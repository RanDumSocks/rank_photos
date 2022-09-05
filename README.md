Fork of a [fork](https://github.com/vodboi/rank_photos) of [the original](https://github.com/weegreenblobbie/rank_photos)

### Additions
- Ability to stop ranking mid-round by sending a SIGINT signal (ctrl-c in cmd window)
- New `-d` argument which specifies where the cached data should be loaded/saved
- Multiple folder support
  - When having multiple folders as an argument, default cache data is saved in the common root of all folders.
  - Filenames are relative to the common root

### Possible future additions
- Algorithm to match up photos intelligently, resulting in quicker results
  - Would determine based on number of matches on a photo, and overall ELO
