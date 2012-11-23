"""Comics module with all comic communications inside"""
import urllib2

##
# Rework of websites.py

# Folders and global variables
FOLDER = "./var/"
PREV, CURR, NEXT = 0, 1, 2
NUM, NAME = 0, 1
NULLCOMIC = [-1, ""]


class Xkcd(object):
    '''Possible to talk to xkcd.com and get image information'''
    def __init__(self):
        """Return the xkcd handle fully updated"""
        self._history = []
        self._folder = FOLDER + "xkcd/"
        self._base_url = "http://xkcd.com/"
        self._base_img = "http://imgs.xkcd.com/comics/"
        self._base_site = urllib2.urlopen(self._base_url).read()
        self.site = ""

        # Navigation variables, first create then set
        self.comics = [NULLCOMIC, NULLCOMIC, NULLCOMIC]
        self._read_file()
        self._set_comics()
        self.update_comics()

    def _read_file(self):
        """Do a simple update on the history"""
        _txt_file = self._folder + "xkcd.txt"
        self._history = []

        with open(_txt_file, "r") as _txt_file:
            lines = _txt_file.read().split(" \n")
            for line in range(len(lines)):
                self._history.append([])
                # Account for being a number or name.
                for part in lines[line].split(" "):
                    try:
                        self._history[line].append(int(part))
                    except ValueError:
                        self._history[line].append(part)

        if [''] in self._history:
            self._history.remove([''])  # Remove the blankline at the end

    def _write_file(self):
        """Do a write to the file based on class's history"""
        _txt_file = self._folder + "xkcd.txt"

        with open(_txt_file, "w") as _txt_file:
            for line in self._history:
                for item in line:
                    _txt_file.write(str(item) + " ")
                _txt_file.write("\n")

    def _set_comics(self):
        """Set the current comic after updating"""
        # If _set_comics() is run for the first time, adjust.
        if self.comics[CURR] == NULLCOMIC:
            self.site = self._base_site
            self.comics[CURR] = self._set_current()

        prev_index, curr_index, next_index, line = 0, 0, 0, 0
        # Find the correct line index of the current comic
        for line in range(len(self._history)):
            if self._history[line] != self.comics[CURR]:
                continue
            curr_index = self._history[line]
            break

        try:
            if curr_index == self._history[0]:
                next_index = self._history[1]  # If curr = 0, next = 1
                prev_index = NULLCOMIC
            else:
                prev_index = self._history[line - 1]
                next_index = self._history[line + 1]

            if next_index == []:
                next_index = NULLCOMIC
        except IndexError:
            next_index = NULLCOMIC

        self.comics[PREV] = prev_index
        self.comics[NEXT] = next_index

    def _add_current(self, current):
        """Append the given current to the _history array"""
        for item in self._history:
            if item == current:
                return current[NAME] + " exists"

        self._history.append(current)
        return current[NAME] + " added"

    def _set_current(self):
        """Return the current comic on the url"""
        def _url_match(pattern, search):
            """Return the final part of the URL based on the pattern"""
            try: for part in search.split('/'):
                if not part in pattern:
                    return part
            except AttributeError:
                return None

        def _line_match(site, pattern):
            """Return a line that matches the given pattern"""
            max_index = len(pattern)
            for line in site.split('\n'):
                split = line.split()
                if not split:
                    continue
                if split[:max_index] == pattern:
                    # Account for formatting on the page
                    return split[max_index].split('<')[0]

            # return case for null
            return None

        _source_img = ["Image", "URL", "(for", "hotlinking/embedding):"]
        _source_comic = ["Permanent", "link", "to", "this", "comic:"]
        _url_name = self._base_img.split('/')
        _url_num = self._base_url.split('/')

        comic_url = _line_match(self.site, _source_comic)
        img_url = _line_match(self.site, _source_img)
        comic_num = _url_match(_url_num, comic_url)
        comic_name = _url_match(_url_name, img_url)

        if comic_num is None or comic_name is None:
            return NULLCOMIC
        return [int(comic_num), comic_name]

    def update_comics(self):
        """Do an update on the current list of comics"""
        try:
            if self._history == [[]]:
                recent = 1
            else:
                recent = int(self._history[-1][NUM])
        except (IndexError, ValueError):
            recent = 1

        for num in range(recent, 1 + int(self.comics[CURR][NUM])):
            url = self._base_url + str(num) + '/'
            try:
                self.site = urllib2.urlopen(url).read()
            except urllib2.HTTPError:
                continue

            current = self._set_current()
            if current == NULLCOMIC:
                continue

            self._add_current(current)

        # Update the comics array and history file
        self.comics[CURR] = NULLCOMIC
        self._write_file()
        self._set_comics()

    def previous(self):
        """Move the comics array to the left"""
        if self.comics[PREV] == NULLCOMIC:
            return
        self.comics[NEXT] = self.comics[CURR]
        self.comics[CURR] = self.comics[PREV]

        for line in range(len(self._history)):
            if self._history[line] == self.comics[CURR]:
                if line == 0:
                    self.comics[PREV] = NULLCOMIC
                else:
                    self.comics[PREV] = self._history[line - 1]

    def next(self):
        """Move the comics array to the right"""
        if self.comics[NEXT] == NULLCOMIC:
            return
        self.comics[PREV] = self.comics[CURR]
        self.comics[CURR] = self.comics[NEXT]

        for line in range(len(self._history)):
            if self._history[line] == self.comics[CURR]:
                if self._history[line] == self._history[-1]:
                    self.comics[NEXT] = NULLCOMIC
                else:
                    self.comics[NEXT] = self._history[line + 1]

if __name__ == '__main__':
    x = Xkcd()
    print x.comics

