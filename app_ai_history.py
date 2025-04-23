import streamlit as st
import pandas as pd
import json

# 預設原料資料庫與營養值 (每100g原料)
ingredient_db = {
    "冷藏未殺菌液蛋白": {"熱量": 52, "蛋白質": 10.2, "脂肪": 0.1, "碳水": 0.8, "糖": 0.0, "鈉": 400},
    "冷藏未殺菌液蛋黃": {"熱量": 322, "蛋白質": 15.8, "脂肪": 26.5, "碳水": 3.6, "糖": 0.0, "鈉": 120},
    "大豆蛋白": {"熱量": 400, "蛋白質": 90.0, "脂肪": 1.2, "碳水": 1.5, "糖": 0.0, "鈉": 750},
    "乳清蛋白": {"熱量": 392, "蛋白質": 80.0, "脂肪": 7.3, "碳水": 5.5, "糖": 5.0, "鈉": 800},
    "精製細砂": {"熱量": 384, "蛋白質": 0.0, "脂肪": 0.0, "碳水": 100.0, "糖": 100.0, "鈉": 0},
    "麥芽糖漿HM85": {"熱量": 302, "蛋白質": 0.0, "脂肪": 0.0, "碳水": 75.0, "糖": 35.0, "鈉": 2},
    "自來水": {"熱量": 0, "蛋白質": 0.0, "脂肪": 0.0, "碳水": 0.0, "糖": 0.0, "鈉": 0},
    "統一麵粉": {"熱量": 357, "蛋白質": 9.8, "脂肪": 1.0, "碳水": 76.0, "糖": 0.3, "鈉": 4},
    "無鋁泡打粉": {"熱量": 156, "蛋白質": 0.0, "脂肪": 0.0, "碳水": 39.0, "糖": 0.0, "鈉": 7500},
    "穀物奶粉": {"熱量": 485, "蛋白質": 9.7, "脂肪": 7.0, "碳水": 79.0, "糖": 2.0, "鈉": 37},
    "赤藻糖醇": {"熱量": 0, "蛋白質": 0.0, "脂肪": 0.0, "碳水": 97.5, "糖": 0.0, "鈉": 0},
    "乳酪粉": {"熱量": 514, "蛋白質": 13.5, "脂肪": 13.6, "碳水": 20.7, "糖": 20.7, "鈉": 0},
    "三合力9285": {"熱量": 0, "蛋白質": 0.0, "脂肪": 0.0, "碳水": 0.0, "糖": 0.0, "鈉": 0},
    "帕瑪森起士粉": {"熱量": 420, "蛋白質": 35.0, "脂肪": 30.0, "碳水": 5.0, "糖": 0.0, "鈉": 1800},
}

st.title("健康長崎蛋糕脆餅模擬器")
st.markdown("可調整各原料比例（%），總和為100%，將自動計算每片(25g)營養標示（含3%水分濃縮）")

# 預設配方
if "配方紀錄" not in st.session_state:
    st.session_state["配方紀錄"] = {}

def calc_nutrition(formula):
    total_water = 0
    water_ratio = {"冷藏未殺菌液蛋白": 0.88, "冷藏未殺菌液蛋黃": 0.50, "自來水": 1.00}
    for k, v in formula.items():
        if k in water_ratio:
            total_water += v * water_ratio[k]
    dry = 100 - total_water
    baked = dry / 0.97
    factor = 25 / baked
    result = {"熱量": 0, "蛋白質": 0, "脂肪": 0, "碳水": 0, "糖": 0, "鈉": 0, "赤藻糖醇": 0}
    for k, v in formula.items():
        ing = ingredient_db[k]
        for key in result:
            if key == "赤藻糖醇" and k == "赤藻糖醇":
                result[key] += 97.5 * v / 100 * factor
            elif key != "赤藻糖醇":
                result[key] += ing[key] * v / 100 * factor
    return {k: round(v, 2) for k, v in result.items()}



def ai_flavor_feedback(formula):
    msg = []
    if formula.get("冷藏未殺菌液蛋白", 0) + formula.get("冷藏未殺菌液蛋黃", 0) + formula.get("自來水", 0) > 45:
        msg.append("口感潤澤、蓬鬆感佳。")
    else:
        msg.append("可能偏乾或膨發不足，可考慮增加液蛋或水分。")
    if formula.get("乳酪粉", 0) + formula.get("帕瑪森起士粉", 0) + formula.get("三合力9285", 0) > 8:
        msg.append("起司風味濃郁，適合重口味起司點心。")
    elif formula.get("三合力9285", 0) < 0.15:
        msg.append("起司香氣偏弱，建議提升香料比例至 0.2%。")
    if formula.get("赤藻糖醇", 0) > 4:
        msg.append("甜感略帶冷涼感，建議適度混合砂糖調和。")
    elif formula.get("精製細砂", 0) < 12:
        msg.append("甜度可能略低，成品風味偏淡。")
    if formula.get("大豆蛋白", 0) + formula.get("乳清蛋白", 0) > 10:
        msg.append("蛋白質含量高，需注意是否影響膨發與口感密實度。")
    return  "\n".join(msg)

with st.form("input_form"):
    st.subheader("輸入配方比例 (%)")
    formula = {}
    cols = st.columns(3)
    for i, ing in enumerate(ingredient_db):
        with cols[i % 3]:
            formula[ing] = st.number_input(ing, 0.0, 100.0, key=ing)
    submitted = st.form_submit_button("執行模擬")

    if submitted:
        total = sum(formula.values())
        if abs(total - 100) > 0.01:
            st.error(f"目前總和為 {total:.2f}%，請調整為100%")
        else:
            nutrition = calc_nutrition(formula)
            feedback = ai_flavor_feedback(formula)
            st.session_state["latest"] = {"formula": formula, "nutrition": nutrition, "feedback": feedback}

if "latest" in st.session_state:
    st.subheader("模擬結果（每25g）")
    st.json(st.session_state["latest"]["nutrition"])
    st.subheader("AI 感官預測與建議")
    st.markdown(st.session_state["latest"]["feedback"])
    save_name = st.text_input("儲存此版本名稱", value="v2.0")
    if st.button("儲存版本"):
        st.session_state["配方紀錄"][save_name] = st.session_state["latest"]

if st.session_state["配方紀錄"]:
    st.subheader("歷史版本對照")
    options = list(st.session_state["配方紀錄"].keys())
    selected = st.multiselect("選擇要比較的版本", options)
    if len(selected) >= 2:
    if selected:
        for ver in selected:
            st.markdown(f"### 📦 {ver} 配方比例 (%):")
            st.json(st.session_state["配方紀錄"][ver]["formula"])

        compare_df = pd.DataFrame({name: st.session_state["配方紀錄"][name]["nutrition"] for name in selected})
        st.dataframe(compare_df.style.format("{:.2f}"))


def ai_flavor_feedback(formula):
    msg = []
    if formula.get("冷藏未殺菌液蛋白", 0) + formula.get("冷藏未殺菌液蛋黃", 0) + formula.get("自來水", 0) > 45:
        msg.append("口感潤澤、蓬鬆感佳。")
    else:
        msg.append("可能偏乾或膨發不足，可考慮增加液蛋或水分。")
    if formula.get("乳酪粉", 0) + formula.get("帕瑪森起士粉", 0) + formula.get("三合力9285", 0) > 8:
        msg.append("起司風味濃郁，適合重口味起司點心。")
    elif formula.get("三合力9285", 0) < 0.15:
        msg.append("起司香氣偏弱，建議提升香料比例至 0.2%。")
    if formula.get("赤藻糖醇", 0) > 4:
        msg.append("甜感略帶冷涼感，建議適度混合砂糖調和。")
    elif formula.get("精製細砂", 0) < 12:
        msg.append("甜度可能略低，成品風味偏淡。")
    if formula.get("大豆蛋白", 0) + formula.get("乳清蛋白", 0) > 10:
        msg.append("蛋白質含量高，需注意是否影響膨發與口感密實度。")
    return "\n".join(msg)
