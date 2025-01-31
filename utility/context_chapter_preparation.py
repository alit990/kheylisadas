class MyChapter:
    def __init__(self, id=None, title=None, name=None, slug=None, audio_url=None, audio_count=None):
        self.d = {}
        if id is not None:
            self.d["id"] = id
        if title is not None:
            self.d["title"] = title
        if name is not None:
            self.d["name"] = name
        if slug is not None:
            self.d["slug"] = slug
        if audio_count is not None:
            self.d["audio_count"] = audio_count
        if audio_url is not None:
            self.d["audio_url"] = ""  # audio_url

    def __repr__(self):
        return str(self.d)


class MyChapterData:
    def __init__(self, name=None):
        self.d = {}
        if name is not None:
            self.d["name"] = name

    def add_chapter(self, key, value):
        self.d[key] = value

    def __repr__(self):
        return str(self.d)


# if __name__ == '__main__':
#     ch1 = Chapter(id=1, title="chapter 1", name="name 1", audio_url="url 1")
#     ch2 = Chapter(id=2, title="chapter 2", name="name 2", audio_url="url 2")
#     ch3 = Chapter(id=3, title="chapter 3", name="name 3", audio_url="url 3")
#     ch4 = Chapter(id=4, title="chapter 4", name="name 4", audio_url="url 4")
#     d = Data('topData')
#     d.add_chapter('chapters', [ch1,ch2,ch3,ch4])
#     print(d)