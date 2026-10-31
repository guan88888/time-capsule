# API接口清单

## 一、认证相关 (已实现)
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 密码登录
- `POST /api/auth/send-code` - 发送验证码
- `POST /api/auth/code-login` - 验证码登录
- `POST /api/auth/forgot-password` - 忘记密码
- `POST /api/auth/reset-password` - 重置密码

## 二、用户相关 (已实现)
- `GET /api/user/me` - 获取当前用户信息
- `PUT /api/user/profile` - 更新用户资料
- `POST /api/user/avatar` - 上传头像
- `DELETE /api/user/avatar` - 删除头像

## 三、胶囊相关 (需要实现)
- `GET /api/capsules` - 获取胶囊列表
  - 查询参数: `filter` (all/locked/unlocked), `type` (target/emotion/gratitude/share)
  - 用途: 首页展示、胶囊列表页
- `GET /api/capsules/{id}` - 获取胶囊详情
  - 用途: 解锁页、回顾页查看胶囊详情
- `POST /api/capsules` - 创建胶囊
  - 请求体: type, title, content, target(可选), unlock_date, tags(可选), allow_share(可选)
  - 用途: 创建胶囊页面
- `PUT /api/capsules/{id}` - 更新胶囊
  - 请求体: title, content, target, tags等
  - 用途: 编辑胶囊
- `PUT /api/capsules/{id}/unlock` - 解锁胶囊
  - 用途: 解锁页面，标记胶囊为已解锁
- `PUT /api/capsules/{id}/review` - 保存回顾
  - 请求体: review, progress(目标胶囊), emotion_score(心境胶囊)
  - 用途: 回顾页面保存回顾内容
- `DELETE /api/capsules/{id}` - 删除胶囊
  - 用途: 删除胶囊

## 四、共享胶囊相关 (需要实现)
- `GET /api/capsules/share/{code}` - 通过共享码获取共享胶囊
  - 用途: 解锁共享胶囊页面
- `POST /api/capsules/{id}/share` - 生成共享码
  - 用途: 共享胶囊页面生成共享码
- `POST /api/capsules/{id}/like` - 点赞共享胶囊
  - 用途: 共享胶囊互动
- `GET /api/capsules/{id}/comments` - 获取评论列表
  - 用途: 查看共享胶囊评论
- `POST /api/capsules/{id}/comments` - 添加评论
  - 请求体: content
  - 用途: 评论共享胶囊

## 五、情绪相关 (需要实现)
- `GET /api/emotions` - 获取情绪记录列表
  - 查询参数: `start_date`, `end_date`
  - 用途: 情绪日历页面
- `POST /api/emotions` - 记录情绪
  - 请求体: score (0-4), capsule_id(可选), date(可选，默认今天)
  - 用途: 回顾页面记录情绪
- `GET /api/emotions/calendar` - 获取情绪日历数据
  - 查询参数: `year`, `month`
  - 用途: 情绪日历页面显示日历
- `GET /api/emotions/stats` - 获取情绪统计
  - 查询参数: `start_date`, `end_date`
  - 用途: 情绪日历页面统计

## 六、成就相关 (需要实现)
- `GET /api/achievements` - 获取成就列表
  - 用途: 成就中心页面
- `POST /api/achievements/{id}/unlock` - 解锁成就
  - 用途: 系统自动解锁或手动解锁成就

