// API接口
import storage from './storage.js'

// 后端API地址 - 开发环境使用本地地址，生产环境需要修改
// 注意：在HBuilderX中运行时，如果使用127.0.0.1无法连接，可以尝试使用localhost
export const BASE_URL = 'http://localhost:8000'  // 或 'http://127.0.0.1:8000'

const api = {
	// 请求封装
	request(url, method = 'GET', data = {}) {
		return new Promise((resolve, reject) => {
			const token = storage.getToken()
			const requestUrl = BASE_URL + url
			
			// 调试信息
			console.log(`[API Request] ${method} ${requestUrl}`, data)
			
			uni.request({
				url: requestUrl,
				method,
				data,
				header: {
					'Authorization': token ? `Bearer ${token}` : '',
					'Content-Type': 'application/json'
				},
				timeout: 10000, // 10秒超时
				success: (res) => {
					console.log(`[API Response] ${method} ${requestUrl}`, res)
					if (res.statusCode >= 200 && res.statusCode < 300) {
						resolve(res.data)
					} else {
						// 处理错误响应
						const errorMsg = res.data?.detail || res.data?.message || `请求失败 (${res.statusCode})`
						
						// 处理401未授权错误 - 游客模式下不自动跳转
						if (res.statusCode === 401) {
							// 游客模式：不自动跳转，让页面自己处理
							console.log('[API] 401 未授权 - 游客模式，不自动跳转')
							// 清除可能过期的token
							storage.removeToken()
						}
						
						reject({
							message: errorMsg,
							statusCode: res.statusCode
						})
					}
				},
				fail: (err) => {
					console.error(`[API Error] ${method} ${requestUrl}`, err)
					// 提供更详细的错误信息
					let errorMessage = '网络请求失败，请检查网络连接'
					if (err.errMsg) {
						if (err.errMsg.includes('timeout')) {
							errorMessage = '请求超时，请检查后端服务是否启动'
						} else if (err.errMsg.includes('fail') || err.errMsg.includes('connect')) {
							// 检查是否是H5环境下的跨域问题
							// #ifdef H5
							errorMessage = '无法连接到服务器。请确认：\n1. 后端服务运行在 http://localhost:8000\n2. 在HBuilderX中配置了代理或使用浏览器直接访问'
							// #endif
							// #ifndef H5
							errorMessage = '无法连接到服务器，请确认后端服务运行在 http://localhost:8000'
							// #endif
						} else {
							errorMessage = err.errMsg
						}
					}
					reject({
						message: errorMessage,
						error: err
					})
				}
			})
		})
	},
	
	// 登录
	async login(account, password) {
		try {
			const res = await this.request('/api/auth/login', 'POST', {
				account: account,
				password: password
			})
			
			// 保存token和用户信息
			storage.setToken(res.token)
			storage.setUserInfo({
				id: res.user.id,
				nickname: res.user.nickname,
				avatar: res.user.avatar || '',
				email: res.user.email || '',
				phone: res.user.phone || ''
			})
			
			return {
				token: res.token,
				userInfo: {
					id: res.user.id,
					nickname: res.user.nickname,
					avatar: res.user.avatar || '',
					email: res.user.email || '',
					phone: res.user.phone || ''
				}
			}
		} catch (error) {
			throw new Error(error.message || '登录失败，请重试')
		}
	},
	
	// 注册（支持验证码）
	async register(data) {
		try {
			const requestData = {
				nickname: data.nickname,
				account: data.email || data.phone,
				password: data.password
			}
			
			// 如果是手机号注册，添加短信验证码
			if (data.sms_code) {
				requestData.sms_code = data.sms_code
			}
			
			const res = await this.request('/api/auth/register', 'POST', requestData)
			
			// 保存token和用户信息
			storage.setToken(res.token)
			storage.setUserInfo({
				id: res.user.id,
				nickname: res.user.nickname,
				avatar: res.user.avatar || '',
				email: res.user.email || '',
				phone: res.user.phone || ''
			})
			
			return {
				token: res.token,
				userInfo: {
					id: res.user.id,
					nickname: res.user.nickname,
					avatar: res.user.avatar || '',
					email: res.user.email || '',
					phone: res.user.phone || ''
				}
			}
		} catch (error) {
			throw new Error(error.message || '注册失败，请重试')
		}
	},
	
	// 带验证码注册（新方法）
	async registerWithSms(data) {
		return this.register(data)
	},
	
	// 忘记密码
	async forgotPassword(account) {
		try {
			const res = await this.request('/api/auth/forgot-password', 'POST', {
				account: account
			})
			return res
		} catch (error) {
			throw new Error(error.message || '请求失败，请重试')
		}
	},
	
	// 重置密码（支持验证码）
	async resetPassword(account, newPassword, smsCode = null) {
		try {
			const res = await this.request('/api/auth/reset-password', 'POST', {
				account: account,
				new_password: newPassword,
				sms_code: smsCode
			})
			return res
		} catch (error) {
			throw new Error(error.message || '重置密码失败，请重试')
		}
	},
	
	// 验证码重置密码（新方法）
	async resetPasswordBySms(phone, code, newPassword) {
		try {
			const res = await this.request('/api/auth/reset-password', 'POST', {
				account: phone,
				new_password: newPassword,
				sms_code: code
			})
			return res
		} catch (error) {
			throw new Error(error.message || '重置密码失败，请重试')
		}
	},
	
	// 发送验证码（新接口，支持场景参数）
	async sendSms(phone, scene = 'register') {
		try {
			const res = await this.request('/api/auth/send-sms', 'POST', {
				phone: phone,
				scene: scene  // register/login/reset_password/change_phone/bind_phone/verify_bind_phone
			})
			return res
		} catch (error) {
			throw new Error(error.message || '发送验证码失败，请重试')
		}
	},
	
	// 发送验证码（兼容旧接口）
	async sendCode(phone) {
		try {
			const res = await this.request('/api/auth/send-code', 'POST', {
				phone: phone
			})
			return res
		} catch (error) {
			throw new Error(error.message || '发送验证码失败，请重试')
		}
	},
	
	// 验证码登录
	async codeLogin(phone, code) {
		try {
			const res = await this.request('/api/auth/code-login', 'POST', {
				phone: phone,
				code: code
			})
			
			// 保存token和用户信息
			storage.setToken(res.token)
			storage.setUserInfo({
				id: res.user.id,
				nickname: res.user.nickname,
				avatar: res.user.avatar || '',
				email: res.user.email || '',
				phone: res.user.phone || ''
			})
			
			return {
				token: res.token,
				userInfo: {
					id: res.user.id,
					nickname: res.user.nickname,
					avatar: res.user.avatar || '',
					email: res.user.email || '',
					phone: res.user.phone || ''
				}
			}
		} catch (error) {
			throw new Error(error.message || '登录失败，请重试')
		}
	},
	
	// 获取当前用户信息（从服务器）
	async getCurrentUser() {
		try {
			const res = await this.request('/api/user/me', 'GET')
			
			// 更新本地存储
			storage.setUserInfo({
				id: res.id,
				nickname: res.nickname,
				avatar: res.avatar ? (res.avatar.startsWith('http') ? res.avatar : BASE_URL + '/uploads/' + res.avatar) : '',
				email: res.email || '',
				phone: res.phone || ''
			})
			
			return res
		} catch (error) {
			throw new Error(error.message || '获取用户信息失败')
		}
	},
	
	// 获取用户信息（从本地缓存）
	getUserInfo() {
		return Promise.resolve(storage.getUserInfo())
	},
	
	// 更新用户资料
	async updateProfile(data) {
		try {
			const res = await this.request('/api/user/profile', 'PUT', {
				nickname: data.nickname,
				email: data.email
			})
			
			// 更新本地存储
			storage.setUserInfo({
				id: res.id,
				nickname: res.nickname,
				avatar: res.avatar ? (res.avatar.startsWith('http') ? res.avatar : BASE_URL + '/uploads/' + res.avatar) : '',
				email: res.email || '',
				phone: res.phone || ''
			})
			
			return res
		} catch (error) {
			throw new Error(error.message || '更新资料失败')
		}
	},
	
	// 上传头像
	async uploadAvatar(filePath) {
		return new Promise((resolve, reject) => {
			const token = storage.getToken()
			
			uni.uploadFile({
				url: BASE_URL + '/api/user/avatar',
				filePath: filePath,
				name: 'file',
				header: {
					'Authorization': token ? `Bearer ${token}` : ''
				},
				success: (res) => {
					if (res.statusCode >= 200 && res.statusCode < 300) {
						try {
							const data = JSON.parse(res.data)
							// 解析返回的消息（格式：消息|相对路径）
							const parts = data.message.split('|')
							const avatarRelativePath = parts.length > 1 ? parts[1] : ''
							
							// 构建完整的头像URL
							let avatarUrl = ''
							if (avatarRelativePath) {
								avatarUrl = BASE_URL + '/uploads/' + avatarRelativePath
							}
							
							// 更新本地用户信息
							const userInfo = storage.getUserInfo()
							if (avatarUrl) {
								userInfo.avatar = avatarUrl
								storage.setUserInfo(userInfo)
							}
							
							resolve({
								message: parts[0] || '上传成功',
								avatarUrl: avatarUrl
							})
						} catch (e) {
							console.error('解析上传响应失败:', e)
							resolve({ 
								message: '上传成功',
								avatarUrl: ''
							})
						}
					} else {
						reject({
							message: '上传失败',
							statusCode: res.statusCode
						})
					}
				},
				fail: (err) => {
					reject({
						message: '上传失败，请检查网络连接',
						error: err
					})
				}
			})
		})
	},
	
	// 更新用户信息（本地方法，已废弃，使用updateProfile）
	updateUserInfo(data) {
		const userInfo = storage.getUserInfo()
		const updated = { ...userInfo, ...data }
		storage.setUserInfo(updated)
		return Promise.resolve(updated)
	},
	
	// ========== 胶囊相关 API ==========
	
	// 获取胶囊列表
	async getCapsules(filter = null, type = null) {
		try {
			let url = '/api/capsules'
			const params = []
			if (filter) params.push(`filter=${filter}`)
			if (type) params.push(`type=${type}`)
			if (params.length > 0) {
				url += '?' + params.join('&')
			}
			const res = await this.request(url, 'GET')
			return res
		} catch (error) {
			throw new Error(error.message || '获取胶囊列表失败')
		}
	},
	
	// 获取胶囊详情
	async getCapsule(id) {
		try {
			const res = await this.request(`/api/capsules/${id}`, 'GET')
			return res
		} catch (error) {
			throw new Error(error.message || '获取胶囊详情失败')
		}
	},
	
	// 创建胶囊
	async createCapsule(data) {
		try {
			const res = await this.request('/api/capsules', 'POST', {
				type: data.type,
				title: data.title,
				content: data.content,
				target: data.target || null,
				unlock_date: data.unlockDate,
				tags: data.tags || [],
				allow_share: data.allowShare || false
			})
			return res
		} catch (error) {
			throw new Error(error.message || '创建胶囊失败')
		}
	},
	
	// 更新胶囊
	async updateCapsule(id, data) {
		try {
			const res = await this.request(`/api/capsules/${id}`, 'PUT', data)
			return res
		} catch (error) {
			throw new Error(error.message || '更新胶囊失败')
		}
	},
	
	// 解锁胶囊
	async unlockCapsule(id) {
		try {
			const res = await this.request(`/api/capsules/${id}/unlock`, 'PUT')
			return res
		} catch (error) {
			throw new Error(error.message || '解锁胶囊失败')
		}
	},
	
	// 保存回顾
	async saveReview(id, data) {
		try {
			const res = await this.request(`/api/capsules/${id}/review`, 'PUT', {
				review: data.review,
				progress: data.progress,
				emotion_score: data.emotionScore
			})
			return res
		} catch (error) {
			throw new Error(error.message || '保存回顾失败')
		}
	},
	
	// 删除胶囊
	async deleteCapsule(id) {
		try {
			const res = await this.request(`/api/capsules/${id}`, 'DELETE')
			return res
		} catch (error) {
			throw new Error(error.message || '删除胶囊失败')
		}
	},
	
	// 通过共享码获取胶囊
	async getSharedCapsule(code) {
		try {
			const res = await this.request(`/api/capsules/share/${code}`, 'GET')
			return res
		} catch (error) {
			throw new Error(error.message || '获取共享胶囊失败')
		}
	},
	
	// 生成共享码
	async generateShareCode(id) {
		try {
			const res = await this.request(`/api/capsules/${id}/share`, 'POST')
			// 后端可能返回 {message, success, capsule} 或 {message, success}
			return res
		} catch (error) {
			throw new Error(error.message || '生成共享码失败')
		}
	},
	
	// 点赞/取消点赞
	async toggleLike(id) {
		try {
			const res = await this.request(`/api/capsules/${id}/like`, 'POST')
			return res
		} catch (error) {
			throw new Error(error.message || '操作失败')
		}
	},
	
	// 获取评论列表
	async getComments(id) {
		try {
			const res = await this.request(`/api/capsules/${id}/comments`, 'GET')
			return res
		} catch (error) {
			throw new Error(error.message || '获取评论失败')
		}
	},
	
	// 添加评论
	async addComment(id, content) {
		try {
			const res = await this.request(`/api/capsules/${id}/comments`, 'POST', {
				content: content
			})
			return res
		} catch (error) {
			throw new Error(error.message || '添加评论失败')
		}
	},
	
	// ========== 情绪相关 API ==========
	
	// 获取情绪记录列表
	async getEmotions(startDate = null, endDate = null) {
		try {
			let url = '/api/emotions'
			const params = []
			if (startDate) params.push(`start_date=${startDate}`)
			if (endDate) params.push(`end_date=${endDate}`)
			if (params.length > 0) {
				url += '?' + params.join('&')
			}
			const res = await this.request(url, 'GET')
			return res
		} catch (error) {
			throw new Error(error.message || '获取情绪记录失败')
		}
	},
	
	// 记录情绪
	async createEmotion(score, capsuleId = null, date = null) {
		try {
			const res = await this.request('/api/emotions', 'POST', {
				score: score,
				capsule_id: capsuleId,
				date: date
			})
			return res
		} catch (error) {
			throw new Error(error.message || '记录情绪失败')
		}
	},
	
	// 获取情绪日历数据
	async getEmotionCalendar(year, month) {
		try {
			const res = await this.request(`/api/emotions/calendar?year=${year}&month=${month}`, 'GET')
			return res
		} catch (error) {
			throw new Error(error.message || '获取情绪日历失败')
		}
	},
	
	// 获取情绪统计
	async getEmotionStats(startDate = null, endDate = null) {
		try {
			let url = '/api/emotions/stats'
			const params = []
			if (startDate) params.push(`start_date=${startDate}`)
			if (endDate) params.push(`end_date=${endDate}`)
			if (params.length > 0) {
				url += '?' + params.join('&')
			}
			const res = await this.request(url, 'GET')
			return res
		} catch (error) {
			throw new Error(error.message || '获取情绪统计失败')
		}
	},
	
	// ========== 成就相关 API ==========
	
	// 获取成就列表
	async getAchievements() {
		try {
			const res = await this.request('/api/achievements', 'GET')
			return res
		} catch (error) {
			throw new Error(error.message || '获取成就列表失败')
		}
	},
	
	// 解锁成就
	async unlockAchievement(id) {
		try {
			const res = await this.request(`/api/achievements/${id}/unlock`, 'POST')
			return res
		} catch (error) {
			throw new Error(error.message || '解锁成就失败')
		}
	},
	
	// ========== AI功能相关 API ==========
	
	// AI生成标题
	async generateTitle(content, count = 3) {
		try {
			const res = await this.request('/api/ai/generate-title', 'POST', {
				content: content,
				count: count
			})
			return res.titles || []
		} catch (error) {
			throw new Error(error.message || 'AI生成标题失败，请重试')
		}
	},
	
	// AI推荐标签
	async recommendTags(title, content, count = 5) {
		try {
			const res = await this.request('/api/ai/recommend-tags', 'POST', {
				title: title,
				content: content,
				count: count
			})
			return res.tags || []
		} catch (error) {
			throw new Error(error.message || 'AI推荐标签失败，请重试')
		}
	},
	
	// AI心理健康建议
	async getMentalSuggestion(emotionScore, reviewText, originalContent) {
		try {
			const res = await this.request('/api/ai/mental-suggestion', 'POST', {
				emotion_score: emotionScore,
				review_text: reviewText,
				original_content: originalContent
			})
			return res.suggestion || ''
		} catch (error) {
			throw new Error(error.message || 'AI生成心理健康建议失败，请重试')
		}
	}
}

export default api

