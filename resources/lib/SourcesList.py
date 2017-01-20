from resources.lib import control
from resources.lib.utils import fetch_sources
import re
import xbmcgui

class DialogProgressWrapper(object):
    def __init__(self, title):
        self._dialog = xbmcgui.DialogProgress()
        self._dialog.create(control.lang(30100))

    def update(self, precentage, name=None):
        text = ""
        if name:
            text = control.lang(30101) % name
        return self._dialog.update(precentage, text)

    def iscanceled(self):
        return self._dialog.iscanceled()

    def close(self):
        return self._dialog.close()

class SourcesList(object):
    def __init__(self, raw_results):
        self._raw_results = raw_results

    def _fetch_sources(self, sources, dialog):
        fetched_sources = fetch_sources(sources, dialog)
        if not sources:
            return None

        self._sources = fetched_sources
        return True

    def _fetch_sources_progress(self, sources):
        dialog = DialogProgressWrapper()
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
