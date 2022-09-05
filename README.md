Fork of a [fork](https://github.com/vodboi/rank_photos) of [the original](https://github.com/weegreenblobbie/rank_photos)
refer to original for install instructions
other fork is for python 3 support

### Additions
- Ability to stop ranking mid-round by sending a SIGINT signal (ctrl-c in cmd window)
- New `-d` argument which specifies where the cached data should be loaded/saved
- Multiple folder support
  - When having multiple folders as an argument, default cache data is saved in the common root of all folders
  - Filenames are relative to the common root
- Escape now gracefully shuts down the program and saves progress
- New `-S` argument which enables an algorithm to match up photos intelligently, resulting in quicker results bassed on number of matches played and similar ELO scores
- New `-s` argument which plays a slideshow of the top ranked images first
  - Left and right arrow keys to go through images, up and down keys to skip 10 instead of 1
  - Press spacebar to open current image in file explorer
  - Escape exists the program
