import streamlit as st
import math
from datetime import datetime
import pytz

st.set_page_config(
    page_title="今晚的星星 ✨",
    page_icon="🌙",
    layout="centered"
)

# ===== 星座資料 =====
CONSTELLATIONS = [
    {
        "name": "獵戶座",
        "emoji": "🏹",
        "ra": 5.5,
        "dec": 0,
        "desc": "冬天最亮的星座，三顆腰帶星很好認",
        "best": "12月 - 2月",
        "is_planet": False,
    },
    {
        "name": "大熊座",
        "emoji": "🐻",
        "ra": 11,
        "dec": 55,
        "desc": "北斗七星是它的一部分",
        "best": "全年可見",
        "is_planet": False,
    },
    {
        "name": "仙后座",
        "emoji": "👸",
        "ra": 1,
        "dec": 60,
        "desc": "W 形狀很好認，可以幫忙找北",
        "best": "10月 - 3月",
        "is_planet": False,
    },
    {
        "name": "天蠍座",
        "emoji": "🦂",
        "ra": 16.5,
        "dec": -30,
        "desc": "鉤子形尾巴，夏季代表星座",
        "best": "6月 - 8月",
        "is_planet": False,
    },
    {
        "name": "獅子座",
        "emoji": "🦁",
        "ra": 10.5,
        "dec": 15,
        "desc": "鉤刀形狀，春天最容易看到",
        "best": "3月 - 5月",
        "is_planet": False,
    },
    {
        "name": "織女星（天琴座）",
        "emoji": "🎵",
        "ra": 18.4,
        "dec": 38,
        "desc": "夏季大三角之一，很亮",
        "best": "6月 - 9月",
        "is_planet": False,
    },
    {
        "name": "牛郎星（天鷹座）",
        "emoji": "🦅",
        "ra": 19.8,
        "dec": 8,
        "desc": "夏季大三角之一，隔著銀河看織女",
        "best": "6月 - 9月",
        "is_planet": False,
    },
    {
        "name": "天津四（天鵝座）",
        "emoji": "🦢",
        "ra": 20.6,
        "dec": 45,
        "desc": "夏季大三角之一，十字形翅膀",
        "best": "6月 - 9月",
        "is_planet": False,
    },
    {
        "name": "南魚座",
        "emoji": "🐟",
        "ra": 22.3,
        "dec": -30,
        "desc": "秋季代表，亮的北落師門",
        "best": "9月 - 11月",
        "is_planet": False,
    },
    {
        "name": "飛馬座",
        "emoji": "🐎",
        "ra": 22.7,
        "dec": 20,
        "desc": "秋季四角形，很好認",
        "best": "10月 - 12月",
        "is_planet": False,
    },
    {
        "name": "英仙座",
        "emoji": "⚔️",
        "ra": 3,
        "dec": 45,
        "desc": "雙星團、著名的流星雨源",
        "best": "11月 - 1月",
        "is_planet": False,
    },
    {
        "name": "金星",
        "emoji": "🌟",
        "is_planet": True,
        "planet": "Venus",
        "desc": "天上最亮的行星，日落後在西邊或日出前在東邊",
        "best": "不定",
    },
    {
        "name": "火星",
        "emoji": "🔴",
        "is_planet": True,
        "planet": "Mars",
        "desc": "紅色行星，很好認",
        "best": "不定",
    },
    {
        "name": "木星",
        "emoji": "🟡",
        "is_planet": True,
        "planet": "Jupiter",
        "desc": "非常亮，有時候比金星還亮",
        "best": "不定",
    },
]

# 行星週期
PLANETS = {
    "Venus": {"cycle": 225, "offset": 0.4},
    "Mars": {"cycle": 687, "offset": 0.6},
    "Jupiter": {"cycle": 433, "offset": 0.1},
}


def estimate_visibility(constellation, lat, month, hour):
    """估算星座可見性"""
    dec = constellation.get("dec", 0)
    altitude = 90 - abs(lat - dec)
    is_northern = dec >= 0

    if is_northern:
        if month >= 11 or month <= 2:
            month_factor = 1.0
        elif month >= 3 and month <= 5:
            month_factor = 0.7
        else:
            month_factor = 0.4
    else:
        if month >= 11 or month <= 2:
            month_factor = 0.8
        else:
            month_factor = 0.3

    if altitude < 5:
        return "down", round(altitude)
    if altitude > 20 and month_factor > 0.5:
        return "up", round(altitude)
    if altitude > 10 and month_factor > 0.3:
        return "rising", round(altitude)
    if altitude > 0:
        return "setting", round(altitude)
    return "down", round(altitude)


def get_planet_visibility(planet_key, lat, month, day):
    """估算行星可見性"""
    p = PLANETS.get(planet_key, {})
    cycle = p.get("cycle", 365)
    ra = ((month - 1) * 30 + day) * 24 / cycle % 24
    altitude = 90 - abs(lat)
    sun_ra = (month * 2 + 6) % 24
    diff = abs(ra - sun_ra)
    angular_dist = min(diff, 24 - diff)

    if angular_dist < 3:
        return "down", round(altitude)
    if angular_dist < 6:
        return "setting", round(altitude)
    if altitude > 10:
        return "up", round(altitude)
    return "rising", round(altitude)


def main():
    st.title("✨ 今晚的星星")
    st.markdown("抬頭看看天上有哪些星座～")

    # 地點輸入
    st.markdown("---")
    st.subheader("📍 設定位置")

    col1, col2 = st.columns(2)
    with col1:
        lat = st.number_input(
            "緯度 (Latitude)",
            value=25.03,
            format="%.4f",
            help="台灣約 25.0°，台北 25.0330°，高雄 22.6273°"
        )
    with col2:
        lng = st.number_input(
            "經度 (Longitude)",
            value=121.56,
            format="%.4f",
            help="台灣約 121.5°"
        )

    # 時區選擇
    tz_name = st.selectbox(
        "🕐 時區",
        ["Asia/Taipei", "Asia/Shanghai", "America/New_York", "Europe/London"],
        index=0
    )

    # 取得現在時間
    tz = pytz.timezone(tz_name)
    now = datetime.now(tz)
    month = now.month
    day = now.day
    hour = now.hour + now.minute / 60

    date_str = now.strftime("%Y年%m月%d日 %A")
    time_str = now.strftime("%H:%M")

    st.markdown("---")
    st.markdown(f"**🕐 {date_str} {time_str}** ({tz_name})")
    st.markdown(f"**📍 {lat:.4f}°N, {lng:.4f}°E**")

    # 計算可見性
    visible = []
    hidden = []

    for c in CONSTELLATIONS:
        if c["is_planet"]:
            status, alt = get_planet_visibility(c["planet"], lat, month, day)
        else:
            status, alt = estimate_visibility(c, lat, month, hour)
        item = {**c, "status": status, "alt": alt}
        if status in ("up", "rising"):
            visible.append(item)
        else:
            hidden.append(item)

    # 排序
    visible.sort(key=lambda x: -x["alt"])
    hidden.sort(key=lambda x: -x["alt"])

    st.markdown("---")

    # 顯示可見的
    if visible:
        st.subheader(f"🌟 現在可以看到（{len(visible)} 個）")
        for c in visible:
            status_emoji = {
                "up": "⬆️ 可見",
                "rising": "🔼 正在升起",
                "setting": "🔽 即將落下",
                "down": "⬇️ 已落下"
            }
            st.markdown(
                f"""
                <div style="
                    background: #1a1a2e;
                    border-radius: 12px;
                    padding: 12px 16px;
                    margin: 8px 0;
                    display: flex;
                    align-items: center;
                    gap: 12px;
                    border: 1px solid #2a2a4a;
                ">
                    <span style="font-size: 1.8rem;">{c['emoji']}</span>
                    <div style="flex: 1;">
                        <div style="font-weight: 600; font-size: 1.05rem;">{c['name']}</div>
                        <div style="font-size: 0.8rem; color: #8888aa;">{c['desc']}</div>
                    </div>
                    <div style="
                        background: #1a3a2a;
                        color: #60dd80;
                        padding: 4px 10px;
                        border-radius: 20px;
                        font-size: 0.75rem;
                        font-weight: 600;
                    ">{status_emoji[c['status']]} {c['alt']}°</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    # 顯示看不見的
    if hidden:
        st.subheader(f"🌙 看不見但存在的（{len(hidden)} 個）")
        for c in hidden:
            st.markdown(
                f"""
                <div style="
                    background: #12122a;
                    border-radius: 12px;
                    padding: 10px 14px;
                    margin: 6px 0;
                    display: flex;
                    align-items: center;
                    gap: 12px;
                    border: 1px solid #1e1e3a;
                    opacity: 0.7;
                ">
                    <span style="font-size: 1.5rem;">{c['emoji']}</span>
                    <div style="flex: 1;">
                        <div style="font-weight: 600;">{c['name']}</div>
                        <div style="font-size: 0.75rem; color: #6666aa;">{c['best']}</div>
                    </div>
                    <div style="
                        background: #2a1a2a;
                        color: #aa6688;
                        padding: 4px 10px;
                        border-radius: 20px;
                        font-size: 0.7rem;
                        font-weight: 600;
                    ">已落下</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    # 小提示
    st.markdown("---")
    st.markdown(
        """
        💡 **觀星小提示：**
        - 把螢幕亮度調低，眼睛約需 **15-20 分鐘** 適應黑暗
        - 建議開啟 **夜間模式** 或紅色濾鏡
        - 避開路燈直射的地方，高樓陽台或空曠處最好
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()