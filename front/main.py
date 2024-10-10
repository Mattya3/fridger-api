import streamlit as st
from datetime import datetime, time, timedelta
import pandas as pd
import requests
import json

ROOT_URL = 'http://192.168.102.25:8000/Ingredients'
response = requests.get(ROOT_URL)
jsons = response.text
# print(jsons)
# ChatGPT APIエンドポイントURL
CHATGPT_API_URL = "https://api.openai.com/v1/chat/completions"
secret_key = ""
# print(secret_key)

# is_expiry: 賞味期限 or 消費期限
# expiry_datetime: 期限時刻
def get_state(is_expiry, expiry_datetime):
    now = datetime.now()
    three_days_from_now = now + timedelta(days=3)
    if is_expiry == "賞味期限":
        return "Yellow" if expiry_datetime < now else "Green"
    elif is_expiry == "消費期限":
        # stateの決定
        if expiry_datetime < now:
            state = "Red"
        elif expiry_datetime < three_days_from_now:
            state = "Yellow"
        else:
            state = "Green"
        return state

# 初期データ（空のデータフレームを使用）
if "food_data" not in st.session_state:
    st.session_state.food_data = pd.DataFrame(columns=["name", "tag", "date", "amount", "unit_majar", "description"])

if "food_name" not in st.session_state:
    st.session_state.food_name = ""

# 過去の手動入力された時刻を保存するための変数をセッション状態に保存
if "manual_time" not in st.session_state:
    st.session_state.manual_time = datetime.now().time()

# 食材の追加フォーム
st.title("食材管理アプリ")

with st.form(key="add_food_form"):
    # 食材の追加フォーム
    name = st.text_input("食材名", value=st.session_state.food_name, max_chars=20)
    is_expiry = st.radio("賞味期限 or 消費期限", ("賞味期限", "消費期限"))
    expiry_date = st.date_input("期限日")

    all_day = st.radio("終日 or 手動入力", ("終日", "手動入力"))  # 初期状態はFalse
    expiry_time = st.time_input("期限時刻", value=st.session_state.manual_time, disabled=False)

    quantity = st.number_input("分量", min_value=1, step=1)

    unit_list = ["mL", "L", "g", "kg", "個", "ダース"]
    select_unit = st.selectbox("単位", unit_list)

    description = st.text_area("メモ", max_chars=200)
    submit_button = st.form_submit_button(label="食材を追加")

    if submit_button & 0 < len(name):
        if all_day == "終日":
            expiry_time = time(23, 59, 59)

        # print(f"expiry_time: {expiry_time}, all_day: {all_day}")
        expiry_datetime = datetime.combine(expiry_date, expiry_time)
        state = get_state(is_expiry, expiry_datetime)

        new_data_json = {"name": name, "tag": is_expiry, "date": expiry_datetime, "amount": quantity, "unit_majar": select_unit, "description": description}
        # new_data_json = json.dumps(new_data_json)
        # print(new_data_json)
        # print(type(new_data_json))
        res = requests.post(
            ROOT_URL,
            json = {"name": name, "tag": is_expiry, "date": expiry_datetime.isoformat(), "amount": quantity, "unit_majar": select_unit, "description": description}
        )
        # print(res.text)
        st.success(f"{name} が追加されました！")
        st.session_state.food_name = ""

# 食材リストの表示
st.header("食材リスト")
res = requests.get(ROOT_URL + "/red")
df_red = pd.json_normalize(res.json())
res = requests.get(ROOT_URL + "/yellow")
df_yellow = pd.json_normalize(res.json())
res = requests.get(ROOT_URL + "/green")
df_green = pd.json_normalize(res.json())

# # 期限順にソート
# sorted_data = st.session_state.food_data.sort_values(by="date")
# 上位3つを表示
st.subheader(f"消費期限が切れたもの")
st.write(df_red)

st.subheader(f"賞味期限が切れたもの　消費期限が近いもの")
st.write(df_yellow)

st.subheader(f"安全なもの")
st.write(df_green)

# 食材の削除
st.header("食材の削除")
res = requests.get(ROOT_URL)
df_all = pd.json_normalize(res.json())
food_list = df_all.drop('id', axis=1).to_string(index=False).split("\n")[1:]
food_id_list = df_all["id"].tolist()

delete_food = st.selectbox("削除する食材を選んでください", food_list)
delete_button = st.button("食材を削除")

if delete_button and delete_food:
    # 選択された食材のインデックスを取得
    selected = food_list.index(delete_food)
    # 対応するidを取得
    delete_food_id = food_id_list[selected]
    res = requests.delete(
        ROOT_URL + "/" + str(delete_food_id),
    )
    if res.status_code == 200:
        st.success("削除されました！")
    else:
        st.error("失敗しました！")

# ChatGPTにデータを送信してレシピを提案する
st.header("レシピ提案")
if st.button("レシピを提案"):
    food_data_pd = pd.concat([df_yellow, df_green], ignore_index=True).to_json(orient="records", force_ascii=False)
    food_data_json = json.loads(food_data_pd)
    if food_data_json:
        # データをJSON形式に変換してChatGPTに送信


        # print(food_data_json)
        prompt = f"""
次のデータフレームは自身の冷蔵庫にある食品の情報を示しています。
{food_data_json}
ただし，nameは食品名，is_expiryは期限日が賞味期限を指すか消費期限を指すか，expiry_dateは期限の日時，amountは量を示す数字，unit_majarは量を示す単位，stateは食品の状態，descriptionは備考を示しています．ただし，unit_majarは["mL", "L", "g", "kg", "個", "ダース"]の6種類であり，stateはGreen，Yellow，Redを示していてGreenは安全，黄色は注意，赤は危険であることを示しています．
次の条件を満たすレシピを提案してください．
・期限が近い食材をできるだけ多く，かつ無理のないペースで消費してください．
・その料理に要する時間をできるだけ短くしてください．
・心身ともに健康に過ごすために必要なエネルギーや栄養素を過不足なくとれる料理を提案してください．
"""
        print(prompt)
        # POSTリクエストの送信
        response = requests.post(
            CHATGPT_API_URL,
            headers={
                "Authorization": f"Bearer {secret_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-4",
                "messages": [
                    {"role": "system", "content": "あなたは優秀な料理家です。"},
                    {"role": "user", "content": prompt}
                ]
            }
        )

        # print(response.text)
        if response.status_code == 200:
            recipe = response.json()["choices"][0]["message"]["content"]
            st.subheader("提案されたレシピ")
            st.write(recipe)
        else:
            st.error("レシピの提案に失敗しました。")
    else:
        st.error("食材データがありません。")