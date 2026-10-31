<template>
	<view class="capsule-list-page">
		<view class="page-header">
			<text class="page-title">我的胶囊</text>
			<view class="filter-tabs">
				<text 
					v-for="tab in tabs" 
					:key="tab.value"
					class="tab-item"
					:class="{'active': currentTab === tab.value}"
					@click="switchTab(tab.value)">
					{{tab.label}}
				</text>
			</view>
		</view>
		
		<scroll-view class="list-container" scroll-y>
			<view class="capsule-item" 
				v-for="capsule in filteredCapsules" 
				:key="capsule.id"
				@click="handleCapsuleClick(capsule)">
				<view class="capsule-icon">
					<text>{{getCapsuleIcon(capsule.type)}}</text>
				</view>
				<view class="capsule-info">
					<text class="capsule-title">{{capsule.title || '未命名胶囊'}}</text>
					<text class="capsule-meta">
						{{getCapsuleTypeName(capsule.type)}} · {{formatDate(capsule.createDate)}}
					</text>
					<view class="capsule-status">
						<text v-if="capsule.isUnlocked" class="status-unlocked">已解锁</text>
						<view v-else class="countdown-wrapper">
							<countdown :target-date="capsule.unlockDate"></countdown>
						</view>
					</view>
				</view>
				<text class="arrow">></text>
			</view>
			
			<view class="empty-state" v-if="filteredCapsules.length === 0">
				<text class="empty-icon">📦</text>
				<text class="empty-text">还没有胶囊</text>
			</view>
		</scroll-view>
		
		<view class="fab" @click="goToCreate">
			<text class="fab-icon">+</text>
		</view>
	</view>
</template>

<script>
	import api from '../../utils/api.js'
	import dateUtil from '../../utils/date.js'
	import countdown from '../../components/countdown/countdown.vue'
	
	export default {
		components: {
			countdown
		},
		data() {
			return {
				currentTab: 'all',
				tabs: [
					{ value: 'all', label: '全部' },
					{ value: 'locked', label: '待解锁' },
					{ value: 'unlocked', label: '已解锁' }
				],
				capsules: []
			}
		},
		computed: {
			filteredCapsules() {
				// 确保capsules是数组
				if (!Array.isArray(this.capsules)) {
					return []
				}
				const now = new Date().getTime()
				return this.capsules.map(capsule => {
					// 安全处理日期
					const unlockDate = capsule.unlock_date ? new Date(capsule.unlock_date).getTime() : 0
					const isUnlocked = capsule.is_unlocked || (!isNaN(unlockDate) && unlockDate <= now)
					return {
						...capsule,
						unlockDate: capsule.unlock_date,
						createDate: capsule.created_at,
						isUnlocked: isUnlocked
					}
				}).filter(capsule => {
					if (this.currentTab === 'all') {
						return true
					} else if (this.currentTab === 'locked') {
						return !capsule.isUnlocked
					} else {
						return capsule.isUnlocked
					}
				}).sort((a, b) => {
					// 日期排序，处理无效日期
					const dateA = a.createDate ? new Date(a.createDate).getTime() : 0
					const dateB = b.createDate ? new Date(b.createDate).getTime() : 0
					if (isNaN(dateA) || isNaN(dateB)) {
						return 0
					}
					return dateB - dateA
				})
			}
		},
		onLoad() {
			this.loadCapsules()
		},
		onShow() {
			this.loadCapsules()
		},
		methods: {
			async loadCapsules() {
				try {
					const filter = this.currentTab === 'all' ? null : this.currentTab
					const capsules = await api.getCapsules(filter)
					this.capsules = capsules
				} catch (error) {
					console.error('加载胶囊失败:', error)
					this.capsules = []
				}
			},
			
			switchTab(tab) {
				this.currentTab = tab
				this.loadCapsules()
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
			
			getCapsuleTypeName(type) {
				const names = {
					'target': '目标胶囊',
					'emotion': '心境胶囊',
					'gratitude': '感恩胶囊',
					'share': '共享胶囊'
				}
				return names[type] || '普通胶囊'
			},
			
			formatDate(date) {
				return dateUtil.formatDate(date, 'YYYY-MM-DD')
			},
			
			handleCapsuleClick(capsule) {
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
			
			goToCreate() {
				uni.navigateTo({
					url: '/pages/create/create'
				})
			}
		}
	}
</script>

<style scoped>
	.capsule-list-page {
		width: 100%;
		min-height: 100vh;
		background: linear-gradient(180deg, #0f0f1e 0%, #1a1a2e 100%);
	}
	
	.page-header {
		padding: 60rpx 40rpx 30rpx;
	}
	
	.page-title {
		font-size: 48rpx;
		font-weight: bold;
		color: #fff;
		display: block;
		margin-bottom: 30rpx;
	}
	
	.filter-tabs {
		display: flex;
		gap: 20rpx;
	}
	
	.tab-item {
		padding: 12rpx 24rpx;
		border-radius: 30rpx;
		font-size: 26rpx;
		color: rgba(255, 255, 255, 0.6);
		background: rgba(255, 255, 255, 0.05);
	}
	
	.tab-item.active {
		background: rgba(108, 92, 231, 0.3);
		color: #fff;
	}
	
	.list-container {
		height: calc(100vh - 300rpx);
		padding: 0 40rpx;
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
	
	.capsule-meta {
		font-size: 24rpx;
		color: rgba(255, 255, 255, 0.6);
		margin-bottom: 10rpx;
	}
	
	.capsule-status {
		font-size: 24rpx;
	}
	
	.status-unlocked {
		color: #4ade80;
	}
	
	.countdown-wrapper {
		color: rgba(108, 92, 231, 1);
	}
	
	.arrow {
		font-size: 32rpx;
		color: rgba(255, 255, 255, 0.4);
		margin-left: 20rpx;
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
</style>

