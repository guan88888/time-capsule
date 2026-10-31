<template>
	<view class="achievement-page">
		<view class="page-header">
			<text class="page-title">成就中心</text>
		</view>
		
		<view class="achievement-stats">
			<view class="stat-card">
				<text class="stat-number">{{achievements.length}}</text>
				<text class="stat-label">已解锁成就</text>
			</view>
			<view class="stat-card">
				<text class="stat-number">{{totalAchievements}}</text>
				<text class="stat-label">总成就数</text>
			</view>
		</view>
		
		<scroll-view class="achievement-list" scroll-y>
			<view class="achievement-section">
				<text class="section-title">已解锁成就</text>
				<view class="achievement-grid">
					<view 
						v-for="achievement in achievements" 
						:key="achievement.id"
						class="achievement-item unlocked">
						<text class="achievement-icon">{{achievement.icon}}</text>
						<text class="achievement-title">{{achievement.title}}</text>
						<text class="achievement-desc">{{achievement.desc}}</text>
						<text class="achievement-date">{{formatDate(achievement.date)}}</text>
					</view>
				</view>
			</view>
			
			<view class="achievement-section">
				<text class="section-title">未解锁成就</text>
				<view class="achievement-grid">
					<view 
						v-for="achievement in lockedAchievements" 
						:key="achievement.id"
						class="achievement-item locked">
						<text class="achievement-icon">🔒</text>
						<text class="achievement-title">{{achievement.title}}</text>
						<text class="achievement-desc">{{achievement.desc}}</text>
					</view>
				</view>
			</view>
			
			<view class="empty-state" v-if="achievements.length === 0 && lockedAchievements.length === 0">
				<text class="empty-icon">🏆</text>
				<text class="empty-text">还没有成就</text>
			</view>
		</scroll-view>
	</view>
</template>

<script>
	import api from '../../utils/api.js'
	import dateUtil from '../../utils/date.js'
	
	export default {
		data() {
			return {
				allAchievements: []  // 从后端获取的完整成就列表
			}
		},
		computed: {
			achievements() {
				return this.allAchievements.filter(a => a.is_unlocked)
			},
			totalAchievements() {
				return this.allAchievements.length
			},
			lockedAchievements() {
				return this.allAchievements.filter(a => !a.is_unlocked)
			}
		},
		onLoad() {
			this.loadAchievements()
		},
		onShow() {
			this.loadAchievements()
		},
		methods: {
			async loadAchievements() {
				try {
					const achievements = await api.getAchievements()
					this.allAchievements = achievements.map(a => ({
						...a,
						desc: a.description,
						date: a.unlocked_at
					}))
				} catch (error) {
					console.error('加载成就失败:', error)
					this.allAchievements = []
				}
			},
			
			formatDate(date) {
				return date ? dateUtil.formatDate(date, 'YYYY-MM-DD') : ''
			}
		}
	}
</script>

<style scoped>
	.achievement-page {
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
	}
	
	.achievement-stats {
		display: flex;
		gap: 20rpx;
		padding: 0 40rpx;
		margin-bottom: 40rpx;
	}
	
	.stat-card {
		flex: 1;
		background: rgba(255, 255, 255, 0.05);
		border-radius: 20rpx;
		padding: 30rpx;
		text-align: center;
		backdrop-filter: blur(10rpx);
		border: 1rpx solid rgba(255, 255, 255, 0.1);
	}
	
	.stat-number {
		display: block;
		font-size: 48rpx;
		font-weight: bold;
		color: #6c5ce7;
		margin-bottom: 10rpx;
	}
	
	.stat-label {
		display: block;
		font-size: 24rpx;
		color: rgba(255, 255, 255, 0.6);
	}
	
	.achievement-list {
		height: calc(100vh - 400rpx);
		padding: 0 40rpx;
	}
	
	.achievement-section {
		margin-bottom: 60rpx;
	}
	
	.section-title {
		display: block;
		font-size: 32rpx;
		font-weight: bold;
		color: #fff;
		margin-bottom: 30rpx;
	}
	
	.achievement-grid {
		display: grid;
		grid-template-columns: repeat(2, 1fr);
		gap: 20rpx;
	}
	
	.achievement-item {
		background: rgba(255, 255, 255, 0.05);
		border-radius: 20rpx;
		padding: 30rpx;
		text-align: center;
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 10rpx;
		border: 2rpx solid transparent;
	}
	
	.achievement-item.unlocked {
		border-color: rgba(108, 92, 231, 0.5);
		background: rgba(108, 92, 231, 0.1);
	}
	
	.achievement-item.locked {
		opacity: 0.5;
	}
	
	.achievement-icon {
		font-size: 60rpx;
		margin-bottom: 10rpx;
	}
	
	.achievement-title {
		font-size: 28rpx;
		font-weight: bold;
		color: #fff;
	}
	
	.achievement-desc {
		font-size: 24rpx;
		color: rgba(255, 255, 255, 0.6);
	}
	
	.achievement-date {
		font-size: 22rpx;
		color: rgba(255, 255, 255, 0.4);
		margin-top: 10rpx;
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
</style>

