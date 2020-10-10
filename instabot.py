from selenium import webdriver
from requests import get
from time import time, sleep
from time import ctime as format_time
from sys import argv
from hashlib import sha256
from os import path, mkdir
from sqlite3 import connect
from secrets import choice,randbelow

uname = ""
pword = ""
DB_NAME = 'st.db'
LOGIN = "https://www.instagram.com/accounts/login/"
HASHTAG = "https://www.instagram.com/explore/tags/"
ACTIVITY = "https://www.instagram.com/accounts/activity/"
INSTA = "https://www.instagram.com/"
IMAGE = "https://www.instagram.com/p/"
DIRECT = "https://www.instagram.com/direct/inbox/"
BASE = "images/"


# DATABASE FUNCTIONS
def insert_db(sql,args=()):
	try:
		db = connect(DB_NAME)
		cursor = db.cursor()
		try:
			cursor.execute(sql,args)
		except:
			log_action('ERROR: failed to execute INSERT statement')
		db.commit()
		db.close()
	except:
		print('ERROR: Failed to load database insert')
def select_db(sql,args=()):
	try:
		db = connect(DB_NAME)
		cursor = db.cursor()
		cursor.execute(sql,args)
		yield cursor.fetchone()
	except:
		log_action('ERROR: Failed to load database select')
	db.close()	

def log_action(action):
	print(action)
	insert_db('INSERT INTO actions VALUES(?,?)',(time(),action))

# SELENIUM CONTROL FUNCTIONS
def load():
	load_browser()
	login()

def load_browser():
	log_action ('LOADING SELENIUM: may take a few moments')
	global browser
	#browser = webdriver.Chrome('/usr/local/bin/chromedriver')
	browser = webdriver.Firefox()
	sleep(3)

def login():
	log_action('LOGIN: loading instagram account {}'.format(uname))
	browser.get(LOGIN)
	sleep(5)
	u = browser.find_element_by_name('username')
	p = browser.find_element_by_name('password')
	u.send_keys(uname)
	p.send_keys(pword)
	sleep(3)
	p.submit()
	sleep(5)

# LOAD ACTION FUNCTIONS
def load_user(username=uname):
	links = []
	try:
		browser.get(INSTA + username)
		sleep(5)
		if is_private() == True:
			log_action('ERROR: can not load user: ')
		for x in browser.find_elements_by_tag_name('a'):
			tmp = x.get_attribute('href')
			if '/p/' in tmp:
				links.append(tmp)
	except:
		log_action('ERROR: can not find user {}'.format(username))
	return links

def load_hashtag(tag):
	log_action('Loading hashtag: {}'.format(tag))
	browser.get(HASHTAG + tag)
	sleep(5)
	links = []
	tmp = browser.find_elements_by_tag_name('a')
	for x in tmp[9:]:
		if '/p/' in x.get_attribute('href'): 
			links.append(x.get_attribute('href'))
	return links

def load_messages():
	log_action('Loading Direct Messages')
	browser.get(DIRECT)
	sleep(4)
	tmp = browser.find_elements_by_tag_name('a')
	if len(tmp) < 1:
		return False
	inbox = []
	for x in tmp:
		attr = x.get_attribute('href')
		if '/direct/' in attr and not 'inbox' in attr:
			message = x.text.split('\n')
			message.append(attr)
			inbox.append(message)
	return inbox

def like_post(url):
	p_id = id_from_url(url)
	if check_like(url):
		return False
	try:
		browser.get(url)
		sleep(5)
		browser.find_element_by_class_name('fr66n').click()
		log_action('Liked post {}'.format(p_id))
		sleep(3)
		try:
			insert_db("INSERT INTO like_log VALUES(?,?)",(url,time()))
		except:
			log_action('ERROR: could not log like {}'.format(p_id))
	except:
		log_action('ERROR: could not like {}'.format(p_id))

def send_comment(url):
	p_id = id_from_url(url)
	if check_comment(url):
		log_action('ERROR: Comment already sent for this Image')
		return False
	log_action('Loading post: {}'.format(p_id))
	text = 'We love it!' # can be connected to gen_comment() function that will generate a comment.
	try:
		browser.get(url)
		sleep(6)
		browser.find_element_by_class_name('X7cDz').click()
		browser.find_element_by_class_name('Ypffh').send_keys(text)
		sleep(4)
		browser.find_element_by_class_name('Ypffh').submit()
		insert_db('INSERT INTO im_log VALUES(?,?,?)',(url,time(),text))
		db.commit()
		log_action('Comment sent: {}'.format(p_id))
	except:
		log_action('ERROR: can not post comment for {}'.format(p_id))
	return True

def check_comment(url):
	tmp = select_db('SELECT COUNT(*) FROM im_log WHERE id=?',(url,))
	return next(tmp)[0]
def check_like(url):
	tmp = select_db('SELECT COUNT(*) FROM like_log WHERE id=?',(url,))
	return next(tmp)[0]

def hide_dialog():
	buttons = browser.find_elements_by_tag_name('button')
	tmp = [x for x in buttons if x.text == 'Not Now']
	if len(tmp) > 0:
		tmp[0].click()

def is_private():
	tmp = browser.find_element_by_class_name('rkEop')
	if 'Private' in tmp:
		return True
	return False

# FILE SYSTEM FUNTIONS
def get_image(url):
	log_action("Loading image url")
	try:
		browser.get(url)
		sleep(5) 
		r = get(browser.find_elements_by_tag_name('img')[1].get_attribute('src'))
		return r.content
	except:
		log_action('Error: Could not download image content.')
	return None

def save_image(url):
	filename = BASE + id_from_url(url)
	if not path.exists(filename):
		try:
			with open(filename,'w+b') as file:
				file.write(get_image(url))
				log_action("Success: Image saved to disk as {}".format(filename))
		except:
			log_action("Error: Can not write the image to disk")
	else:
		log_action("Error: you already downloaded this image.")

# SMALL FUNCTIONS
def random(max):
	return randbelow(max)

def id_from_url(url):
	return url.split('/')[4]
