import re
import urllib2

_EMBED_EXTRACTORS = {}

def load_video_from_url(in_url):
    IFRAME_RE = re.compile("<iframe.+?src=\"(.+?)\"")
    page_content = urllib2.urlopen(in_url).read()
    embeded_url = IFRAME_RE.findall(page_content)[0]
    try:
        print "Probing source: %s" % embeded_url
        page_content = urllib2.urlopen(embeded_url).read()
    except urllib2.URLError:
        return None # Dead link, Skip result
    except:
        raise
    for extractor in _EMBED_EXTRACTORS.keys():
        if embeded_url.startswith(extractor):
            return _EMBED_EXTRACTORS[extractor](embeded_url, page_content)
    print "[*E*] No extractor found for %s" % embeded_url
    raise Exception("No extractor found for %s" % embeded_url)

def __register_extractor(url, function):
    _EMBED_EXTRACTORS[url] = function

def __ignore_extractor(url, content):
    return None

def __extractor_factory(regex, double_ref=False, match=0, debug=False):
    def f(url, content):
        if debug:
            print url
            print content
            print re.findall(regex, content, re.DOTALL)
            raise

        regex_url = re.findall(regex, content, re.DOTALL)[match]
        if double_ref:
            req = urllib2.Request(regex_url)
            req.add_header('Referer', url)
            video_url = urllib2.urlopen(req).geturl()
        else:
            video_url = regex_url
        return video_url
    return f

__register_extractor("http://auengine.com/",
                    __extractor_factory("var\svideo_link\s=\s'(.+?)';"))
__register_extractor("http://mp4upload.com/", 
                    __extractor_factory("'file':\s'(.+?)',"))
__register_extractor("http://videonest.net/", 
                    __extractor_factory("\[\{file:\"(.+?)\"\}\],"))
__register_extractor("http://animebam.com/", 
                    __extractor_factory("sources:\s\[\{file:\s\"(.+?)\",", True))
__register_extractor("http://embed.yourupload.com/", 
                    __extractor_factory("file:\s'(.+?)\.mp4',", True))
# TODO: debug to find how to extract
__register_extractor("http://embed.videoweed.es/", __ignore_extractor)
__register_extractor("http://embed.novamov.com/", __ignore_extractor)
__register_extractor("http://www.animeram.tv/files/ads/160.html", __ignore_extractor)
