from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
#chromedriver version : ChromeDriver 119.0.6045.159
from dotenv import load_dotenv
import os

# MySQL 연결 및 데이터 가져오기
import mysql.connector

def crawl():
    load_dotenv()
    mydb = mysql.connector.connect(
    host=os.environ.get("MYSQL_HOST"),
    user=os.environ.get("MYSQL_USERNAME"),
    password=os.environ.get("MYSQL_PASSWORD"),
    database=os.environ.get("DATABASE"),
    port=os.environ.get("MYSQL_PORT")
    )
    mycursor = mydb.cursor()
    mycursor.execute("SELECT name FROM stores where address is null")
    result = mycursor.fetchall()

    print(len(result))
    # Selenium 웹 드라이버 설정
    webdriver_service = Service('../chromedriver.exe')  # 웹 드라이버 경로 설정
    webdriver_options = Options()
    webdriver_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36')
    webdriver_options.add_argument('--headless')
    driver = webdriver.Chrome(service=webdriver_service, options=webdriver_options)
    #URLS 검색후첫링크, sololink-xpath, multilink-xpath
    VALUES = ['//*[@id="_pcmap_list_scroll_container"]/ul/li[1]/div[1]/div/a[1]/div/div/span[1]',
        '//*[@id="app-root"]/div/div/div/div[5]/div/div[2]/div/div/div[1]/div/a/span[1]',
        ]
    # 크롤링 및 데이터 저장
    for row in result:
        name = row[0]
        print("name : "+name)
        driver.get(f"https://map.naver.com/v5/search/{name}?c=15,0,0,0,dh")
        try:
        #검색 후 여러값들이 나오는지 확인
            driver.switch_to.default_content()
            WebDriverWait(driver,2).until(
            EC.presence_of_element_located((By.ID, "searchIframe"))
            )
            driver.switch_to.frame("searchIframe")
            WebDriverWait(driver,2).until(
                EC.presence_of_element_located((By.XPATH, VALUES[0]))
            )
            firstlink = driver.find_element(By.XPATH, VALUES[0])
            firstlink.click()
        #첫링크 이동 후 주소 가져오기
            driver.switch_to.default_content()
            WebDriverWait(driver,4).until(EC.presence_of_element_located((By.ID, "entryIframe")))
            driver.switch_to.frame("entryIframe")
            WebDriverWait(driver,1).until(
                EC.presence_of_element_located((By.XPATH, VALUES[1]))
            )
            address = driver.find_element(By.XPATH, VALUES[1]).text
            if(address[:2]!="전남"):
                continue
            driver.switch_to.default_content()
        except:
        #검색 후 여러값들이 나오지 않는 경우 바로 나왔는지 아니면 없는지 확인
            try:
                driver.switch_to.default_content()
                driver.switch_to.frame("entryIframe")
                address = driver.find_element(By.XPATH, VALUES[1]).text
                if(address[:2]!="전남"):
                    continue
            except:
                continue
            
            
        print(f"address : {address}")
        #주소를 데이터베이스에 저장
        sql = "UPDATE stores SET address = %s WHERE name = %s"
        val = (address, name)
        mycursor.execute(sql, val)
        mydb.commit()

    print(len(result))
    print(mycursor.execute("SELECT COUNT(*) as row_count FROM stores where address is null"))
    # MySQL 연결 종료
    mycursor.close()
    mydb.close()

    print("크롤링이 완료되었습니다.")

