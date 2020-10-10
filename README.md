# instabot
An instagram bot to get hastags/users pictures, downloading images, sending comments or liking images.

example:

import instabot as ib

ib.load()

tag = ib.load_hashtag('love')

ib.save_image(tag[3])

will save the 3rd most recent image with the hashtag 'love'
