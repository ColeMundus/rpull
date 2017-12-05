from concurrent.futures import ThreadPoolExecutor
from pprint import pprint
import urllib.request
import argparse
import requests
import json
import time
import sys
import os
import re

try: 
    from BeautifulSoup import BeautifulSoup
except ImportError:
    from bs4 import BeautifulSoup

parser = argparse.ArgumentParser()
parser.add_argument('url', help='Input url to download')
parser.add_argument('-q', '--quiet', action='store_true', help='Make program output silent')
parser.add_argument('-p', '--path', default='rips/', help='Destination download path')
parser.add_argument('-t', '--threads', type=int, default=20, help='Number of threads to use when downloading')
parser.add_argument('-o', '--overwrite', help='Overwrite files that are already downloaded')
parser.add_argument('--sfw', action='store_true', help='Restrict to SFW content')
parser.add_argument('--min-score', dest='min', type=int, help='Minimum score to download')
parser.add_argument('--max-score', dest='max', type=int, help='Mamimum score to download')
parser.add_argument('--progress', '--bar', '-b', action='store_true', help='Enable progress bar')
parser.add_argument('--author', help='Restrict to submission author')
args = parser.parse_args()

if args.path[-1] != '/':
	args.path += '/'

if not os.path.exists(args.path):
	os.makedirs(args.path)

if args.quiet:
	def print(*args):
		pass

def format_opts(url):
	if args.sfw:
		url += '&over_18=false'
	if args.min:
		url += '&score=>' + str(args.min-1)
	if args.max:
		url += '&score=<' + str(args.max+1)
	if args.author:
		url += '&author=' + args.author
	url += '&size=500'
	return url

executor = ThreadPoolExecutor(max_workers=args.threads)
futures = []
def reddit_download(sub):
	print('Subreddit:', sub)
	args.path += sub + '/'
	print('Download Path:', args.path)
	print('Download threads:', args.threads)
	if not os.path.exists(args.path):
		os.makedirs(args.path)
	url = sub
	r = json.loads(requests.get('https://api.pushshift.io/reddit/search/submission/?subreddit={}'.format(format_opts(url))).text)
	while len(r['data']) > 0:
		last = r['data'][-1]['created_utc']
		if args.progress:
			urls = tqdm([i['url'] for i in r['data']])
		else:
			urls = [i['url'] for i in r['data']]
		for x in urls:
			a = executor.submit(pull, x)
			futures.append(a)
		r = json.loads(requests.get('https://api.pushshift.io/reddit/search/submission/?subreddit={}'.format(format_opts(url) + '&before=' + str(last))).text)

def redd_download(url):
	p = args.path + url.split('/')[-1]
	if not os.path.isfile(p) or args.overwrite:
		try:
			urllib.request.urlretrieve(url, p)
		except Exception as e:
			try:
				print('[x]', str(e.code) + ':', url)
			except:
				print(e)
def v_redd_download(url):
	p = args.path + url.split('/')[-1] + '.mp4'
	if not os.path.isfile(p) or args.overwrite:
		try:
			urllib.request.urlretrieve(url + '/DASH_2_4_M', p)
		except Exception as e:
			try:
				print('[x]', str(e.code) + ':', url)
			except:
				print(e)
def reddituploads_download(url):
	url = re.sub('&amp;', '&', url)
	p = args.path + url.split('/')[-1].split('?')[0] + '.jpg'
	if not os.path.isfile(p) or args.overwrite:
		try:
			urllib.request.urlretrieve(url, p)
		except Exception as e:
			try:
				print('[x]', str(e.code) + ':', url)
			except:
				print(e)
def tumblr_download(url):
	p = args.path + url.split('/')[-1]
	if not os.path.isfile(p) or args.overwrite:
		try:
			urllib.request.urlretrieve(url, p)
		except Exception as e:
			try:
				print('[x]', str(e.code) + ':', url)
			except:
				if str(e.reason) == '[Errno -2] Name or service not known':
					print('[x] File Moved:', url)
				else:
					print(e)
def gfycat_download(url):
	g = re.findall('<noscript>.*</noscript>', requests.get('https://gfycat.com/' + url.split('/')[-1]).text)[1]
	g = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', g)
	url = g[2]
	p = args.path + url.split('/')[-1].split('?')[0]
	if not os.path.isfile(p) or args.overwrite:
		try:
			urllib.request.urlretrieve(url, p)
		except Exception as e:
			try:
				print('[x]', str(e.code) + ':', url)
			except:
				print(e)
def imgur_download(url):
	if 'i.imgur.com' in url:
		p = args.path + url.split('/')[-1].split('?')[0]
		if not os.path.isfile(p) or args.overwrite:
			try:
				urllib.request.urlretrieve(url, p)
			except Exception as e:
				try:
					print('[x]', str(e.code) + ':', url)
				except:
					print(e)
	if 'gifv' in url:
		p = args.path + url.split('/')[-1][:-1].split('?')[0]
		if not os.path.isfile(p) or args.overwrite:
			try:
				urllib.request.urlretrieve(url[:-1], p)
			except Exception as e:
				try:
					print('[x]', str(e.code) + ':', url)
				except:
					print(e)
	else:
		r = requests.get(url)
		img = BeautifulSoup(r.content, "html.parser", from_encoding="iso-8859-1").findAll('img', class_='post-image-placeholder')
		for l in img:
			l = 'https:' + l['src'].split('?')[0]
			if '/a/' in url or '/gallery/' in url:
				p = args.path + url.split('/')[-1].split('?')[0] + '/'
				if not os.path.exists(p):
					os.makedirs(p) 
				p += l.split('/')[-1]
			else:
				p = args.path + l.split('/')[-1].split('?')[0]
			if not os.path.isfile(p) or args.overwrite:
				try:
					urllib.request.urlretrieve(l, p)
				except Exception as e:
					try:
						print('[x]', str(e.code) + ':', l)
					except:
						print(e)
def pull(url):
	if 'imgur.com' in url:
		imgur_download(url)
	elif 'i.redd.it' in url:
		redd_download(url)
	elif 'v.redd.it' in url:
		v_redd_download(url)
	elif 'i.reddituploads.com' in url:
		reddituploads_download(url)
	elif 'media.tumblr.com' in url:
		tumblr_download(url)
	elif 'gfycat.com' in url:
		gfycat_download(url)
	else:
		print('[x] Not Supported:', url)
def test_type(url):
	if 'reddit.com/r/' in url:
		sub = re.findall('\/r\/\w*', url)[0][3:]
		print('Using Subreddit Downloader')
		reddit_download(sub)
	else:
		pull(url)

test_type(args.url)
