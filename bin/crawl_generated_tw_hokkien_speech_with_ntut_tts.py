# -*- coding: utf-8 -*-
# file: 
# date: 2024-02-07
#
# This program will building speech audios by leveraging 
# http://tts001.iptcloud.net:8804/
#
# Try:
# python ./bin/crawl_generated_tw_hokkien_speech_with_ntut_tts.py demo_configs/crawl_generated_tw_hokkien_speech_with_ntut_tts.json
#
# And here are some references
#
# Run Selenium Python script without headless mode on Linux Server:
# https://unix.stackexchange.com/questions/516212/run-selenium-python-script-without-headless-mode-on-linux-server
#
# How to click and select download audio file using selenium and python in chrome for this particular link
# https://stackoverflow.com/questions/69927668/how-to-click-and-select-download-audio-file-using-selenium-and-python-in-chrome
# 
# Install older versions of google-chrome-stable, on ubuntu 14.10
# https://unix.stackexchange.com/questions/233185/install-older-versions-of-google-chrome-stable-on-ubuntu-14-10


import sys
import os
import json
import time
import requests
import random
import hashlib
import opencc
from tqdm import tqdm
from typing import Dict, List, Final, Union, Optional, Any
from selenium.webdriver import Chrome, Firefox
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.remote.webelement import WebElement
from pyvirtualdisplay import Display

sys.path.append(
    os.path.join(os.path.dirname(__file__), "..", "src")
)
from audiopipeline.utils import remove_punctuations_alphabets


DEBUG: Final[bool] = False
NTUT_HOKKIEN_TTS_URL: Final[str] = "http://tts001.iptcloud.net:8804/"


def get_downloaded_wav_file_name(transcript: str) -> str:
    md5_hash = hashlib.md5()
    md5_hash.update(transcript.encode('utf-8'))
    return md5_hash.hexdigest() + ".wav"


def run_webdriver(
    webdriver: Optional[Union[Chrome, Firefox]], text: str, download_dir: str,  
    sleep: int=1
) -> Dict:
    print("Calling TTS with: %s" % text)
    audio_final_file: str = get_downloaded_wav_file_name(text) 
    audio_final_path: str = os.path.join(download_dir, audio_final_file)
    
    if not os.path.exists(audio_final_path):
        webdriver.get(NTUT_HOKKIEN_TTS_URL)

        accent_option: WebElement = webdriver.find_element("id", "accent")
        accent_selector: Select = Select(accent_option)
        if random.random() <= 0.5:
            # 強勢腔（高雄腔）
            accent_selector.select_by_index(0)
        else:
            # 次強勢腔（台北腔）
            accent_selector.select_by_index(1)

        gender_option: WebElement = webdriver.find_element("id", "gender")
        gender_selector: Select = Select(gender_option)
        if random.random() <= 0.5:
            # 男聲
            gender_selector.select_by_index(0)
        else:
            # 女聲
            gender_selector.select_by_index(1)

        text_frame: WebElement = webdriver.find_element("id", "js-input")
        text_frame.send_keys(text)
        time.sleep(0.5)

        trans2pinyin_btn: WebElement = webdriver.find_element("id", "js-translate")
        trans2pinyin_btn.click()
        time.sleep(1)
        
        tts_btn: WebElement = webdriver.find_element("id", "button1")
        tts_btn.click()
        
        audio: WebElement = webdriver.find_element("id", "audio1")
        audio_source_url: str = ""
        audio_file: str = ""
        while audio_source_url == "":
            audio_source_url = audio.get_attribute("src")
            time.sleep(0.1)

        audio_file = audio_source_url.split("/")[-1] + ".wav"

        webdriver.get(audio_source_url)
        webdriver.execute_script("""
            let aLink = document.createElement("a");
            let videoSrc = document.querySelector("video").firstChild.src;
            aLink.href = videoSrc;
            aLink.download = "";
            aLink.click();
            aLink.remove();
        """)

        audio_dump_path: str = os.path.join(download_dir, audio_file)
        while not os.path.exists(audio_dump_path):
            time.sleep(0.1)

        os.system("mv %s %s" % (audio_dump_path, audio_final_path))
        time.sleep(sleep)
    else:
        print("Audio %s already exists" % audio_final_path)

    record: Dict = {
        "text": text, "path": audio_final_path
    }
    return record

def webdriver_init(browser: str) -> Any:
    webdriver: Optional[Union[Chrome, Firefox]] = None
    options: Optional[Union[ChromeOptions, FirefoxOptions]] = None
    
    if browser == "chrome":
        options = ChromeOptions()
        expt_prefs: Dict = {
            "download.default_directory": output_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": False,
            "profile.default_content_setting_values.notifications": 2,
            "safebrowsing.disable_download_protection": True,
            "excludeSwitches": ['enable-automation'],
        }
        options.add_experimental_option("prefs", expt_prefs)
        options.add_argument('--user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"')
        options.add_argument("--start-maximized")
        options.add_argument("--disable-popup-blocking")
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-browser-side-navigation')
        #options.add_argument("--headless")
        
        webdriver = Chrome(options=options)
        params = {'behavior': 'allow', 'downloadPath': output_dir}
        webdriver.execute_cdp_cmd('Page.setDownloadBehavior', params)

    return webdriver


if __name__ == "__main__":
    os.environ["DBUS_SESSION_BUS_ADDRESS"] = "/some/nonsense"

    conf: Dict = json.loads(open(sys.argv[1], "r").read()) 
    print(conf)

    output_dir: str = os.path.abspath(conf["output_dir"])
    browser: str = conf["driver"]
    text_path: str = conf["text_path"]
    headless: bool = conf["headless"]
    min_char_num: int = conf["min_char_num"]
    max_char_num: int = conf["max_char_num"]
    sleep_sec: int = conf["sleep"]

    os.system("mkdir -p %s" % output_dir)
    
    if headless:
        display: Display = Display(visible=0, size=(800, 600))
        display.start()
    
    webdriver: Any = webdriver_init(browser)
        
    text_data: List[Dict] = [
        json.loads(x) for x in open(text_path, "r").read().split("\n") if x not in {""}
    ]
    out_metadata_path: str = os.path.join(output_dir, "metadata.jsonl")
    print("out_metadata_path: %s" % out_metadata_path)
    for i, record in enumerate(tqdm(text_data)):
        if i == 0:
            out_metadata_file = open(out_metadata_path, "w")
        else:
            out_metadata_file = open(out_metadata_path, "a")

        processed_text: str = opencc.OpenCC('s2tw.json').convert(
            remove_punctuations_alphabets(record["text"])
        )
        
        if len(processed_text) < min_char_num:
            print("Skip %s" % processed_text)
            continue
        if len(processed_text) >  max_char_num:
            processed_text = processed_text[:max_char_num]

        sample: Dict = run_webdriver(webdriver, processed_text, output_dir, sleep_sec)
        print("Writing:", sample)
        out_metadata_file.write(json.dumps(sample, ensure_ascii=False) + "\n")
        out_metadata_file.close()
    
    webdriver.quit()
    if headless:
        display.stop()
