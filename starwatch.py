import streamlit as st
import math
from datetime import datetime
import pytz

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

# ===== 台灣主要城市座標 =====
TAIWAN_CITIES = [
    {"name": "台北", "lat": 25.0330, "lng": 121.5654, "color": "#FF6B6B"},
    {"name": "新北", "lat": 25.0120, "lng": 121.4657, "color": "#FF8E8E"},
    {"name": "桃園", "lat": 24.9936, "lng": 121.3010, "color": "#FFB0B0"},
    {"name": "新竹", "lat": 24.8017, "lng": 120.9714, "color": "#FFD93D"},
    {"name": "台中", "lat": 24.1477, "lng": 120.6736, "color": "#6BCB77"},
    {"name": "彰化", "lat": 24.0757, "lng": 120.5160, "color": "#7ED68B"},
    {"name": "台南", "lat": 22.9998, "lng": 120.2269, "color": "#4D96FF"},
    {"name": "高雄", "lat": 22.6273, "lng": 120.3014, "color": "#845EC2"},
    {"name": "屏東", "lat": 22.5519, "lng": 120.5487, "color": "#9B72CF"},
    {"name": "宜蘭", "lat": 24.5970, "lng": 121.6325, "color": "#00C9A7"},
    {"name": "花蓮", "lat": 23.9910, "lng": 121.6111, "color": "#FF8066"},
    {"name": "台東", "lat": 22.7973, "lng": 121.0714, "color": "#FF9F68"},
    {"name": "基隆", "lat": 25.1283, "lng": 121.7419, "color": "#FFB5B5"},
    {"name": "苗栗", "lat": 24.5602, "lng": 120.8214, "color": "#A8E6CF"},
    {"name": "雲林", "lat": 23.7092, "lng": 120.4313, "color": "#B8E8A0"},
    {"name": "南投", "lat": 23.9160, "lng": 120.6636, "color": "#C5E8B7"},
    {"name": "嘉義", "lat": 23.4802, "lng": 120.4491, "color": "#88D8B0"},
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
    # 行星
    {"name": "金星 (Venus)", "constellation": "行星", "ra": None, "dec": None, "mag": -4.0, "is_planet": True},
    {"name": "火星 (Mars)", "constellation": "行星", "ra": None, "dec": None, "mag": -2.0, "is_planet": True},
    {"name": "木星 (Jupiter)", "constellation": "行星", "ra": None, "dec": None, "mag": -2.5, "is_planet": True},
]

PLANET_CYCLES = {"Venus": 225, "Mars": 687, "Jupiter": 433}


def get_planet_position(planet_key, month, day):
    cycle = PLANET_CYCLES.get(planet_key, 365)
    ra = ((month - 1) * 30 + day) * 24 / cycle % 24
    return ra, 0


def stars_to_altaz(star, lat, month, day, hour):
    lst = hour + (month - 3) * 2
    if star.get("is_planet"):
        pn = star["name"].split(" ")[0].replace("(", "").replace(")", "")
        key_map = {"金星": "Venus", "火星": "Mars", "木星": "Jupiter"}
        ra, dec = get_planet_position(key_map.get(pn, "Venus"), month, day)
    else:
        ra, dec = star["ra"], star["dec"]

    ha = (lst - ra) % 24
    lat_r, dec_r, ha_r = math.radians(lat), math.radians(dec), math.radians(ha * 15)
    sin_alt = math.sin(dec_r) * math.sin(lat_r) + math.cos(dec_r) * math.cos(lat_r) * math.cos(ha_r)
    altitude = math.degrees(math.asin(sin_alt))
    cos_az = (math.sin(dec_r) - math.sin(lat_r) * sin_alt) / max(0.001, math.cos(lat_r) * math.cos(math.asin(sin_alt)))
    cos_az = max(-1, min(1, cos_az))
    azimuth = math.degrees(math.acos(cos_az))
    if math.sin(ha_r) > 0:
        azimuth = 360 - azimuth
    return altitude, azimuth, ra, dec


def get_azimuth_direction(az):
    """把方位角轉成方向文字"""
    dirs = ["北", "東北", "東", "東南", "南", "西南", "西", "西北"]
    idx = round(az / 45) % 8
    return dirs[idx]


def make_taiwan_map(lat, lng):
    """用 plotly 畫台灣地圖 + 你的位置 + 方向指示"""
    # 台灣邊界（大約範圍）
    taiwan_lats = [25.30, 25.30, 24.20, 22.80, 22.10, 22.10, 23.50, 25.00, 25.30]
    taiwan_lons = [121.50, 122.00, 122.00, 121.50, 120.40, 119.50, 119.50, 120.80, 121.50]

    fig = go.Figure()

    # 台灣輪廓
    fig.add_trace(go.Scattergeo(
        lat=taiwan_lats,
        lon=taiwan_lons,
        mode="lines",
        line=dict(color="#4a9fff", width=2),
        fill="toself",
        fillcolor="rgba(74, 159, 255, 0.1)",
        name="台灣",
        hoverinfo="skip",
    ))

    # 城市
    for city in TAIWAN_CITIES:
        fig.add_trace(go.Scattergeo(
            lat=[city["lat"]],
            lon=[city["lng"]],
            mode="markers+text",
            marker=dict(size=10, color=city["color"], opacity=0.8),
            text=[city["name"]],
            textposition="top center",
            textfont=dict(size=9, color="white"),
            name=city["name"],
            hovertemplate=f"<b>{city['name']}</b><br>緯度: {city['lat']:.2f}°<br>經度: {city['lng']:.2f}°<extra></extra>",
        ))

    # 你的位置
    fig.add_trace(go.Scattergeo(
        lat=[lat],
        lon=[lng],
        mode="markers",
        marker=dict(size=16, color="#FFD700", line=dict(color="#FF6B00", width=2)),
        name="你的位置",
        hovertemplate=f"<b>📍 你的位置</b><br>緯度: {lat:.4f}°<br>經度: {lng:.4f}°<extra></extra>",
    ))

    # 方向箭頭（用 Scatter 而不是 Scattergeo 疊加）
    arrow_data = {
        "北": (0, "#FF4444"),
        "東": (90, "#44FF44"),
        "南": (180, "#4444FF"),
        "西": (270, "#FFFF44"),
    }
    for direction, (angle, color) in arrow_data.items():
        offset = 0.3
        end_lat = lat + offset * math.cos(math.radians(angle))
        end_lng = lng + offset * math.sin(math.radians(angle))
        fig.add_trace(go.Scattergeo(
            lat=[lat, end_lat],
            lon=[lng, end_lng],
            mode="lines",
            line=dict(color=color, width=3),
            name=direction,
        ))

    fig.update_geo(
        projection_type="mercator",
        center=dict(lat=lat, lon=lng),
    )

    fig.update_layout(
        paper_bgcolor="#0a0a1a",
        plot_bgcolor="#0a0a1a",
        height=350,
        margin=dict(l=0, r=0, t=20, b=0),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color="white", size=10),
            yanchor="top", y=0.99,
            xanchor="left", x=1.02,
        ),
        annotations=[
            dict(text="🧭 方向顏色", showarrow=False, x=1.01, y=0.85, xref="paper", yref="paper",
                 font=dict(color="rgba(255,255,255,0.6)", size=11), xanchor="left"),
            dict(text="🔴 北", showarrow=False, x=1.01, y=0.80, xref="paper", yref="paper",
                 font=dict(color="#FF4444", size=10), xanchor="left"),
            dict(text="🟢 東", showarrow=False, x=1.01, y=0.76, xref="paper", yref="paper",
                 font=dict(color="#44FF44", size=10), xanchor="left"),
            dict(text="🔵 南", showarrow=False, x=1.01, y=0.72, xref="paper", yref="paper",
                 font=dict(color="#4444FF", size=10), xanchor="left"),
            dict(text="🟡 西", showarrow=False, x=1.01, y=0.68, xref="paper", yref="paper",
                 font=dict(color="#FFFF44", size=10), xanchor="left"),
        ]
    )
    return fig


def make_star_chart(stars, lat, month, day, hour):
    alts, azs, names, mags, colors = [], [], [], [], []

    for star in stars:
        alt, az, _, _ = stars_to_altaz(star, lat, month, day, hour)
        if alt > -5:
            alts.append(alt)
            azs.append(az)
            names.append(star["name"])
            mags.append(star["mag"])
            colors.append(star["constellation"])

    r_polar = [90 - a for a in alts]
    fig = go.Figure()

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

    theta_grid = list(range(0, 360, 5))
    fig.add_trace(go.Scatterpolar(
        r=[90] * len(theta_grid),
        theta=theta_grid,
        mode="lines",
        line=dict(color="rgba(255,255,255,0.3)", width=1),
        name="地平線",
        hoverinfo="skip",
    ))

    for az, label in [(0, "N"), (90, "E"), (180, "S"), (270, "W")]:
        fig.add_annotation(x=az, y=0, text=f"<b>{label}</b>", showarrow=False,
                          font=dict(size=14, color="rgba(255,255,255,0.6)"))

    fig.update_layout(
        polar=dict(
            bgcolor="#0a0a1a",
            angularaxis=dict(direction="clockwise", tickcolor="rgba(255,255,255,0.4)",
                            tickfont=dict(size=10, color="rgba(255,255,255,0.5)"), rotation=90),
            radialaxis=dict(tickfont=dict(size=8, color="rgba(255,255,255,0.4)"), tickvals=[30, 60],
                            ticktext=["60°", "30°"], gridcolor="rgba(255,255,255,0.08)",
                            linecolor="rgba(255,255,255,0.1)"),
        ),
        paper_bgcolor="#0a0a1a",
        plot_bgcolor="#0a0a1a",
        showlegend=True,
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="rgba(255,255,255,0.7)"),
                    yanchor="top", y=0.99, xanchor="left", x=1.02),
        height=500,
        margin=dict(l=20, r=120, t=20, b=20),
    )
    return fig


def main():
    st.title("✨ 今晚的星星")
    st.markdown("抬頭看看天上有哪些星座～")

    col1, col2 = st.columns([1, 2])

    with col1:
        with st.container():
            st.subheader("📍 你的位置")
            # 快速選擇城市
            city_names = ["手動輸入"] + [c["name"] for c in TAIWAN_CITIES]
            selected_city = st.selectbox("選擇城市或手動輸入", city_names, index=0)

            if selected_city == "手動輸入":
                lat = st.number_input("緯度", value=25.03, format="%.4f", key="lat")
                lng = st.number_input("經度", value=121.56, format="%.4f", key="lng")
            else:
                city = next((c for c in TAIWAN_CITIES if c["name"] == selected_city), None)
                if city:
                    lat, lng = city["lat"], city["lng"]
                    st.info(f"📍 **{selected_city}** ({lat:.4f}°, {lng:.4f}°)")
                else:
                    lat, lng = 25.03, 121.56

            tz_name = st.selectbox(
                "🕐 時區",
                ["Asia/Taipei", "Asia/Shanghai", "America/New_York", "Europe/London"],
                index=0, key="tz"
            )

            use_manual_time = st.checkbox("✏️ 手動設定時間")
            if use_manual_time:
                col_h, col_m = st.columns(2)
                with col_h:
                    manual_hour = st.slider("小時", 0, 23, 21, key="hour")
                with col_m:
                    manual_min = st.slider("分鐘", 0, 59, 0, key="min")
            else:
                manual_hour, manual_min = None, None

    tz = pytz.timezone(tz_name)
    now = datetime.now(tz)
    month, day = now.month, now.day

    if use_manual_time:
        hour = manual_hour + manual_min / 60
        date_str = now.strftime("%Y年%m月%d日")
        time_str = f"{manual_hour:02d}:{manual_min:02d}"
    else:
        hour = now.hour + now.minute / 60
        date_str = now.strftime("%Y年%m月%d日 %A")
        time_str = now.strftime("%H:%M")

    with col2:
        st.markdown(f"**🕐 {date_str} {time_str}**")
        st.markdown("---")

        if HAS_PLOTLY:
            # 台灣地圖
            fig_map = make_taiwan_map(lat, lng)
            st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.warning("需要安裝 plotly 才能顯示地圖")

    st.markdown("---")

    if HAS_PLOTLY:
        fig = make_star_chart(STARS, lat, month, day, hour)
        st.plotly_chart(fig, use_container_width=True)

    with st.expander("📖 怎么看懂這張圖？"):
        st.markdown("""
        - **中心點** = 頭頂（天頂）
        - **外圈** = 地平線
        - **N/E/S/W** = 北/東/南/西 方向
        - **仰角** = 星星離地平線多高（90°=頭頂，0°=地平線）
        """)

    # ===== 可見性列表 + 方向指引 =====
    st.markdown("---")
    visible, hidden = [], []

    for star in STARS:
        alt, az, _, _ = stars_to_altaz(star, lat, month, day, hour)
        status = "up" if alt > 20 else ("rising" if alt > 0 else "down")
        direction = get_azimuth_direction(az)
        item = {**star, "alt": round(alt, 1), "az": round(az, 1), "status": status, "direction": direction}
        if status in ("up", "rising"):
            visible.append(item)
        else:
            hidden.append(item)

    visible.sort(key=lambda x: -x["alt"])
    hidden.sort(key=lambda x: -x["alt"])

    col_up, col_down = st.columns(2)

    with col_up:
        st.subheader(f"🌟 現在可見（{len(visible)} 個）")
        for v in visible:
            direction_emoji = {"北": "🔴", "東北": "🟠", "東": "🟢", "東南": "🟡",
                               "南": "🔵", "西南": "🟣", "西": "🟡", "西北": "⚪"}
            emoji = direction_emoji.get(v["direction"], "⚪")
            st.markdown(
                f"{emoji} **{v['name']}** [{v['constellation']}] "
                f"⬆️ {v['alt']}° | {v['direction']}方向"
            )

    with col_down:
        st.subheader(f"🌙 已落下（{len(hidden)} 個）")
        for h in hidden[:8]:
            st.markdown(f"~~{h['name']}~~")

    st.markdown("---")
    st.caption("💡 觀星小提示：眼睛適應黑暗約需 15-20 分鐘，避開路燈、空曠處最佳～")


if __name__ == "__main__":
    main()