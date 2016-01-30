"""
This file contains functions to download locally some papers, eventually using
a proxy.
"""
import socket
import socks
import sys
import urllib


# Default socket to use, if no proxy is used
DEFAULT_SOCKET = socket.socket


def download(url, proxies=[None]):
    """
    Download a PDF or DJVU document from a url, eventually using proxies.

    :params url: The URL to the PDF/DJVU document to fetch.
    :params proxies: An optional list of proxies to use. Proxies will be \
            used sequentially. Proxies should be a list of proxy strings. \
            Do not forget to include ``None`` in the list if you want to try \
            direct fetching without any proxy.

    :returns: A tuple of the raw content of the downloaded data and its \
            associated content-type. Returns ``(None, None)`` if it was \
            unable to download the document.

    >>> download("http://arxiv.org/pdf/1312.4006.pdf") # doctest: +SKIP
    """
    # Loop over all available connections
    for proxy in proxies:
        # Handle no proxy case
        if proxy is None:
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

        # Try to fetch the URL using the current proxy
        try:
            r = urllib.request.urlopen(url)
            try:
                size = int(dict(r.info())['content-length'].strip())
            except KeyError:
                try:
                    size = int(dict(r.info())['Content-Length'].strip())
                except KeyError:
                    size = 0
            # Download the document
            dl = b""
            dl_size = 0
            while True:
                buf = r.read(1024)
                if buf:
                    dl += buf
                    dl_size += len(buf)
                    if size != 0:
                        # Write progress bar on stdout
                        done = int(50 * dl_size / size)
                        sys.stdout.write("\r[%s%s]" %
                                         ('='*done, ' '*(50-done)))
                        sys.stdout.write(" "+str(int(float(done)/52*100))+"%")
                        sys.stdout.flush()
                else:
                    break
            # Fetch content type
            contenttype = False
            contenttype_req = None
            try:
                contenttype_req = dict(r.info())['content-type']
            except KeyError:
                try:
                    contenttype_req = dict(r.info())['Content-Type']
                except KeyError:
                    continue
            if 'pdf' in contenttype_req:
                contenttype = 'pdf'
            elif 'djvu' in contenttype_req:
                contenttype = 'djvu'

            # Check content type and status code are ok
            if r.getcode() != 200 or contenttype is False:
                # Else, try with the next available proxy
                continue

            # Return a tuple of the downloaded content and the content-type
            return (dl, contenttype)
        # If an exception occurred, continue with next available proxy
        except (urllib.error.URLError, socket.error, ValueError):
            continue

    # In case of running out of proxies, return (None, None)
    return (None, None)
