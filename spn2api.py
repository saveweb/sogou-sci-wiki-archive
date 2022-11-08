# <IA API 部分的代码，抄的

import sys
import logging
import re
import time
import functools
import requests


logger = logging.getLogger(__name__)

user_status = None # 在 is_archive_available() 中加载
API_AUTH = None # S3 帐号密码！！！！！！！！！！！！！！！！# 写死之处

def LOAD_API_AUTH(API_AUTH_CUSTOM):
    global API_AUTH
    if ("LOW " not in API_AUTH_CUSTOM) or (":" not in API_AUTH_CUSTOM):
        raise Exception("S3 key is not valid (Shoub be like 'LOW $accesskey:$secret')\nSee https://archive.org/account/s3.php ")
    API_AUTH = API_AUTH_CUSTOM

DEFAULT_TIMEOUT = 32

sess = requests.Session()


def _assert(expr, msg=''):
    if not expr:
        raise AssertionError(msg)


def retry(try_count=3, retry_interval=2, retry_interval_step=3):
    def _retry(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            _retry_interval = retry_interval

            for i in range(try_count):
                try:
                    _result = func(*args, **kwargs)
                    if i > 0:
                        logger.warning('(Try %d/%d) %r success', i + 1, try_count, func.__name__)

                    return _result
                except Exception as e:
                    if i < try_count - 1:
                        logger.warning('(Try %d/%d) %r got exception %r: %r', i + 1, try_count, func.__name__, type(e), e)

                        if _retry_interval < 0:
                            _retry_interval = 0

                        logger.warning('Wait %.2f s to retry', _retry_interval)
                        time.sleep(_retry_interval)
                        _retry_interval += retry_interval_step

                        logger.warning('(Try %d/%d) retrying ...', i + 2, try_count)
                    else:
                        raise e

        return wrapper

    return _retry


@retry(try_count=10, retry_interval=1, retry_interval_step=5)
def http_get_request(*args, **kwargs):
    # default kwargs
    kwargs_real = {
        'timeout': DEFAULT_TIMEOUT,
    }
    kwargs_real.update(kwargs)

    logger.debug('http_get_request: args=%r, kwargs=%r, cookies=%r', args, kwargs_real, sess.cookies)
    r = sess.get(*args, **kwargs_real)

    return r


@retry(try_count=10, retry_interval=1, retry_interval_step=5)
def http_post_request(*args, **kwargs):
    # default kwargs
    kwargs_real = {
        'timeout': DEFAULT_TIMEOUT,
    }
    kwargs_real.update(kwargs)

    logger.debug('http_post_request: args=%r, kwargs=%r, cookies=%r', args, kwargs_real, sess.cookies)
    r = sess.post(*args, **kwargs_real)

    return r


def is_valid_job_id(s):
    if type(s) is not str:
        return False

    regex = '^spn2\-[0-9a-f]{40}$'
    if re.search(regex, s):
        return True
    else:
        return False


@retry(try_count=8, retry_interval=2, retry_interval_step=5)
def _archive(url):
    """
    Possible API result:
    {"url":"https://example.com/","job_id":"spn2-0123456789abcdef0123456789abcdef12345678"}
    {"message": "Cannot resolve host example.com.", "status": "error", "status_ext": "error:invalid-host-resolution"}
    """

    api_url = 'https://web.archive.org/save/'
    headers = {
        'Authorization': API_AUTH,
        'Accept': 'application/json',
    }
    data = {
        'url': url,
        'if_not_archived_within': '30d',
        'skip_first_archive': '1',
        'js_behavior_timeout': '30',
        #'capture_screenshot': '1',
    }
    r = http_post_request(api_url, headers=headers, data=data)

    _assert(r.status_code == 200, f'archive.org archive API status code: {r.status_code}, content: {r.text[:256]}')
    _assert('application/json' in r.headers['Content-Type'], f'archive.org archive API Content-Type: {r.headers["Content-Type"]}')

    # order of result JSON dict key is not fixed
    return dict(sorted(r.json().items()))


@retry(try_count=8, retry_interval=2, retry_interval_step=5)
def _get_job_status(job_id):
    url = f'https://web.archive.org/save/status/{job_id}'
    r = http_get_request(url)

    _assert(r.status_code == 200, f'archive.org get_job_status API status code: {r.status_code}, content: {r.text[:256]}')
    _assert('application/json' in r.headers['Content-Type'], f'archive.org get_job_status API Content-Type: {r.headers["Content-Type"]}')

    # order of result JSON dict key is not fixed
    result = dict(sorted(r.json().items()))

    # delete useless info, shrink data size
    if 'outlinks' in result:
        del result['outlinks']

    if 'resources' in result:
        del result['resources']

    return result

# IA API 部分的代码，抄的>

#########################################

@retry(try_count=8, retry_interval=2, retry_interval_step=5)
def get_user_status():
    api_url = 'https://web.archive.org/save/status/user'
    headers = {
        'Authorization': API_AUTH,
        'Accept': 'application/json',
    }
    r = http_get_request(api_url, headers=headers)

    # order of result JSON dict key is not fixed
    result = dict(sorted(r.json().items()))

    return result

def is_archive_available():
    global user_status
    if user_status is None:#初始化
        print('Initializing user_status ...')
        user_status = get_user_status()
        print('user_status:', user_status)

    if user_status['daily_captures_limit'] <= user_status['daily_captures']:#快照数量是否超限
        raise Exception("API: daily_captures_limit reached! (limit:",user_status['daily_captures_limit'],")")

    if user_status['available'] >= 1:#缓存
        time.sleep(1.5)
        print("API: available:",user_status['available']) #调试用
        user_status['available'] -= 1
        if user_status['available'] == 0:#重新获取状态
            time.sleep(2.5)
            user_status = get_user_status()
        return True
    else:
        user_status = get_user_status()#重新获取状态
        return False

def do_archive(url):
    while is_archive_available() == False:
        time.sleep(6)#别把 IA 淦爆了

    job_tick = _archive(url)
    print(job_tick)#凭票入场

    #if 'job_id' in job_tick:
        #if is_valid_job_id(job_tick['job_id']) == True:
            #job_status = _get_job_status(job_tick['job_id'])
            #while job_status['status'] == 'pending'
                #time.sleep(3)
                #job_status = _get_job_status(job_tick['job_id'])
            #print(job_status['status'])

########################################
