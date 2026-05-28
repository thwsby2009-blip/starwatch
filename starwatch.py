import streamlit as st
import math
import time
from datetime import datetime, timezone
import calendar

try:
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    HAS_MPL = True
except ImportError:
    HAS_MPL = False

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

# 台灣輪廓（簡化多邊形）
TAIWAN_OUTLINE = [
    (25.30, 121.50), (25.30, 122.00), (25.20, 121.95), (24.90, 122.00),
    (24.50, 121.80), (24.20, 121.70), (23.80, 121.60), (23.50, 121.50),
    (23.20, 121.30), (22.80, 121.20), (22.50, 121.00), (22.20, 120.80),
    (22.10, 120.60), (22.10, 120.40), (22.30, 120.20), (22.60, 120.10),
    (23.00, 119.80), (23.30, 119.60), (23.50, 119.50), (23.80, 119.60),
    (24.00, 119.80), (24.20, 120.00), (24.50, 120.10), (24.80, 120.20),
    (25.00, 120.40), (25.10, 120.60), (25.20, 120.80), (25.30, 121.00),
    (25.30, 121.50),
]

# ===== 星座 / 亮星資料 =====
STARS = [
    {"name": "Betelgeuse", "constellation": "Orion", "ra": 5.92, "dec": 7.41, "mag": 0.5},
    {"name": "Rigel", "constellation": "Orion", "ra": 5.24, "dec": -8.20, "mag": 0.13},
    {"name": "Alnitak", "constellation": "Orion", "ra": 5.68, "dec": -1.94, "mag": 1.77},
    {"name": "Alnilam", "constellation": "Orion", "ra": 5.60, "dec": -1.20, "mag": 1.69},
    {"name": "Mintaka", "constellation": "Orion", "ra": 5.53, "dec": -0.30, "mag": 2.09},
    {"name": "Dubhe", "constellation": "Ursa Major", "ra": 11.06, "dec": 61.75, "mag": 1.79},
    {"name": "Merak", "constellation": "Ursa Major", "ra": 11.03, "dec": 56.38, "mag": 2.37},
    {"name": "Phecda", "constellation": "Ursa Major", "ra": 11.90, "dec": 53.69, "mag": 2.44},
    {"name": "Megrez", "constellation": "Ursa Major", "ra": 12.26, "dec": 57.03, "mag": 3.31},
    {"name": "Alioth", "constellation": "Ursa Major", "ra": 12.90, "dec": 55.96, "mag": 1.77},
    {"name": "Mizar", "constellation": "Ursa Major", "ra": 13.40, "dec": 54.93, "mag": 2.27},
    {"name": "Alkaid", "constellation": "Ursa Major", "ra": 13.79, "dec": 49.31, "mag": 1.86},
    {"name": "Vega", "constellation": "Lyra", "ra": 18.62, "dec": 38.78, "mag": 0.03},
    {"name": "Altair", "constellation": "Aquila", "ra": 19.85, "dec": 8.87, "mag": 0.77},
    {"name": "Deneb", "constellation": "Cygnus", "ra": 20.69, "dec": 45.28, "mag": 1.25},
    {"name": "Antares", "constellation": "Scorpius", "ra": 16.49, "dec": -26.43, "mag": 1.06},
    {"name": "Regulus", "constellation": "Leo", "ra": 10.14, "dec": 11.97, "mag": 1.35},
    {"name": "Denebola", "constellation": "Leo", "ra": 11.82, "dec": 14.57, "mag": 2.14},
    {"name": "Schedar", "constellation": "Cassiopeia", "ra": 0.68, "dec": 56.54, "mag": 2.23},
    {"name": "Caph", "constellation": "Cassiopeia", "ra": 0.15, "dec": 60.72, "mag": 2.28},
    {"name": "Fomalhaut", "constellation": "Piscis Austrinus", "ra": 22.96, "dec": -29.62, "mag": 1.16},
    {"name": "Mirfak", "constellation": "Perseus", "ra": 3.41, "dec": 49.86, "mag": 1.79},
    {"name": "Venus", "is_planet": True, "ra": None, "dec": None, "mag": -4.0, "constellation": "Planets"},
    {"name": "Mars", "is_planet": True, "ra": None, "dec": None, "mag": -2.0, "constellation": "Planets"},
    {"name": "Jupiter", "is_planet": True, "ra": None, "dec": None, "mag": -2.5, "constellation": "Planets"},
]

PLANET_CYCLES = {"Venus": "Venus", "Mars": "Mars", "Jupiter": "Jupiter"}
PLANET_PERIODS = {"Venus": 225, "Mars": 687, "Jupiter": 433}

CONSTELLATION_COLORS = {
    "Orion": "#FF6B6B",
    "Ursa Major": "#4ECDC4",
    "Lyra": "#C7ECEE",
    "Aquila": "#F7DC6F",
    "Cygnus": "#85C1E9",
    "Scorpius": "#F1948A",
    "Leo": "#F9E79F",
    "Cassiopeia": "#AED6F1",
    "Piscis Austrinus": "#82E0AA",
    "Perseus": "#BB8FCE",
    "Planets": "#F8C471",
}


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


def make_taiwan_map(lat, lng):
    """用 matplotlib 畫台灣地圖 + 方向標示"""
    fig, ax = plt.subplots(figsize=(5, 4.5))
    fig.patch.set_facecolor("#0d0d1a")
    ax.set_facecolor("#0d0d1a")

    # 台灣輪廓
    outline_lats = [p[0] for p in TAIWAN_OUTLINE]
    outline_lngs = [p[1] for p in TAIWAN_OUTLINE]
    ax.fill(outline_lngs, outline_lats, color="#1a2a4a", alpha=0.6)
    ax.plot(outline_lngs, outline_lats, color="#4a9fff", linewidth=1.2)

    # 城市點
    for city in TAIWAN_CITIES:
        ax.scatter(city["lng"], city["lat"], s=8, c="#8888cc", alpha=0.5, zorder=2)
        ax.text(city["lng"], city["lat"] + 0.05, city["name"],
                fontsize=5, color="#8888bb", ha="center", va="bottom", alpha=0.7)

    # 你的位置
    ax.scatter(lng, lat, s=120, c="#FFD700", edgecolors="#FF6B00",
               linewidth=2, zorder=5, marker="o")

    # 方向線（從你的位置往外）
    dir_data = [
        ("N", 0, "#FF4444"), ("NE", 45, "#FF8844"),
        ("E", 90, "#44FF44"), ("SE", 135, "#44FF88"),
        ("S", 180, "#4444FF"), ("SW", 225, "#8844FF"),
        ("W", 270, "#FFFF44"), ("NW", 315, "#FF4444"),
    ]
    offset = 0.25
    for label, angle, color in dir_data:
        end_lat = lat + offset * math.cos(math.radians(angle))
        end_lng = lng + offset * math.sin(math.radians(angle)) * 0.8  # 緯度校正
        ax.plot([lng, end_lng], [lat, end_lat], color=color, linewidth=1, alpha=0.6)
        ax.text(end_lng, end_lat + 0.02, label, fontsize=6,
                color=color, ha="center", va="bottom", alpha=0.8, fontweight="bold")

    ax.set_xlim(119.2, 122.3)
    ax.set_ylim(21.8, 25.6)
    ax.set_aspect(1.1)
    ax.tick_params(colors="#555577", labelsize=5)
    ax.spines["bottom"].set_color("#333355")
    ax.spines["top"].set_color("#333355")
    ax.spines["left"].set_color("#333355")
    ax.spines["right"].set_color("#333355")
    ax.set_xlabel("經度", color="#555577", fontsize=6)
    ax.set_ylabel("緯度", color="#555577", fontsize=6)
    ax.tick_params(colors="#555577", labelsize=5)

    return fig


def make_star_chart(stars, lat, month, day, hour):
    fig = go.Figure()

    by_constellation = {}
    for star in stars:
        alt, az = compute_position(star, lat, month, day, hour)
        c = star["constellation"]
        if c not in by_constellation:
            by_constellation[c] = {"r": [], "theta": [], "names": []}
        r = 90 - min(max(alt, 0), 90)
        by_constellation[c]["r"].append(r)
        by_constellation[c]["theta"].append(az)
        by_constellation[c]["names"].append(star["name"])

    for const_name, data in by_constellation.items():
        color = CONSTELLATION_COLORS.get(const_name, "#AAAAAA")
        fig.add_trace(go.Scatterpolar(
            r=data["r"], theta=data["theta"],
            mode="markers+text",
            marker=dict(size=10, color=color, opacity=0.85),
            text=data["names"], textposition="top center",
            textfont=dict(size=8, color=color),
            name=const_name,
            hovertemplate="%{text}<br>仰角: %{r:.0f}°<extra></extra>",
        ))

    t = list(range(0, 360, 5))
    fig.add_trace(go.Scatterpolar(
        r=[90] * len(t), theta=t, mode="lines",
        line=dict(color="rgba(255,255,255,0.25)", width=1),
        name="地平線", hoverinfo="skip",
    ))

    for az, label in [(0, "N"), (90, "E"), (180, "S"), (270, "W")]:
        fig.add_annotation(x=az, y=0, text=f"<b>{label}</b>", showarrow=False,
                          font=dict(size=13, color="rgba(255,255,255,0.5)"),
                          xref="paper", yref="paper",
                          xanchor="center", yanchor="bottom",
                          ax=az, ay=0, xshift=0, yshift=-5)

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
                tickvals=[30, 60], ticktext=["60°", "30°"],
                range=[0, 100], gridcolor="rgba(255,255,255,0.06)",
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
            yanchor="top", y=0.98, xanchor="right", x=0.98,
        ),
    )
    return fig


def main():
    st.title("✨ 今晚的星星")
    st.caption("抬頭看看天上有哪些星座～")

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

        manual = st.checkbox("✏️ 手動時間")
        if manual:
            h = st.slider("小時", 0, 23, 21)
            m = st.slider("分鐘", 0, 59, 0)
        else:
            h, m = None, None

    now = datetime.now()
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

    # --- 台灣地圖（matplotlib）---
    if HAS_MPL:
        fig_map = make_taiwan_map(lat, lng)
        st.pyplot(fig_map)
        plt.close(fig_map)
        st.caption("🔴 你的位置  |  方向線 N/E/S/W 幫你對應天空方向")
    else:
        st.info("需要 matplotlib 才能顯示台灣地圖")

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