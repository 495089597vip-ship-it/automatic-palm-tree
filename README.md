# 🎥 抖音链接管理系统

一个完整的抖音链接管理工具，集成了 Streamlit 界面、SQLite 数据库、Windows 剪贴板自动监听和 OpenAI AI 分析功能。

## ✨ 功能特性

- ✅ **Streamlit Web 界面** - 现代化、易用的用户界面
- ✅ **SQLite 数据库** - 本地化数据存储，无需服务器
- ✅ **手动链接管理** - 支持添加标题、作者、内容、分类、备注
- ✅ **Windows 剪贴板监听** - 自动检测并保存 Douyin 链接
- ✅ **自动去重** - 防止重复链接
- ✅ **链接查看** - 浏览所有已保存的链接
- ✅ **搜索功能** - 按关键词搜索链接
- ✅ **分类管理** - 按分类组织链接
- ✅ **OpenAI AI 分析** - 自动分析抖音内容特点和优化建议
- ✅ **数据导出** - 支持 CSV 和 JSON 导出
- ✅ **统计信息** - 查看数据统计和分类分布
- ❌ **不包含** - 自动刷抖音、自动点赞、自动评论、自动滑动等违规功能

## 📋 系统要求

- Python 3.8+
- Windows 操作系统（剪贴板监听功能）
- （可选）OpenAI API Key 用于 AI 分析功能

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 OpenAI API（可选）

创建 `.env` 文件在项目根目录：

```env
OPENAI_API_KEY=your_api_key_here
```

### 3. 运行应用

```bash
streamlit run app.py
```

应用将自动在浏览器中打开，通常地址为 `http://localhost:8501`

## 📁 项目结构

```
automatic-palm-tree/
├── app.py              # 主应用程序（Streamlit）
├── database.py         # 数据库模块（SQLite）
├── ai_analyzer.py      # AI 分析模块（OpenAI）
├── requirements.txt    # 项���依赖
├── .env               # 环境变量配置（需要创建）
└── README.md          # 项目说明
```

## 📖 使用指南

### 添加链接

1. 在「添加链接」页面粘贴或输入抖音链接
2. 填写标题、作者、内容描述等信息
3. 选择分类
4. 点击「保存链接」按钮

### 自动监听剪贴板

1. 在「添加链接」页面点击「启动剪贴板监听」
2. 系统会自动检测复制到剪贴板中的抖音链接
3. 自动保存新链接并显示通知
4. 点击「停止剪贴板监听」可停止监听

### 查看和搜索

- **查看链接** - 浏览所有保存的链接，支持编辑和删除
- **搜索链接** - 按关键词搜索标题、作者、内容、备注
- **分类浏览** - 按分类查看链接

### AI 分析

1. 确保已配置 OpenAI API Key
2. 在「AI 分析」页面选择分析选项
3. 选择要分析的内容或批量分析
4. 系统将生成详细的内容分析报告

分析内容包括：
- 内容类型和特点
- 目标受众
- 互动潜力
- 优化建议
- 关键词提取

### 导出数据

- 支持导出为 CSV 格式（可在 Excel 中打开）
- 支持导出为 JSON 格式（用于数据集成）

## 🛠️ 配置说明

### requirements.txt

- `streamlit` - Web 应用框架
- `openpyxl` - Excel 处理库
- `python-dotenv` - 环境变量管理
- `pyperclip` - 剪贴板访问（Windows）
- `openai` - OpenAI API 客户端
- `pandas` - 数据处理和导出

### .env 文件示例

```env
# OpenAI API 配置
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

## 📊 数据库结构

### douyin_links 表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| url | TEXT | 抖音链接（唯一） |
| title | TEXT | 视频标题 |
| author | TEXT | 创作者名称 |
| content | TEXT | 内容描述 |
| notes | TEXT | 用户备注 |
| category | TEXT | 分类 |
| analysis | TEXT | AI 分析结果 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

## 🔒 隐私和安全

- 所有数据存储在本地 SQLite 数据库中
- 不收集任何个人信息
- API Key 仅用于 OpenAI 服务
- 支持本地离线使用（不需要 AI 分析）

## ⚠️ 注意事项

1. **链接有效期** - 抖音链接可能会过期，保存的链接未来可能无法访问
2. **API 费用** - 使用 OpenAI API 会产生费用，请检查您的账户额度
3. **剪贴板监听** - 仅在 Windows 上支持，其他操作系统需要安装相应的剪贴板工具
4. **网络连接** - AI 分析功能需要网络连接

## 📝 常见问题

### Q: 如何安装 pyperclip 后剪贴板仍然无法工作？

A: 确保您在 Windows 系统上。如果仍有问题，尝试以管理员身份运行 Streamlit。

### Q: OpenAI API 返回错误怎么办？

A: 检查以下内容：
- API Key 是否正确
- 账户是否有足够的额度
- 网络连接是否正常
- API 是否暂时不可用

### Q: 如何重置数据库？

A: 删除项目目录中的 `douyin_links.db` 文件，重新运行应用会自动创建新数据库。

### Q: 支持多用户吗？

A: 当前版本是单机应用，使用同一数据库。所有用户共享相同的链接库。

## 🐛 故障排除

### 应用无法启动

```bash
# 检查依赖是否安装
pip install -r requirements.txt

# 重新运行
streamlit run app.py
```

### 数据库锁定

如果遇到数据库被锁定的错误：
1. 关闭所有应用实例
2. 删除可能存在的 `.db-wal` 和 `.db-shm` 文件
3. 重新启动应用

### 导出失败

确保：
- 硬盘空间充足
- 项目目录有写入权限
- 输出文件未被其他程序占用

## 📦 依赖版本

所有依赖都是最新的稳定版本，已在 Python 3.8+ 上测试通过。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来改进这个项目。

## 📄 许可证

本项目采用 MIT 许可证。

## 🙏 致谢

- [Streamlit](https://streamlit.io/) - 前端框架
- [OpenAI](https://openai.com/) - AI 分析能力
- [SQLite](https://www.sqlite.org/) - 数据库引擎

## 📞 联系方式

如有问题或建议，欢迎通过 GitHub Issues 联系我们。

---

**最后更新**: 2024
**版本**: 1.0.0
