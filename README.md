# coffee-timer
import streamlit as st
import google.generativeai as genai
import time

# ページの設定
st.set_page_config(page_title="Coffee Timer", page_icon="☕", layout="centered")

# --- データの保存（時間貯金）の準備 ---
if 'total_focus_time' not in st.session_state:
    st.session_state.total_focus_time = 0

# タイトル
st.title("☕ 焙煎コーヒータイマー")
st.write("集中した時間をストックし、マスターに極上の1杯をオーダーしましょう。")

# セキュリティのため、APIキーは画面上で入力
api_key = st.text_input("Gemini APIキーを入力（パスワードのように隠れます）", type="password")
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
    st.write("") # 位置調整
    is_test = st.checkbox("テストモード（数秒で完了）")

if st.button("▶️ タイマー開始！", use_container_width=True):
    if not api_key:
        st.error("一番上にAPIキーを入力してください！")
    elif not task_name:
        st.warning("取り組む作業を入力してください（マスターがメッセージの参考にします！）")
    else:
        progress_bar = st.progress(0)
        status_text = st.empty()

        # テストモードなら5秒、通常なら設定した分数（秒換算）
        total_seconds = 5 if is_test else work_time * 60

        for i in range(total_seconds):
            progress_bar.progress((i + 1) / total_seconds)
            mins, secs = divmod(total_seconds - i - 1, 60)
            status_text.markdown(f"### ⏳ 残り時間: {mins:02d}:{secs:02d} ... 集中しています🔥")
            time.sleep(1)
        
        # タイマー完了後、時間をストックに追加
        st.session_state.total_focus_time += work_time
        status_text.markdown(f"### ✅ お疲れ様でした！ {work_time}分 の生豆を収穫しました🌱")
        time.sleep(2) # メッセージを2秒見せてから画面を更新
        st.rerun()

st.markdown("---")

# ==========================================
# 2. カフェカウンター（オーダーする）
# ==========================================
st.header("🏪 2. カフェカウンター")
st.write(f"現在のストック： **{st.session_state.total_focus_time} 分** / 60 分")

# 60分に向けたプログレスバー
goal_progress = min(st.session_state.total_focus_time / 60.0, 1.0)
st.progress(goal_progress)

# 60分以上貯まったらオーダー画面を表示
if st.session_state.total_focus_time >= 60:
    st.success("🎉 60分のストックが貯まりました！極上の1杯をオーダーできます。")
    
    col_bean, col_menu = st.columns(2)
    with col_bean:
        bean_choice = st.selectbox("🫘 豆の種類", [
            "エチオピア（イルガチェフェ）", "ケニア（ケニアAA）", "タンザニア（キリマンジャロ）",
            "イエメン（モカ・マタリ）", "インドネシア（マンデリン）", "インドネシア（トラジャ）",
            "インド（モンスーン・マラバール）", "コロンビア（スプレモ）", "ブラジル（セラード）",
            "グアテマラ（アンティグア）", "コスタリカ（タラス）", "ルワンダ（インゾヴ）",
            "パナマ（ゲイシャ）", "ジャマイカ（ブルーマウンテン）", "ハワイ（コナ）", "ベトナム（ロブスタ）"
        ])
    with col_menu:
        menu_choice = st.selectbox("☕️ メニュー", [
            "ドリップコーヒー（王道の黒）", "コールドブリュー（透明な青）", "カフェ・ラテ（癒やしの白）",
            "エスプレッソ・トニック（爽快の黄）", "アフォガート（ご褒美の金）", "カフェ・モカ（甘美な茶）",
            "ウィンナーコーヒー（優雅な銀）", "ニトロ・コールドブリュー（滑らかな琥珀）",
            "コーヒー・フラッペ（氷の水色）", "カフェ・マキアート（情熱の茜色）"
        ])
        
    if st.button("🛎️ マスターにオーダーする", use_container_width=True):
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        with st.spinner("マスターが豆を挽き、心を込めて抽出しています..."):
            prompt = f"""
            あなたはこだわりのカフェのマスターです。常連客が合計60分以上の集中作業（今回の主な作業：{task_name}）を見事に達成し、
            あなたに「{bean_choice}」の豆を使った「{menu_choice}」をオーダーしました。
            
            以下の要素を必ず入れて、極上のねぎらいのメッセージを出力してください。
            1. HARIOのキャニスターから豆を取り出し、抽出する美しい情景描写
            2. オーダーされた豆（{bean_choice}）の産地の特徴や個性を活かしたプロらしいウンチク
            3. オーダーされたメニュー（{menu_choice}）の仕上がりと、それが疲れた脳や体にどう沁み渡るかの表現
            4. お客様の努力（60分の集中と、{task_name}という作業内容）を心から称賛し、明日への活力を与える温かい一言
            
            トーンは落ち着いていて、知性的で、しかし心温まるマスターの口調でお願いします。
            """
            try:
                response = model.generate_content(prompt)
                st.markdown("### 📜 マスターからのメッセージ")
                st.info(response.text)
                
                # オーダー完了後、ストックから60分を消費する
                st.session_state.total_focus_time -= 60
                st.caption("※オーダーが完了し、ストックから60分を消費しました。")
                
            except Exception as e:
                st.error("エラーが発生しました。APIキーが正しいか確認してください。")
else:
    st.info(f"💡 極上の1杯まで、あと **{60 - st.session_state.total_focus_time} 分** の集中が必要です！")
