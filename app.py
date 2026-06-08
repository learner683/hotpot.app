import streamlit as st
import json
import os

st.set_page_config(page_title="热点事件分析看板", layout="wide")
st.title("📊 热点事件分析看板")

DATA_FILE = "final_reports.json"

if not os.path.exists(DATA_FILE):
    st.error(f"❌ 找不到数据文件 `{DATA_FILE}`，请先运行 pipeline.py 生成报告。")
    st.stop()

with open(DATA_FILE, "r", encoding="utf-8") as f:
    events = json.load(f)

if not events:
    st.warning("⚠️ 没有事件数据")
    st.stop()

# ---- 侧边栏简化 ----
st.sidebar.header("📈 概览")
st.sidebar.metric("事件总数", len(events))
keyword = st.sidebar.text_input("🔍 搜索事件关键词")
if keyword:
    events = [ev for ev in events if keyword.lower() in ev.get("summary", "").lower()
              or any(keyword.lower() in t.lower() for t in ev.get("titles", []))]

st.subheader(f"共 {len(events)} 个热点事件")

# ---- 主区域：简化卡片布局（不用 columns）----
for ev in events:
    # 使用 expander，内部直接用垂直排列
    with st.expander(
            f"🔥 {ev.get('summary', '未知事件')} | 热度 {ev.get('total_hot', 0)} | 相关条目 {ev.get('item_count', 0)}"):
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
            if "background" in material:
                st.write(f"背景: {material['background'][:100]}...")
            if "key_points" in material:
                st.write("关键点:")
                for kp in material["key_points"][:3]:
                    st.write(f"- {kp}")
        else:
            st.write("无素材")

        st.markdown("**📄 完整分析报告**")
        report = ev.get("report", "")
        if report:
            st.markdown(report)
        else:
            st.info("该事件尚未生成报告")

st.markdown("---")
st.caption("自动生成 · 数据来源：微博热搜 → 聚合去重 → AI 分析")