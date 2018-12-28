# -*- coding: utf-8 -*-

"""
Nova web client
"""

import os
import re
import ssl
import sys
import urllib2
import xbmcaddon
from time import sleep
from urlparse import urlparse
from contextlib import closing
from elementum.provider import log, get_setting
from cookielib import LWPCookieJar
from urllib import urlencode
from utils import encode_dict

from xbmc import translatePath

try:
    ssl._create_default_https_context = ssl._create_unverified_context
except:
    log.debug("Skipping SSL workaround due to old Python version")

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 " \
             "(KHTML, like Gecko) Chrome/53.0.2785.21 Safari/537.36"
try:
    PATH_TEMP = translatePath("special://temp").decode(sys.getfilesystemencoding(), 'ignore')
except:
    PATH_TEMP = translatePath("special://temp").decode('utf-8')

if get_setting("use_opennic_dns", bool):
    import socket
    prv_getaddrinfo = socket.getaddrinfo
    dns_cache = {('nnm-club.lib', 80, 0, 1): [(2, 1, 0, '', ('81.17.30.22', 80))], ('rustorka.lib', 80, 0, 1): [(2, 1, 0, '', ('93.171.158.6', 80))], ('rutracker.lib', 80, 0, 1): [(2, 1, 0, '', ('195.82.146.214', 80))], ('rutor.lib', 80, 0, 1): [(2, 1, 0, '', ('185.191.239.206', 80))]}

    def new_getaddrinfo(*args):
        try:
            return dns_cache[args]
        except KeyError:
            res = prv_getaddrinfo(*args)
            dns_cache[args] = res
            return res

    socket.getaddrinfo = new_getaddrinfo


class Client:
    """
    Web client class with automatic charset detection and decoding
    """
    def __init__(self, info=None):
        self._counter = 0
        self._cookies_filename = ''
        self._cookies = LWPCookieJar()
        self.user_agent = USER_AGENT
        self.info = info
        self.proxy_url = None
        self.content = None
        self.status = None
        self.headers = dict()

        if get_setting("use_elementum_proxy", bool):
            elementum_addon = xbmcaddon.Addon(id='plugin.video.elementum')
            if elementum_addon and elementum_addon.getSetting('internal_proxy_enabled') == "true":
                self.proxy_url = "{}://{}:{}".format("http", "127.0.0.1", "65222")
                if info and "internal_proxy_url" in info:
                    self.proxy_url = info["internal_proxy_url"]

    @classmethod
    def _create_cookies(self, payload):
        return urlencode(payload)

    def _read_cookies(self, url=''):
        cookies_path = os.path.join(PATH_TEMP, 'nova')
        if not os.path.exists(cookies_path):
            try:
                os.makedirs(cookies_path)
            except Exception as e:
                log.debug("Error creating cookies directory: %s" % repr(e))
        self._cookies_filename = os.path.join(cookies_path, urlparse(url).netloc + '_cookies.jar')
        if os.path.exists(self._cookies_filename):
            try:
                self._cookies.load(self._cookies_filename)
            except Exception as e:
                log.debug("Reading cookies error: %s" % repr(e))

    def _save_cookies(self):
        try:
            self._cookies.save(self._cookies_filename)
        except Exception as e:
            log.debug("Saving cookies error: %s" % repr(e))

    def _good_spider(self):
        self._counter += 1
        if self._counter > 1:
            sleep(0.25)

    def cookies(self):
        """ Saved client cookies

        Returns:
            list: A list of saved Cookie objects
        """
        return self._cookies

    def open(self, url, language='en', post_data=None, get_data=None):
        """ Opens a connection to a webpage and saves its HTML content in ``self.content``

        Args:
            url        (str): The URL to open
            language   (str): The language code for the ``Content-Language`` header
            post_data (dict): POST data for the request
            get_data  (dict): GET data for the request
        """
        if not post_data:
            post_data = {}
        if get_data:
            url += '?' + urlencode(get_data)

        log.debug("Opening URL: %s" % repr(url))
        result = False

        data = urlencode(post_data) if len(post_data) > 0 else None
        req = urllib2.Request(url, data)

        self._read_cookies(url)
        log.debug("Cookies for %s: %s" % (repr(url), repr(self._cookies)))

        handlers = []

        if get_setting("use_elementum_proxy", bool):
            proxyHandler = urllib2.ProxyHandler({
                'http': self.proxy_url,
                'https': self.proxy_url,
            })
            handlers.append(proxyHandler)

        cookieHandler = urllib2.HTTPCookieProcessor(self._cookies)
        handlers.append(cookieHandler)

        opener = urllib2.build_opener(*handlers)
        req.add_header('User-Agent', self.user_agent)
        req.add_header('Content-Language', language)
        req.add_header("Accept-Encoding", "gzip")
        req.add_header("Origin", url)
        req.add_header("Referer", url)

        try:
            self._good_spider()
            with closing(opener.open(req)) as response:
                self.headers = response.headers
                self._save_cookies()
                if response.headers.get("Content-Encoding", "") == "gzip":
                    import zlib
                    self.content = zlib.decompressobj(16 + zlib.MAX_WBITS).decompress(response.read())
                else:
                    self.content = response.read()

                charset = response.headers.getparam('charset')

                if not charset:
                    match = re.search("""<meta(?!\s*(?:name|value)\s*=)[^>]*?charset\s*=[\s"']*([^\s"'/>]*)""", self.content)
                    if match:
                        charset = match.group(1)

                if charset and charset.lower() == 'utf-8':
                    charset = 'utf-8-sig'  # Changing to utf-8-sig to remove BOM if found on decode from utf-8

                if charset:
                    log.debug('Decoding charset from %s for %s' % (charset, repr(url)))
                    self.content = self.content.decode(charset, 'replace')

                self.status = response.getcode()
            result = True

        except urllib2.HTTPError as e:
            self.status = e.code
            log.warning("Status for %s : %s" % (repr(url), str(self.status)))

        except urllib2.URLError as e:
            self.status = repr(e.reason)
            log.warning("Status for %s : %s" % (repr(url), self.status))

        except Exception as e:
            import traceback
            log.error("%s failed with %s:" % (repr(url), repr(e)))
            map(log.debug, traceback.format_exc().split("\n"))

        log.debug("Status for %s : %s" % (repr(url), str(self.status)))

        return result

    def login(self, url, data, fails_with):
        """ Login wrapper around ``open``

        Args:
            url        (str): The URL to open
            data      (dict): POST login data
            fails_with (str): String that must **not** be included in the response's content

        Returns:
            bool: Whether or not login was successful
        """
        result = False
        if self.open(url.encode('utf-8'), post_data=encode_dict(data)):
            result = True
            if fails_with in self.content:
                self.status = 'Wrong username or password'
                result = False
        return result
