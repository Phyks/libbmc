"""
This file contains functions to download locally some papers, eventually using
a proxy.
"""
import socket
import sys
import urllib

import socks


# Default socket to use, if no proxy is used
DEFAULT_SOCKET = socket.socket


def _download_helper(url):
    """
    Handle the download of an URL, using the proxy currently set in \
            :mod:`socks`.

    :param url: The URL to download.
    :returns: A tuple of the raw content of the downloaded data and its \
            associated content-type. Returns None if it was \
            unable to download the document.
    """
    # Try to fetch the URL using the current proxy
    try:
        request = urllib.request.urlopen(url)
        try:
            size = int(dict(request.info())['content-length'].strip())
        except KeyError:
            try:
                size = int(dict(request.info())['Content-Length'].strip())
            except KeyError:
                size = 0
        # Download the document
        doc = b""
        doc_size = 0
        while True:
            buf = request.read(1024)
            if buf:
                doc += buf
                doc_size += len(buf)
                if size != 0:
                    # Write progress bar on stdout
                    done = int(50 * doc_size / size)
                    sys.stdout.write("\r[%s%s]" %
                                     ('='*done, ' '*(50-done)))
                    sys.stdout.write(" "+str(int(float(done)/52*100))+"%")
                    sys.stdout.flush()
            else:
                break
        # Fetch content type
        contenttype = None
        contenttype_req = None
        try:
            contenttype_req = dict(request.info())['content-type']
        except KeyError:
            try:
                contenttype_req = dict(request.info())['Content-Type']
            except KeyError:
                return None
        if 'pdf' in contenttype_req:
            contenttype = 'pdf'
        elif 'djvu' in contenttype_req:
            contenttype = 'djvu'

        # Check content type and status code are ok
        if request.getcode() != 200 or contenttype is None:
            # Else, try with the next available proxy
            return None

        # Return a tuple of the downloaded content and the content-type
        return (doc, contenttype)
    # If an exception occurred, continue with next available proxy
    except (urllib.error.URLError, socket.error, ValueError):
        return None


def download(url, proxies=None):
    """
    Download a PDF or DJVU document from a url, eventually using proxies.

    :params url: The URL to the PDF/DJVU document to fetch.
    :params proxies: An optional list of proxies to use. Proxies will be \
            used sequentially. Proxies should be a list of proxy strings. \
            Do not forget to include ``""`` (empty string) in the list if \
            you want to try direct fetching without any proxy.

    :returns: A tuple of the raw content of the downloaded data and its \
            associated content-type. Returns ``(None, None)`` if it was \
            unable to download the document.

    >>> download("http://arxiv.org/pdf/1312.4006.pdf") # doctest: +SKIP
    """
    # Handle default argument
    if proxies is None:
        proxies = [""]

    # Loop over all available connections
    for proxy in proxies:
        # Handle no proxy case
        if proxy == "":
            socket.socket = DEFAULT_SOCKET
        # Handle SOCKS proxy
        elif proxy.startswith('socks'):
            if proxy[5] == '4':
                proxy_type = socks.SOCKS4
            else:
                proxy_type = socks.SOCKS5
            proxy = proxy[proxy.find('://') + 3:]
            try:
                proxy, port = proxy.split(':')
            except ValueError:
                port = None
            socks.set_default_proxy(proxy_type, proxy, port)
            socket.socket = socks.socksocket
        # Handle generic HTTP proxy
        else:
            try:
                proxy, port = proxy.split(':')
            except ValueError:
                port = None
            socks.set_default_proxy(socks.HTTP, proxy, port)
            socket.socket = socks.socksocket

        downloaded = _download_helper(url)
        if downloaded is not None:
            return downloaded

    # In case of running out of proxies, return (None, None)
    return (None, None)
