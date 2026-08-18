import streamlit as st
import google.generativeai as genai
import time
import random

# ページの設定
st.set_page_config(page_title="Coffee Timer", page_icon="☕", layout="centered")

# --- データの保存（時間貯金・コレクション・APIキー）の準備 ---
if 'total_focus_time' not in st.session_state:
    st.session_state.total_focus_time = 0

if 'collection' not in st.session_state:
    st.session_state.collection = []

# タイトル
st.title("☕ 焙煎コーヒータイマー")
st.write("集中した時間をストックし、マスターへ「注文」して極上のコレクションを増やしましょう。")

# セキュリティのため、APIキーはセッション状態に保存して消えないようにする
api_key_input = st.text_input("Gemini APIキーを入力（パスワードのように隠れます）", type="password")
if api_key_input:
    st.session_state.api_key = api_key_input

st.markdown("---")

# ==========================================
# 1. 作業タイマー（生豆を貯める）
# ==========================================
st.header("⏱️ 1. 作業タイマー")
task_name = st.text_input("これから取り組む作業", placeholder="例：Goodnotesでノートまとめ、読書など")

col_time, col_test = st.columns([2, 1])
with col_time:
    work_time = st.number_input("集中する時間（分）", min_value=1, max_value=120, value=25)
with col_test:
    st.write("") 
    is_test = st.checkbox("テストモード（数秒で完了）")

if st.button("▶️ タイマー開始！", use_container_width=True):
    current_key = st.session_state.get('api_key', '')
    if not current_key:
        st.error("一番上にAPIキーを入力してください！")
    elif not task_name:
        st.warning("取り組む作業を入力してください（マスターがメッセージの参考にします！）")
    else:
        progress_bar = st.progress(0)
        status_text = st.empty()

        total_seconds = 5 if is_test else work_time * 60

        for i in range(total_seconds):
            progress_bar.progress((i + 1) / total_seconds)
            mins, secs = divmod(total_seconds - i - 1, 60)
            status_text.markdown(f"### ⏳ 残り時間: {mins:02d}:{secs:02d} ... 集中しています🔥")
            time.sleep(1)
        
        st.session_state.total_focus_time += work_time
        status_text.markdown(f"### ✅ お疲れ様でした！ {work_time}分 の生豆を収穫しました🌱")
        time.sleep(2)
        st.rerun()

st.markdown("---")

# ==========================================
# 2. カフェカウンター（注文する）
# ==========================================
st.header("🏪 2. カフェカウンター")
st.write(f"現在のストック： **{st.session_state.total_focus_time} 分** / 60 分")

goal_progress = min(st.session_state.total_focus_time / 60.0, 1.0)
st.progress(goal_progress)

beans_list = [
    "エチオピア（イルガチェフェ）", "ケニア（ケニアAA）", "タンザニア（キリマンジャロ）",
    "イエメン（モカ・マタリ）", "インドネシア（マンデリン）", "インドネシア（トラジャ）",
    "インド（モンスーン・マラバール）", "コロンビア（スプレモ）", "ブラジル（セラード）",
    "グアテマラ（アンティグア）", "コスタリカ（タラス）", "ルワンダ（インゾヴ）",
    "パナマ（ゲイシャ）", "ジャマイカ（ブルーマウンテン）", "ハワイ（コナ）", "ベトナム（ロブスタ）"
]

menus_dict = {
    "ドリップコーヒー": "☕",
    "コールドブリュー": "🧊",
    "カフェ・ラテ": "🥛",
    "エスプレッソ・トニック": "🍋",
    "アフォガート": "🍨",
    "カフェ・モカ": "🍫",
    "ウィンナーコーヒー": "☁️",
    "ニトロ・コールドブリュー": "🫧",
    "コーヒー・フラッペ": "🥤",
    "カフェ・マキアート": "🤎"
}

if st.session_state.total_focus_time >= 60:
    st.success("🎉 60分のストックが貯まりました！下の欄に「注文」と入力してください。")
    
    order_input = st.text_input("チャット入力欄", placeholder="「注文」と入力してEnter、またはボタンを押してください")
    
    # 「注文」と入力された、またはボタンが押された場合
    if order_input == "注文" or st.button("🛎️ 注文する", use_container_width=True):
        current_key = st.session_state.get('api_key', '')
        if not current_key:
            st.error("APIキーが記憶されていません。一番上で一度キーを入れ直してください！")
        else:
            bean_choice = random.choice(beans_list)
            menu_choice = random.choice(list(menus_dict.keys()))
            menu_icon = menus_dict[menu_choice]
            
            # シンプルな見栄えの表示
            st.markdown(f"<h1 style='text-align: center; font-size: 60px;'>{menu_icon} ☕</h1>", unsafe_allow_html=True)
            st.markdown(f"<h3 style='text-align: center;'>【本日のランダム一杯】<br>{bean_choice} × {menu_choice}</h3>", unsafe_allow_html=True)
            
            genai.configure(api_key=current_key)
            # モデル名を最新の flash に変更
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            with st.spinner("マスターが豆を挽き、心を込めて抽出しています..."):
                prompt = f"""
                あなたはこだわりのカフェのマスターです。常連客が合計60分以上の集中作業（今回の主な作業：{task_name}）を見事に達成しました。
                お客様が「注文」と声をかけ、マスターであるあなたがランダムに選んだ「{bean_choice}」の豆を使った「{menu_choice}」を提供します。
                
                以下の要素を必ず入れて、極上のねぎらいのメッセージを出力してください。
                1. 丁寧なドリップの情景描写
                2. 選ばれた豆（{bean_choice}）の産地の特徴やウンチク
                3. メニュー（{menu_choice}）の味わいの表現
                4. お客様の努力（{task_name}）を称賛する温かい一言
                
                トーンは落ち着いていて、知性的で心温まるマスターの口調でお願いします。
                """
                try:
                    response = model.generate_content(prompt)
                    st.markdown("### 📜 マスターからのメッセージ")
                    st.info(response.text)
                    
                    # コレクションに追加
                    st.session_state.collection.append(f"{menu_icon} {bean_choice} ✕ {menu_choice} （作業: {task_name}）")
                    
                    # ストックから60分を消費
                    st.session_state.total_focus_time -= 60
                    st.success("✨ コレクションに新しい一杯が追加されました！")
                    
                except Exception as e:
                    st.error(f"エラーが発生しました: {e}")
else:
    st.info(f"💡 極上の1杯まで、あと **{60 - st.session_state.total_focus_time} 分** の集中が必要です！")

# ==========================================
# 3. コレクション一覧
# ==========================================
st.markdown("---")
st.header("📖 マイコレクション")
if len(st.session_state.collection) == 0:
    st.write("まだコレクションはありません。集中時間を貯めて最初の1杯をオーダーしましょう！")
else:
    for item in reversed(st.session_state.collection):
        st.markdown(f"- {item}")
