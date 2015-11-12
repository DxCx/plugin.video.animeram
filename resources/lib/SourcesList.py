from resources.lib import control
from resources.lib import embed_extractor
import re
import xbmcgui

class SourcesList(object):
    def __init__(self, raw_results):
        self._raw_results = raw_results

    def _fetch_sources(self, sources, dialog):
        fetched_sources = []
        factor = 100.0 / len(sources)

        for i, do in enumerate(sources):
            if dialog.iscanceled():
                return None

            name, url = do
            try:
                dialog.update(int(i * factor), control.lang(30101) % name)
                fetched_url = embed_extractor.load_video_from_url(url)
                if fetched_url is not None:
                    fetched_sources.append(("%03d | %s" % (len(fetched_sources) + 1, name), fetched_url))
                else:
                    print "Skipping invalid source %s" % name
                dialog.update(int(i * factor), "")
            except:
                print "[*E*] Skiping %s because Exception at parsing" % name
                raise

        if not len(fetched_sources):
            # No Valid sources found
            return None

        self._sources = dict(fetched_sources)
        return True

    def _fetch_sources_progress(self, sources):
        dialog = xbmcgui.DialogProgress()
        dialog.create(control.lang(30100))
        ret = self._fetch_sources(sources, dialog)
        dialog.close()

        return ret

    def _read_sources(self):
        if not len(self._raw_results):
            # No Sources to start with
            return None

        return self._fetch_sources_progress(self._raw_results)

    def _select_source(self):
        if len(self._sources) == 1:
            print "1 source was found, returning it"
            return self._sources.values()[0]

        dialog = xbmcgui.Dialog()
        slist = sorted(self._sources.keys())
        sel = dialog.select(control.lang(30102), slist)
        if sel == -1:
            return None
        return self._sources[slist[sel]]

    def get_video_link(self):
        if not self._read_sources():
            dialog = xbmcgui.Dialog()
            dialog.notification(control.lang(30103), "", xbmcgui.NOTIFICATION_ERROR)
            return None
        return self._select_source()

    @property
    def name(self):
        return self._name
