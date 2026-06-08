import streamlit as st
import json
import os
import warnings
warnings.filterwarnings("ignore")
# ---- 页面配置 ----
st.set_page_config(page_title="热点事件分析看板", layout="wide")
st.title("📊 热点事件分析看板")

# ---- 加载数据 ----
DATA_FILE = "final_reports.json"

if not os.path.exists(DATA_FILE):
    st.error(f"❌ 找不到数据文件 `{DATA_FILE}`，请先运行 `pipeline.py` 生成报告。")
    st.stop()

with open(DATA_FILE, "r", encoding="utf-8") as f:
    events = json.load(f)

if not events:
    st.warning("⚠️ 没有事件数据")
    st.stop()

# ---- 侧边栏：统计与过滤 ----
st.sidebar.header("📈 概览")
st.sidebar.metric("事件总数", len(events))
avg_hot = sum(ev.get("total_hot", 0) for ev in events) // max(len(events), 1)
st.sidebar.metric("平均热度", avg_hot)

# 搜索过滤
keyword = st.sidebar.text_input("🔍 搜索事件关键词")
if keyword:
    events = [
        ev for ev in events
        if keyword.lower() in ev.get("summary", "").lower()
        or any(keyword.lower() in t.lower() for t in ev.get("titles", []))
    ]

# 排序方式
sort_by = st.sidebar.selectbox("排序方式", ["热度", "时间"], index=0)

# 热度降序（已经是降序，可微调）
if sort_by == "热度":
    events = sorted(events, key=lambda x: x.get("total_hot", 0), reverse=True)
else:
    # 简单按事件id或采集时间，这里用事件id
    events = sorted(events, key=lambda x: x.get("event_id", 0))

# 刷新按钮
if st.sidebar.button("🔄 重新加载数据"):
    st.rerun()

# ---- 主区域：事件列表 ----
st.subheader(f"共 {len(events)} 个热点事件")

for ev in events:
    with st.expander(f"🔥 {ev.get('summary', '未知事件')} | 热度 {ev.get('total_hot', 0)} | 相关条目 {ev.get('item_count', 0)}"):
        col1, col2 = st.columns([1, 2])

        with col1:
            st.markdown("**事件摘要**")
            st.write(ev.get("summary", ""))
            st.markdown("**相关标题**")
            for t in ev.get("titles", []):
                st.write(f"- {t}")
            st.markdown("**来源平台**")
            sources = ev.get("sources", [])
            st.write(", ".join(sources) if sources else "微博")
            st.markdown("**搜索素材**")
            material = ev.get("search_material", {})
            if material:
                # 显示部分素材摘要
                if "background" in material:
                    st.write(f"背景: {material['background'][:100]}...")
                if "key_points" in material:
                    st.write("关键点:")
                    for kp in material["key_points"][:3]:
                        st.write(f"- {kp}")
            else:
                st.write("无素材")

        with col2:
            st.markdown("**📄 完整分析报告**")
            report = ev.get("report", "")
            if report:
                st.markdown(report, unsafe_allow_html=False)
            else:
                st.info("该事件尚未生成报告")

st.markdown("---")
st.caption("自动生成 · 数据来源：微博热搜 → 聚合去重 → AI 分析")