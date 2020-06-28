from selenium import webdriver
import requests
import logging
import argparse


pages = 12
def login(_id, pw):
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    with webdriver.Chrome('./chromedriver', options=options) as driver:
        driver.implicitly_wait(5)
        driver.get('http://www.aihub.or.kr/user/login')
        driver.find_element_by_id('edit-name').send_keys(_id)
        driver.find_element_by_id('edit-pass').send_keys(pw)
        driver.find_element_by_id('edit-submit').click()


        urls = list()
        for page in range(0, pages+1):
            logger.info('GET donwload url from page {0}...'.format(page))
            driver.get('http://www.aihub.or.kr/user/8642/download_list?page={0}'.format(page))
            tbody = driver.find_element_by_xpath('//*[@id="block-stig-sub-system-main"]/div/div/div/table/tbody')

            for name, url in zip(tbody.find_elements_by_css_selector('.views-field.views-field-field-file-name'), tbody.find_elements_by_css_selector('.file.file--mime-application-zip.file--package-x-generic')):
                urls.append([name.text, url.find_element_by_tag_name('a').get_attribute('href')])



        logger.info('Success to get download urls[{0}].'.format(len(urls)))

        cookies_dict = {}
        for cookie in driver.get_cookies():
            cookies_dict[cookie['name']] = cookie['value']

        return urls, cookies_dict


def get_file(filename, url, cookies):

    headers = {
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Referer': '{0}'.format(url),
        'Accept-Language': 'en-US,en;q=0.9,ko;q=0.8',
    }


    res = requests.get(url, headers=headers, cookies=cookies)

    with open('{0}'.format(filename), 'wb') as f:
        f.write(res.content)

if __name__ =='__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--auth-id', dest='account', type=str, default='', required=True)
    parser.add_argument('--auth-pw', dest='password', type=str, default='', required=True)

    args = parser.parse_args()

    logger = logging.getLogger('logger')
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter('[ %(levelname)s | %(filename)s: %(lineno)s] %(asctime)s > %(message)s')
        file_handler = logging.FileHandler('log.log')
        file_handler.setFormatter(formatter)
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)



    _id = args.account
    pw = args.password

    urls , cookies = login(_id, pw)
    _from = int(input('Enter index of start (0 ~ {0}) : '.format(len(urls))))
    to = int(input('Enter index of end (0 ~ {0}) : '.format(len(urls))))

    urls = urls[_from:to+1]

    for url in urls:
        logger.info('Downloading {0} from {1}'.format(*url))
        get_file(*url, cookies)

