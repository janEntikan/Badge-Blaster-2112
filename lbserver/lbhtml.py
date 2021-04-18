import pickle
import os
import time

HEAD = '''<html><head><title>Leader Board</title><style type="text/css">
    .tg  {border-collapse:collapse;border-spacing:20;background-color:#000000;border-color:#000000;color:#ffffff;font-family:"Lucida Console", Monaco, monospace !important;;font-size:16px;text-align:center;vertical-align:middle;}
</style></head><body><table class="tg"><tbody>$$ENTRIES$$</tbody></table></body></html>'''


def generate_html(content):
    print('Fetching current leader board...')
    try:
        with open('leaderboard.db', 'rb') as fd:
            lb = pickle.load(fd)
    except (pickle.UnpicklingError, pickle.PickleError, OSError, FileNotFoundError) as err:
        print(f'Got an error while reading/unpickling the file: {err}')
        return []
    print('Got: ', lb)
    print('Checking for changes...')
    ret = []
    if len(content) == len(lb):
        for a, b in zip(content, lb):
            if a != b:
                ret = lb + []
                print('Found a difference')
                break
    elif len(content) == 0:
        ret = lb + []
    if ret:
        snippet = ''.join([f'<tr><td>{i + 1}&nbsp;&nbsp;</td><td style="text-align:left">{n}&nbsp;&nbsp;</td><td style="text-align:right">{s}</td></tr>' for i, (n, s) in enumerate(lb)])
        with open('leaderboard.html', 'w') as fd:
            fd.write(HEAD.replace('$$ENTRIES$$', snippet))
        print('HTML updated')
    return ret


def main():
    last_content = []

    while True:
        res = generate_html(last_content)
        if res:
            print('New leader board to copy: ', res)
            last_content = res
            os.system('scp leaderboard.html #####INSERT NEW LOCATION HERE#####')
        time.sleep(30)


if __name__ == '__main__':
    print('starting script')
    pid = os.fork()
    if pid:
        print('waiting a bit until exiting')
        time.sleep(5)
    else:
        main()

