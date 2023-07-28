from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import pyperclip as pp
import time
from random import uniform, randrange, shuffle
import os
from tkinter import *
import sys

window = Tk()
window.title("선택적공감머신")
window.geometry("500x500")
window.resizable(False, False)

def main_1():
    # 크롬 드라이버 경로 지정. os를 스지 않고 가능하다면 해보자.
    driverFolder : str= os.getcwd()+'/selenium/chromedriver.exe'

    #자신의 아이디, 비밀번호
    yourid : str = "id를 입력해주세요"
    yourpassword : str = "비밀번호를 입력해주세요!"

    # 좋아요를 누르기 전 스크롤을 할 때 스크롤 최소, 최대 시간
    scrollMinPauseTime : float = 0.5
    scrollMaxPauseTime : float = 5.0

    # 원하는 태그 목록
    searchWords : list = ["검색하고", "싶은", "검색어를", "리스트", "형태로", "입력"]

    # 태그 순서 섞기
    shuffle(searchWords)

    # 각 태그당 좋아요를 누를 최소, 최대 개수
    tagMinNum : int = 40
    tagMaxNum : int = 60

    #좋아요 누른 개수, 다음 태그로 넘어가는 개수
    clickedLikeNum : int = 0
    stopTagNum : int = 0

    # 이웃 블로그 최대 수(이웃이 많을 경우 스크롤 제한하기)
    maxneighbornum = 20
    driverFolder : str= os.getcwd()+'/selenium/chromedriver.exe'

    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_argument('--no-sandbox')
    options.add_argument("disable-gpu")
    # options.add_argument('headless')
    options.add_argument('window-size=1920x1080')
    options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")
    driver = webdriver.Chrome(options=options)

    def inputkeys(myId : str, placeholder : str):
        pp.copy(myId)
        idInput = driver.find_element(By.XPATH, f"//input[@placeholder='{placeholder}']")
        idInput.click()
        pp.copy(myId)
        time.sleep(uniform(3.0, 10.0))
        idInput.send_keys(Keys.CONTROL, 'v')
        
    def login(naverid : str, naverpassword : str):
        driver.get("https://nid.naver.com/nidlogin.login?svctype=262144&url=http://m.naver.com/aside/")    
        inputkeys(naverid, "아이디")
        inputkeys(naverpassword, "비밀번호")
        driver.find_element(By.XPATH, f"//input[@placeholder='비밀번호']").send_keys(Keys.ENTER)
        time.sleep(2)

    def searchBlog(searchWord : str, articleLimit : int):
        adress = "https://m.search.naver.com/search.naver?where=m_blog&query="+searchWord+"&nso=so%3Add%2Cp%3Aall"
        driver.get(adress)

        articles = driver.find_elements(By.XPATH, "//div[@class='total_wrap']/a")
        numOfArticles = len(articles)
        SCROLL_PAUSE_TIME = 0.5
        while numOfArticles < articleLimit :
            articles = driver.find_elements(By.XPATH, "//div[@class='total_wrap']/a")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(SCROLL_PAUSE_TIME)
            numOfArticles = len(driver.find_elements(By.XPATH, "//div[@class='total_wrap']/a"))
        
        articles = driver.find_elements(By.XPATH, "//div[@class='total_wrap']/a")
        numOfArticles = len(articles)
        urls = []
        for i in range(numOfArticles):
            url = str(articles[i].get_attribute("href"))
            urls.append(url)
        return urls

    def openBlog(url):
        driver.execute_script(f"window.open('{url}');")
        driver.switch_to.window(driver.window_handles[1])

    def closeBlog():
        driver.close()
        driver.switch_to.window(driver.window_handles[0])

    def availableLike():
        nonlocal stopTagNum
        try : 
            confirmlike = driver.find_element(By.XPATH, "//*[@id='body']/div[10]/div/div[1]/div/div/a").get_attribute("class").split(" ")
            if "on" in confirmlike :
                stopTagNum += 1
                print(f'이미 좋아요 누른 게시물 {stopTagNum}개')
                return False
            elif "off" in confirmlike : 
                return True
        except Exception as e: 
            print(e)
            print('좋아요가 제한된 게시물')
            return False

    def scrollEndPosition():
        document_height = int(driver.execute_script("return document.body.scrollHeight"))
        now_scroll_height = int(driver.execute_script("return window.scrollY + window.innerHeight"))
        if now_scroll_height + 200 >= document_height:
            return False
        else : 
            return True
        
    def clickLike():
        while scrollEndPosition():
            driver.find_element(By.XPATH, "//body").send_keys(Keys.PAGE_DOWN)
            time.sleep(uniform(scrollMinPauseTime, scrollMaxPauseTime))
        
        like_btn = driver.find_element(By.XPATH, "//div[@class='btn_like']/div")
        driver.execute_script("arguments[0].scrollIntoView({block : 'center'});", like_btn)
        like_btn.click()
        nonlocal clickedLikeNum
        clickedLikeNum += 1
        print(f"블로그 좋아요를 {clickedLikeNum}개 누름")
        closeBlog()
        
    def neighborNewFeed(maxnum : int):
        driver.get("https://m.blog.naver.com/FeedList.naver")
        time.sleep(uniform(6, 15))
        
        neighborBlogs = driver.find_elements(By.XPATH, "//div/ul/li//div[@class ='text_area___UrFH']//a")   
        print(len(neighborBlogs))
        numOfneighborblogs = len(neighborBlogs)
        
        SCROLL_PAUSE_TIME = 1
        # while numOfneighborblogs < maxnum :
        for i in range (20):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(SCROLL_PAUSE_TIME)
            numOfneighborblogs = len(driver.find_elements(By.XPATH, "//div[@class='total_wrap']/a"))
            print(numOfneighborblogs) 
            neighborBlogs = driver.find_elements(By.XPATH, "//div/ul/li//div[@class ='text_area___UrFH']//a")
            if scrollEndPosition() == False:
                break
            
        neighborBlogs = driver.find_elements(By.XPATH, "//div/ul/li//div[@class ='text_area___UrFH']//a")
        neighborUrls = []
        for neighborBlog in neighborBlogs:
            neighborUrls.append(neighborBlog.get_attribute('href'))
        return neighborUrls

    login(yourid, yourpassword)
                
    urls = neighborNewFeed(maxneighbornum)

    # 이웃 새글 공감 누르기
    for url in urls:
        openBlog(url)
        # 블로그 페이지 로딩을 위한 시간
        time.sleep(uniform(3.0, 7.0))
            
        # 좋아요가 클릭 가능한지 확인 후 클릭, 아니면 창 닫기 
        if availableLike() :
            clickLike()
        else : 
            closeBlog()
            
    # 설정한 태그 공감 누르기
    # for searchWord in searchWords :
    #     urls = searchBlog(searchWord, randrange(tagMinNum, tagMaxNum))
    #     for url in urls:
    #         openBlog(url)
    #         # 블로그 페이지 로딩을 위한 시간
    #         time.sleep(uniform(3.0, 7.0))
            
    #        # 좋아요가 클릭 가능한지 확인 후 클릭, 아니면 창 닫기 
    #         if availableLike() :
    #             clickLike()
    #         else : 
    #             closeBlog()
                
    driver.quit()
def main_2():
    driverFolder : str= os.getcwd()+'/selenium/chromedriver.exe'

    #자신의 아이디, 비밀번호
    yourid : str = "kei011380"
    yourpassword : str = "haedal2020!"

    # 좋아요를 누르기 전 스크롤을 할 때 스크롤 최소, 최대 시간
    scrollMinPauseTime : float = 0.5
    scrollMaxPauseTime : float = 5.0

    # 원하는 태그 목록
    searchWords : list = ["검색하고", "싶은", "검색어를", "리스트", "형태로", "입력"]

    # 태그 순서 섞기
    shuffle(searchWords)

    # 각 태그당 좋아요를 누를 최소, 최대 개수
    tagMinNum : int = 40
    tagMaxNum : int = 60

    #좋아요 누른 개수, 다음 태그로 넘어가는 개수
    clickedLikeNum : int = 0
    stopTagNum : int = 0

    # 이웃 블로그 최대 수(이웃이 많을 경우 스크롤 제한하기)
    maxneighbornum = 20
    driverFolder : str= os.getcwd()+'/selenium/chromedriver.exe'

    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_argument('--no-sandbox')
    options.add_argument("disable-gpu")
    # options.add_argument('headless')
    options.add_argument('window-size=1920x1080')
    options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")
    driver = webdriver.Chrome(options=options)

    def inputkeys(myId : str, placeholder : str):
        pp.copy(myId)
        idInput = driver.find_element(By.XPATH, f"//input[@placeholder='{placeholder}']")
        idInput.click()
        pp.copy(myId)
        time.sleep(uniform(3.0, 10.0))
        idInput.send_keys(Keys.CONTROL, 'v')
        
    def login(naverid : str, naverpassword : str):
        driver.get("https://nid.naver.com/nidlogin.login?svctype=262144&url=http://m.naver.com/aside/")    #블로그 추천
        inputkeys(naverid, "아이디")
        inputkeys(naverpassword, "비밀번호")
        driver.find_element(By.XPATH, f"//input[@placeholder='비밀번호']").send_keys(Keys.ENTER)
        time.sleep(2)

    def searchBlog(searchWord : str, articleLimit : int):
        adress = "https://m.search.naver.com/search.naver?where=m_blog&query="+searchWord+"&nso=so%3Add%2Cp%3Aall"
        driver.get(adress)

        articles = driver.find_elements(By.XPATH, "//div[@class='total_wrap']/a")
        numOfArticles = len(articles)
        SCROLL_PAUSE_TIME = 0.5
        while numOfArticles < articleLimit :
            articles = driver.find_elements(By.XPATH, "//div[@class='total_wrap']/a")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(SCROLL_PAUSE_TIME)
            numOfArticles = len(driver.find_elements(By.XPATH, "//div[@class='total_wrap']/a"))
        
        articles = driver.find_elements(By.XPATH, "//div[@class='total_wrap']/a")
        numOfArticles = len(articles)
        urls = []
        for i in range(numOfArticles):
            url = str(articles[i].get_attribute("href"))
            urls.append(url)
        return urls

    def openBlog(url):
        driver.execute_script(f"window.open('{url}');")
        driver.switch_to.window(driver.window_handles[1])

    def closeBlog():
        driver.close()
        driver.switch_to.window(driver.window_handles[0])

    def availableLike():
        nonlocal stopTagNum
        try : 
            confirmlike = driver.find_element(By.XPATH, "//*[@id='body']/div[10]/div/div[1]/div/div/a").get_attribute("class").split(" ")
            if "on" in confirmlike :
                stopTagNum += 1
                print(f'이미 좋아요 누른 게시물 {stopTagNum}개')
                return False
            elif "off" in confirmlike : 
                return True
        except Exception as e: 
            print(e)
            print('좋아요가 제한된 게시물')
            return False

    def scrollEndPosition():
        document_height = int(driver.execute_script("return document.body.scrollHeight"))
        now_scroll_height = int(driver.execute_script("return window.scrollY + window.innerHeight"))
        if now_scroll_height + 200 >= document_height:
            return False
        else : 
            return True
        
    def clickLike():
        while scrollEndPosition():
            driver.find_element(By.XPATH, "//body").send_keys(Keys.PAGE_DOWN)
            time.sleep(uniform(scrollMinPauseTime, scrollMaxPauseTime))
        
        like_btn = driver.find_element(By.XPATH, "//div[@class='btn_like']/div")
        driver.execute_script("arguments[0].scrollIntoView({block : 'center'});", like_btn)
        like_btn.click()
        nonlocal clickedLikeNum
        clickedLikeNum += 1
        print(f"블로그 좋아요를 {clickedLikeNum}개 누름")
        closeBlog()
        
    def neighborNewFeed(maxnum : int):
        driver.get("https://m.blog.naver.com/Recommendation.naver")
        time.sleep(uniform(6, 15))
        
        neighborBlogs = driver.find_elements(By.XPATH, "//div[@class ='postlist__LXY3R']//a")
        print(len(neighborBlogs))
        numOfneighborblogs = len(neighborBlogs)
        
        SCROLL_PAUSE_TIME = 1
        # while numOfneighborblogs < maxnum :
        for i in range (20):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(SCROLL_PAUSE_TIME)
            numOfneighborblogs = len(driver.find_elements(By.XPATH, "//div[@class='total_wrap']/a"))
            print(numOfneighborblogs) 
            neighborBlogs = driver.find_elements(By.XPATH, "//div[@class ='postlist__LXY3R']//a")
            if scrollEndPosition() == False:
                break
            
        neighborBlogs = driver.find_elements(By.XPATH, "//div[@class ='postlist__LXY3R']//a")
        neighborUrls = []
        for neighborBlog in neighborBlogs:
            neighborUrls.append(neighborBlog.get_attribute('href'))
        return neighborUrls

    login(yourid, yourpassword)
                
    urls = neighborNewFeed(maxneighbornum)

    # 이웃 새글 공감 누르기
    for url in urls:
        openBlog(url)
        # 블로그 페이지 로딩을 위한 시간
        time.sleep(uniform(1.0, 7.0))
            
        # 좋아요가 클릭 가능한지 확인 후 클릭, 아니면 창 닫기 
        if availableLike() :
            clickLike()
        else : 
            closeBlog()
            
    # 설정한 태그 공감 누르기
    # for searchWord in searchWords :
    #     urls = searchBlog(searchWord, randrange(tagMinNum, tagMaxNum))
    #     for url in urls:
    #         openBlog(url)
    #         # 블로그 페이지 로딩을 위한 시간
    #         time.sleep(uniform(1.0, 7.0))
            
    #        # 좋아요가 클릭 가능한지 확인 후 클릭, 아니면 창 닫기 
    #         if availableLike() :
    #             clickLike()
    #         else : 
    #             closeBlog()
                
    driver.quit()
def main_3():
    # global search
    # search=input("검색어를 입력하세요.")
    # 크롬 드라이버 경로 지정. os를 스지 않고 가능하다면 해보자.
    driverFolder : str= os.getcwd()+'/selenium/chromedriver.exe'

    #자신의 아이디, 비밀번호
    yourid : str = "kei011380"
    yourpassword : str = "haedal2020!"

    # 좋아요를 누르기 전 스크롤을 할 때 스크롤 최소, 최대 시간
    scrollMinPauseTime : float = 0.5
    scrollMaxPauseTime : float = 5.0

    # 원하는 태그 목록
    searchWords : list = ["검색하고", "싶은", "검색어를", "리스트", "형태로", "입력"]

    # 태그 순서 섞기
    shuffle(searchWords)

    # 각 태그당 좋아요를 누를 최소, 최대 개수
    tagMinNum : int = 40
    tagMaxNum : int = 60

    #좋아요 누른 개수, 다음 태그로 넘어가는 개수
    clickedLikeNum : int = 0
    stopTagNum : int = 0

    # 이웃 블로그 최대 수(이웃이 많을 경우 스크롤 제한하기)
    maxneighbornum = 20
    driverFolder : str= os.getcwd()+'/selenium/chromedriver.exe'

    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_argument('--no-sandbox')
    options.add_argument("disable-gpu")
    # options.add_argument('headless')
    options.add_argument('window-size=1920x1080')
    options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")
    driver = webdriver.Chrome(options=options)

    def inputkeys(myId : str, placeholder : str):
        pp.copy(myId)
        idInput = driver.find_element(By.XPATH, f"//input[@placeholder='{placeholder}']")
        idInput.click()
        pp.copy(myId)
        time.sleep(uniform(3.0, 10.0))
        idInput.send_keys(Keys.CONTROL, 'v')
        
    def login(naverid : str, naverpassword : str):
        driver.get("https://nid.naver.com/nidlogin.login?svctype=262144&url=http://m.naver.com/aside/")    #블로그 추천
        inputkeys(naverid, "아이디")
        inputkeys(naverpassword, "비밀번호")
        driver.find_element(By.XPATH, f"//input[@placeholder='비밀번호']").send_keys(Keys.ENTER)
        time.sleep(2)

    def searchBlog(searchWord : str, articleLimit : int):
        adress = "https://m.search.naver.com/search.naver?where=m_blog&query="+searchWord+"&nso=so%3Add%2Cp%3Aall"
        driver.get(adress)

        articles = driver.find_elements(By.XPATH, "//div[@class='total_wrap']/a")
        numOfArticles = len(articles)
        SCROLL_PAUSE_TIME = 0.5
        while numOfArticles < articleLimit :
            articles = driver.find_elements(By.XPATH, "//div[@class='total_wrap']/a")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(SCROLL_PAUSE_TIME)
            numOfArticles = len(driver.find_elements(By.XPATH, "//div[@class='total_wrap']/a"))
        
        articles = driver.find_elements(By.XPATH, "//div[@class='total_wrap']/a")
        numOfArticles = len(articles)
        urls = []
        for i in range(numOfArticles):
            url = str(articles[i].get_attribute("href"))
            urls.append(url)
        return urls

    def openBlog(url):
        driver.execute_script(f"window.open('{url}');")
        driver.switch_to.window(driver.window_handles[1])

    def closeBlog():
        driver.close()
        driver.switch_to.window(driver.window_handles[0])

    def availableLike():
        nonlocal stopTagNum
        try : 
            confirmlike = driver.find_element(By.XPATH, "//*[@id='body']/div[10]/div/div[1]/div/div/a").get_attribute("class").split(" ")
            if "on" in confirmlike :
                stopTagNum += 1
                print(f'이미 좋아요 누른 게시물 {stopTagNum}개')
                return False
            elif "off" in confirmlike : 
                return True
        except Exception as e: 
            print(e)
            print('좋아요가 제한된 게시물')
            return False

    def scrollEndPosition():
        document_height = int(driver.execute_script("return document.body.scrollHeight"))
        now_scroll_height = int(driver.execute_script("return window.scrollY + window.innerHeight"))
        if now_scroll_height + 200 >= document_height:
            return False
        else : 
            return True
        
    def clickLike():
        while scrollEndPosition():
            driver.find_element(By.XPATH, "//body").send_keys(Keys.PAGE_DOWN)
            time.sleep(uniform(scrollMinPauseTime, scrollMaxPauseTime))
        
        like_btn = driver.find_element(By.XPATH, "//div[@class='btn_like']/div")
        driver.execute_script("arguments[0].scrollIntoView({block : 'center'});", like_btn)
        like_btn.click()
        nonlocal clickedLikeNum
        clickedLikeNum += 1
        print(f"블로그 좋아요를 {clickedLikeNum}개 누름")
        closeBlog()
        
    def neighborNewFeed(maxnum : int):
        adress = "https://m.blog.naver.com/SectionPostSearch.naver?orderType=sim&searchValue="+entry.get()
        driver.get(adress)
        time.sleep(uniform(6, 15))
        
        neighborBlogs = driver.find_elements(By.XPATH, "//div[@class ='postlist__LXY3R']//a")
        print(len(neighborBlogs))
        numOfneighborblogs = len(neighborBlogs)
        
        SCROLL_PAUSE_TIME = 1
        # while numOfneighborblogs < maxnum :
        for i in range (20):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(SCROLL_PAUSE_TIME)
            numOfneighborblogs = len(driver.find_elements(By.XPATH, "//div[@class='total_wrap']/a"))
            print(numOfneighborblogs) 
            neighborBlogs = driver.find_elements(By.XPATH, "//div[@class ='postlist__LXY3R']//a")
            if scrollEndPosition() == False:
                break
            
        neighborBlogs = driver.find_elements(By.XPATH, "//div[@class ='postlist__LXY3R']//a")
        neighborUrls = []
        for neighborBlog in neighborBlogs:
            neighborUrls.append(neighborBlog.get_attribute('href'))
        return neighborUrls


        
    login(yourid, yourpassword)
                
    urls = neighborNewFeed(maxneighbornum)

    # 이웃 새글 공감 누르기
    for url in urls:
        openBlog(url)
        # 블로그 페이지 로딩을 위한 시간
        time.sleep(uniform(1.0, 7.0))
            
        # 좋아요가 클릭 가능한지 확인 후 클릭, 아니면 창 닫기 
        if availableLike() :
            clickLike()
        else : 
            closeBlog()
            
    # 설정한 태그 공감 누르기
    # for searchWord in searchWords :
    #     urls = searchBlog(searchWord, randrange(tagMinNum, tagMaxNum))
    #     for url in urls:
    #         openBlog(url)
    #         # 블로그 페이지 로딩을 위한 시간
    #         time.sleep(uniform(1.0, 7.0))
            
    #        # 좋아요가 클릭 가능한지 확인 후 클릭, 아니면 창 닫기 
    #         if availableLike() :
    #             clickLike()
    #         else : 
    #             closeBlog()
                
    driver.quit()
def end():
    sys.exit()
button1 = Button(window, text="1. 이웃 블로그 공감", command=main_1)
button1.grid(row=100, column=1) 
button2 = Button(window, text="2. 추천 블로그 공감", command=main_2)
button2.grid(row=100, column=2)
entry= Entry(window)
entry.grid(row=50, column=3)     

button3 = Button(window, text="3. 검색 시작", command=main_3)
button3.grid(row=100, column=3)

button4 = Button(window, text="종료", command=end)
button4.grid(row=400, column=2)

# label = Label(window)
# label.pack()

window.mainloop()