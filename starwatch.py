import streamlit as st
import math
from datetime import datetime
import pytz

# plotly for interactive star chart
try:
    import plotly.express as px
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

st.set_page_config(
    page_title="今晚的星星 ✨",
    page_icon="🌙",
    layout="wide"
)

# ===== 星座 / 亮星資料 =====
# name, ra(小時), dec(度), magnitude(視星等，越低越亮)
STARS = [
    # 獵戶座
    {"name": "參宿四 (Betelgeuse)", "constellation": "獵戶座", "ra": 5.92, "dec": 7.41, "mag": 0.5},
    {"name": "參宿七 (Rigel)", "constellation": "獵戶座", "ra": 5.24, "dec": -8.20, "mag": 0.13},
    {"name": "參宿一", "constellation": "獵戶座", "ra": 5.68, "dec": -1.94, "mag": 1.77},
    {"name": "參宿二", "constellation": "獵戶座", "ra": 5.60, "dec": -1.20, "mag": 1.69},
    {"name": "參宿三", "constellation": "獵戶座", "ra": 5.53, "dec": -0.30, "mag": 2.09},
    # 大熊座（北斗七星）
    {"name": "天樞 (Dubhe)", "constellation": "大熊座", "ra": 11.06, "dec": 61.75, "mag": 1.79},
    {"name": "天璇 (Merak)", "constellation": "大熊座", "ra": 11.03, "dec": 56.38, "mag": 2.37},
    {"name": "天璣 (Phecda)", "constellation": "大熊座", "ra": 11.90, "dec": 53.69, "mag": 2.44},
    {"name": "天權 (Megrez)", "constellation": "大熊座", "ra": 12.26, "dec": 57.03, "mag": 3.31},
    {"name": "玉衡 (Alioth)", "constellation": "大熊座", "ra": 12.90, "dec": 55.96, "mag": 1.77},
    {"name": "開陽 (Mizar)", "constellation": "大熊座", "ra": 13.40, "dec": 54.93, "mag": 2.27},
    {"name": "搖光 (Alkaid)", "constellation": "大熊座", "ra": 13.79, "dec": 49.31, "mag": 1.86},
    # 織女星、牛郎星、天津四
    {"name": "織女星 (Vega)", "constellation": "天琴座", "ra": 18.62, "dec": 38.78, "mag": 0.03},
    {"name": "牛郎星 (Altair)", "constellation": "天鷹座", "ra": 19.85, "dec": 8.87, "mag": 0.77},
    {"name": "天津四 (Deneb)", "constellation": "天鵝座", "ra": 20.69, "dec": 45.28, "mag": 1.25},
    # 天蠍座
    {"name": "心宿二 (Antares)", "constellation": "天蠍座", "ra": 16.49, "dec": -26.43, "mag": 1.06},
    # 獅子座
    {"name": "軒轅十四 (Regulus)", "constellation": "獅子座", "ra": 10.14, "dec": 11.97, "mag": 1.35},
    {"name": "五帝座一 (Denebola)", "constellation": "獅子座", "ra": 11.82, "dec": 14.57, "mag": 2.14},
    # 仙后座
    {"name": "王良四 (Schedar)", "constellation": "仙后座", "ra": 0.68, "dec": 56.54, "mag": 2.23},
    {"name": "王良一", "constellation": "仙后座", "ra": 0.15, "dec": 60.72, "mag": 2.28},
    # 南魚座
    {"name": "北落師門 (Fomalhaut)", "constellation": "南魚座", "ra": 22.96, "dec": -29.62, "mag": 1.16},
    # 英仙座
    {"name": "天船三 (Mirfak)", "constellation": "英仙座", "ra": 3.41, "dec": 49.86, "mag": 1.79},
    # 行星（金星、火星、木星 — 近似位置）
    {"name": "金星 (Venus)", "constellation": "行星", "ra": None, "dec": None, "mag": -4.0, "is_planet": True},
    {"name": "火星 (Mars)", "constellation": "行星", "ra": None, "dec": None, "mag": -2.0, "is_planet": True},
    {"name": "木星 (Jupiter)", "constellation": "行星", "ra": None, "dec": None, "mag": -2.5, "is_planet": True},
]

PLANET_CYCLES = {
    "Venus": 225,
    "Mars": 687,
    "Jupiter": 433,
}


def get_planet_position(planet_name, month, day):
    cycle = PLANET_CYCLES.get(planet_name, 365)
    ra = ((month - 1) * 30 + day) * 24 / cycle % 24
    dec = 0  # 行星大約在黃道上
    return ra, dec


def stars_to_altaz(star, lat, month, day, hour):
    """將赤道座標轉換為地平座標（高度角/方位角）"""
    # 赤經 -> 時角
    # 近似：Local Sidereal Time
    lst = hour + (month - 3) * 2  # 粗略估計
    if star.get("is_planet"):
        planet_name = star["name"].split(" ")[0]
        if planet_name == "金星":
            ra, dec = get_planet_position("Venus", month, day)
        elif planet_name == "火星":
            ra, dec = get_planet_position("Mars", month, day)
        else:
            ra, dec = get_planet_position("Jupiter", month, day)
    else:
        ra = star["ra"]
        dec = star["dec"]

    ha = lst - ra
    if ha < 0:
        ha += 24

    # 轉為弧度
    lat_r = math.radians(lat)
    dec_r = math.radians(dec)
    ha_r = math.radians(ha * 15)

    # 地平高度
    sin_alt = (
        math.sin(dec_r) * math.sin(lat_r)
        + math.cos(dec_r) * math.cos(lat_r) * math.cos(ha_r)
    )
    altitude = math.degrees(math.asin(sin_alt))

    # 方位角
    cos_az = (math.sin(dec_r) - math.sin(lat_r) * sin_alt) / (
        math.cos(lat_r) * math.cos(math.asin(sin_alt))
    )
    cos_az = max(-1, min(1, cos_az))
    azimuth = math.degrees(math.acos(cos_az))
    if math.sin(ha_r) > 0:
        azimuth = 360 - azimuth

    return altitude, azimuth, ra, dec


def make_star_chart(stars, lat, month, day, hour):
    """用 plotly 畫互動星體圖"""
    alts, azs, names, mags, colors, sizes = [], [], [], [], [], []

    for star in stars:
        alt, az, ra, dec = stars_to_altaz(star, lat, month, day, hour)
        # 只顯示地平線以上的
        if alt > 0 or star.get("is_planet"):
            alts.append(alt)
            azs.append(az)
            names.append(star["name"])
            mags.append(star["mag"])
            colors.append(star["constellation"])

    # 建立 polar 圖（方位角-高度）
    # 轉換：polar 圖的 theta 是方位角，r 是(90-高度)
    r_polar = [90 - a for a in alts]

    fig = go.Figure()

    # 定義每個星座的顏色
    color_map = {
        "獵戶座": "#FF6B6B",
        "大熊座": "#4ECDC4",
        "天琴座": "#C7ECEE",
        "天鷹座": "#F7DC6F",
        "天鵝座": "#85C1E9",
        "天蠍座": "#F1948A",
        "獅子座": "#F9E79F",
        "仙后座": "#AED6F1",
        "南魚座": "#82E0AA",
        "英仙座": "#BB8FCE",
        "行星": "#F8C471",
    }

    for constellation_name, color in color_map.items():
        mask = [c == constellation_name for c in colors]
        if any(mask):
            fig.add_trace(go.Scatterpolar(
                r=[r_polar[i] for i, m in enumerate(mask) if m],
                theta=[azs[i] for i, m in enumerate(mask) if m],
                mode="markers+text",
                marker=dict(size=12, color=color, opacity=0.9),
                text=[names[i] for i, m in enumerate(mask) if m],
                textposition="top center",
                textfont=dict(size=9, color=color),
                name=constellation_name,
                hovertemplate="%{text}<br>仰角: %{r}°<extra></extra>",
            ))

    # 畫地平線
    theta_grid = list(range(0, 360, 5))
    r_horizon = [90] * len(theta_grid)
    fig.add_trace(go.Scatterpolar(
        r=r_horizon,
        theta=theta_grid,
        mode="lines",
        line=dict(color="rgba(255,255,255,0.3)", width=1),
        name="地平線",
        hoverinfo="skip",
    ))

    # 方位標籤
    for az, label in [(0, "N"), (90, "E"), (180, "S"), (270, "W")]:
        fig.add_annotation(
            x=az, y=0,
            text=f"<b>{label}</b>",
            showarrow=False,
            font=dict(size=14, color="rgba(255,255,255,0.6)"),
        )

    fig.update_layout(
        polar=dict(
            bgcolor="#0a0a1a",
            angularaxis=dict(
                direction="clockwise",
                tickcolor="rgba(255,255,255,0.4)",
                tickfont=dict(size=10, color="rgba(255,255,255,0.5)"),
                rotation=90,
            ),
            radialaxis=dict(
                tickfont=dict(size=8, color="rgba(255,255,255,0.4)"),
                tickvals=[30, 60],
                ticktext=["60°", "30°"],
                gridcolor="rgba(255,255,255,0.08)",
                linecolor="rgba(255,255,255,0.1)",
            ),
        ),
        paper_bgcolor="#0a0a1a",
        plot_bgcolor="#0a0a1a",
        showlegend=True,
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color="rgba(255,255,255,0.7)"),
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=1.02,
        ),
        height=550,
        margin=dict(l=20, r=120, t=20, b=20),
    )

    return fig


def main():
    st.title("✨ 今晚的星星")
    st.markdown("抬頭看看天上有哪些星座～")

    # 側邊欄設定
    with st.sidebar:
        st.header("📍 設定")
        lat = st.number_input(
            "緯度",
            value=25.03,
            format="%.2f",
            help="台灣約 25.0°，台北 25.03，高雄 22.63"
        )
        lng = st.number_input("經度", value=121.56, format="%.2f")
        tz_name = st.selectbox(
            "🕐 時區",
            ["Asia/Taipei", "Asia/Shanghai", "America/New_York", "Europe/London"],
            index=0
        )

        # 手動設定時間
        use_manual_time = st.checkbox("✏️ 手動設定時間")
        if use_manual_time:
            col1, col2 = st.columns(2)
            with col1:
                manual_hour = st.slider("小時", 0, 23, 21)
            with col2:
                manual_min = st.slider("分鐘", 0, 59, 0)
        else:
            manual_hour = None
            manual_min = None

    tz = pytz.timezone(tz_name)
    now = datetime.now(tz)
    month = now.month
    day = now.day

    if use_manual_time:
        hour = manual_hour + manual_min / 60
        date_str = now.strftime("%Y年%m月%d日")
        time_str = f"{manual_hour:02d}:{manual_min:02d}"
    else:
        hour = now.hour + now.minute / 60
        date_str = now.strftime("%Y年%m月%d日 %A")
        time_str = now.strftime("%H:%M")

    st.markdown(f"**🕐 {date_str} {time_str}** | **📍 {lat:.2f}°N {lng:.2f}°E**")

    if not HAS_PLOTLY:
        st.error("需要安裝 plotly 才能顯示星體圖！請在 requirements.txt 加入 `plotly` 並重新 deploy。")
        return

    # 畫星體圖
    fig = make_star_chart(STARS, lat, month, day, hour)
    st.plotly_chart(fig, use_container_width=True)

    # 說明
    with st.expander("📖 怎么看懂這張圖？"):
        st.markdown("""
        - **中心點** = 頭頂（天頂）
        - **外圈** = 地平線
        - **N / E / S / W** = 北 / 東 / 南 / 西 方向
        - **顏色** = 不同的星座
        - **滑鼠懸停**可以看到星體名稱和仰角
        - 拉到外圈邊緣等於「快要落下去了」
        """)

    # ===== 可見性列表 =====
    st.markdown("---")
    col_left, col_right = st.columns(2)

    visible = []
    hidden = []

    for star in STARS:
        if star.get("is_planet"):
            planet_name = star["name"].split(" ")[0]
            ra, _ = get_planet_position(planet_name.replace("(", "").replace(")", "").split(" ")[0] if "Venus" in star["name"] else star["name"].split(" ")[0], month, day)
            alt, az, _, _ = stars_to_altaz({**star, "ra": ra, "dec": 0}, lat, month, day, hour)
        else:
            alt, az, _, _ = stars_to_altaz(star, lat, month, day, hour)

        status = "up" if alt > 20 else ("rising" if alt > 0 else "down")
        item = {**star, "alt": round(alt, 1), "az": round(az, 1), "status": status}
        if status in ("up", "rising"):
            visible.append(item)
        else:
            hidden.append(item)

    visible.sort(key=lambda x: -x["alt"])
    hidden.sort(key=lambda x: -x["alt"])

    with col_left:
        st.subheader(f"🌟 現在可見（{len(visible)} 個）")
        for v in visible:
            st.markdown(
                f"**{v['name']}** [{v['constellation']}] "
                f"⬆️ {v['alt']}° / {v['az']}°"
            )

    with col_right:
        st.subheader(f"🌙 已落下（{len(hidden)} 個）")
        for h in hidden[:8]:
            st.markdown(
                f"~~{h['name']}~~ [{h['constellation']}] "
                f"⬇️ {h['alt']}°"
            )

    st.markdown("---")
    st.caption(
        "💡 觀星小提示：眼睛適應黑暗約需 15-20 分鐘，"
        "避開路燈、高樓陽台或空曠處最佳～"
    )


if __name__ == "__main__":
    main()