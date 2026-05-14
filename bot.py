import os
import json
import requests
import time
import base64
import threading
import anthropic
import telebot
from flask import Flask

# ==============================================================================
# [설정 1] API 키 및 봇 상태 관리
# ==============================================================================
CLAUDE_API_KEY = "sk-a0930e3ebdb7c2358c23a52f9eb01ea7dac076cb721c5b2dbe4da843eb11d018"
CLAUDE_BASE_URL = "https://aiprimetech.io"
PEXELS_API_KEY = "z9EFVT2LMQQgLRQzpRqtVRi86ySFL2GPeqZHSSMwZkCtqi3RRYNGGGkc"

# ❗텔레그램 토큰을 반드시 다시 넣어주세요❗
TELEGRAM_TOKEN = "6471858413:AAHmM-DbecDZjKv1OLz07KiEcADz3syBd2c"

client_claude = anthropic.Anthropic(
    api_key=CLAUDE_API_KEY, 
    base_url=CLAUDE_BASE_URL,
    default_headers={"User-Agent": "Mozilla/5.0"}
) 

bot = telebot.TeleBot(TELEGRAM_TOKEN)
is_running = False  # 봇 비상정지 스위치

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
# [공통] 헬퍼 함수 (메시지 및 스마트 슬립)
# ==============================================================================
def send_msg(chat_id, text):
    try:
        bot.send_message(chat_id, text)
        print(text)
    except Exception as e:
        print(f"텔레그램 통신 에러: {e}")

def smart_sleep(seconds):
    """지정된 시간(초)만큼 대기하되, 1초마다 is_running을 검사하여 강제 종료 시 즉시 탈출합니다."""
    global is_running
    for _ in range(seconds):
        if not is_running: break
        time.sleep(1)

# ==============================================================================
# [핵심] Claude API 자동 스위칭 함수 (4중 Fallback)
# ==============================================================================
def call_claude_api(prompt, max_tokens, chat_id, step_name):
    """에러 발생 시 모델을 바꿔가며 돌파하는 무적의 함수"""
    global is_running
    
    # 순서대로 찔러볼 공식/비공식 모델 리스트 (하이쿠 우선 -> 소넷 백업)
    CLAUDE_MODELS = [
        "claude-3-haiku-20240307",      # 공식 하이쿠 (가장 빠름, 대기 없음)
        "claude-3-5-sonnet-20241022",   # 최신 소넷
        "claude-3-5-haiku-20241022",    # 최신 하이쿠
        "claude-sonnet-4-7"             # 기존 가명 백업
    ]
    
    send_msg(chat_id, f"💡 [{step_name}] AI 연결을 시도합니다...")
    
    for model_name in CLAUDE_MODELS:
        for attempt in range(2): # 각 모델당 2번씩 끈질기게 시도
            if not is_running: return None
            try:
                msg = client_claude.messages.create(
                    model=model_name,
                    max_tokens=max_tokens,
                    messages=[{"role": "user", "content": prompt}]
                )
                return msg.content[0].text
            except Exception as e:
                if not is_running: return None
                send_msg(chat_id, f"⚠️ [{model_name}] 혼잡/오류. 10초 대기 후 돌파 시도...")
                smart_sleep(10)
                
    send_msg(chat_id, f"❌ 모든 AI 모델이 응답하지 않습니다. 이번 작업은 건너뜁니다.")
    return None

# ==============================================================================
# [기능 함수 모음]
# ==============================================================================
def get_free_image(keyword, chat_id):
    if not is_running: return None
    send_msg(chat_id, f"📸 Pexels 이미지 검색 중: '{keyword}'...")
    try:
        url = f"https://api.pexels.com/v1/search?query={keyword}&per_page=1&orientation=landscape"
        headers = {"Authorization": PEXELS_API_KEY}
        res = requests.get(url, headers=headers)
        if res.status_code == 200 and res.json().get('photos'):
            return requests.get(res.json()['photos'][0]['src']['large']).content
    except: pass
    return None

def get_or_create_term(base_url, headers, endpoint, name):
    if not is_running: return None
    slug = name.strip().lower().replace(" ", "-")
    try:
        res = requests.get(f"{base_url}/{endpoint}?search={name}", headers=headers)
        if res.status_code == 200 and res.json():
            for item in res.json():
                if item['name'].lower() == name.lower(): return item['id']
        res_create = requests.post(f"{base_url}/{endpoint}", headers=headers, json={"name": name, "slug": slug})
        if res_create.status_code in [200, 201]: return res_create.json()['id']
    except: pass
    return None

def upload_to_wordpress(task_info, data, thumb_data, chat_id):
    if not is_running: return
    send_msg(chat_id, f"📤 워드프레스 업로드 중 -> [{task_info['site_name']}]...")
    token = base64.b64encode(f"{task_info['wp_user']}:{task_info['wp_pass']}".encode()).decode('utf-8')
    headers = {'Authorization': f'Basic {token}'}
    base_url = task_info['wp_url']

    cat_id = get_or_create_term(base_url, headers, 'categories', task_info['keyword'])
    tag_ids = [tid for t in data.get('tags', []) if (tid := get_or_create_term(base_url, headers, 'tags', t))]

    thumb_id = None
    if thumb_data:
        try:
            res = requests.post(f"{base_url}/media", headers=headers, files={'file': (f"{task_info['keyword']}.jpg", thumb_data, 'image/jpeg')})
            if res.status_code in [200, 201]: thumb_id = res.json().get('id')
        except: pass

    try:
        post_data = {
            'title': data.get('headline', f"{task_info['keyword']} Guide"),
            'content': data.get('blog_body_html', ''),
            'status': 'publish', 'categories': [cat_id] if cat_id else [], 'tags': tag_ids,
            'slug': task_info['keyword'].strip().lower().replace(" ", "-")
        }
        if thumb_id: post_data['featured_media'] = thumb_id
        
        res_post = requests.post(f"{base_url}/posts", headers=headers, json=post_data)
        if res_post.status_code in [200, 201]: send_msg(chat_id, f"✅ 포스팅 성공! 링크:\n{res_post.json().get('link')}")
        else: send_msg(chat_id, f"❌ 업로드 실패: {res_post.text}")
    except Exception as e: send_msg(chat_id, f"❌ 통신 에러: {e}")

# ==============================================================================
# [메인 실행 스레드 (봇의 두뇌)]
# ==============================================================================
def process_tasks_in_background(chat_id, tasks_to_run):
    global is_running
    
    for task in tasks_to_run:
        if not is_running: break
        send_msg(chat_id, f"\n▶️ [작업 {task['display_id']}] {task['site_name']} ({task['keyword']}) 시작...")
        
        # 1. 목차 기획
        prompt1 = f"""You are an elite SEO Strategist. Create a highly detailed, professional blog post outline about "{task['keyword']}".
        Include: 1. 5 key factual points to rank on Google. 2. A structured outline (H2/H3). 3. 10 LSI keywords. Output ONLY the structured text."""
        outline = call_claude_api(prompt1, 1500, chat_id, "Agent 1 - 목차 기획")
        if not outline or not is_running: continue
        
        # 2. 본문 작성
        prompt2 = f"You are a Viral Content Director. Write an engaging blog post based strictly on this outline. Tone: Witty, Native US English. Over 1500 words. Focus Keyword: {task['keyword']}\nOutline: {outline}"
        draft = call_claude_api(prompt2, 3500, chat_id, "Agent 2 - 본문 작성")
        if not draft or not is_running: continue

        # 3. JSON 포맷팅
        prompt3 = f"""Format this draft into a strict JSON object. RULES: Headline starts with "{task['keyword']}". First sentence contains "{task['keyword']}". Use HTML tags (<h2>, <p>). Add link to {task['target_website']}. Output ONLY raw JSON:
        {{"headline": "{task['keyword']}: ...", "seo_description": "...", "tags": ["tag1", "tag2"], "blog_body_html": "<p>...</p>"}}
        Draft: {draft}"""
        json_text = call_claude_api(prompt3, 4000, chat_id, "Agent 3 - 포맷 검수")
        if not json_text or not is_running: continue
        
        try:
            if json_text.startswith("```json"): json_text = json_text[7:-3].strip()
            elif json_text.startswith("```"): json_text = json_text[3:-3].strip()
            result_data = json.loads(json_text)
        except:
            send_msg(chat_id, "❌ JSON 파싱 실패. 이 작업을 건너뜁니다.")
            continue

        if not is_running: break
        thumb_data = get_free_image(task['keyword'], chat_id)
        upload_to_wordpress(task, result_data, thumb_data, chat_id)
        
        if not is_running: break
        send_msg(chat_id, "과부하 방지 10초 휴식...")
        smart_sleep(10)
        
    if is_running:
        send_msg(chat_id, "🎉 지시하신 모든 포스팅이 완료되었습니다! 다음 명령을 기다립니다.")
    is_running = False

# ==============================================================================
# [텔레그램 명령어 수신부]
# ==============================================================================
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "🤖 **초고속 수익화 봇 가동!**\n- 시작: `1-1` 또는 `A` 입력\n- 강제종료: `/stop` 입력", parse_mode="Markdown")

@bot.message_handler(commands=['stop'])
def stop_bot(message):
    global is_running
    if is_running:
        is_running = False
        bot.reply_to(message, "🛑 강제 정지 신호를 보냈습니다! 진행 중이던 통신이 끝나는 즉시 봇이 멈춥니다.")
    else:
        bot.reply_to(message, "현재 실행 중인 작업이 없습니다.")

@bot.message_handler(func=lambda message: True)
def handle_run_command(message):
    global is_running
    chat_id = message.chat.id
    user_input = message.text.strip().upper()
    
    if is_running:
        send_msg(chat_id, "⚠️ 이미 다른 작업이 실행 중입니다. 멈추시려면 `/stop`을 입력하세요.")
        return

    for i, task in enumerate(tasks): task['display_id'] = f"{(i // 8) + 1}-{(i % 8) + 1}"
    group_map = {'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4, 'F': 5, 'G': 6, 'H': 7}
    tasks_to_run = [t for t in tasks if (user_input in group_map and int(t['display_id'].split('-')[1]) == group_map[user_input] + 1) or t['display_id'] == user_input]

    if not tasks_to_run:
        send_msg(chat_id, "❌ 매칭되는 작업 번호가 없습니다. (예: 1-1 또는 A)")
        return
    
    is_running = True
    send_msg(chat_id, f"🚀 총 {len(tasks_to_run)}개의 작업을 백그라운드에서 시작합니다! (정지: /stop)")
    threading.Thread(target=process_tasks_in_background, args=(chat_id, tasks_to_run)).start()

# ==============================================================================
# [Render 클라우드 가짜 웹서버 (위장막)]
# ==============================================================================
app = Flask(__name__)
@app.route('/')
def home(): return "Telegram Bot is Running smoothly!"

def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

if __name__ == "__main__":
    threading.Thread(target=run_flask).start() # 가짜 웹서버 가동
    print("클라우드용 텔레그램 봇 가동 시작...")
    bot.polling(none_stop=True) # 텔레그램 귀 열어두기