<template>
	<view class="settings-page">
		<view class="page-header">
			<text class="back-btn" @click="goBack">←</text>
			<text class="page-title">设置</text>
		</view>
		
		<scroll-view class="settings-list" scroll-y>
			<view class="settings-section">
				<text class="section-title">账户设置</text>
				<view class="setting-item" @click="editNickname">
					<text class="setting-label">昵称</text>
					<text class="setting-value">{{userInfo.nickname || '未设置'}}</text>
					<text class="setting-arrow">></text>
				</view>
				<view class="setting-item" @click="editAvatar">
					<text class="setting-label">头像</text>
					<text class="setting-value">点击更换</text>
					<text class="setting-arrow">></text>
				</view>
			</view>
			
			<view class="settings-section">
				<text class="section-title">隐私设置</text>
				<view class="setting-item">
					<text class="setting-label">数据加密</text>
					<switch :checked="settings.encryption" @change="onEncryptionChange" color="#6c5ce7"/>
				</view>
				<view class="setting-item">
					<text class="setting-label">云同步</text>
					<switch :checked="settings.cloudSync" @change="onCloudSyncChange" color="#6c5ce7"/>
				</view>
			</view>
			
			<view class="settings-section">
				<text class="section-title">通知设置</text>
				<view class="setting-item">
					<text class="setting-label">解锁提醒</text>
					<switch :checked="settings.unlockReminder" @change="onUnlockReminderChange" color="#6c5ce7"/>
				</view>
				<view class="setting-item">
					<text class="setting-label">情绪打卡提醒</text>
					<switch :checked="settings.emotionReminder" @change="onEmotionReminderChange" color="#6c5ce7"/>
				</view>
			</view>
			
			<view class="settings-section">
				<text class="section-title">其他</text>
				<view class="setting-item" @click="handleAbout">
					<text class="setting-label">关于我们</text>
					<text class="setting-arrow">></text>
				</view>
				<view class="setting-item" @click="handleFeedback">
					<text class="setting-label">意见反馈</text>
					<text class="setting-arrow">></text>
				</view>
				<view class="setting-item" @click="handleClearCache">
					<text class="setting-label">清除缓存</text>
					<text class="setting-arrow">></text>
				</view>
			</view>
		</scroll-view>
	</view>
</template>

<script>
	import storage from '../../utils/storage.js'
	import api, { BASE_URL } from '../../utils/api.js'
	
	export default {
		data() {
			return {
				userInfo: {},
				settings: {
					encryption: true,
					cloudSync: false,
					unlockReminder: true,
					emotionReminder: true
				}
			}
		},
		onLoad() {
			this.loadUserInfo()
			this.loadSettings()
		},
		onShow() {
			this.loadUserInfo()
		},
		methods: {
			async loadUserInfo() {
				// 先从本地加载
				this.userInfo = storage.getUserInfo()
				
				// 从服务器获取最新信息
				try {
					const userInfo = await api.getCurrentUser()
					// 处理头像URL，确保是完整URL
					let avatarUrl = ''
					if (userInfo.avatar) {
						if (userInfo.avatar.startsWith('http')) {
							avatarUrl = userInfo.avatar
						} else {
							avatarUrl = BASE_URL + '/uploads/' + userInfo.avatar
						}
					}
					
					this.userInfo = {
						id: userInfo.id,
						nickname: userInfo.nickname,
						avatar: avatarUrl,
						email: userInfo.email || '',
						phone: userInfo.phone || ''
					}
				} catch (error) {
					console.error('获取用户信息失败:', error)
				}
			},
			
			loadSettings() {
				const saved = uni.getStorageSync('settings')
				if (saved) {
					this.settings = { ...this.settings, ...saved }
				}
			},
			
			saveSettings() {
				uni.setStorageSync('settings', this.settings)
			},
			
			editNickname() {
				uni.showModal({
					title: '修改昵称',
					editable: true,
					placeholderText: '请输入新昵称',
					success: async (res) => {
						if (res.confirm && res.content) {
							const newNickname = res.content.trim()
							if (!newNickname) {
								uni.showToast({
									title: '昵称不能为空',
									icon: 'none'
								})
								return
							}
							
							uni.showLoading({
								title: '更新中...'
							})
							
							try {
								await api.updateProfile({
									nickname: newNickname
								})
								uni.hideLoading()
								uni.showToast({
									title: '修改成功',
									icon: 'success'
								})
								// 重新加载用户信息
								await this.loadUserInfo()
							} catch (error) {
								uni.hideLoading()
								uni.showToast({
									title: error.message || '修改失败',
									icon: 'none',
									duration: 2000
								})
							}
						}
					}
				})
			},
			
			editAvatar() {
				uni.chooseImage({
					count: 1,
					sourceType: ['album', 'camera'],
					success: async (res) => {
						const tempFilePath = res.tempFilePaths[0]
						
						uni.showLoading({
							title: '上传中...'
						})
						
						try {
							const result = await api.uploadAvatar(tempFilePath)
							uni.hideLoading()
							
							if (result.avatarUrl) {
								// 更新本地头像URL
								this.userInfo.avatar = result.avatarUrl
								storage.setUserInfo(this.userInfo)
							}
							
							uni.showToast({
								title: result.message || '头像已更新',
								icon: 'success'
							})
							
							// 重新加载用户信息
							await this.loadUserInfo()
						} catch (error) {
							uni.hideLoading()
							uni.showToast({
								title: error.message || '上传失败',
								icon: 'none',
								duration: 2000
							})
						}
					},
					fail: (err) => {
						console.error('选择图片失败:', err)
					}
				})
			},
			
			onEncryptionChange(e) {
				this.settings.encryption = e.detail.value
				this.saveSettings()
			},
			
			onCloudSyncChange(e) {
				this.settings.cloudSync = e.detail.value
				this.saveSettings()
				if (e.detail.value) {
					uni.showToast({
						title: '云同步已开启',
						icon: 'success'
					})
				}
			},
			
			onUnlockReminderChange(e) {
				this.settings.unlockReminder = e.detail.value
				this.saveSettings()
			},
			
			onEmotionReminderChange(e) {
				this.settings.emotionReminder = e.detail.value
				this.saveSettings()
			},
			
			handleAbout() {
				uni.showModal({
					title: '关于时空胶囊',
					content: '时空胶囊 v1.0.0\n记录时光，遇见未来',
					showCancel: false
				})
			},
			
			handleFeedback() {
				uni.showToast({
					title: '反馈功能开发中',
					icon: 'none'
				})
			},
			
			handleClearCache() {
				uni.showModal({
					title: '提示',
					content: '确定要清除缓存吗？',
					success: (res) => {
						if (res.confirm) {
							// 清除缓存逻辑
							uni.showToast({
								title: '缓存已清除',
								icon: 'success'
							})
						}
					}
				})
			},
			
			getAvatarUrl() {
				if (this.userInfo.avatar) {
					if (this.userInfo.avatar.startsWith('http')) {
						return this.userInfo.avatar
					}
					// 如果是相对路径，拼接BASE_URL
					return BASE_URL + '/uploads/' + this.userInfo.avatar
				}
				return ''
			},
			
			editEmail() {
				uni.showModal({
					title: '修改邮箱',
					editable: true,
					placeholderText: '请输入邮箱',
					success: async (res) => {
						if (res.confirm) {
							const newEmail = res.content ? res.content.trim() : ''
							
							uni.showLoading({
								title: '更新中...'
							})
							
							try {
								await api.updateProfile({
									email: newEmail || null
								})
								uni.hideLoading()
								uni.showToast({
									title: '修改成功',
									icon: 'success'
								})
								// 重新加载用户信息
								await this.loadUserInfo()
							} catch (error) {
								uni.hideLoading()
								uni.showToast({
									title: error.message || '修改失败',
									icon: 'none',
									duration: 2000
								})
							}
						}
					}
				})
			},
			
			goBack() {
				uni.navigateBack()
			}
		}
	}
</script>

<style scoped>
	.settings-page {
		width: 100%;
		min-height: 100vh;
		background: linear-gradient(180deg, #0f0f1e 0%, #1a1a2e 100%);
	}
	
	.page-header {
		display: flex;
		align-items: center;
		padding: 60rpx 40rpx 30rpx;
	}
	
	.back-btn {
		font-size: 48rpx;
		color: #fff;
		margin-right: 30rpx;
	}
	
	.page-title {
		font-size: 40rpx;
		font-weight: bold;
		color: #fff;
	}
	
	.settings-list {
		height: calc(100vh - 200rpx);
		padding: 0 40rpx;
	}
	
	.settings-section {
		margin-bottom: 60rpx;
	}
	
	.section-title {
		display: block;
		font-size: 28rpx;
		color: rgba(255, 255, 255, 0.6);
		margin-bottom: 20rpx;
	}
	
	.setting-item {
		background: rgba(255, 255, 255, 0.05);
		border-radius: 20rpx;
		padding: 30rpx;
		margin-bottom: 20rpx;
		display: flex;
		align-items: center;
		backdrop-filter: blur(10rpx);
		border: 1rpx solid rgba(255, 255, 255, 0.1);
	}
	
	.setting-label {
		flex: 1;
		font-size: 32rpx;
		color: #fff;
	}
	
	.setting-value {
		font-size: 28rpx;
		color: rgba(255, 255, 255, 0.6);
		margin-right: 20rpx;
	}
	
	.setting-arrow {
		font-size: 32rpx;
		color: rgba(255, 255, 255, 0.4);
	}
	
	.avatar-preview {
		margin-right: 20rpx;
	}
	
	.avatar-thumb {
		width: 60rpx;
		height: 60rpx;
		border-radius: 50%;
	}
</style>

