from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

# 对异常的处理目前都是结束进程



LOGIN_URL = 'https://www.ulearning.cn/ulearning_web/indexStatic.jsp'
COURSE_URL = 'https://ua.ulearning.cn/learnCourse/learnCourse.html?courseId='
COURSE_ID = [
    '8363',  # 形式与政策
    '751',   # 中国近代史
    '750',   # 马克思基本原理
 ]
# 每门课第一张的ID
CHAPTER_ID = [
    '2204365',  # 形势与政策
    '2637179',  # 近代史
]
# 存储页面点击失败的item
RETRY_LIST = []

def _judge(methon, elem):
    flag = True
    try:
        methon(elem)
    except:
        flag =  False
    finally:
        return flag

def _login(username, passwd):
    driver.get(LOGIN_URL)
    # 登录按钮
    login_btn = driver.find_element_by_id('login-link')
    # 点击登录
    login_btn.click()
    # 用户名
    user = driver.find_element_by_id('username')
    user.send_keys(username)
    # 用户密码
    password = driver.find_element_by_id('passwd')
    password.send_keys(passwd)
    # 登录按钮
    submit = driver.find_element_by_id('loginBtn-order')
    submit.click()
    # 判断是否登录成功
    if _judge(driver.find_element_by_css_selector, '.header-linfo'):
        print('登录成功')
    else:
        print('登录失败')
        error_msg = driver.find_element_by_css_selector('.errorMsg').text
        print('原因是'+error_msg)
        driver.quit()

# 获取章节进度
def _get_chapter_schedule():
    pass


# 将点击3次都失败的页面加入RETRY_LIST
def _add_fail_page(item):
    RETRY_LIST.append(item)

def _next_page():
    # 处理出现多页面同时观看的提示
    _deal_multi_page()
    # 处理第一个弹窗
    _deal_first_tip()
    flag = True
    while flag:
        # 点击下一页
        bt = driver.find_element_by_css_selector('div.next-page-btn.cursor')
        bt.click()
        time.sleep(1)
        # 跳过所有提示

        if _judge(driver.find_element_by_class_name, 'close-btn'):
            bt = driver.find_element_by_class_name('close-btn')
            try:
                bt.click()
                print('---close-btn--')
                time.sleep(1)
            except:
                pass
        elif _judge(driver.find_element_by_xpath, "//button[contains(@class,'btn-hollow')]"):
            bt = driver.find_element_by_xpath("//button[contains(@class,'btn-hollow')]")
            try:
                bt.click()
            except:
                pass
        if _judge(driver.find_element_by_xpath, "//button[@class='btn-hollow section-stat']"):
            bt = driver.find_element_by_xpath("//button[@class='btn-hollow section-stat']")
            try:
                bt.click()
            except:
                pass


def t():
    # 处理出现多页面同时观看的提示
    _deal_multi_page()
    # 处理第一个弹窗
    _deal_first_tip()
    # 下面获取每一小节的item
    time.sleep(1)
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.page-name.cursor')))
    items = driver.find_elements_by_css_selector('div.page-name.cursor')
    print('等待前item数量：', len(items))
    time.sleep(5)
    items = driver.find_elements_by_css_selector('div.page-name.cursor')
    print('等待后item数量：', len(items))
    # 开始遍历学习每一小节
    time.sleep(1)
    cnt = 0
    for i in items:
        time.sleep(2)
        try:
            i.click()
            title = i.find_element_by_css_selector('div.text  > span').text
            print(title)
        except:
            print('此页面点击失败,重试')
            time.sleep(1.5)
            try:
                i.click()
            except:
                cnt += 1
                print('重试失败', cnt)
                _add_fail_page(i)

        time.sleep(1.5)
        # 跳过所有提示
        if _judge(driver.find_element_by_class_name, 'close-btn'):
            bt = driver.find_element_by_class_name('close-btn')
            try:
                bt.click()
                print('---close-btn--')
                time.sleep(1)
            except:
                pass
    print('失败页面总数：', cnt)
    print('开始将失败页面重新点击')
    for i in RETRY_LIST:
        try:
            i.click()
        except:
                i.find_element_by_xpath('span').click()



def _run_class(course_id, chapter_id):
    url = COURSE_URL + course_id + '&chapterId=' + chapter_id
    # 进入课程
    driver.get(url)
    #  t()
    _next_page()



def _deal_multi_page():
    try:
        WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.modal-info > .title')))
        bt = driver.find_element_by_css_selector('button.btn-hollow')
        if bt != None:
            print('出现了多页面学习提示框')
            bt.click()
    except:
        pass


# 处理第一个弹窗
def _deal_first_tip():
    # 点击弹出的提示页面 防止干扰
    loctor = (By.CSS_SELECTOR, 'div.close-btn')
    try:
        WebDriverWait(driver, 20).until(EC.text_to_be_present_in_element(loctor, '跳过所有提示'))
        tip = driver.find_element_by_css_selector('div.close-btn')
        tip.click()
    except:
        print('没有第一个提示弹窗出现')


# 判断是否为视频页面
def _is_video_page():
    if _judge(driver.find_element_by_css_selector, '.video-element'):
        return True

def _is_video_over():
    '''
    根据传入的driver来判断视频是否看完
    :return:
    TRUE or FALSE
    '''
    text = driver.find_element_by_css_selector('div.video-info > div > div.text > span').text
    if text == '已看完':
        return  True
    else:
        return False

# 增加视频播放等待时间
def _add_video_sleep_time(time=0):
    '''
    在等待计算的剩余视频时长后，判断视频是否看完，否则增加等待时间
    :return:
    '''
    # 尝试3次增加等待时间
    if time == 3:
        print('此节视频播放出现问题，跳过进入下一小节')

    if _is_video_over():
        print('视频播放结束')
        return True
    else:
        time.sleep(10)
        time += 1
        _add_video_sleep_time(time)


# 获取并计算视频播放耗费的时间
def _calculate_video_time():
    text = 0
    # 尝试次数
    retry = 0
    while text == 0 and retry < 3:
        retry += 1
        try:
            WebDriverWait(driver, 30).until(EC.visibility_of_element_located(
                (By.CSS_SELECTOR, '.jwcontrolbar  > span.jwgroup.jwright > span')))
            text = driver.find_element_by_css_selector('.jwcontrolbar  > span.jwgroup.jwright > span').text
        except:
            pass
    a, b = text.split(':')
    t = int(a) * 60 + int(b)
    print('视频播放还剩大约', t, '秒')
    return t+2


def _study():
    # 处理出现多页面同时观看的提示
    _deal_multi_page()
    # 处理第一个弹窗
    _deal_first_tip()
    # 下面获取每一小节的item
    time.sleep(2)
    WebDriverWait(driver,20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.page-name.cursor')))
    items = driver.find_elements_by_css_selector('div.page-icon + span')
    # print('等待前item数量：', len(items))
    # time.sleep(10)
    # items = driver.find_elements_by_css_selector('div.page-name.cursor')
    # print('等待后item数量：',len(items))
    # 开始遍历学习每一小节
    time.sleep(2)
    for i in items:
        time.sleep(1)
        try:
            i.click()
        except:
            print('此页面点击失败,重试')
            time.sleep(1)
            try:
                i.click()
            except:
                print('重试失败')
        time.sleep(1.5)
        # 跳过所有提示
        if _judge(driver.find_element_by_class_name, 'close-btn'):
            bt = driver.find_element_by_class_name('close-btn')
            try:
                bt.click()
                print('---close-btn--')
                time.sleep(1)
            except:
                pass
        # 视频观看提示
        # elif _judge(driver.find_element_by_css_selector, 'btn-submit'):
        #     # 点击知道了
        #     print('---btn-submit--')
        #     bt = driver.find_element_by_css_selector('btn-submit')
        #     try:
        #         bt.click()
        #         time.sleep(1)
        #     except:
        #         pass
        # 判断是否视频页面
        t1 = time.time()########################
        if _is_video_page():
            print('视频页面')
            # 点击播放按钮
            # driver.find_element_by_css_selector('.jwdisplayIcon .jwicon').click()
            if _is_video_over():
                pass
            else:
                print('没看完')
                # 计算视频播放时间
                # sleep_time = _calculate_video_time()
                # time.sleep(sleep_time)
                # 最后再判断视频是否看完，没有就增加等待时间
                # _add_video_sleep_time()
        else:
            print('非视频页面')
        t2 = time.time()
        print('耗时：', t2-t1)
# 计算视频所需播放时间




opt = webdriver.ChromeOptions()
# 创建chrome无界面对象
driver = webdriver.Chrome(options=opt)
# 设置全局显性等待
driver.implicitly_wait(2)

_login('20164045033', 'dk154310')
_run_class(COURSE_ID[0],CHAPTER_ID[0])

