<template>
	<view class="share-page">
		<view class="page-header">
			<text class="back-btn" @click="goBack">←</text>
			<text class="page-title">共享胶囊</text>
		</view>
		
		<view class="share-tabs">
			<text 
				class="tab-item"
				:class="{'active': currentTab === 'create'}"
				@click="switchTab('create')">
				创建共享
			</text>
			<text 
				class="tab-item"
				:class="{'active': currentTab === 'unlock'}"
				@click="switchTab('unlock')">
				解锁共享
			</text>
		</view>
		
		<!-- 创建共享 -->
		<view class="tab-content" v-if="currentTab === 'create'">
			<scroll-view class="content-scroll" scroll-y>
				<view class="section">
					<text class="section-title">选择要共享的胶囊</text>
					<view class="capsule-list">
						<view 
							v-for="capsule in shareableCapsules" 
							:key="capsule.id"
							class="capsule-item"
							:class="{'selected': selectedCapsule?.id === capsule.id}"
							@click="selectCapsule(capsule)">
							<text class="capsule-icon">{{getCapsuleIcon(capsule.type)}}</text>
							<view class="capsule-info">
								<text class="capsule-title">{{capsule.title || '未命名胶囊'}}</text>
								<text class="capsule-date">{{formatDate(capsule.created_at)}}</text>
							</view>
						</view>
					</view>
				</view>
				
				<view class="section" v-if="selectedCapsule">
					<text class="section-title">共享信息</text>
					<view class="share-code-box">
						<text class="code-label">共享密语</text>
						<view class="code-display">
							<text class="code-text">{{selectedCapsule.share_code || '未生成'}}</text>
							<text class="copy-btn" @click="copyCode">复制</text>
						</view>
					</view>
					<view class="share-link-box">
						<text class="link-label">分享链接</text>
						<view class="link-display">
							<text class="link-text">{{shareLink}}</text>
							<text class="copy-btn" @click="copyLink">复制</text>
						</view>
					</view>
				</view>
			</scroll-view>
		</view>
		
		<!-- 解锁共享 -->
		<view class="tab-content" v-if="currentTab === 'unlock'">
			<view class="unlock-form">
				<view class="input-group">
					<text class="input-label">输入共享密语</text>
					<input 
						class="input-field" 
						v-model="shareCode" 
						placeholder="请输入8位共享密语"
						placeholder-style="color: rgba(255,255,255,0.4)"
						maxlength="8"
					/>
				</view>
				<button class="btn-primary" @click="handleUnlockShare">解锁共享胶囊</button>
			</view>
		</view>
	</view>
</template>

<script>
	import api from '../../utils/api.js'
	import dateUtil from '../../utils/date.js'
	
	export default {
		data() {
			return {
				currentTab: 'create',
				capsules: [],
				selectedCapsule: null,
				shareCode: ''
			}
		},
		computed: {
			shareableCapsules() {
				return this.capsules.filter(c => c.type === 'share' || c.is_shared)
			},
			shareLink() {
				if (!this.selectedCapsule || !this.selectedCapsule.share_code) {
					return '请先选择胶囊'
				}
				return `https://timecapsule.app/share/${this.selectedCapsule.share_code}`
			}
		},
		onLoad() {
			this.loadCapsules()
		},
		methods: {
			async loadCapsules() {
				try {
					const capsules = await api.getCapsules()
					this.capsules = capsules
				} catch (error) {
					console.error('加载胶囊失败:', error)
					this.capsules = []
				}
			},
			
			switchTab(tab) {
				this.currentTab = tab
			},
			
			async selectCapsule(capsule) {
				this.selectedCapsule = capsule
				// 如果没有共享码，生成一个
				if (!capsule.share_code) {
					try {
						const res = await api.generateShareCode(capsule.id)
						// 如果后端返回了胶囊数据，直接使用
						if (res.capsule) {
							this.selectedCapsule = res.capsule
							// 更新列表中的胶囊
							const index = this.capsules.findIndex(c => c.id === capsule.id)
							if (index >= 0) {
								this.capsules[index] = res.capsule
							}
						} else {
							// 兼容旧版本：重新加载胶囊获取更新后的共享码
							const updated = await api.getCapsule(capsule.id)
							this.selectedCapsule = updated
							// 更新列表中的胶囊
							const index = this.capsules.findIndex(c => c.id === capsule.id)
							if (index >= 0) {
								this.capsules[index] = updated
							}
						}
					} catch (error) {
						uni.showToast({
							title: error.message || '生成共享码失败',
							icon: 'none'
						})
					}
				}
			},
			
			copyCode() {
				if (!this.selectedCapsule?.share_code) return
				// #ifdef H5
				navigator.clipboard.writeText(this.selectedCapsule.share_code)
				// #endif
				// #ifndef H5
				uni.setClipboardData({
					data: this.selectedCapsule.share_code,
					success: () => {
						uni.showToast({
							title: '已复制',
							icon: 'success'
						})
					}
				})
				// #endif
			},
			
			copyLink() {
				if (!this.shareLink || this.shareLink === '请先选择胶囊') return
				// #ifdef H5
				navigator.clipboard.writeText(this.shareLink)
				// #endif
				// #ifndef H5
				uni.setClipboardData({
					data: this.shareLink,
					success: () => {
						uni.showToast({
							title: '已复制',
							icon: 'success'
						})
					}
				})
				// #endif
			},
			
			async handleUnlockShare() {
				if (!this.shareCode || this.shareCode.length !== 8) {
					uni.showToast({
						title: '请输入8位共享密语',
						icon: 'none'
					})
					return
				}
				
				// 跳转到解锁页面
				uni.navigateTo({
					url: `/pages/share-unlock/share-unlock?code=${this.shareCode.toUpperCase()}`
				})
			},
			
			getCapsuleIcon(type) {
				const icons = {
					'target': '🎯',
					'emotion': '💭',
					'gratitude': '🙏',
					'share': '🔗'
				}
				return icons[type] || '📦'
			},
			
			formatDate(date) {
				return dateUtil.formatDate(date || new Date(), 'YYYY-MM-DD')
			},
			
			goBack() {
				uni.navigateBack()
			}
		}
	}
</script>

<style scoped>
	.share-page {
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
	
	.share-tabs {
		display: flex;
		padding: 0 40rpx;
		margin-bottom: 30rpx;
		gap: 20rpx;
	}
	
	.tab-item {
		flex: 1;
		text-align: center;
		padding: 20rpx;
		border-radius: 16rpx;
		font-size: 28rpx;
		color: rgba(255, 255, 255, 0.6);
		background: rgba(255, 255, 255, 0.05);
	}
	
	.tab-item.active {
		background: rgba(108, 92, 231, 0.3);
		color: #fff;
	}
	
	.tab-content {
		padding: 0 40rpx;
	}
	
	.content-scroll {
		height: calc(100vh - 300rpx);
	}
	
	.section {
		margin-bottom: 60rpx;
	}
	
	.section-title {
		display: block;
		font-size: 32rpx;
		font-weight: bold;
		color: #fff;
		margin-bottom: 30rpx;
	}
	
	.capsule-list {
		display: flex;
		flex-direction: column;
		gap: 20rpx;
	}
	
	.capsule-item {
		background: rgba(255, 255, 255, 0.05);
		border-radius: 20rpx;
		padding: 30rpx;
		display: flex;
		align-items: center;
		border: 2rpx solid transparent;
	}
	
	.capsule-item.selected {
		border-color: #6c5ce7;
		background: rgba(108, 92, 231, 0.2);
	}
	
	.capsule-icon {
		font-size: 60rpx;
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
		margin-bottom: 10rpx;
	}
	
	.capsule-date {
		font-size: 24rpx;
		color: rgba(255, 255, 255, 0.6);
	}
	
	.share-code-box,
	.share-link-box {
		background: rgba(255, 255, 255, 0.05);
		border-radius: 20rpx;
		padding: 30rpx;
		margin-bottom: 30rpx;
	}
	
	.code-label,
	.link-label {
		display: block;
		font-size: 28rpx;
		color: rgba(255, 255, 255, 0.6);
		margin-bottom: 20rpx;
	}
	
	.code-display,
	.link-display {
		display: flex;
		align-items: center;
		justify-content: space-between;
	}
	
	.code-text,
	.link-text {
		flex: 1;
		font-size: 32rpx;
		color: #fff;
		font-weight: bold;
		word-break: break-all;
		margin-right: 20rpx;
	}
	
	.copy-btn {
		padding: 12rpx 24rpx;
		background: rgba(108, 92, 231, 0.3);
		border-radius: 12rpx;
		font-size: 24rpx;
		color: #fff;
	}
	
	.unlock-form {
		padding: 60rpx 0;
	}
	
	.input-group {
		margin-bottom: 40rpx;
	}
	
	.input-label {
		color: rgba(255, 255, 255, 0.7);
		font-size: 28rpx;
		margin-bottom: 16rpx;
		display: block;
	}
	
	.input-field {
		background: rgba(255, 255, 255, 0.1);
		border-radius: 16rpx;
		padding: 24rpx;
		color: #fff;
		font-size: 32rpx;
		border: 1rpx solid rgba(255, 255, 255, 0.1);
		width: 100%;
		box-sizing: border-box;
		text-transform: uppercase;
	}
	
	.btn-primary {
		width: 100%;
		background: linear-gradient(135deg, #6c5ce7 0%, #a29bfe 100%);
		color: #fff;
		border-radius: 50rpx;
		padding: 24rpx;
		font-size: 32rpx;
		border: none;
		box-shadow: 0 8rpx 20rpx rgba(108, 92, 231, 0.3);
	}
</style>

