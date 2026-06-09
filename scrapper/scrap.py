import requests, re
import datetime
from bs4 import BeautifulSoup
from newspaper import Article
#from pytz import timezone
from operator import itemgetter
from scrapper.load_write import load_db_todict,load_db_tolist,write_todb
from django.conf import settings
from .models import Keywords, Media, News
from django.utils import timezone

# get_kisa_status()
# 인터넷 진흥원의 인터넷 침해사고 경보단계를 가져오는 함수
def get_kisa_status():
  r = requests.get("https://www.krcert.or.kr/main.do")
  # r kisa 메인 페이지 url을 인자로 request.get 을 실행하고 r로 반환 받음.
  soup = BeautifulSoup(r.text, "html.parser")
  # soup r.txt 를 soup으로 parsing
  kisa_status = soup.find("div", {"class": "inWrap"}).find("span", {"class": "state"}).string
  # kisa_status parsing한 soup에서 div class=inWrap 태그를 찾아, 그 하위의 span class=state 로 감싼 string을 kisa_status로 반환
  return kisa_status
  # kisa_status 반환

# time_check()
# 뉴스 수집 시간을 str 로 변환하고, 오늘 요일을 확인하는 함수. csv 파일 저장시 파일명으로 사용
def time_check():  
  #current_timef = datetime.datetime.now(timezone("Asia/Seoul")).strftime('%Y-%m-%d %H:%M:%S')
  current_timef = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  current_time = datetime.datetime.strptime(current_timef, '%Y-%m-%d %H:%M:%S')
  w_day = current_time.weekday()  # 요일체크  
  return current_time,w_day

# convert_time()
# get_news()에서 사용할 수 있게 검색된 news의 pubTime을 str로 변환
def convert_time(time):
  # print(time)       
  strip = datetime.datetime.strptime(time, '%a, %d %b %Y %H:%M:%S +0900')
  converted_str = strip.strftime('%Y-%m-%d %H:%M:%S')
  converted = datetime.datetime.strptime(converted_str, '%Y-%m-%d %H:%M:%S')  
  # print(converted)
  return converted  

# edit_media_list()
# domain 과 신문사 name을 개체로 만들어서 media_list에 추가해 반환하는 함수
# db화로 인해 불필요
'''
def edit_media_list(domain, name, media_list):
    site_info = {"domain": domain, "media_name": name}
    media_list.append(site_info)    
    return media_list
'''


# brush_Text
# tag 및 뉴라인을 제거
def brush_text(text):
  x = str(text) 
  #obj의 part 부분만을 str x 로 선언 
  x = re.sub('<.+?>', '', x, 0, re.I | re.S)  
  x = re.sub('&quot;', '', x, 0, re.I | re.S)
  x = re.sub('&apos;', '', x, 0, re.I | re.S)
  x = re.sub(r'\r?\n', '', x, 0, re.I | re.S)
  #정규식을 | 을 사용하 나열시 최초 매칭되는 것 하나만 sub처리되기 때문에 각각 개별 처리  
  #print(str(x))
  return str(x)


# get_brand()
# domain을 requeset로 soup화 하여 title tag의 내용물을 신문사 이름으로 반환하는 함수
def get_brand(domain,headers):  
  if Media.objects.filter(domain=domain).exists():
  # if any(d['domain'] == domain for d in media_list):
    # domain이 테이블 안에 있으면    
    # site_info meia_list에서 domain 값을 가진 개체를 site_info로 반환    
    # name site_info의 media_name을 name으로 반환
    return Media.objects.get(domain=domain)
    # name과 media_list 반환
  else:
    # domain이 media_list에 없으면
      try:
        rst = requests.get(
          f"http://{domain}",
          allow_redirects=True,
          timeout=10,
          headers=headers,
          verify=False)
        # rst domain 을 reguest.get()에 인자로 주고 rst를 반환받음
      except:
        # request.get() 했을 때 오류가 발생하면
        print(f'get {domain} failed')
        name = Media(domain=domain, media_name=domain)
        name.save()
        # name domain 값을 name으로 처리
        # media_list = edit_media_list(domain, name, media_list)
        # new_media domain, name 을 edit_media_list에 인자로 주고 반환값으로 media_list 갱신
        return Media.objects.get(domain=domain)
        # return name, media_list
        # name, media_list 반환
      else:
        # request.get()이 정상적으로 실행되면
        print(f'now checking {domain}')        
        rst.encoding = rst.apparent_encoding
        # rst.encoding rst개체를 원문 기사 인코딩 방식대로 인코딩처리. euc-kr로 나타내는게 목적이지만 원문 기사가 euc-kr이 아니었다면 여전히 깨질 수 있음. 
        soup = BeautifulSoup(rst.text, 'html.parser')
        print(soup)
        # soup rst.text 를 soup으로 parsing
        try:
          name = soup.find("head").find("title").string
          # name head tag의 title tag 문자열을 name으로 반환시도해서
        except:
          # title tag 가 없는 등 오류가 발생하면
          print(f'soup {domain} failed')
          name = Media(domain=domain, media_name=domain)
          name.save()
          # name domain 값을 name으로 처리
          # media_list = edit_media_list(domain, name, media_list)
          # media_list domain, name 을 edit_media_list에 인자로 주고 반환값으로 media_list 갱신
          return Media.objects.get(domain=domain)
          # return name, media_list
          # name, media_list 반환
        else:
          # name 값이 정상적으로 반환되면
          # media_list = edit_media_list(domain, name, media_list)
          # media_list domain, name 을 edit_media_list에 인자로 주고 반환값으로 media_list 갱신
          print(f'{domain} name is {name}')
          name = brush_text(name)
          new_media = Media(domain=domain, media_name=name)
          new_media.save()
          return new_media
          # return name, media_list
          # name, media_list 반환

# extract_domain()
# 기사 link에서 최상위 도메인 주소를 추출하는 함수
def extract_domain(link):
  extract_domain = link.split('/')  
  if len(extract_domain) < 2 :
    # 기사 link 입력이 제대로 되어 있지 않을 때의 처리
    domain = "도메인 에러"
    return domain
  else:
    domain = extract_domain[2]  
    return domain

# make_text()
# 인자로 받은 link, header스로 기사 본문을 수집하고, 본문과 domain 주소를 반환하는 함수
def make_text(link, headers):
  domain = extract_domain(link)   
  try:        
    a = Article(link, language='ko', headers=headers, verify=False)
    # a link를 인자로 newspaper3k의 article 메써드 실행
    a.download()
    # a 를 download() 하고
    a.parse()
    # a 를 parse() 여기까지 해야 a.text 호출이 가능.
  except:
    text = "본문을 가져올 수 없습니다(SSL Certificate 에러)"
    # text article 메써드 실행 중 오류가 발생하면 에러 메세지로 본문 대체
    return text, domain
    # text, domain 반환
  else:
    text = a.text
    # text a.text 본문을 text로 선언
    if len(text) < 20:
      text = "본문을 가져올 수 없습니다(newspaper3k가 내용을 가져오지 못함)"
      # text 본문이 20글자 미만일 경우 엉뚱한 부분을 parsing 해 온것으로 처리
      return text, domain
      # text, domain 반환
    else:
      return text, domain
      # text, domain 반환

# remove_tag()
# entry 개체의 title, description의 태그를 제거 후 반환 

# make_article()
# entry 개체를 표시할 정보에 맞춰 다듬는 함수
def make_article(entry, cat):
  headers = {'User-Agent':
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'}
  # headers 기사 본문 수집과 신문사 정보를 얻을 때 사용할 header
  text, domain = make_text(entry['originallink'], headers)  
  cat_obj = Keywords.objects.get(keyword=cat)
  # text, domain make_text()에 entry link값을 인로 주고 기사 본문과 domain 주소를 반환받음  
  result = News(
    title = brush_text(entry.get('title')),    
    description = brush_text(entry.get('description')),
    pubDate = convert_time(entry.get('pubDate')),    
    link = entry['originallink'],
    text = brush_text(text),
    media = get_brand(domain,headers)
    )  
  result.save()  
  result.cat.add(cat_obj)
  #print(result)
  # 위에서 반환 받은 값으로 entry 를 result로 재구성
  # return result
  # result 개체와 meida_list 반환

# get_news()
# naver news api 로 word에 관련된 뉴스 기사를 검색하는 함수
def get_news(word, current_time, w_day):  
  sorted_news_list = []
  # sorted_news_list 최종 반환할 sorted_news_list를 초기화
  na_id = settings.N_ID
  # NA_id naver news api id
  na_psd = settings.N_PWD
  # na_psd naver news api passowrd
  encode_type = 'json'  
  # encode_type naver news api 출력 방식 : json 또는 xml
  max_display = 10
  # max_display 검색어당 가져올 뉴스 수
  sort = 'sim'
  # sort 결과값의 정렬기준 : 시간순 date, 관련도 순 sim
  start = 1
  # start 출력 위치
  headers_naver = {'User-Agent':
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36',
    'X-Naver-Client-Id': na_id,
    'X-Naver-Client-Secret': na_psd}
  # headers_naver bot block 방지용 header 
  print(f'{word} 기사 검색중')
  url = f'https://openapi.naver.com/v1/search/news.{encode_type}?query="{word}"&display={str(int(max_display))}&start={str(int(start))}&sort={sort}'
  try:
  # url new api 실제 사용 url. 위에서 선언한 변수 값을 선언
    news_request = requests.get(url, headers=headers_naver)
    # news_request request로 받은 json 파일을 new_request로 선언
  except:
    print(f"'{word}' news request  error")
    return sorted_news_list
  else:   
    news_list = news_request.json()["items"]   
    # news_list news_rqueset의 개체들을 list로 변환
    for news in news_list:         
      pubDate = convert_time(news['pubDate'])      
      # pubDate = news_list 개체의 pubdate를 비교 가능한 형태로 변환    
      dayDiff = (current_time - pubDate).days      
      # dayDiff 오늘 날짜 - 기사 날짜 
      if w_day == 0 and dayDiff < 3:                
        sorted_news_list.append(news)
        # sorted_news_list 오늘이 월요일이면 72시간 이내 기사만 sorted_news_list에 추가
      elif w_day != 0 and dayDiff <= 1:          
        # sorted_news_list 오늘이 월요일이 아니면 48시간 이내 기사만 sorted_news_list에 추가
        sorted_news_list.append(news)
      else:
        pass      
    return sorted_news_list
  # sorted_news_list 반환

# News 모델의 데이터를 읽어서 json 으로 줄 수 있도록 모두 string으로 변환
# db 데이터에 pubdate 기준으로 필터를 걸어서 그날자 기사가 없으면 rase error 하는 로직 필요
def load_news(search_date, w_day):
  str_list = []  
  days = 3 if w_day == 0 else 2     
  #news_list = News.objects.all().order_by('-pubDate')  
  news_list = News.objects.filter(pubDate__range=(timezone.now()-datetime.timedelta(days=days),timezone.now())).order_by('-pubDate')  
  for news in news_list:    
    item = {
      'title': news.title,
      'description' : news.description,
      'text': news.text,
      'pubDate': datetime.datetime.strftime(news.pubDate,'%Y-%m-%d %H:%M:%S'),
      'cat': ', '.join(news.cat.all().values_list('keyword', flat=True)),
      'link': news.link,
      'media': news.media.media_name
    }  
    str_list.append(item)    
  return str_list
  

# init()
# main.py에서 flask app으로 호출되며 수집된 기사를 list로 반환하는 함수. 
# home(/)이 호출될 때마다 실행되며, 현재 replit.com에서 flask 페이지가 두번씩 호출되는 버그가 있어, 변수를 전역으로 사용할 경우 '변수=함수' 사용시 결과 값이 2개 이상 리턴될 수 있음. 
# 버그를 회피하기 위해 반드시 함수내 변수로만 지정하고 global을 사용하지 말것 
def init():
  # part 1. 인자에 사용할 변수들  
  scrapped_news = []
  # scrapped_news 뉴스 리스트 초기화 
  current_time, w_day = time_check()
  # current_time, w_day 현재 time과 요일
  search_date = current_time.strftime('%Y-%m-%d') 
  # current_time에서 date 만 Y-M-D형태로 추출. db 파일명으로 사용.
    
  # part 2. 기사 처리 
  if not News.objects.filter(pubDate__date=datetime.date.today()).count() == 0:
    scrapped_news = load_news(search_date, w_day)
    print("DB에서 기사를 불러왔습니다.")    
    # 이미 수집해서 db 파일을 작성했으면 이걸 load  
    return scrapped_news      
  else:  
    # DB에 내용이 없는 경우
    print("불러올 기사 파일이 없습니다. ")
    # media 는 이제 db에서 직접 쿼리할 수 있으므로 리스트를 만들어 넘겨주지 않아도 됨   
    # media_list = Media.objects.all()           

    keywords =  Keywords.objects.all().values_list('keyword', flat=True)
    #keywords =  Keywords.objects.all()[:2].values_list('keyword', flat=True)
    # 뉴스에서 검색할 키워드  

    for key in keywords:      
      news_list = get_news(key, current_time, w_day)      
      # keywords 의 각 검색어를 인자로 get_new를 실행하고 결과를 news_list로 반환받음
      if len(news_list) < 1:
        print(f"{key}로 검색된 기사가 없습니다")
        pass
      else:
        for entry in news_list:
          # 반환 받은 news_list중 중복 기사를 처리                  
          # cat(egory) 값을 검색어word로 선언하고
          if News.objects.filter(link=entry['originallink']).exists():
            print("중복")
            add_key = Keywords.objects.get(keyword=key)
            News.objects.get(link=entry['originallink']).cat.add(add_key)
          else:
            print("신규")     
            make_article(entry, key)    
            # 중복 기사가 아닐 경우 entry를 cat, media_list와 함께 make_article 함수에 인자로 던져주고 result,medi_list를 반환받음
            # Media_list를 반환 받을 필요가 있는지 확인해볼 것.          
            #if result["media"] == "도메인 에러" : 
              # new api 결과에서 link가 누락된 기사 예외처리
            #  pass
            #else:
            #  scrapped_news.append(result)
          # 반환받은 result 개체를 scrapped_news에 추가
    # part 3. 수집 결과 반환              
    # sorted_scrapped_news = sorted(scrapped_news, key=itemgetter('pubDate'), reverse=True)
    # 수집이 끝난 scrapped_news 리스트를 최신 순으로 정렬    )
    # write_todb(sorted_scrapped_news, f'news_{search_date}')
    # sorted_scrapped news를 new_년-월-일.csv로 저장    
    # write_todb(media_list,'media')
    # 반환받은 media_list를 media.csv에 덮어쓰기는 것으로 이제 db로 전환했기 때문에 주석처리
    print("뉴스 수집을 완료하였습니다.")
    scrapped_news = load_news(search_date, w_day)
    return scrapped_news
    # scrapped_news = load_db_todict(f'news_{search_date}')
    # return sorted_scrapped_news
    # scrapped_news  
    
    # 리스트화 필요
    # new_년-월-일.csv에서 load한 기사를 scrapped_news로 반환

