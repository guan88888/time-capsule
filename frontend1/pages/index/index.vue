<template>
	<view class="star-field">
		<!-- 星空背景 -->
		<view class="stars" v-for="(star, index) in stars" :key="index" 
			:style="{left: star.x + '%', top: star.y + '%', animationDelay: star.delay + 's'}">
		</view>
		
		<!-- 顶部导航 -->
		<view class="nav-bar">
			<view class="nav-title">时空胶囊</view>
			<view class="nav-actions">
				<view class="nav-icon" @click="goToProfile">
					<text class="iconfont">👤</text>
				</view>
			</view>
		</view>
		
		<!-- 胶囊展示区域 -->
		<scroll-view class="capsule-container" scroll-y>
			<view class="welcome-text">
				<text class="title">{{ isGuest ? '欢迎体验' : '欢迎回来' }}</text>
				<text class="subtitle">{{ isGuest ? '登录后可以创建专属时空胶囊' : '你的时空胶囊正在等待解锁' }}</text>
			</view>
			
			<!-- 游客提示 -->
			<view class="guest-hint" v-if="isGuest" @click="goToLogin">
				<text class="guest-hint-icon">👋</text>
				<text class="guest-hint-text">游客模式 · 点击登录解锁更多功能</text>
				<text class="guest-hint-arrow">→</text>
			</view>
			
			<!-- 胶囊列表 -->
			<view class="capsules-list">
				<view 
					v-for="capsule in displayCapsules" 
					:key="capsule.id"
					class="capsule-item"
					:class="{'unlocked': capsule.isUnlocked}"
					@click="handleCapsuleClick(capsule)">
					<view class="capsule-icon">
						<text>{{getCapsuleIcon(capsule.type)}}</text>
					</view>
					<view class="capsule-info">
						<text class="capsule-title">{{capsule.title || '未命名胶囊'}}</text>
						<text class="capsule-type">{{getCapsuleTypeName(capsule.type)}}</text>
						<view class="capsule-countdown" v-if="!capsule.isUnlocked">
							<countdown :target-date="capsule.unlockDate"></countdown>
						</view>
						<text class="capsule-status" v-else>已解锁</text>
					</view>
				</view>
			</view>
			
			<!-- 空状态 -->
			<view class="empty-state" v-if="displayCapsules.length === 0">
				<text class="empty-icon">🌌</text>
				<text class="empty-text">还没有胶囊，创建第一个吧</text>
			</view>
		</scroll-view>
		
		<!-- 创建按钮 -->
		<view class="fab" @click="goToCreate">
			<text class="fab-icon">+</text>
		</view>
	</view>
</template>

<script>
	import api from '../../utils/api.js'
	import storage from '../../utils/storage.js'
	import dateUtil from '../../utils/date.js'
	import countdown from '../../components/countdown/countdown.vue'
	
	export default {
		components: {
			countdown
		},
		data() {
			return {
				stars: [],
				capsules: [],
				isGuest: false,
				// 游客演示数据
				demoCapsules: [
					{
						id: 'demo-1',
						title: '新年愿望',
						type: 'target',
						unlock_date: '2026-12-31T23:59:59',
						is_unlocked: false
					},
					{
						id: 'demo-2',
						title: '给未来的自己',
						type: 'emotion',
						unlock_date: '2026-06-01T00:00:00',
						is_unlocked: false
					},
					{
						id: 'demo-3',
						title: '感谢生命中的美好',
						type: 'gratitude',
						unlock_date: '2025-01-01T00:00:00',
						is_unlocked: true
					}
				]
			}
		},
		computed: {
			displayCapsules() {
				// 确保capsules是数组
				if (!Array.isArray(this.capsules)) {
					return []
				}
				return this.capsules.map(capsule => {
					return {
						...capsule,
						unlockDate: capsule.unlock_date,
						isUnlocked: capsule.is_unlocked || dateUtil.isUnlocked(capsule.unlock_date)
					}
				}).sort((a, b) => {
					// 未解锁的排在前面
					if (a.isUnlocked !== b.isUnlocked) {
						return a.isUnlocked ? 1 : -1
					}
					// 日期排序，处理无效日期
					const dateA = a.unlockDate ? new Date(a.unlockDate).getTime() : 0
					const dateB = b.unlockDate ? new Date(b.unlockDate).getTime() : 0
					if (isNaN(dateA) || isNaN(dateB)) {
						return 0
					}
					return dateA - dateB
				})
			}
		},
		onLoad() {
			this.initStars()
			this.checkGuestMode()
			this.loadCapsules()
		},
		onShow() {
			this.checkGuestMode()
			this.loadCapsules()
		},
		methods: {
			// 检查是否游客模式
			checkGuestMode() {
				this.isGuest = storage.isGuest()
			},
			
			// 初始化星空
			initStars() {
				const stars = []
				for (let i = 0; i < 100; i++) {
					stars.push({
						x: Math.random() * 100,
						y: Math.random() * 100,
						delay: Math.random() * 3
					})
				}
				this.stars = stars
			},
			
			// 加载胶囊
			async loadCapsules() {
				// 游客模式：显示演示数据
				if (this.isGuest) {
					this.capsules = this.demoCapsules
					return
				}
				
				try {
					const capsules = await api.getCapsules()
					this.capsules = capsules
				} catch (error) {
					console.error('加载胶囊失败:', error)
					// 如果加载失败，显示演示数据
					if (storage.isGuest()) {
						this.capsules = this.demoCapsules
					} else {
						this.capsules = []
					}
				}
			},
			
			// 获取胶囊图标
			getCapsuleIcon(type) {
				const icons = {
					'target': '🎯',
					'emotion': '💭',
					'gratitude': '🙏',
					'share': '🔗'
				}
				return icons[type] || '📦'
			},
			
			// 获取胶囊类型名称
			getCapsuleTypeName(type) {
				const names = {
					'target': '目标胶囊',
					'emotion': '心境胶囊',
					'gratitude': '感恩胶囊',
					'share': '共享胶囊'
				}
				return names[type] || '普通胶囊'
			},
			
			// 处理胶囊点击
			handleCapsuleClick(capsule) {
				// 游客模式：显示登录提示
				if (this.isGuest) {
					storage.requireLogin('查看胶囊详情')
					return
				}
				
				if (capsule.isUnlocked) {
					uni.navigateTo({
						url: `/pages/review/review?id=${capsule.id}`
					})
				} else {
					uni.navigateTo({
						url: `/pages/unlock/unlock?id=${capsule.id}`
					})
				}
			},
			
			// 跳转到创建页面
			goToCreate() {
				// 游客模式：显示登录提示
				if (this.isGuest) {
					storage.requireLogin('创建胶囊')
					return
				}
				
				uni.navigateTo({
					url: '/pages/create/create'
				})
			},
			
			// 跳转到个人中心
			goToProfile() {
				uni.navigateTo({
					url: '/pages/profile/profile'
				})
			},
			
			// 跳转到登录页
			goToLogin() {
				uni.navigateTo({
					url: '/pages/login/login'
				})
			}
		}
	}
</script>

<style scoped>
	.star-field {
		width: 100%;
		height: 100vh;
		background: linear-gradient(180deg, #0f0f1e 0%, #1a1a2e 50%, #16213e 100%);
		position: relative;
		overflow: hidden;
	}
	
	.stars {
		position: absolute;
		width: 2rpx;
		height: 2rpx;
		background: #fff;
		border-radius: 50%;
		animation: twinkle 3s infinite;
	}
	
	@keyframes twinkle {
		0%, 100% { opacity: 0.3; }
		50% { opacity: 1; }
	}
	
	.nav-bar {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 60rpx 40rpx 30rpx;
		position: relative;
		z-index: 10;
	}
	
	.nav-title {
		font-size: 48rpx;
		font-weight: bold;
		color: #fff;
		text-shadow: 0 0 20rpx rgba(108, 92, 231, 0.5);
	}
	
	.nav-icon {
		width: 60rpx;
		height: 60rpx;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 40rpx;
	}
	
	.capsule-container {
		height: calc(100vh - 200rpx);
		padding: 0 40rpx;
	}
	
	.welcome-text {
		text-align: center;
		margin: 40rpx 0 60rpx;
	}
	
	.title {
		display: block;
		font-size: 56rpx;
		font-weight: bold;
		color: #fff;
		margin-bottom: 20rpx;
	}
	
	.subtitle {
		display: block;
		font-size: 28rpx;
		color: rgba(255, 255, 255, 0.6);
	}
	
	.capsules-list {
		margin-bottom: 200rpx;
	}
	
	.capsule-item {
		background: rgba(255, 255, 255, 0.05);
		border-radius: 24rpx;
		padding: 30rpx;
		margin-bottom: 30rpx;
		display: flex;
		align-items: center;
		backdrop-filter: blur(10rpx);
		border: 1rpx solid rgba(255, 255, 255, 0.1);
		transition: all 0.3s;
	}
	
	.capsule-item:active {
		transform: scale(0.98);
		background: rgba(255, 255, 255, 0.1);
	}
	
	.capsule-item.unlocked {
		border-color: rgba(108, 92, 231, 0.5);
		box-shadow: 0 0 20rpx rgba(108, 92, 231, 0.3);
	}
	
	.capsule-icon {
		width: 100rpx;
		height: 100rpx;
		background: rgba(108, 92, 231, 0.2);
		border-radius: 50%;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 50rpx;
		margin-right: 30rpx;
	}
	
	.capsule-info {
		flex: 1;
		display: flex;
		flex-direction: column;
	}
	
	.capsule-title {
		font-size: 32rpx;
		color: #fff;
		font-weight: 500;
		margin-bottom: 10rpx;
	}
	
	.capsule-type {
		font-size: 24rpx;
		color: rgba(255, 255, 255, 0.6);
		margin-bottom: 10rpx;
	}
	
	.capsule-countdown {
		font-size: 24rpx;
		color: rgba(108, 92, 231, 1);
	}
	
	.capsule-status {
		font-size: 24rpx;
		color: #4ade80;
	}
	
	.empty-state {
		text-align: center;
		padding: 200rpx 0;
	}
	
	.empty-icon {
		font-size: 120rpx;
		display: block;
		margin-bottom: 40rpx;
	}
	
	.empty-text {
		font-size: 28rpx;
		color: rgba(255, 255, 255, 0.5);
	}
	
	.fab {
		position: fixed;
		right: 40rpx;
		bottom: 120rpx;
		width: 120rpx;
		height: 120rpx;
		background: linear-gradient(135deg, #6c5ce7 0%, #a29bfe 100%);
		border-radius: 50%;
		display: flex;
		align-items: center;
		justify-content: center;
		box-shadow: 0 8rpx 30rpx rgba(108, 92, 231, 0.4);
		z-index: 100;
	}
	
	.fab-icon {
		font-size: 60rpx;
		color: #fff;
		font-weight: 300;
	}
	
	/* 游客提示样式 */
	.guest-hint {
		display: flex;
		align-items: center;
		justify-content: center;
		background: linear-gradient(135deg, rgba(108, 92, 231, 0.3) 0%, rgba(162, 155, 254, 0.2) 100%);
		border-radius: 20rpx;
		padding: 24rpx 32rpx;
		margin-bottom: 40rpx;
		border: 1rpx solid rgba(108, 92, 231, 0.4);
	}
	
	.guest-hint-icon {
		font-size: 36rpx;
		margin-right: 16rpx;
	}
	
	.guest-hint-text {
		font-size: 26rpx;
		color: rgba(255, 255, 255, 0.9);
		flex: 1;
	}
	
	.guest-hint-arrow {
		font-size: 28rpx;
		color: #a29bfe;
	}
</style>
