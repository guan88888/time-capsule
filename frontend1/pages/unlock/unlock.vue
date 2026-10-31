<template>
	<view class="unlock-page">
		<view class="stars-bg">
			<view class="star" v-for="(star, index) in stars" :key="index"
				:style="{left: star.x + '%', top: star.y + '%', animationDelay: star.delay + 's'}">
			</view>
		</view>
		
		<view class="unlock-content" v-if="capsule">
			<view class="capsule-display">
				<view class="capsule-icon-large">
					<text>{{getCapsuleIcon(capsule.type)}}</text>
				</view>
				<text class="capsule-title">{{capsule.title || '未命名胶囊'}}</text>
				<text class="capsule-type">{{getCapsuleTypeName(capsule.type)}}</text>
			</view>
			
			<view class="countdown-section">
				<text class="countdown-label">解锁倒计时</text>
				<countdown 
					:target-date="capsule.unlockDate" 
					@expired="onCountdownExpired">
				</countdown>
			</view>
			
			<view class="unlock-info">
				<view class="info-item">
					<text class="info-label">创建时间</text>
					<text class="info-value">{{formatDate(capsule.createDate)}}</text>
				</view>
				<view class="info-item">
					<text class="info-label">解锁时间</text>
					<text class="info-value">{{formatDate(capsule.unlockDate)}}</text>
				</view>
			</view>
			
			<button 
				class="btn-unlock" 
				:class="{'disabled': !canUnlock}"
				:disabled="!canUnlock"
				@click="handleUnlock">
				{{canUnlock ? '解锁胶囊' : '等待解锁时间'}}
			</button>
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
				stars: [],
				capsule: null,
				canUnlock: false,
				unlocking: false
			}
		},
		onLoad(options) {
			this.initStars()
			if (options.id) {
				this.loadCapsule(options.id)
			}
		},
		methods: {
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
			
			async loadCapsule(id) {
				try {
					const capsule = await api.getCapsule(id)
					// 如果胶囊已解锁，直接跳转到回顾页面
					if (capsule.is_unlocked) {
						uni.redirectTo({
							url: `/pages/review/review?id=${id}`
						})
						return
					}
					this.capsule = {
						...capsule,
						unlockDate: capsule.unlock_date,
						createDate: capsule.created_at
					}
					this.checkUnlockStatus()
				} catch (error) {
					uni.showToast({
						title: error.message || '胶囊不存在',
						icon: 'none'
					})
					setTimeout(() => {
						uni.navigateBack()
					}, 1500)
				}
			},
			
			checkUnlockStatus() {
				if (this.capsule) {
					this.canUnlock = dateUtil.isUnlocked(this.capsule.unlockDate)
				}
			},
			
			onCountdownExpired() {
				this.canUnlock = true
			},
			
			async handleUnlock() {
				if (!this.canUnlock || this.unlocking) {
					if (!this.canUnlock) {
						uni.showToast({
							title: '还未到解锁时间',
							icon: 'none'
						})
					}
					return
				}
				
				this.unlocking = true
				uni.showLoading({ title: '解锁中...' })
				
				try {
					await api.unlockCapsule(this.capsule.id)
					uni.hideLoading()
					
					// 跳转到回顾页面
					uni.redirectTo({
						url: `/pages/review/review?id=${this.capsule.id}`
					})
				} catch (error) {
					uni.hideLoading()
					uni.showToast({
						title: error.message || '解锁失败',
						icon: 'none'
					})
				} finally {
					this.unlocking = false
				}
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
				return dateUtil.formatDate(date, 'YYYY-MM-DD HH:mm')
			}
		}
	}
</script>

<style scoped>
	.unlock-page {
		width: 100%;
		min-height: 100vh;
		position: relative;
		overflow-y: auto;
		overflow-x: hidden;
	}
	
	.stars-bg {
		position: absolute;
		width: 100%;
		height: 100%;
		background: linear-gradient(180deg, #0f0f1e 0%, #1a1a2e 100%);
	}
	
	.star {
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
	
	.unlock-content {
		position: relative;
		z-index: 10;
		height: 100vh;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		padding: 60rpx;
	}
	
	.capsule-display {
		text-align: center;
		margin-bottom: 80rpx;
	}
	
	.capsule-icon-large {
		width: 200rpx;
		height: 200rpx;
		background: rgba(108, 92, 231, 0.3);
		border-radius: 50%;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 100rpx;
		margin: 0 auto 40rpx;
		box-shadow: 0 0 40rpx rgba(108, 92, 231, 0.5);
		animation: pulse 2s infinite;
	}
	
	@keyframes pulse {
		0%, 100% { transform: scale(1); }
		50% { transform: scale(1.05); }
	}
	
	.capsule-title {
		display: block;
		font-size: 48rpx;
		font-weight: bold;
		color: #fff;
		margin-bottom: 20rpx;
	}
	
	.capsule-type {
		display: block;
		font-size: 28rpx;
		color: rgba(255, 255, 255, 0.6);
	}
	
	.countdown-section {
		text-align: center;
		margin-bottom: 60rpx;
		background: rgba(255, 255, 255, 0.05);
		border-radius: 24rpx;
		padding: 40rpx;
		width: 100%;
		backdrop-filter: blur(10rpx);
	}
	
	.countdown-label {
		display: block;
		font-size: 28rpx;
		color: rgba(255, 255, 255, 0.7);
		margin-bottom: 20rpx;
	}
	
	.unlock-info {
		width: 100%;
		margin-bottom: 60rpx;
	}
	
	.info-item {
		display: flex;
		justify-content: space-between;
		padding: 24rpx;
		background: rgba(255, 255, 255, 0.05);
		border-radius: 16rpx;
		margin-bottom: 20rpx;
	}
	
	.info-label {
		font-size: 28rpx;
		color: rgba(255, 255, 255, 0.6);
	}
	
	.info-value {
		font-size: 28rpx;
		color: #fff;
	}
	
	.btn-unlock {
		width: 100%;
		background: linear-gradient(135deg, #6c5ce7 0%, #a29bfe 100%);
		color: #fff;
		border-radius: 50rpx;
		padding: 24rpx;
		font-size: 32rpx;
		border: none;
		box-shadow: 0 8rpx 20rpx rgba(108, 92, 231, 0.3);
	}
	
	.btn-unlock.disabled {
		background: rgba(255, 255, 255, 0.1);
		color: rgba(255, 255, 255, 0.4);
		box-shadow: none;
	}
</style>

