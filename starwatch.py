import streamlit as st
import math
from datetime import datetime
import pytz

try:
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

st.set_page_config(
    page_title="今晚的星星 ✨",
    page_icon="🌙",
    layout="centered"
)

# ===== 台灣主要城市座標 =====
TAIWAN_CITIES = [
    {"name": "台北", "lat": 25.0330, "lng": 121.5654},
    {"name": "新北", "lat": 25.0120, "lng": 121.4657},
    {"name": "桃園", "lat": 24.9936, "lng": 121.3010},
    {"name": "新竹", "lat": 24.8017, "lng": 120.9714},
    {"name": "台中", "lat": 24.1477, "lng": 120.6736},
    {"name": "彰化", "lat": 24.0757, "lng": 120.5160},
    {"name": "台南", "lat": 22.9998, "lng": 120.2269},
    {"name": "高雄", "lat": 22.6273, "lng": 120.3014},
    {"name": "屏東", "lat": 22.5519, "lng": 120.5487},
    {"name": "宜蘭", "lat": 24.5970, "lng": 121.6325},
    {"name": "花蓮", "lat": 23.9910, "lng": 121.6111},
    {"name": "台東", "lat": 22.7973, "lng": 121.0714},
    {"name": "基隆", "lat": 25.1283, "lng": 121.7419},
    {"name": "苗栗", "lat": 24.5602, "lng": 120.8214},
    {"name": "雲林", "lat": 23.7092, "lng": 120.4313},
    {"name": "南投", "lat": 23.9160, "lng": 120.6636},
    {"name": "嘉義", "lat": 23.4802, "lng": 120.4491},
]

# ===== 星座 / 亮星資料 =====
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
    # 天琴座 / 天鷹座 / 天鵝座
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
    # 行星（簡化）
    {"name": "金星", "is_planet": True, "ra": None, "dec": None, "mag": -4.0, "constellation": "行星"},
    {"name": "火星", "is_planet": True, "ra": None, "dec": None, "mag": -2.0, "constellation": "行星"},
    {"name": "木星", "is_planet": True, "ra": None, "dec": None, "mag": -2.5, "constellation": "行星"},
]

PLANET_CYCLES = {"金星": "Venus", "火星": "Mars", "木星": "Jupiter"}
PLANET_PERIODS = {"Venus": 225, "Mars": 687, "Jupiter": 433}


def get_planet_ra(name_en, month, day):
    period = PLANET_PERIODS.get(name_en, 365)
    return ((month - 1) * 30 + day) * 24 / period % 24


def compute_position(star, lat, month, day, hour):
    if star.get("is_planet"):
        for cn, en in PLANET_CYCLES.items():
            if cn in star["name"]:
                ra = get_planet_ra(en, month, day)
                dec = 0.0
                break
        else:
            ra, dec = 6.0, 0.0
    else:
        ra, dec = star["ra"], star["dec"]

    lst = hour + (month - 3) * 2
    ha = (lst - ra) % 24

    lat_r = math.radians(lat)
    dec_r = math.radians(dec)
    ha_r = math.radians(ha * 15)

    sin_alt = math.sin(dec_r) * math.sin(lat_r) + math.cos(dec_r) * math.cos(lat_r) * math.cos(ha_r)
    sin_alt = max(-1, min(1, sin_alt))
    altitude = math.degrees(math.asin(sin_alt))

    # 避免 divide by zero
    cos_denom = math.cos(lat_r) * math.cos(math.asin(sin_alt))
    if abs(cos_denom) < 0.001:
        azimuth = 180.0
    else:
        cos_az = (math.sin(dec_r) - math.sin(lat_r) * sin_alt) / cos_denom
        cos_az = max(-1, min(1, cos_az))
        azimuth = math.degrees(math.acos(cos_az))
        if math.sin(ha_r) > 0:
            azimuth = 360 - azimuth

    return altitude, azimuth


def azimuth_to_direction(az):
    dirs = ["北", "東北", "東", "東南", "南", "西南", "西", "西北"]
    return dirs[round(az / 45) % 8]


CONSTELLATION_COLORS = {
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


def make_star_chart(stars, lat, month, day, hour):
    fig = go.Figure()

    # 按星座分組
    by_constellation = {}
    for star in stars:
        alt, az = compute_position(star, lat, month, day, hour)
        c = star["constellation"]
        if c not in by_constellation:
            by_constellation[c] = {"r": [], "theta": [], "names": []}
        r = 90 - alt  # polar: center=90°, edge=0°
        by_constellation[c]["r"].append(r)
        by_constellation[c]["theta"].append(az)
        by_constellation[c]["names"].append(star["name"])

    for const_name, data in by_constellation.items():
        color = CONSTELLATION_COLORS.get(const_name, "#AAAAAA")
        fig.add_trace(go.Scatterpolar(
            r=data["r"],
            theta=data["theta"],
            mode="markers+text",
            marker=dict(size=10, color=color, opacity=0.85),
            text=data["names"],
            textposition="top center",
            textfont=dict(size=8, color=color),
            name=const_name,
            hovertemplate="%{text}<br>仰角: %{r:.0f}°<extra></extra>",
        ))

    # 地平圈
    t = list(range(0, 360, 5))
    fig.add_trace(go.Scatterpolar(
        r=[90] * len(t), theta=t,
        mode="lines",
        line=dict(color="rgba(255,255,255,0.25)", width=1),
        name="地平線",
        hoverinfo="skip",
    ))

    for az, label in [(0, "N"), (90, "E"), (180, "S"), (270, "W")]:
        fig.add_annotation(x=az, y=0, text=f"<b>{label}</b>", showarrow=False,
                          font=dict(size=13, color="rgba(255,255,255,0.5)"),
                          xref="paper", yref="paper",
                          xanchor="center", yanchor="bottom",
                          ax=az, ay=0,
                          xshift=0, yshift=-5)

    fig.update_layout(
        polar=dict(
            bgcolor="#0d0d1a",
            angularaxis=dict(
                direction="clockwise",
                tickvals=[0, 45, 90, 135, 180, 225, 270, 315],
                ticktext=["N", "NE", "E", "SE", "S", "SW", "W", "NW"],
                tickcolor="rgba(255,255,255,0.3)",
                tickfont=dict(size=9, color="rgba(255,255,255,0.4)"),
                rotation=90,
            ),
            radialaxis=dict(
                tickvals=[30, 60],
                ticktext=["60°", "30°"],
                range=[0, 100],
                gridcolor="rgba(255,255,255,0.06)",
                linecolor="rgba(255,255,255,0.1)",
                tickfont=dict(size=8, color="rgba(255,255,255,0.35)"),
            ),
        ),
        paper_bgcolor="#0d0d1a",
        plot_bgcolor="#0d0d1a",
        margin=dict(l=10, r=10, t=10, b=10),
        height=480,
        showlegend=True,
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color="rgba(255,255,255,0.6)", size=9),
            yanchor="top", y=0.98,
            xanchor="right", x=0.98,
        ),
    )
    return fig


def main():
    st.title("✨ 今晚的星星")
    st.caption("抬頭看看天上有哪些星座～")

    # --- Sidebar ---
    with st.sidebar:
        st.subheader("📍 位置")
        city_names = ["手動輸入"] + [c["name"] for c in TAIWAN_CITIES]
        selected = st.selectbox("城市", city_names, index=0)
        if selected == "手動輸入":
            lat = st.number_input("緯度", value=25.03, format="%.2f")
            lng = st.number_input("經度", value=121.56, format="%.2f")
        else:
            city = next(c for c in TAIWAN_CITIES if c["name"] == selected)
            lat, lng = city["lat"], city["lng"]
            st.info(f"📍 {selected}")

        tz_name = st.selectbox("🕐 時區",
                               ["Asia/Taipei", "Asia/Shanghai", "Asia/Tokyo",
                                "America/New_York", "Europe/London"],
                               index=0)

        manual = st.checkbox("✏️ 手動時間")
        if manual:
            h = st.slider("小時", 0, 23, 21)
            m = st.slider("分鐘", 0, 59, 0)
        else:
            h, m = None, None

    tz = pytz.timezone(tz_name)
    now = datetime.now(tz)
    month, day = now.month, now.day

    if manual and h is not None:
        hour = h + m / 60
        time_str = f"{h:02d}:{m:02d}"
        date_str = now.strftime("%Y年%m月%d日")
    else:
        hour = now.hour + now.minute / 60
        time_str = now.strftime("%H:%M")
        date_str = now.strftime("%Y年%m月%d日 %A")

    col_t, col_l = st.columns(2)
    col_t.metric("🕐 時間", f"{date_str} {time_str}")
    place = selected if selected != "手動輸入" else f"{lat:.2f}°N {lng:.2f}°E"
    col_l.metric("📍 地點", place)

    # --- Star chart ---
    if HAS_PLOTLY:
        fig = make_star_chart(STARS, lat, month, day, hour)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("需要 plotly 才能顯示星圖")

    # --- Constellation list ---
    st.markdown("---")
    visible, hidden = [], []
    for star in STARS:
        alt, az = compute_position(star, lat, month, day, hour)
        status = "up" if alt > 0 else "down"
        direction = azimuth_to_direction(az)
        item = {"name": star["name"], "constellation": star["constellation"],
                "alt": round(alt, 1), "direction": direction, "status": status}
        if status == "up":
            visible.append(item)
        else:
            hidden.append(item)

    visible.sort(key=lambda x: -x["alt"])
    hidden.sort(key=lambda x: -x["alt"])

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"**🌟 現在可見** ({len(visible)})")
        for v in visible:
            st.markdown(f"- **{v['name']}** [{v['constellation']}] "
                       f"⬆️ {v['alt']}° | {v['direction']}")

    with c2:
        st.markdown(f"**🌙 已落下** ({len(hidden)})")
        for h in hidden[:10]:
            st.markdown(f"- ~~{h['name']}~~")

    st.caption("💡 眼睛適應黑暗約需 15-20 分鐘，去暗處看星星～")


if __name__ == "__main__":
    main()