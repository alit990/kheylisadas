from datetime import datetime

if __name__ == '__main__':
    # dt_obj = datetime.strptime('01.01.0001 09:38:42',
    #                            '%d.%m.%Y %H:%M:%S')
    # millisec = dt_obj.timestamp() * 1000
    #
    # print(millisec)


    def get_sec(time_str):
        """Get seconds from time."""
        h, m, s = time_str.split(':')
        return int(h) * 3600 + int(m) * 60 + int(s)


    print(get_sec('1:23:45'))
    print(get_sec('02:15'))
    print(get_sec('0:00:25'))