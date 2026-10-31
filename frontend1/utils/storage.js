// 本地存储工具
const STORAGE_KEYS = {
	TOKEN: 'token',
	USER_INFO: 'userInfo',
	CAPSULES: 'capsules',
	ACHIEVEMENTS: 'achievements',
	EMOTIONS: 'emotions',
	SETTINGS: 'settings',
	IS_GUEST: 'isGuest'
}

export default {
	// 设置token
	setToken(token) {
		uni.setStorageSync(STORAGE_KEYS.TOKEN, token)
	},
	
	// 获取token
	getToken() {
		return uni.getStorageSync(STORAGE_KEYS.TOKEN)
	},
	
	// 清除token
	removeToken() {
		uni.removeStorageSync(STORAGE_KEYS.TOKEN)
	},
	
	// 设置用户信息
	setUserInfo(userInfo) {
		uni.setStorageSync(STORAGE_KEYS.USER_INFO, userInfo)
	},
	
	// 获取用户信息
	getUserInfo() {
		return uni.getStorageSync(STORAGE_KEYS.USER_INFO) || {}
	},
	
	// 保存胶囊
	saveCapsule(capsule) {
		const capsules = this.getCapsules()
		const index = capsules.findIndex(c => c.id === capsule.id)
		if (index >= 0) {
			capsules[index] = capsule
		} else {
			capsules.push(capsule)
		}
		uni.setStorageSync(STORAGE_KEYS.CAPSULES, capsules)
	},
	
	// 获取所有胶囊
	getCapsules() {
		return uni.getStorageSync(STORAGE_KEYS.CAPSULES) || []
	},
	
	// 获取胶囊
	getCapsule(id) {
		const capsules = this.getCapsules()
		return capsules.find(c => c.id === id)
	},
	
	// 删除胶囊
	deleteCapsule(id) {
		const capsules = this.getCapsules()
		const filtered = capsules.filter(c => c.id !== id)
		uni.setStorageSync(STORAGE_KEYS.CAPSULES, filtered)
	},
	
	// 保存成就
	saveAchievement(achievement) {
		const achievements = this.getAchievements()
		if (!achievements.find(a => a.id === achievement.id)) {
			achievements.push(achievement)
			uni.setStorageSync(STORAGE_KEYS.ACHIEVEMENTS, achievements)
		}
	},
	
	// 获取成就
	getAchievements() {
		return uni.getStorageSync(STORAGE_KEYS.ACHIEVEMENTS) || []
	},
	
	// 保存情绪记录
	saveEmotion(emotion) {
		const emotions = this.getEmotions()
		emotions.push(emotion)
		uni.setStorageSync(STORAGE_KEYS.EMOTIONS, emotions)
	},
	
	// 获取情绪记录
	getEmotions() {
		return uni.getStorageSync(STORAGE_KEYS.EMOTIONS) || []
	},
	
	// 清除所有数据
	clearAll() {
		Object.values(STORAGE_KEYS).forEach(key => {
			uni.removeStorageSync(key)
		})
	},
	
	// 游客模式相关
	isGuest() {
		return !this.getToken()
	},
	
	setGuestMode(isGuest) {
		uni.setStorageSync(STORAGE_KEYS.IS_GUEST, isGuest)
	},
	
	// 检查是否已登录
	isLoggedIn() {
		return !!this.getToken()
	},
	
	// 需要登录时显示提示
	requireLogin(actionName = '该功能') {
		if (this.isGuest()) {
			uni.showModal({
				title: '需要登录',
				content: `${actionName}需要登录后使用，是否前往登录？`,
				confirmText: '去登录',
				cancelText: '继续浏览',
				success: (res) => {
					if (res.confirm) {
						uni.navigateTo({
							url: '/pages/login/login'
						})
					}
				}
			})
			return false
		}
		return true
	}
}

