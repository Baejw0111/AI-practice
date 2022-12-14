import os
import sys
import urllib.request
from selenium import webdriver
from time import sleep
from bs4 import BeautifulSoup

from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# keyword = input('검색어 : ')
# maxImages = int(input('다운로드 시도할 최대 이미지 수 : '))
keyword=[['Cirrus clouds',100],
         ['Cirrostratus clouds',100],
         ['Cirrocumulus clouds',101],
         ['Altostratus clouds',100],
         ['Altocumulus clouds',101],
         ['Stratus clouds',101],
         ['Stratocumulus clouds',100],
         ['Nimbostratus clouds',101],
         ['Cumulonimbus clouds',103],
         ['Cumulus clouds',105]]
maxImages=150

# 크롬 드라이버 설정
# (크롤링할 때 웹 페이지 띄우지 않음, gpu 사용 안함, 한글 지원, user-agent 헤더 추가)
options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument('--disable-gpu')
options.add_argument('lang=ko_KR')
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36")
options.add_experimental_option("excludeSwitches", ["enable-logging"])
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=options)

for i in keyword:
    # 프로젝트에 미리 생성해놓은 crawled_img폴더 안에 하위 폴더 생성
    # 폴더명에는 입력한 키워드, 이미지 수 정보를 표시함
    path = 'crawled_img/'+i[0]+'_'+str(maxImages)

    try:
        # 중복되는 폴더 명이 없다면 생성
        if not os.path.exists(path):
            os.makedirs(path)
        # 중복된다면 문구 출력 후 프로그램 종료
        else:
            print('이전에 같은 [검색어, 이미지 수]로 다운로드한 폴더가 존재합니다.')
            # sys.exit(0)
            continue
    except OSError:
        print ('os error')
        sys.exit(0)

    pages = int((maxImages-1)/i[1])+1 #한 페이지당 표시되는 이미지 수(100)을 참고하여 확인할 페이지 수 계산
    imgCount = 0 # 추출 시도 이미지 수
    success = 0 # 추출 성공 이미지 수
    finish = False # 이미지에 모두 접근했는지 여부

    for j in range(1,int(pages)+1):
        #웹 페이지 접근 후 1초동안 로드를 기다림
        driver.get('https://www.shutterstock.com/ko/search/'+i[0]+'/?page='+str(j))
        sleep(1)

        #크롤링이 가능하도록 html코드 가공
        html = driver.page_source
        soup = BeautifulSoup(html,'html.parser')

        imgs = soup.select('div.jss194.jss196.jss198 img') #요소 선택

        #마지막 페이지 여부 결정
        lastPage=False
        if len(imgs)!=i[1]:
            lastPage=True

        #5번 제목에서 설명함
        for img in imgs:
            src = ""
            src = img.get('src')

            if len(src):
                src = str(src).split()[0] #가장 작은 사이즈의 이미지 경로 추출
                # print(src)
                filename = src.split('/')[-1] #이미지 경로에서 날짜 부분뒤의 순 파일명만 추출
                # print(filename)
                saveUrl = path+'/'+filename #저장 경로 결정
                # print(saveUrl,"\n")

                #파일 저장
                #user-agent 헤더를 가지고 있어야 접근 허용하는 사이트도 있을 수 있음(pixabay가 이에 해당)
                req = urllib.request.Request(src, headers={'User-Agent': 'Mozilla/5.0'})
                try:
                    imgUrl = urllib.request.urlopen(req).read() #웹 페이지 상의 이미지를 불러옴
                    with open(saveUrl,"wb") as f: #디렉토리 오픈
                        f.write(imgUrl) #파일 저장
                    success+=1
                except urllib.error.HTTPError:
                    print('에러')
                    sys.exit(0)

            imgCount+=1

            if imgCount==maxImages:
                finish = True #입력한 이미지 수 만큼 모두 접근했음을 알림
                break
        
        #finish가 참이거나 더 이상 접근할 이미지가 없을 경우 크롤링 종료
        if finish or lastPage:
            break

    print(i[0]+' 성공 : '+str(success)+', 실패 : '+str(maxImages-success))