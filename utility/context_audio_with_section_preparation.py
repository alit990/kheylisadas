from django.templatetags.static import static


class Ch:
    def __init__(self, title=None, name=None, start_time=None):
        self.d = {}
        if title is not None:
            self.d["title"] = title
        if name is not None:
            self.d["name"] = name
        if start_time is not None:
            self.d["start_time"] = start_time

    def __repr__(self):
        return str(self.d)


class Au:
    FREE = 1
    LOCKED = 2
    LOCKED_WITH_QUESTION = 3
    LOCKED_RELY_TO_QUESTION = 4

    def __init__(self, id=None, title=None, name=None, description=None, image_url=None, audio_url=None, is_lock=None,
                 type=None, like_count=None, dislike_count=None, fake_like_count=None, fake_dislike_count=None, user_vote=None, added_playlist=None, artist=None,
                 url=None):
        self.d = {}
        if id is not None:
            self.d["id"] = id
        if title is not None:
            self.d["title"] = title
        if name is not None:
            self.d["name"] = name
            self.d["artist"] = "خیلی ساده ست"
        if description is not None:
            self.d["description"] = description
        if image_url is not None:
            self.d["image_url"] = static('assets/img/audio-icon.png')
        if audio_url is not None:
            self.d["audio_url"] = ""
            # self.d["audio_url"] = audio_url
        if is_lock is not None:
            if is_lock:
                self.d["is_lock"] = "True"
            else:
                self.d["is_lock"] = "False"
        if type is not None:
            self.d["type"] = type
            match type:
                case self.FREE:
                    self.d["theme_color"] = "#FFFFFFFF"
                case self.LOCKED:
                    self.d["theme_color"] = "#FFFFFFFF"
                case self.LOCKED_WITH_QUESTION:
                    self.d["theme_color"] = "#FFFFFFFF"
                case self.LOCKED_RELY_TO_QUESTION:
                    self.d["theme_color"] = "#FFFFFFFF"
            self.d["audio_url"] = ""
        else:
            self.d["theme_color"] = "#FFFFFFFF"
        if like_count is not None:
            self.d["like_count"] = like_count
        if dislike_count is not None:
            self.d["dislike_count"] = dislike_count
        if fake_like_count is not None:
            self.d["fake_like_count"] = fake_like_count
        if fake_dislike_count is not None:
            self.d["fake_dislike_count"] = fake_dislike_count
        if user_vote is not None:
            self.d["user_vote"] = user_vote
        if added_playlist is not None:
            if added_playlist:
                self.d["added_playlist"] = "True"
            else:
                self.d["added_playlist"] = "False"
        if url is not None:
            self.d["url"] = url

    def add_chapter(self, key, value):
        self.d[key] = value

    def __repr__(self):
        return str(self.d)


class Sec:
    def __init__(self, id=None, title=None, name=None, description=None):
        self.d = {}
        if id is not None:
            self.d["id"] = id
        if title is not None:
            self.d["title"] = title
        if name is not None:
            self.d["name"] = name
        if description is not None:
            self.d["description"] = description

    def add_audio(self, key, value):
        self.d[key] = value

    def __repr__(self):
        return str(self.d)


class D:
    def __init__(self, name=None):
        self.d = {}
        if name is not None:
            self.d["name"] = name

    def add_section(self, key, value):
        self.d[key] = value

    def __repr__(self):
        return str(self.d)

# if __name__ == '__main__':
#     s1 = Section(title="section 1", name="bakhsh 1", description="tozihate lazem 1")
#     s2 = Section(title="section 2", name="bakhsh 2", description="tozihate lazem bakhsh 2")
#     a1 = Audio(title="audio 1", name="soti 1", image_url="...", audio_url="...", description="tozihate lazem audio 1")
#     a2 = Audio(title="audio 2", name="soti 2", image_url="...", audio_url="...", description="tozihate lazem audio 2")
#     a3 = Audio(title="audio 3", name="soti 3", image_url="...", audio_url="...", description="tozihate lazem audio 3")
#     ch1 = Chapter(title="chapter 1", name="ghesmat 1", start_time="00:00", end_time="00:54")
#     ch2 = Chapter(title="chapter 2", name="ghesmat 2", start_time="00:54", end_time="01:20")
#     ch3 = Chapter(title="chapter 3", name="ghesmat 3", start_time="00:00", end_time="01:51")
#     ch4 = Chapter(title="chapter 4", name="ghesmat 4", start_time="00:00", end_time="01:44")
#     a1.add_chapter('chapters', ch1)
#     a1.add_chapter('chapters', ch2)
#     a2.add_chapter('chapters', ch3)
#     a3.add_chapter('chapters', ch4)
#     s1.add_audio('audios', [a1, a2])
#     s2.add_audio('audios', a3)
#     d = Data('TopData')
#     d.add_section('sections', [s1,s2])
#     print(d)
#
#
#     # for section in sections:
#     #     s.append(Section(title=section., name="bakhsh 1", description="tozihate lazem 1"))
#     #
#     # s = Section('Section_1')
#     # audio1 = Audio('audio_1')
#     # audio1.add('src', 'src1')
#     # audio1.add('chapters', [Chapter('Chapter_1'), Chapter('Chapter_2'), Chapter('Chapter_3')])
#     # s.add('audio-01', audio1)
#     # audio2 = Audio('audio_2')
#     # audio2.add('src', 'src2')
#     # audio2.add('chapters', [Chapter('Chapter_4'), Chapter('Chapter_5')])
#     #
#     # s.add('audio-02', audio2)
#     #
#     # s2 = Section('Section_1')
#     # audio1 = Audio('audio_1')
#     # audio1.add('src', 'src1')
#     # audio1.add('chapters', [Chapter('Chapter_1'), Chapter('Chapter_2'), Chapter('Chapter_3')])
#     # s2.add('audio-01', audio1)
#     # audio2 = Audio('audio_2')
#     # audio2.add('src', 'src2')
#     # audio2.add('chapters', [Chapter('Chapter_4'), Chapter('Chapter_5')])
#     #
#     # s2.add('audio-02', audio2)
#     #
#     # d = Data('TopData')
#     # d.add('Section_1', s)
#     # d.add('Section_2', s2)
#     # print(d)
#     # # print(s.d['audio-01'])
