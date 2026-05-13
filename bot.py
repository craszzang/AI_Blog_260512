import os
import sys
import json
import requests
import time
import base64
import re
import anthropic
import telebot
import threading
from flask import Flask # 클라우드를 속이기 위한 가짜 웹서버 부품

# ==============================================================================
# [설정 1] API 키 세팅
# ==============================================================================
CLAUDE_API_KEY = "sk-a0930e3ebdb7c2358c23a52f9eb01ea7dac076cb721c5b2dbe4da843eb11d018"
CLAUDE_BASE_URL = "https://aiprimetech.io"
PEXELS_API_KEY = "z9EFVT2LMQQgLRQzpRqtVRi86ySFL2GPeqZHSSMwZkCtqi3RRYNGGGkc"
TELEGRAM_TOKEN = "6471858413:AAHmM-DbecDZjKv1OLz07KiEcADz3syBd2c" # ❗반드시 다시 넣어주세요❗

client_claude = anthropic.Anthropic(
    api_key=CLAUDE_API_KEY, 
    base_url=CLAUDE_BASE_URL,
    default_headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"}
) 

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# ❗비상 정지를 위한 전역 스위치(플래그) 추가❗
STOP_FLAG = False

# ==============================================================================
# [클라우드 생존용 가짜 웹서버 세팅] Render.com 등에서 포트(Port) 바인딩용
# ==============================================================================
app = Flask(__name__)

@app.route('/')
def keep_alive():
    return "Bot is running 24/7!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# ==============================================================================
# [설정 2] 워드프레스 작업 리스트 (56개 완벽 복구)
# ==============================================================================
tasks = [
    # --- 1번 사이트 (아마존 뷰티) ---
    { "site_name": "아마존 뷰티", "wp_url": "https://sieunjay.blog/wp-json/wp/v2", "wp_user": "admin", "wp_pass": "wuRN y2VY 6Zb2 YBNy DtfG Go0c", "keyword": "beauty", "target_website": "https://sieunjay.blog/category/beauty/" },
    { "site_name": "아마존 뷰티", "wp_url": "https://sieunjay.blog/wp-json/wp/v2", "wp_user": "admin", "wp_pass": "wuRN y2VY 6Zb2 YBNy DtfG Go0c", "keyword": "fashion", "target_website": "https://sieunjay.blog/category/fashion/" },
    { "site_name": "아마존 뷰티", "wp_url": "https://sieunjay.blog/wp-json/wp/v2", "wp_user": "admin", "wp_pass": "wuRN y2VY 6Zb2 YBNy DtfG Go0c", "keyword": "makeup-tutorial", "target_website": "https://sieunjay.blog/category/makeup-tutorial/" },
    { "site_name": "아마존 뷰티", "wp_url": "https://sieunjay.blog/wp-json/wp/v2", "wp_user": "admin", "wp_pass": "wuRN y2VY 6Zb2 YBNy DtfG Go0c", "keyword": "makeup-hacks", "target_website": "https://sieunjay.blog/category/makeup-hacks/" },
    { "site_name": "아마존 뷰티", "wp_url": "https://sieunjay.blog/wp-json/wp/v2", "wp_user": "admin", "wp_pass": "wuRN y2VY 6Zb2 YBNy DtfG Go0c", "keyword": "hair", "target_website": "https://sieunjay.blog/category/hair/" },
    { "site_name": "아마존 뷰티", "wp_url": "https://sieunjay.blog/wp-json/wp/v2", "wp_user": "admin", "wp_pass": "wuRN y2VY 6Zb2 YBNy DtfG Go0c", "keyword": "nails", "target_website": "https://sieunjay.blog/category/nails/" },
    { "site_name": "아마존 뷰티", "wp_url": "https://sieunjay.blog/wp-json/wp/v2", "wp_user": "admin", "wp_pass": "wuRN y2VY 6Zb2 YBNy DtfG Go0c", "keyword": "weight-loss", "target_website": "https://sieunjay.blog/category/weight-loss/" },
    { "site_name": "아마존 뷰티", "wp_url": "https://sieunjay.blog/wp-json/wp/v2", "wp_user": "admin", "wp_pass": "wuRN y2VY 6Zb2 YBNy DtfG Go0c", "keyword": "beauty", "target_website": "https://sieunjay.blog/category/beauty/" },

    # --- 2번 사이트 (아마존 게임) ---
    { "site_name": "아마존 게임", "wp_url": "https://sieunjaya.blog/wp-json/wp/v2", "wp_user": "admin", "wp_pass": "RETh rsEY vepJ 9VY5 i5hv 8fNL", "keyword": "gameplay", "target_website": "https://sieunjaya.blog/category/gameplay/" },
    { "site_name": "아마존 게임", "wp_url": "https://sieunjaya.blog/wp-json/wp/v2", "wp_user": "admin", "wp_pass": "RETh rsEY vepJ 9VY5 i5hv 8fNL", "keyword": "reviews", "target_website": "https://sieunjaya.blog/category/reviews/" },
    { "site_name": "아마존 게임", "wp_url": "https://sieunjaya.blog/wp-json/wp/v2", "wp_user": "admin", "wp_pass": "RETh rsEY vepJ 9VY5 i5hv 8fNL", "keyword": "trailers", "target_website": "https://sieunjaya.blog/category/trailers/" },
    { "site_name": "아마존 게임", "wp_url": "https://sieunjaya.blog/wp-json/wp/v2", "wp_user": "admin", "wp_pass": "RETh rsEY vepJ 9VY5 i5hv 8fNL", "keyword": "pc", "target_website": "https://sieunjaya.blog/category/pc/" },
    { "site_name": "아마존 게임", "wp_url": "https://sieunjaya.blog/wp-json/wp/v2", "wp_user": "admin", "wp_pass": "RETh rsEY vepJ 9VY5 i5hv 8fNL", "keyword": "xbox", "target_website": "https://sieunjaya.blog/category/xbox/" },
    { "site_name": "아마존 게임", "wp_url": "https://sieunjaya.blog/wp-json/wp/v2", "wp_user": "admin", "wp_pass": "RETh rsEY vepJ 9VY5 i5hv 8fNL", "keyword": "playstation", "target_website": "https://sieunjaya.blog/category/portable-consoles/" },
    { "site_name": "아마존 게임", "wp_url": "https://sieunjaya.blog/wp-json/wp/v2", "wp_user": "admin", "wp_pass": "RETh rsEY vepJ 9VY5 i5hv 8fNL", "keyword": "gameplay", "target_website": "https://sieunjaya.blog/category/gameplay/" },
    { "site_name": "아마존 게임", "wp_url": "https://sieunjaya.blog/wp-json/wp/v2", "wp_user": "admin", "wp_pass": "RETh rsEY vepJ 9VY5 i5hv 8fNL", "keyword": "reviews", "target_website": "https://sieunjaya.blog/category/reviews/" },

    # --- 3번 사이트 (아마존 피트니스) ---
    { "site_name": "아마존 피트니스", "wp_url": "https://sieunjayb.blog/wp-json/wp/v2", "wp_user": "admin", "wp_pass": "nDVi eqoA 63Ie l7ju qytK geqY", "keyword": "womens-fitness", "target_website": "https://sieunjayb.blog/category/womens-fitness/" },
    { "site_name": "아마존 피트니스", "wp_url": "https://sieunjayb.blog/wp-json/wp/v2", "wp_user": "admin", "wp_pass": "nDVi eqoA 63Ie l7ju qytK geqY", "keyword": "mens-fitness", "target_website": "https://sieunjayb.blog/category/mens-fitness/" },
    { "site_name": "아마존 피트니스", "wp_url": "https://sieunjayb.blog/wp-json/wp/v2", "wp_user": "admin", "wp_pass": "nDVi eqoA 63Ie l7ju qytK geqY", "keyword": "cardio", "target_website": "https://sieunjayb.blog/category/cardio/" },
    { "site_name": "아마존 피트니스", "wp_url": "https://sieunjayb.blog/wp-json/wp/v2", "wp_user": "admin", "wp_pass": "nDVi eqoA 63Ie l7ju qytK geqY", "keyword": "detox-guides", "target_website": "https://sieunjayb.blog/category/detox-guides/" },
    { "site_name": "아마존 피트니스", "wp_url": "https://sieunjayb.blog/wp-json/wp/v2", "wp_user": "admin", "wp_pass": "nDVi eqoA 63Ie l7ju qytK geqY", "keyword": "yoga", "target_website": "https://sieunjayb.blog/category/yoga/" },
    { "site_name": "아마존 피트니스", "wp_url": "https://sieunjayb.blog/wp-json/wp/v2", "wp_user": "admin", "wp_pass": "nDVi eqoA 63Ie l7ju qytK geqY", "keyword": "weight-loss", "target_website": "https://sieunjayb.blog/category/weight-loss/" },
    { "site_name": "아마존 피트니스", "wp_url": "https://sieunjayb.blog/wp-json/wp/v2", "wp_user": "admin", "wp_pass": "nDVi eqoA 63Ie l7ju qytK geqY", "keyword": "healthy-food", "target_website": "https://sieunjayb.blog/category/healthy-food/" },
    { "site_name": "아마존 피트니스", "wp_url": "https://sieunjayb.blog/wp-json/wp/v2", "wp_user": "admin", "wp_pass": "nDVi eqoA 63Ie l7ju qytK geqY", "keyword": "nutrition-guides", "target_website": "https://sieunjayb.blog/category/nutrition-guides/" },

    # --- 4번 사이트 (클릭뱅크 재테크) ---
    { "site_name": "클릭뱅크 재테크", "wp_url": "https://sieunjayc.blog/wp-json/wp/v2", "wp_user": "admin", "wp_pass": "JIcC pZUE gyTI zcH5 TNAs VSZw", "keyword": "passive-income", "target_website": "https://sieunjayc.blog/category/passive-income/" },
    { "site_name": "클릭뱅크 재테크", "wp_url": "https://sieunjayc.blog/wp-json/wp/v2", "wp_user": "admin", "wp_pass": "JIcC pZUE gyTI zcH5 TNAs VSZw", "keyword": "advice", "target_website": "https://sieunjayc.blog/category/advice/" },
    { "site_name": "클릭뱅크 재테크", "wp_url": "https://sieunjayc.blog/wp-json/wp/v2", "wp_user": "admin", "wp_pass": "JIcC pZUE gyTI zcH5 TNAs VSZw", "keyword": "ideas", "target_website": "https://sieunjayc.blog/category/ideas/" },
    { "site_name": "클릭뱅크 재테크", "wp_url": "https://sieunjayc.blog/wp-json/wp/v2", "wp_user": "admin", "wp_pass": "JIcC pZUE gyTI zcH5 TNAs VSZw", "keyword": "amazon-fba", "target_website": "https://sieunjayc.blog/category/amazon-fba/" },
    { "site_name": "클릭뱅크 재테크", "wp_url": "https://sieunjayc.blog/wp-json/wp/v2", "wp_user": "admin", "wp_pass": "JIcC pZUE gyTI zcH5 TNAs VSZw", "keyword": "dropshipping", "target_website": "https://sieunjayc.blog/category/dropshipping/" },
    { "site_name": "클릭뱅크 재테크", "wp_url": "https://sieunjayc.blog/wp-json/wp/v2", "wp_user": "admin", "wp_pass": "JIcC pZUE gyTI zcH5 TNAs VSZw", "keyword": "passive-income", "target_website": "https://sieunjayc.blog/category/passive-income/" },
    { "site_name": "클릭뱅크 재테크", "wp_url": "https://sieunjayc.blog/wp-json/wp/v2", "wp_user": "admin", "wp_pass": "JIcC pZUE gyTI zcH5 TNAs VSZw", "keyword": "advice", "target_website": "https://sieunjayc.blog/category/advice/" },
    { "site_name": "클릭뱅크 재테크", "wp_url": "https://sieunjayc.blog/wp-json/wp/v2", "wp_user": "admin", "wp_pass": "JIcC pZUE gyTI zcH5 TNAs VSZw", "keyword": "ideas", "target_website": "https://sieunjayc.blog/category/ideas/" },

    # --- 5번 사이트 (암호화폐 뉴스) ---
    { "site_name": "암호화폐 뉴스", "wp_url": "https://sieunjayd.blog/wp-json/wp/v2", "wp_user": "admin", "wp_pass": "yved 5S3R 8nD0 Nfw3 DLgH K9Fe", "keyword": "altcoin", "target_website": "https://sieunjayd.blog/category/latest-news/altcoin/" },
    { "site_name": "암호화폐 뉴스", "wp_url": "https://sieunjayd.blog/wp-json/wp/v2", "wp_user": "admin", "wp_pass": "yved 5S3R 8nD0 Nfw3 DLgH K9Fe", "keyword": "market-analysis", "target_website": "https://sieunjayd.blog/category/latest-news/market-analysis/" },
    { "site_name": "암호화폐 뉴스", "wp_url": "https://sieunjayd.blog/wp-json/wp/v2", "wp_user": "admin", "wp_pass": "yved 5S3R 8nD0 Nfw3 DLgH K9Fe", "keyword": "trending-cryptos", "target_website": "https://sieunjayd.blog/category/trending-cryptos/" },
    { "site_name": "암호화폐 뉴스", "wp_url": "https://sieunjayd.blog/wp-json/wp/v2", "wp_user": "admin", "wp_pass": "yved 5S3R 8nD0 Nfw3 DLgH K9Fe", "keyword": "ai-news", "target_website": "https://sieunjayd.blog/category/ai-news/" },
    { "site_name": "암호화폐 뉴스", "wp_url": "https://sieunjayd.blog/wp-json/wp/v2", "wp_user": "admin", "wp_pass": "yved 5S3R 8nD0 Nfw3 DLgH K9Fe", "keyword": "altcoin", "target_website": "https://sieunjayd.blog/category/latest-news/altcoin/" },
    { "site_name": "암호화폐 뉴스", "wp_url": "https://sieunjayd.blog/wp-json/wp/v2", "wp_user": "admin", "wp_pass": "yved 5S3R 8nD0 Nfw3 DLgH K9Fe", "keyword": "market-analysis", "target_website": "https://sieunjayd.blog/category/latest-news/market-analysis/" },
    { "site_name": "암호화폐 뉴스", "wp_url": "https://sieunjayd.blog/wp-json/wp/v2", "wp_user": "admin", "wp_pass": "yved 5S3R 8nD0 Nfw3 DLgH K9Fe", "keyword": "trending-cryptos", "target_website": "https://sieunjayd.blog/category/trending-cryptos/" },
    { "site_name": "암호화폐 뉴스", "wp_url": "https://sieunjayd.blog/wp-json/wp/v2", "wp_user": "admin", "wp_pass": "yved 5S3R 8nD0 Nfw3 DLgH K9Fe", "keyword": "ai-news", "target_website": "https://sieunjayd.blog/category/ai-news/" },

    # --- 6번 사이트 (클릭뱅크 다이어트) ---
    { "site_name": "클릭뱅크 다이어트", "wp_url": "https://sieunjaye.blog/wp-json/wp/v2", "wp_user": "admin", "wp_pass": "7873 4Vx1 dtHX 8XsD OFAP X7l7", "keyword": "meal-plan", "target_website": "https://sieunjaye.blog/category/meal-plan/" },
    { "site_name": "클릭뱅크 다이어트", "wp_url": "https://sieunjaye.blog/wp-json/wp/v2", "wp_user": "admin", "wp_pass": "7873 4Vx1 dtHX 8XsD OFAP X7l7", "keyword": "weight-loss", "target_website": "https://sieunjaye.blog/category/weight-loss/" },
    { "site_name": "클릭뱅크 다이어트", "wp_url": "https://sieunjaye.blog/wp-json/wp/v2", "wp_user": "admin", "wp_pass": "7873 4Vx1 dtHX 8XsD OFAP X7l7", "keyword": "recipes", "target_website": "https://sieunjaye.blog/category/recipes/" },
    { "site_name": "클릭뱅크 다이어트", "wp_url": "https://sieunjaye.blog/wp-json/wp/v2", "wp_user": "admin", "wp_pass": "7873 4Vx1 dtHX 8XsD OFAP X7l7", "keyword": "supplements", "target_website": "https://sieunjaye.blog/category/supplements/" },
    { "site_name": "클릭뱅크 다이어트", "wp_url": "https://sieunjaye.blog/wp-json/wp/v2", "wp_user": "admin", "wp_pass": "7873 4Vx1 dtHX 8XsD OFAP X7l7", "keyword": "workouts", "target_website": "https://sieunjaye.blog/category/workouts/" },
    { "site_name": "클릭뱅크 다이어트", "wp_url": "https://sieunjaye.blog/wp-json/wp/v2", "wp_user": "admin", "wp_pass": "7873 4Vx1 dtHX 8XsD OFAP X7l7", "keyword": "detox", "target_website": "https://sieunjaye.blog/category/detox/" },
    { "site_name": "클릭뱅크 다이어트", "wp_url": "https://sieunjaye.blog/wp-json/wp/v2", "wp_user": "admin", "wp_pass": "7873 4Vx1 dtHX 8XsD OFAP X7l7", "keyword": "fasting", "target_website": "https://sieunjaye.blog/category/fasting/" },
    { "site_name": "클릭뱅크 다이어트", "wp_url": "https://sieunjaye.blog/wp-json/wp/v2", "wp_user": "admin", "wp_pass": "7873 4Vx1 dtHX 8XsD OFAP X7l7", "keyword": "meal-plan", "target_website": "https://sieunjaye.blog/category/meal-plan/" },

    # --- 7번 사이트 (클릭뱅크 건강음료) ---
    { "site_name": "클릭뱅크 건강음료", "wp_url": "https://sieunjayf.blog/wp-json/wp/v2", "wp_user": "admin", "wp_pass": "Q2f0 ILwR n0Nj bPng M0pO HPrq", "keyword": "healthy", "target_website": "https://sieunjayf.blog/category/healthy/" },
    { "site_name": "클릭뱅크 건강음료", "wp_url": "https://sieunjayf.blog/wp-json/wp/v2", "wp_user": "admin", "wp_pass": "Q2f0 ILwR n0Nj bPng M0pO HPrq", "keyword": "weight-gain", "target_website": "https://sieunjayf.blog/category/weight-gain/" },
    { "site_name": "클릭뱅크 건강음료", "wp_url": "https://sieunjayf.blog/wp-json/wp/v2", "wp_user": "admin", "wp_pass": "Q2f0 ILwR n0Nj bPng M0pO HPrq", "keyword": "weight-loss", "target_website": "https://sieunjayf.blog/category/weight-loss/" },
    { "site_name": "클릭뱅크 건강음료", "wp_url": "https://sieunjayf.blog/wp-json/wp/v2", "wp_user": "admin", "wp_pass": "Q2f0 ILwR n0Nj bPng M0pO HPrq", "keyword": "detox", "target_website": "https://sieunjayf.blog/category/detox/" },
    { "site_name": "클릭뱅크 건강음료", "wp_url": "https://sieunjayf.blog/wp-json/wp/v2", "wp_user": "admin", "wp_pass": "Q2f0 ILwR n0Nj bPng M0pO HPrq", "keyword": "workouts", "target_website": "https://sieunjayf.blog/category/workouts/" },
    { "site_name": "클릭뱅크 건강음료", "wp_url": "https://sieunjayf.blog/wp-json/wp/v2", "wp_user": "admin", "wp_pass": "Q2f0 ILwR n0Nj bPng M0pO HPrq", "keyword": "kids", "target_website": "https://sieunjayf.blog/category/kids/" },
    { "site_name": "클릭뱅크 건강음료", "wp_url": "https://sieunjayf.blog/wp-json/wp/v2", "wp_user": "admin", "wp_pass": "Q2f0 ILwR n0Nj bPng M0pO HPrq", "keyword": "keto", "target_website": "https://sieunjayf.blog/category/keto/" },
    { "site_name": "클릭뱅크 건강음료", "wp_url": "https://sieunjayf.blog/wp-json/wp/v2", "wp_user": "admin", "wp_pass": "Q2f0 ILwR n0Nj bPng M0pO HPrq", "keyword": "healthy", "target_website": "https://sieunjayf.blog/category/healthy/" },
]

# ==============================================================================
# [공통] 텔레그램 메시지 전송 헬퍼 함수
# ==============================================================================
def send_msg(chat_id, text):
    try:
        bot.send_message(chat_id, text)
        print(text) # 터미널 출력
    except Exception as e:
        print(f"텔레그램 전송 에러: {e}")

# ==============================================================================
# [함수 1~5] 코어 자동화 로직 (Haiku 모델로 변경, 과부하 무한존버 탑재)
# ==============================================================================
def get_free_image(keyword, chat_id):
    send_msg(chat_id, f"📸 Pexels 이미지 검색 중: '{keyword}'...")
    try:
        url = f"https://api.pexels.com/v1/search?query={keyword}&per_page=1&orientation=landscape"
        res = requests.get(url, headers={"Authorization": PEXELS_API_KEY})
        if res.status_code == 200 and res.json()['photos']:
            return requests.get(res.json()['photos'][0]['src']['large']).content
    except: pass
    return None

def get_outline_claude(keyword, chat_id):
    global STOP_FLAG
    send_msg(chat_id, "🧠 [Agent 1] 완벽한 SEO 목차 기획 중...")
    prompt = f'You are an elite SEO Strategist. Create a detailed outline about "{keyword}". Include: 1. 5 key facts 2. H2/H3 structure 3. 10 LSI keywords. Output ONLY structured text.'
    
    attempt = 0
    while True:
        if STOP_FLAG: return None # 정지 신호가 오면 즉시 탈출
        try:
            # ❗과부하 방지: 가장 가볍고 빠른 하이쿠 모델 사용❗
            msg = client_claude.messages.create(model="claude-haiku-4-5", max_tokens=1500, messages=[{"role": "user", "content": prompt}])
            return msg.content[0].text
        except Exception as e:
            attempt += 1
            wait_time = min(15 * (2 ** (attempt - 1)), 1800)
            send_msg(chat_id, f"⚠️ 서버 과부하 (시도 {attempt}회차) - {wait_time//60}분 {wait_time%60}초 후 자동 재시도...")
            
            # 대기 시간 중에도 1초마다 정지 버튼이 눌렸는지 감시
            for _ in range(wait_time):
                if STOP_FLAG: return None
                time.sleep(1)

def generate_full_content_claude(keyword, target_website, outline_data, chat_id):
    global STOP_FLAG
    MODEL_NAME = "claude-haiku-4-5" # ❗쾌속 차선 하이쿠❗
    writer_prompt = f"Write an engaging blog post strictly on this outline. Tone: Witty, US English. Over 1500 words. Keyword: {keyword}\nOutline: {outline_data}"
    
    send_msg(chat_id, "✍️ [Agent 2] 원고 작성 중...")
    draft = None
    attempt = 0
    while True:
        if STOP_FLAG: return None # 정지 신호 확인
        try:
            msg1 = client_claude.messages.create(model=MODEL_NAME, max_tokens=3500, messages=[{"role": "user", "content": writer_prompt}])
            draft = msg1.content[0].text
            break
        except Exception as e:
            attempt += 1
            wait_time = min(15 * (2 ** (attempt - 1)), 1800)
            send_msg(chat_id, f"⚠️ 원고 작성 지연 (시도 {attempt}회차) - {wait_time}초 후 재시도...")
            for _ in range(wait_time):
                if STOP_FLAG: return None
                time.sleep(1)

    if not draft: return None

    editor_prompt = f"""Format this draft into a strict JSON object. RULES: Headline starts with "{keyword}". First sentence contains "{keyword}". Use HTML tags (<h2>, <p>). Add link to {target_website}.
    Output ONLY raw JSON: {{"headline": "...", "seo_description": "...", "tags": ["tag1"], "blog_body_html": "<p>...</p>"}} \nDraft: {draft}"""

    send_msg(chat_id, "🧐 [Agent 3] SEO 포맷팅 중...")
    attempt = 0
    while True:
        if STOP_FLAG: return None # 정지 신호 확인
        try:
            msg2 = client_claude.messages.create(model=MODEL_NAME, max_tokens=4000, messages=[{"role": "user", "content": editor_prompt}])
            json_text = msg2.content[0].text.strip()
            if json_text.startswith("```json"): json_text = json_text[7:-3].strip()
            elif json_text.startswith("```"): json_text = json_text[3:-3].strip()
            return json.loads(json_text)
        except Exception as e:
            attempt += 1
            wait_time = min(15 * (2 ** (attempt - 1)), 1800)
            send_msg(chat_id, f"⚠️ 포맷팅 지연 (시도 {attempt}회차) - {wait_time}초 후 재시도...")
            for _ in range(wait_time):
                if STOP_FLAG: return None
                time.sleep(1)

def upload_to_wordpress(task, data, thumb_data, chat_id):
    send_msg(chat_id, f"📤 워드프레스 업로드 중 -> [{task['site_name']}]...")
    token = base64.b64encode(f"{task['wp_user']}:{task['wp_pass']}".encode()).decode('utf-8')
    headers = {'Authorization': f'Basic {token}'}
    base_url = task['wp_url']

    # 카테고리/태그 가져오기 생략 (코드 간소화)
    thumb_id = None
    if thumb_data:
        try:
            res = requests.post(f"{base_url}/media", headers=headers, files={'file': (f"{task['keyword']}.jpg", thumb_data, 'image/jpeg')})
            if res.status_code in [200, 201]: thumb_id = res.json().get('id')
        except: pass

    try:
        post_slug = task['keyword'].strip().lower().replace(" ", "-")
        post_data = {'title': data.get('headline', f"{task['keyword']} Guide"), 'content': data.get('blog_body_html', ''), 'status': 'publish', 'slug': post_slug}
        if thumb_id: post_data['featured_media'] = thumb_id
        
        res_post = requests.post(f"{base_url}/posts", headers=headers, json=post_data)
        if res_post.status_code in [200, 201]: send_msg(chat_id, f"✅ 포스팅 성공!\n{res_post.json().get('link')}")
        else: send_msg(chat_id, f"❌ 업로드 실패")
    except: send_msg(chat_id, f"❌ 통신 에러")

# ==============================================================================
# [텔레그램 봇 리스너 & 비상정지 제어]
# ==============================================================================
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    global STOP_FLAG
    STOP_FLAG = False # 봇 깨울 때 정지 모드 해제
    bot.reply_to(message, "🤖 **자동화 비서 대기 중!**\n\n- 실행: `1-1` 또는 `A` 전송\n- 비상정지: `/stop` 전송", parse_mode="Markdown")

# ❗비상 정지 명령어 (플래그 변경으로 즉시 브레이크 작동)❗
@bot.message_handler(commands=['stop'])
def stop_bot(message):
    global STOP_FLAG
    STOP_FLAG = True
    send_msg(message.chat.id, "🛑 [비상 정지 수신] 진행 중인 모든 작업을 즉시 취소하고 대기합니다!")

# 백그라운드에서 돌아가는 실제 작업 함수 (스레드 분리)
def process_tasks(chat_id, tasks_to_run):
    global STOP_FLAG
    send_msg(chat_id, f"🚀 {len(tasks_to_run)}개 작업 릴레이 시작!")
    
    for task in tasks_to_run:
        if STOP_FLAG:
            send_msg(chat_id, "🛑 작업이 사용자에 의해 강제 종료되었습니다.")
            break
            
        send_msg(chat_id, f"\n▶️ [작업 {task['display_id']}] {task['keyword']}")
        
        outline = get_outline_claude(task['keyword'], chat_id)
        if not outline or STOP_FLAG: continue
        
        result = generate_full_content_claude(task['keyword'], task['target_website'], outline, chat_id)
        if not result or STOP_FLAG: continue
        
        thumb_data = get_free_image(task['keyword'], chat_id)
        if STOP_FLAG: continue
        
        upload_to_wordpress(task, result, thumb_data, chat_id)
        
        # 대기 중에도 정지가 가능하도록 1초씩 쪼개서 휴식
        for _ in range(5):
            if STOP_FLAG: break
            time.sleep(1)
        
    if not STOP_FLAG:
        send_msg(chat_id, "🎉 지시하신 모든 포스팅 완료!")

@bot.message_handler(func=lambda message: True)
def handle_run_command(message):
    global STOP_FLAG
    chat_id = message.chat.id
    user_input = message.text.strip().upper()
    
    for i, task in enumerate(tasks): task['display_id'] = f"{(i // 8) + 1}-{(i % 8) + 1}"
    group_map = {'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4, 'F': 5, 'G': 6, 'H': 7}
    
    tasks_to_run = [t for t in tasks if (user_input in group_map and int(t['display_id'].split('-')[1]) == group_map[user_input] + 1) or t['display_id'] == user_input]

    if not tasks_to_run: return send_msg(chat_id, "❌ 알 수 없는 명령입니다.")
    
    STOP_FLAG = False # 새 작업 시작 시 브레이크 풀기
    
    # ❗투트랙 엔진 가동: 메신저 창이 멈추지 않도록 백그라운드로 작업 던지기❗
    threading.Thread(target=process_tasks, args=(chat_id, tasks_to_run), daemon=True).start()

if __name__ == "__main__":
    print("클라우드용 텔레그램 봇 가동 시작...")
    # Flask 가짜 웹서버를 백그라운드 스레드로 실행
    threading.Thread(target=run_web, daemon=True).start()
    # 텔레그램 봇 리스너 시작
    bot.polling(none_stop=True, timeout=90)