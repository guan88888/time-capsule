// 日期工具
export default {
	// 格式化日期
	formatDate(date, format = 'YYYY-MM-DD HH:mm:ss') {
		if (!date) return ''
		const d = new Date(date)
		const year = d.getFullYear()
		const month = String(d.getMonth() + 1).padStart(2, '0')
		const day = String(d.getDate()).padStart(2, '0')
		const hour = String(d.getHours()).padStart(2, '0')
		const minute = String(d.getMinutes()).padStart(2, '0')
		const second = String(d.getSeconds()).padStart(2, '0')
		
		return format
			.replace('YYYY', year)
			.replace('MM', month)
			.replace('DD', day)
			.replace('HH', hour)
			.replace('mm', minute)
			.replace('ss', second)
	},
	
	// 计算倒计时
	getCountdown(targetDate) {
		if (!targetDate) {
			return {
				days: 0,
				hours: 0,
				minutes: 0,
				seconds: 0,
				isExpired: true
			}
		}
		const now = new Date().getTime()
		const target = new Date(targetDate).getTime()
		if (isNaN(target)) {
			return {
				days: 0,
				hours: 0,
				minutes: 0,
				seconds: 0,
				isExpired: true
			}
		}
		const diff = target - now
		
		if (diff <= 0) {
			return {
				days: 0,
				hours: 0,
				minutes: 0,
				seconds: 0,
				isExpired: true
			}
		}
		
		const days = Math.floor(diff / (1000 * 60 * 60 * 24))
		const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60))
		const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))
		const seconds = Math.floor((diff % (1000 * 60)) / 1000)
		
		return {
			days,
			hours,
			minutes,
			seconds,
			isExpired: false
		}
	},
	
	// 判断是否已解锁
	isUnlocked(unlockDate) {
		if (!unlockDate) return false
		const targetTime = new Date(unlockDate).getTime()
		if (isNaN(targetTime)) return false
		return new Date().getTime() >= targetTime
	},
	
	// 生成唯一ID
	generateId() {
		return Date.now().toString(36) + Math.random().toString(36).substr(2)
	}
}

