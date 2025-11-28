# MEDIACH ( 2ch / arhivach images & videos downloader )

The fast and simple downloader for 2ch & arhivach threads that you have been missing.

```console
$ git clone https://github.com/khylko98/mediach.git
```

or

```console
$ git clone git@github.com:khylko98/mediach.git
```

## Usage

```console
$ cd mediach                                                                                                    # go to mediach folder
$ python -m venv venv                                                                                           # create virtual environment
$ source ./venv/bin/activate                                                                                    # activate virtual env.
$ pip install -U pip                                                                                            # update pip
$ pip install -r requirements.txt                                                                               # install dependencies
$ python main.py /home/user/2ch both https://2ch.org/b/res/322069228.html https://arhivach.vc/thread/1222333/   # download images and videos
```

The console response could look like this:

```console
$ [OK] Found 40 media files in https://2ch.org/b/res/322069228.html
$ ✓ Saved: https://2ch.org/b/src/322069228/17642861345180.mp4
$ ✓ Saved: https://2ch.org/b/src/322069228/17642693784040.png
$ ...
$ [OK] Found 38 media files in https://arhivach.vc/thread/1222333/
$ ✓ Saved: https://arhivach.vc/storage/f/a5/fa50c227e6f9110595af756fbze7f783.jpg
$ ✓ Saved: https://i.arhivach.vc/storage/6/ce/9cez6bf9b1cyub318c6182d2e5a021c0.mp4
$ ...
$
$ Time: 27.69 seconds.
```
