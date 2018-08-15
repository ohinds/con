#!/usr/bin/env python

import http.cookiejar as cookielib
import os
import urllib
import re
import string
import sys
from bs4 import BeautifulSoup

class LinkedInParser(object):
    """Login and parse info from linkedin. Modded from an SO question.
    """

    def __init__(self, login, password):
        """ Start up... """
        self.login = login
        self.password = password

        # Simulate browser with cookies enabled
        cookie_filename = "parser.cookies.txt"
        self.cj = cookielib.MozillaCookieJar(cookie_filename)
        if os.access(cookie_filename, os.F_OK):
            self.cj.load()
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPRedirectHandler(),
            urllib.request.HTTPHandler(debuglevel=0),
            urllib.request.HTTPSHandler(debuglevel=0),
            urllib.request.HTTPCookieProcessor(self.cj)
        )
        self.opener.addheaders = [
            ('User-agent', ('Mozilla/4.0 (compatible; MSIE 6.0; '
                           'Windows NT 5.2; .NET CLR 1.1.4322)'))
        ]

        # Login
        self.login_page()

        title = str(self.load_title())
        expected_title = '<title>LinkedIn</title>'

        if title == expected_title:
            print('Login successful')
            self.cj.save()

        else:
            print('Login failed')


    def load_page(self, url, data=None):
        """Utility function to load HTML from URLs for us with hack to
        continue despite 404

        """
        # We'll print the url in case of infinite loop
        # print "Loading URL: %s" % url
        try:
            if data is not None:
                response = self.opener.open(url, data)
            else:
                response = self.opener.open(url)
            return ''.join([str(l) for l in response.readlines()])
        except Exception as e:
            # If URL doesn't load for ANY reason, try again...  Quick
            # and dirty solution for 404 returns because of network
            # problems However, this could infinite loop if there's an
            # actual problem
            return self.loadPage(url, data)

    def load_soup(self, url, data=None):
        """
        Combine loading of URL, HTML, and parsing with BeautifulSoup
        """
        html = self.load_page(url, data)
        soup = BeautifulSoup(html, "html5lib")
        return soup

    def login_page(self):
        """
        Handle login. This should populate our cookie jar.
        """
        soup = self.load_soup("https://www.linkedin.com/")
        csrf = soup.find(id="loginCsrfParam-login")['value']
        login_data = urllib.parse.urlencode({
            'session_key': self.login,
            'session_password': self.password,
            'loginCsrfParam': csrf,
        }).encode('utf8')

        self.load_page("https://www.linkedin.com/uas/login-submit", login_data)
        return

    def load_title(self):
        soup = self.load_soup("https://www.linkedin.com/feed/")
        return soup.find("title")


def main(argv):

    # load the user credentials
    cred_file = 'cred.txt'
    with open(cred_file) as fp:
        content = fp.read().strip().rstrip()
        username = content.split()[0]
        password = content[len(username):].strip()

    parser = LinkedInParser(username, password)
    connect_page = parser.load_soup(
        'https://www.linkedin.com/mynetwork/invite-connect/connections/')


if __name__ == "__main__":
    sys.exit(main(sys.argv))
