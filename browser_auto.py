from selenium import webdriver

search_word = input("무엇을 검색하고 싶으세요? : ")
# 셀레니움 크롬 웹드라이버로 자동으로 google 사이트 접속
browser = webdriver.Chrome("./driver/chromedriver.exe")
browser.get("https://google.co.kr")

# 검색창에 검색어 '셀레니움'입력 후 submit()
browser.find_element_by_name("q").send_keys(search_word)
browser.find_element_by_name("q").submit()

# 검색결과 제목의 html 태그가 <h3 class="LC20lb">, 검색결과 제목 출력
result_list = browser.find_elements_by_class_name("LC20lb")
for result in result_list:
    print(result.text)

# 첫 번째 검색결과 클릭해서 페이지 이동
try:
    browser.find_elements_by_class_name("LC20lb")[0].click()
except:
    print("아마도 이동할 페이지 없음")
    browser.close()
