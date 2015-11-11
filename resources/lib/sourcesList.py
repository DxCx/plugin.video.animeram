import resources.lib.embed_extractor as embed_extractor
import re
import urllib2
import xbmcgui

class sourcesList(object):
    _SOURCES_UL_RE = re.compile("<ul class=\"video.+?\".+?>(.+?)</ul>", re.DOTALL)
    _VIDEO_NAME_RE = re.compile("<h1>(.+?)</h1>", re.DOTALL)
    def __init__(self, animeram_url):
        # Fetch the url
        sources_page = self._fetch_url(animeram_url)

        # Read the name
        self._name = self._VIDEO_NAME_RE.findall(sources_page)[0]

        # Read the raw sources
        sources =  self._SOURCES_UL_RE.findall(sources_page)[1]
        link_regex = re.compile("<a href=\"%s/(\d+)/\">(.+?)</a>" % animeram_url, re.DOTALL)
        self._raw_results = [(res[1], "%s/%s" % (animeram_url, res[0])) for res in link_regex.findall(sources)]

    def _fetch_url(self, url):
        response = urllib2.urlopen(url)
        resp_content = response.read()
        response.close()
        return resp_content

    def _fetch_sources(self, sources, dialog):
        fetched_sources = []
        factor = 100.0 / len(sources)

        for i, do in enumerate(sources):
            if dialog.iscanceled():
                return -1

            name, url = do
            try:
                dialog.update(int(i * factor), "Processing %s" % name)
                fetched_url = embed_extractor.load_video_from_url(url)
                if fetched_url is not None:
                    fetched_sources.append(("%d | %s" % (len(fetched_sources) + 1, name), fetched_url))
                else:
                    print "Skipping invalid source %s" % name
                dialog.update(int(i * factor), "")
            except:
                print "[*E*] Skiping %s because Exception at parsing" % name

        if not len(fetched_sources):
            # No Valid sources found
            return -1

        self._sources = dict(fetched_sources)
        return 0

    def _fetch_sources_progress(self, sources):
        dialog = xbmcgui.DialogProgress()
        dialog.create("Fetching Sources")
        ret = self._fetch_sources(sources, dialog)
        dialog.close()

        return ret

    def _read_sources(self):
        if not len(self._raw_results):
            # No Sources to start with
            return -1

        return self._fetch_sources_progress(self._raw_results)

    def _select_source(self):
        dialog = xbmcgui.Dialog()
        slist = sorted(self._sources.keys())
        sel = dialog.select("Please choose source: ", slist)
        if sel == -1:
            return -1
        return self._sources[slist[sel]]

    def get_video_link(self):
        if -1 == self._read_sources():
            dialog = xbmcgui.Dialog()
            dialog.notification("Couldn't find eliable sources", "", xbmcgui.NOTIFICATION_ERROR)
            return -1
        return self._select_source()

    @property
    def name(self):
        return self._name
