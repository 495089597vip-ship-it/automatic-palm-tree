import streamlit as st
import os
import sys
import threading
import time
from datetime import datetime
from database import DouyinDatabase
from ai_analyzer import AIAnalyzer
from dotenv import load_dotenv

load_dotenv()

# Try to import pyperclip for clipboard monitoring
try:
    import pyperclip
    CLIPBOARD_AVAILABLE = True
except ImportError:
    CLIPBOARD_AVAILABLE = False

# Initialize session state
if 'db' not in st.session_state:
    st.session_state.db = DouyinDatabase()

if 'analyzer' not in st.session_state:
    st.session_state.analyzer = AIAnalyzer()

if 'clipboard_running' not in st.session_state:
    st.session_state.clipboard_running = False

if 'clipboard_last_value' not in st.session_state:
    st.session_state.clipboard_last_value = ""

if 'page' not in st.session_state:
    st.session_state.page = "添加链接"

# Page configuration
st.set_page_config(
    page_title="抖音链接管理系统",
    page_icon="🎥",
    layout="wide"
)

def is_douyin_url(url: str) -> bool:
    """Check if URL is a Douyin link"""
    return 'douyin.com' in url or 'iesdouyin.com' in url

def clipboard_listener():
    """Monitor clipboard for Douyin links"""
    if not CLIPBOARD_AVAILABLE:
        return
    
    while st.session_state.clipboard_running:
        try:
            current_value = pyperclip.paste()
            
            if (current_value != st.session_state.clipboard_last_value and 
                is_douyin_url(current_value)):
                st.session_state.clipboard_last_value = current_value
                success, message = st.session_state.db.add_link(current_value)
                
                # Store notification
                if 'clipboard_notifications' not in st.session_state:
                    st.session_state.clipboard_notifications = []
                
                st.session_state.clipboard_notifications.append({
                    'url': current_value,
                    'success': success,
                    'message': message,
                    'time': datetime.now()
                })
            
            time.sleep(1)  # Check every second
        except Exception as e:
            pass

def main():
    st.title("🎥 抖音链接管理系统")
    
    # Sidebar navigation
    with st.sidebar:
        st.header("导航菜单")
        page = st.radio(
            "选择功能",
            ["添加链接", "查看链接", "搜索链接", "分类管理", "AI分析", "导出数据", "统计信息", "设置"]
        )
        st.session_state.page = page
        
        # Display statistics
        stats = st.session_state.db.get_statistics()
        st.divider()
        st.subheader("📊 统计")
        st.metric("总链接数", stats['total'])
        st.metric("已分析", stats['analyzed'])
    
    # Main content
    if page == "添加链接":
        page_add_link()
    elif page == "查看链接":
        page_view_links()
    elif page == "搜索链接":
        page_search_links()
    elif page == "分类管理":
        page_category_management()
    elif page == "AI分析":
        page_ai_analysis()
    elif page == "导出数据":
        page_export_data()
    elif page == "统计信息":
        page_statistics()
    elif page == "设置":
        page_settings()

def page_add_link():
    st.header("添加抖音链接")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        url = st.text_input("🔗 抖音链接", placeholder="粘贴抖音链接或复制 https://www.douyin.com/...")
    
    with col2:
        st.write("")
        st.write("")
        if CLIPBOARD_AVAILABLE:
            if st.button("📋 从剪贴板读取"):
                try:
                    url = pyperclip.paste()
                    st.rerun()
                except:
                    st.warning("无法读取剪贴板")
    
    col1, col2 = st.columns(2)
    with col1:
        title = st.text_input("📝 标题", placeholder="视频标题")
        author = st.text_input("👤 作者", placeholder="创作者名称")
    
    with col2:
        content = st.text_area("📄 内容描述", placeholder="视频内容简介", height=80)
    
    category = st.selectbox(
        "分类",
        ["未分类", "美食", "美妆", "服装", "电商", "教育", "娱乐", "体育", "其他"]
    )
    
    notes = st.text_area("📌 备注", placeholder="任何其他信息或想法", height=80)
    
    if st.button("💾 保存链接", use_container_width=True):
        if not url:
            st.error("请输入抖音链接")
        elif not is_douyin_url(url):
            st.error("请输入有效的抖音链接 (douyin.com 或 iesdouyin.com)")
        else:
            success, message = st.session_state.db.add_link(
                url, title, author, content, notes, category
            )
            if success:
                st.success(f"✅ {message}")
                st.balloons()
            else:
                st.warning(f"⚠️ {message}")
    
    # Clipboard monitor section
    st.divider()
    st.subheader("📋 Windows 剪贴板监听")
    
    if not CLIPBOARD_AVAILABLE:
        st.warning("⚠️ 需要安装 pyperclip: pip install pyperclip")
    else:
        col1, col2 = st.columns(2)
        with col1:
            if not st.session_state.clipboard_running:
                if st.button("▶️ 启动剪贴板监听", use_container_width=True):
                    st.session_state.clipboard_running = True
                    thread = threading.Thread(target=clipboard_listener, daemon=True)
                    thread.start()
                    st.success("✅ 剪贴板监听已启动")
                    st.rerun()
            else:
                if st.button("⏹️ 停止剪贴板监听", use_container_width=True):
                    st.session_state.clipboard_running = False
                    st.info("剪贴板监听已停止")
                    st.rerun()
        
        with col2:
            if st.session_state.clipboard_running:
                st.info("🟢 监听中...")
        
        # Display notifications
        if 'clipboard_notifications' in st.session_state:
            if st.session_state.clipboard_notifications:
                st.subheader("最近的自动保存")
                for notif in st.session_state.clipboard_notifications[-5:]:
                    if notif['success']:
                        st.success(f"✅ {notif['url'][:50]}... - {notif['time'].strftime('%H:%M:%S')}")
                    else:
                        st.warning(f"⚠️ {notif['message']} - {notif['time'].strftime('%H:%M:%S')}")

def page_view_links():
    st.header("查看所有链接")
    
    links = st.session_state.db.get_all_links()
    
    if not links:
        st.info("还没有保存任何链接")
        return
    
    st.subheader(f"共有 {len(links)} 个链接")
    
    for link in links:
        with st.container():
            col1, col2 = st.columns([4, 1])
            
            with col1:
                st.write(f"**📝 {link['title'] or '无标题'}**")
                st.write(f"👤 {link['author'] or '未知作者'}")
                st.write(f"🔗 {link['url']}")
                if link['content']:
                    st.write(f"📄 {link['content']}")
                if link['category']:
                    st.write(f"🏷️ 分类: {link['category']}")
                if link['notes']:
                    st.write(f"📌 备注: {link['notes']}")
                if link['analysis']:
                    with st.expander("查看 AI 分析"):
                        st.write(link['analysis'])
            
            with col2:
                col_edit, col_delete = st.columns(2)
                with col_edit:
                    if st.button("✏️", key=f"edit_{link['id']}"):
                        st.session_state.editing_id = link['id']
                        st.rerun()
                with col_delete:
                    if st.button("🗑️", key=f"delete_{link['id']}"):
                        st.session_state.db.delete_link(link['id'])
                        st.success("已删除")
                        st.rerun()
            
            st.divider()

def page_search_links():
    st.header("🔍 搜索链接")
    
    search_term = st.text_input("输入搜索关键词", placeholder="搜索标题、作者、内容、备注...")
    
    if search_term:
        results = st.session_state.db.search_links(search_term)
        
        if results:
            st.subheader(f"找到 {len(results)} 个结果")
            for link in results:
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    st.write(f"**📝 {link['title'] or '无标题'}**")
                    st.write(f"👤 {link['author'] or '未知作者'}")
                    st.write(f"🔗 {link['url']}")
                    if link['notes']:
                        st.write(f"📌 {link['notes']}")
                
                with col2:
                    if st.button("🔗 复制", key=f"copy_{link['id']}"):
                        if CLIPBOARD_AVAILABLE:
                            pyperclip.copy(link['url'])
                            st.success("已复制到剪贴板")
                st.divider()
        else:
            st.info("未找到匹配的链接")

def page_category_management():
    st.header("🏷️ 分类管理")
    
    categories = st.session_state.db.get_categories()
    
    if categories:
        st.subheader("按分类浏览")
        
        for category in categories:
            with st.expander(f"📁 {category}"):
                links = st.session_state.db.get_by_category(category)
                st.write(f"共有 {len(links)} 个链接")
                
                for link in links:
                    st.write(f"- **{link['title'] or '无标题'}** - {link['author'] or '未知作者'}")
                    st.write(f"  🔗 {link['url']}")
    else:
        st.info("还没有分类")

def page_ai_analysis():
    st.header("🤖 AI 内容分析")
    
    if not st.session_state.analyzer.is_available():
        st.error("❌ 未配置 OpenAI API Key")
        st.info("请在 .env 文件中设置 OPENAI_API_KEY")
        return
    
    links = st.session_state.db.get_all_links()
    
    if not links:
        st.info("没有可分析的链接")
        return
    
    st.subheader("选择要分析的内容")
    
    analysis_option = st.radio(
        "分析选项",
        ["分析单个内容", "批量分析所有未分析内容", "批量分析全部内容"]
    )
    
    if analysis_option == "分析单个内容":
        selected_link = st.selectbox(
            "选择链接",
            links,
            format_func=lambda x: f"{x['title'] or '无标题'} - {x['author'] or '未知作者'}"
        )
        
        if st.button("🚀 开始分析", use_container_width=True):
            with st.spinner("分析中..."):
                success, analysis = st.session_state.analyzer.analyze_content(
                    selected_link['title'] or '',
                    selected_link['author'] or '',
                    selected_link['content'] or '',
                    selected_link['notes'] or ''
                )
                
                if success:
                    st.session_state.db.update_link(selected_link['id'], analysis=analysis)
                    st.success("✅ 分析完成")
                    st.subheader("分析结果")
                    st.write(analysis)
                else:
                    st.error(f"❌ {analysis}")
    
    elif analysis_option == "批量分析所有未分析内容":
        unanalyzed = [link for link in links if not link['analysis']]
        
        if not unanalyzed:
            st.info("所有内容都已分析")
            return
        
        st.write(f"找到 {len(unanalyzed)} 个未分析的内容")
        
        if st.button("🚀 开始分析", use_container_width=True):
            progress_bar = st.progress(0)
            
            for idx, link in enumerate(unanalyzed):
                with st.spinner(f"分析中 ({idx+1}/{len(unanalyzed)})..."):
                    success, analysis = st.session_state.analyzer.analyze_content(
                        link['title'] or '',
                        link['author'] or '',
                        link['content'] or '',
                        link['notes'] or ''
                    )
                    
                    if success:
                        st.session_state.db.update_link(link['id'], analysis=analysis)
                
                progress_bar.progress((idx + 1) / len(unanalyzed))
            
            st.success("✅ 所有内容分析完成")
    
    else:  # Batch analyze all
        if st.button("🚀 分析所有内容", use_container_width=True):
            progress_bar = st.progress(0)
            
            for idx, link in enumerate(links):
                with st.spinner(f"分析中 ({idx+1}/{len(links)})..."):
                    success, analysis = st.session_state.analyzer.analyze_content(
                        link['title'] or '',
                        link['author'] or '',
                        link['content'] or '',
                        link['notes'] or ''
                    )
                    
                    if success:
                        st.session_state.db.update_link(link['id'], analysis=analysis)
                
                progress_bar.progress((idx + 1) / len(links))
            
            st.success("✅ 所有内容分析完成")

def page_export_data():
    st.header("📤 导出数据")
    
    links = st.session_state.db.get_all_links()
    
    if not links:
        st.info("没有数据可导出")
        return
    
    st.write(f"共有 {len(links)} 个链接可导出")
    
    export_format = st.radio("选择导出格式", ["CSV", "JSON"])
    
    if st.button("📥 导出", use_container_width=True):
        if export_format == "CSV":
            success, message = st.session_state.db.export_to_csv("douyin_links_export.csv")
            if success:
                st.success(f"✅ {message}")
                with open("douyin_links_export.csv", "r", encoding='utf-8-sig') as f:
                    st.download_button(
                        label="⬇️ 下载 CSV 文件",
                        data=f.read(),
                        file_name="douyin_links.csv",
                        mime="text/csv"
                    )
            else:
                st.error(f"❌ {message}")
        
        else:  # JSON
            import json
            json_data = json.dumps(links, ensure_ascii=False, indent=2, default=str)
            st.download_button(
                label="⬇️ 下载 JSON 文件",
                data=json_data,
                file_name="douyin_links.json",
                mime="application/json"
            )
            st.success("✅ JSON 文件已准备好下载")

def page_statistics():
    st.header("📊 统计信息")
    
    stats = st.session_state.db.get_statistics()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("总链接数", stats['total'])
    
    with col2:
        st.metric("已分析", stats['analyzed'])
    
    with col3:
        if stats['total'] > 0:
            analysis_rate = (stats['analyzed'] / stats['total']) * 100
            st.metric("分析完成率", f"{analysis_rate:.1f}%")
    
    st.divider()
    
    if stats['categories']:
        st.subheader("按分类统计")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.bar_chart(stats['categories'])
        
        with col2:
            for category, count in stats['categories'].items():
                st.write(f"🏷️ {category}: {count}")

def page_settings():
    st.header("⚙️ 设置")
    
    st.subheader("OpenAI 配置")
    
    if st.session_state.analyzer.is_available():
        st.success("✅ OpenAI API 已配置")
        api_key = os.getenv('OPENAI_API_KEY')
        masked_key = api_key[:10] + "***" + api_key[-5:] if api_key else "未配置"
        st.write(f"API Key: {masked_key}")
    else:
        st.warning("⚠️ OpenAI API 未配置")
        st.info("""
        要启用 AI 分析功能，请：
        1. 在项目目录创建 .env 文件
        2. 添加: OPENAI_API_KEY=你的API密钥
        3. 保存并重新运行应用
        """)
    
    st.divider()
    
    st.subheader("剪贴板监听")
    if CLIPBOARD_AVAILABLE:
        st.success("✅ pyperclip 已安装")
    else:
        st.warning("⚠️ pyperclip 未安装")
        st.info("运行命令: pip install pyperclip")
    
    st.divider()
    
    st.subheader("数据库信息")
    stats = st.session_state.db.get_statistics()
    st.write(f"数据库文件: douyin_links.db")
    st.write(f"总记录数: {stats['total']}")
    
    if st.button("🔄 刷新统计"):
        st.rerun()

if __name__ == "__main__":
    main()
