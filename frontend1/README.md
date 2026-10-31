# 时空胶囊 App - 前端项目

## 项目简介

时空胶囊是一款记录时光、遇见未来的App。用户可以创建不同类型的胶囊（目标、心境、感恩、共享），在设定的时间解锁并回顾，同时提供情绪追踪、成就系统等功能。

## 技术栈

- **框架**: uni-app (Vue 3)
- **开发工具**: HBuilderX
- **存储**: 本地存储 (uni.storage)

## 项目结构

```
frontend1/
├── pages/              # 页面目录
│   ├── index/          # 主页面（星空场景）
│   ├── login/          # 登录页面
│   ├── register/       # 注册页面
│   ├── profile/        # 个人中心
│   ├── create/         # 创建胶囊
│   ├── capsule-list/   # 胶囊列表
│   ├── unlock/         # 解锁胶囊
│   ├── review/         # 回顾胶囊
│   ├── share/          # 共享胶囊
│   ├── share-unlock/   # 解锁共享胶囊
│   ├── emotion-calendar/ # 情绪日历
│   ├── achievement/    # 成就中心
│   └── settings/       # 设置页面
├── components/         # 组件目录
│   └── countdown/      # 倒计时组件
├── utils/              # 工具函数
│   ├── storage.js      # 本地存储工具
│   ├── encrypt.js      # 加密工具
│   ├── date.js         # 日期工具
│   └── api.js          # API接口
├── common/             # 公共资源
│   └── common.css      # 公共样式
├── static/             # 静态资源
│   └── tabbar/         # TabBar图标
├── App.vue             # 应用入口
├── main.js             # 主入口文件
├── pages.json          # 页面配置
└── manifest.json       # 应用配置

```

## 功能模块

### 1. 用户账户管理
- 用户注册/登录（邮箱、手机号）
- 个人信息设置
- 数据备份与恢复

### 2. 胶囊创建与管理
- 胶囊类型：目标胶囊、心境胶囊、感恩胶囊、共享胶囊
- 内容编辑（支持文本、图片、语音）
- 定时封装
- 加密存储
- 标签分类

### 3. 胶囊解锁与回顾
- 定时解锁
- 内容回顾
- 目标进度追踪
- 情绪评分
- 心理健康建议

### 4. 共享胶囊
- 生成共享链接与密语
- 解锁共享胶囊
- 互动功能（点赞、评论）

### 5. 心理健康与情感反馈
- 情绪日历
- 情绪趋势分析
- 心理健康建议

### 6. 成就与奖励系统
- 成就解锁
- 成就展示
- 进度激励

### 7. 可视化界面
- 星空场景背景
- 胶囊可视化展示
- 倒计时功能

## 使用说明

### 开发环境

1. 使用 HBuilderX 打开项目
2. 运行到浏览器/App/小程序

### 配置说明

1. **TabBar图标**: 需要在 `static/tabbar/` 目录下放置图标文件
   - home.png / home-active.png
   - capsule.png / capsule-active.png
   - achievement.png / achievement-active.png
   - profile.png / profile-active.png

2. **API配置**: 在 `utils/api.js` 中配置后端API地址

### 数据存储

- 所有数据默认存储在本地（uni.storage）
- 支持云同步功能（需配置后端）
- 胶囊内容使用Base64加密（实际项目中应使用更安全的加密方式）

## 注意事项

1. 当前版本使用模拟数据，实际部署需要连接后端API
2. 加密功能使用Base64编码，生产环境应使用AES等更安全的加密方式
3. TabBar图标需要自行添加
4. 部分功能（如云同步、社交分享）需要后端支持

## 开发计划

- [ ] 连接后端API
- [ ] 实现图片上传功能
- [ ] 实现语音录制功能
- [ ] 完善云同步功能
- [ ] 添加推送通知
- [ ] 优化加密算法
- [ ] 添加数据导出功能

## 许可证

MIT License

