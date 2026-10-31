<template>
	<view class="profile-page">
		<view class="profile-header">
			<view class="avatar-section">
				<image 
					class="avatar" 
					:src="getAvatarUrl()" 
					mode="aspectFill"
					@click="isGuest ? goToLogin() : goToSettings()"
				></image>
				<text class="nickname">{{isGuest ? '游客用户' : (userInfo.nickname || '用户')}}</text>
				<text class="guest-badge" v-if="isGuest">点击头像登录</text>
				<text class="email" v-else-if="userInfo.email">{{userInfo.email}}</text>
				<text class="phone" v-else-if="userInfo.phone">{{userInfo.phone}}</text>
			</view>
		</view>
		
		<!-- 游客登录提示 -->
		<view class="login-prompt" v-if="isGuest">
			<view class="login-card" @click="goToLogin">
				<text class="login-icon">🔓</text>
				<view class="login-text">
					<text class="login-title">登录账号</text>
					<text class="login-desc">登录后可使用完整功能</text>
				</view>
				<text class="login-arrow">→</text>
			</view>
			<view class="login-card" @click="goToRegister">
				<text class="login-icon">✨</text>
				<view class="login-text">
					<text class="login-title">注册账号</text>
					<text class="login-desc">创建专属时空胶囊</text>
				</view>
				<text class="login-arrow">→</text>
			</view>
		</view>
		
		<view class="menu-list">
			<view class="menu-item" @click="handleMenuClick('settings')">
				<text class="menu-icon">⚙️</text>
				<text class="menu-label">设置</text>
				<text class="menu-arrow">></text>
			</view>
			<view class="menu-item" @click="handleMenuClick('emotion')">
				<text class="menu-icon">📅</text>
				<text class="menu-label">情绪日历</text>
				<text class="menu-arrow">></text>
			</view>
			<view class="menu-item" @click="handleMenuClick('share')">
				<text class="menu-icon">🔗</text>
				<text class="menu-label">共享胶囊</text>
				<text class="menu-arrow">></text>
			</view>
			<view class="menu-item" @click="handleMenuClick('backup')">
				<text class="menu-icon">☁️</text>
				<text class="menu-label">数据备份</text>
				<text class="menu-arrow">></text>
			</view>
			<view class="menu-item" @click="handleMenuClick('restore')">
				<text class="menu-icon">📥</text>
				<text class="menu-label">数据恢复</text>
				<text class="menu-arrow">></text>
			</view>
		</view>
		
		<view class="logout-section" v-if="!isGuest">
			<button class="btn-logout" @click="handleLogout">退出登录</button>
		</view>
	</view>
</template>

<script>
	import storage from '../../utils/storage.js'
	import api, { BASE_URL } from '../../utils/api.js'
	
	export default {
		data() {
			return {
				userInfo: {},
				isGuest: false
			}
		},
		onLoad() {
			this.checkGuestMode()
			this.loadUserInfo()
		},
		onShow() {
			this.checkGuestMode()
			this.loadUserInfo()
		},
		methods: {
			checkGuestMode() {
				this.isGuest = storage.isGuest()
			},
			
			async loadUserInfo() {
				// 游客模式不加载用户信息
				if (this.isGuest) {
					this.userInfo = {}
					return
				}
				
				// 先从本地加载，显示更快
				this.userInfo = storage.getUserInfo()
				
				// 然后从服务器获取最新信息
				try {
					const userInfo = await api.getCurrentUser()
					this.userInfo = {
						id: userInfo.id,
						nickname: userInfo.nickname,
						avatar: userInfo.avatar ? (userInfo.avatar.startsWith('http') ? userInfo.avatar : BASE_URL + '/uploads/' + userInfo.avatar) : '',
						email: userInfo.email || '',
						phone: userInfo.phone || ''
					}
				} catch (error) {
					console.error('获取用户信息失败:', error)
					// 如果获取失败，使用本地缓存
				}
			},
			
			// 跳转到登录页
			goToLogin() {
				uni.navigateTo({
					url: '/pages/login/login'
				})
			},
			
			// 跳转到注册页
			goToRegister() {
				uni.navigateTo({
					url: '/pages/register/register'
				})
			},
			
			// 处理菜单点击
			handleMenuClick(menu) {
				// 游客模式需要登录
				if (this.isGuest) {
					storage.requireLogin('该功能')
					return
				}
				
				switch(menu) {
					case 'settings':
						this.goToSettings()
						break
					case 'emotion':
						this.goToEmotionCalendar()
						break
					case 'share':
						this.goToShare()
						break
					case 'backup':
						this.handleBackup()
						break
					case 'restore':
						this.handleRestore()
						break
				}
			},
			
			goToSettings() {
				uni.navigateTo({
					url: '/pages/settings/settings'
				})
			},
			
			goToEmotionCalendar() {
				uni.navigateTo({
					url: '/pages/emotion-calendar/emotion-calendar'
				})
			},
			
			goToShare() {
				uni.navigateTo({
					url: '/pages/share/share'
				})
			},
			
			handleBackup() {
				uni.showToast({
					title: '备份功能开发中',
					icon: 'none'
				})
			},
			
			handleRestore() {
				uni.showToast({
					title: '恢复功能开发中',
					icon: 'none'
				})
			},
			
			getAvatarUrl() {
				if (this.userInfo.avatar) {
					// 如果是完整URL，直接返回
					if (this.userInfo.avatar.startsWith('http')) {
						return this.userInfo.avatar
					}
					// 如果是相对路径，拼接BASE_URL
					return BASE_URL + '/uploads/' + this.userInfo.avatar
				}
				return '/static/default-avatar.png'
			},
			
			handleLogout() {
				uni.showModal({
					title: '提示',
					content: '确定要退出登录吗？',
					success: (res) => {
						if (res.confirm) {
							storage.removeToken()
							storage.clearAll()
							uni.reLaunch({
								url: '/pages/login/login'
							})
						}
					}
				})
			}
		}
	}
</script>

<style scoped>
	.profile-page {
		width: 100%;
		min-height: 100vh;
		background: linear-gradient(180deg, #0f0f1e 0%, #1a1a2e 100%);
	}
	
	.profile-header {
		padding: 80rpx 40rpx 60rpx;
		text-align: center;
	}
	
	.avatar-section {
		display: flex;
		flex-direction: column;
		align-items: center;
	}
	
	.avatar {
		width: 160rpx;
		height: 160rpx;
		border-radius: 50%;
		background: rgba(255, 255, 255, 0.1);
		margin-bottom: 30rpx;
		border: 4rpx solid rgba(108, 92, 231, 0.5);
	}
	
	.nickname {
		font-size: 40rpx;
		font-weight: bold;
		color: #fff;
		margin-bottom: 10rpx;
	}
	
	.email {
		font-size: 26rpx;
		color: rgba(255, 255, 255, 0.6);
	}
	
	.menu-list {
		padding: 0 40rpx;
	}
	
	.menu-item {
		background: rgba(255, 255, 255, 0.05);
		border-radius: 20rpx;
		padding: 30rpx;
		margin-bottom: 20rpx;
		display: flex;
		align-items: center;
		backdrop-filter: blur(10rpx);
		border: 1rpx solid rgba(255, 255, 255, 0.1);
	}
	
	.menu-icon {
		font-size: 40rpx;
		margin-right: 30rpx;
	}
	
	.menu-label {
		flex: 1;
		font-size: 32rpx;
		color: #fff;
	}
	
	.menu-arrow {
		font-size: 32rpx;
		color: rgba(255, 255, 255, 0.4);
	}
	
	.logout-section {
		padding: 60rpx 40rpx;
	}
	
	.btn-logout {
		width: 100%;
		background: rgba(255, 59, 48, 0.2);
		color: #ff3b30;
		border-radius: 50rpx;
		padding: 24rpx;
		font-size: 32rpx;
		border: 1rpx solid rgba(255, 59, 48, 0.3);
	}
	
	/* 游客样式 */
	.guest-badge {
		font-size: 24rpx;
		color: #a29bfe;
		margin-top: 10rpx;
	}
	
	.login-prompt {
		padding: 0 40rpx 40rpx;
	}
	
	.login-card {
		display: flex;
		align-items: center;
		background: linear-gradient(135deg, rgba(108, 92, 231, 0.3) 0%, rgba(162, 155, 254, 0.2) 100%);
		border-radius: 20rpx;
		padding: 30rpx;
		margin-bottom: 20rpx;
		border: 1rpx solid rgba(108, 92, 231, 0.4);
	}
	
	.login-icon {
		font-size: 48rpx;
		margin-right: 24rpx;
	}
	
	.login-text {
		flex: 1;
		display: flex;
		flex-direction: column;
	}
	
	.login-title {
		font-size: 32rpx;
		color: #fff;
		font-weight: 500;
		margin-bottom: 8rpx;
	}
	
	.login-desc {
		font-size: 24rpx;
		color: rgba(255, 255, 255, 0.6);
	}
	
	.login-arrow {
		font-size: 32rpx;
		color: #a29bfe;
	}
	
	.phone {
		font-size: 26rpx;
		color: rgba(255, 255, 255, 0.6);
	}
</style>

