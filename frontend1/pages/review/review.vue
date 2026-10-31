<template>
	<view class="review-page">
		<view class="page-header">
			<text class="back-btn" @click="goBack">←</text>
			<text class="page-title">回顾胶囊</text>
		</view>
		
		<scroll-view class="review-container" scroll-y v-if="capsule">
			<!-- 胶囊内容 -->
			<view class="section">
				<view class="capsule-header">
					<text class="capsule-icon">{{getCapsuleIcon(capsule.type)}}</text>
					<view class="capsule-header-info">
						<text class="capsule-title">{{capsule.title || '未命名胶囊'}}</text>
						<text class="capsule-date">{{formatDate(capsule.createDate)}}</text>
					</view>
				</view>
				
				<view class="content-box">
					<text class="content-label">胶囊内容</text>
					<text class="content-text">{{decryptedContent}}</text>
				</view>
			</view>
			
			<!-- 目标胶囊回顾 -->
			<view class="section" v-if="capsule.type === 'target'">
				<text class="section-title">目标回顾</text>
				<view class="content-box" v-if="capsule.target">
					<text class="content-label">原定目标</text>
					<text class="content-text">{{decryptedTarget}}</text>
				</view>
				
				<view class="progress-section">
					<text class="progress-label">完成进度</text>
					<view class="progress-bar">
						<view class="progress-fill" :style="{width: (capsule.progress || 0) + '%'}"></view>
					</view>
					<view class="progress-input">
						<input 
							type="number" 
							v-model.number="progressValue" 
							class="progress-input-field"
							placeholder="0-100"
							max="100"
							min="0"
						/>
						<text class="progress-unit">%</text>
					</view>
				</view>
			</view>
			
			<!-- 心境胶囊回顾 -->
			<view class="section" v-if="capsule.type === 'emotion'">
				<text class="section-title">心境回顾</text>
				<view class="emotion-rating">
					<text class="emotion-label">当前情绪评分</text>
					<view class="emotion-emoji">
						<text 
							v-for="(emoji, index) in emotionEmojis" 
							:key="index"
							class="emoji-item"
							:class="{'active': emotionScore === index}"
							@click="selectEmotion(index)">
							{{emoji}}
						</text>
					</view>
					<text class="emotion-desc">{{getEmotionDesc(emotionScore)}}</text>
				</view>
			</view>
			
			<!-- 回顾记录 -->
			<view class="section">
				<text class="section-title">回顾与反思</text>
				<textarea 
					class="review-textarea" 
					v-model="reviewText" 
					placeholder="记录你的回顾与反思..."
					placeholder-style="color: rgba(255,255,255,0.4)"
					:maxlength="1000"
				></textarea>
				<text class="char-count">{{reviewText.length}}/1000</text>
			</view>
			
			<!-- 心理建议 -->
			<view class="section" v-if="capsule.type === 'emotion' && emotionScore !== null">
				<text class="section-title">心理健康建议</text>
				<view class="suggestion-box">
					<text class="suggestion-text">{{getSuggestion(emotionScore)}}</text>
				</view>
			</view>
		</scroll-view>
		
		<view class="footer-actions">
			<button class="btn-primary" @click="handleSave">保存回顾</button>
		</view>
	</view>
</template>

<script>
	import api from '../../utils/api.js'
	import dateUtil from '../../utils/date.js'
	
	export default {
		data() {
			return {
				capsule: null,
				reviewText: '',
				progressValue: 0,
				emotionScore: null,
				emotionEmojis: ['😢', '😔', '😐', '🙂', '😊'],
				saving: false
			}
		},
		computed: {
			decryptedContent() {
				if (!this.capsule) return ''
				return this.capsule.content
			},
			decryptedTarget() {
				if (!this.capsule || !this.capsule.target) return ''
				return this.capsule.target
			}
		},
		onLoad(options) {
			if (options.id) {
				this.loadCapsule(options.id)
			}
		},
		methods: {
			async loadCapsule(id) {
				try {
					const capsule = await api.getCapsule(id)
					this.capsule = {
						...capsule,
						createDate: capsule.created_at  // 统一字段名
					}
					
					// 加载已有数据
					this.reviewText = capsule.review || ''
					this.progressValue = capsule.progress || 0
					this.emotionScore = capsule.emotion_score !== null ? capsule.emotion_score : null
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
			
			selectEmotion(index) {
				this.emotionScore = index
			},
			
			getEmotionDesc(score) {
				if (score === null) return '请选择情绪'
				const descs = ['非常难过', '有点低落', '平静', '还不错', '非常开心']
				return descs[score] || ''
			},
			
			getSuggestion(score) {
				const suggestions = [
					'如果感到难过，可以尝试深呼吸、听音乐或与朋友聊天。记住，情绪是暂时的，一切都会好起来的。',
					'情绪低落时，可以尝试做一些轻松的活动，比如散步、阅读或冥想。给自己一些时间和空间。',
					'保持平静是很好的状态。可以继续关注当下，做一些让自己感到充实的事情。',
					'心情不错！继续保持这种积极的状态，可以尝试一些新的活动或挑战。',
					'太棒了！保持这种积极的心态，可以分享你的快乐给身边的人，让正能量传递下去。'
				]
				return suggestions[score] || ''
			},
			
			async handleSave() {
				if (this.saving) return
				
				this.saving = true
				uni.showLoading({ title: '保存中...' })
				
				try {
					const data = {
						review: this.reviewText
					}
					
					if (this.capsule.type === 'target') {
						data.progress = this.progressValue
					}
					
					if (this.capsule.type === 'emotion' && this.emotionScore !== null) {
						data.emotionScore = this.emotionScore
					}
					
					await api.saveReview(this.capsule.id, data)
					
					uni.hideLoading()
					uni.showToast({
						title: '保存成功',
						icon: 'success'
					})
					
					setTimeout(() => {
						uni.navigateBack()
					}, 1500)
				} catch (error) {
					uni.hideLoading()
					uni.showToast({
						title: error.message || '保存失败',
						icon: 'none'
					})
				} finally {
					this.saving = false
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
			
			formatDate(date) {
				return dateUtil.formatDate(date, 'YYYY-MM-DD HH:mm')
			},
			
			goBack() {
				uni.navigateBack()
			}
		}
	}
</script>

<style scoped>
	.review-page {
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
	
	.review-container {
		height: calc(100vh - 200rpx);
		padding: 0 40rpx;
	}
	
	.section {
		margin-bottom: 60rpx;
	}
	
	.capsule-header {
		display: flex;
		align-items: center;
		margin-bottom: 30rpx;
	}
	
	.capsule-icon {
		font-size: 80rpx;
		margin-right: 30rpx;
	}
	
	.capsule-header-info {
		flex: 1;
		display: flex;
		flex-direction: column;
	}
	
	.capsule-title {
		font-size: 36rpx;
		font-weight: bold;
		color: #fff;
		margin-bottom: 10rpx;
	}
	
	.capsule-date {
		font-size: 24rpx;
		color: rgba(255, 255, 255, 0.6);
	}
	
	.content-box {
		background: rgba(255, 255, 255, 0.05);
		border-radius: 20rpx;
		padding: 30rpx;
	}
	
	.content-label {
		display: block;
		font-size: 24rpx;
		color: rgba(255, 255, 255, 0.6);
		margin-bottom: 20rpx;
	}
	
	.content-text {
		display: block;
		font-size: 32rpx;
		color: #fff;
		line-height: 1.8;
		white-space: pre-wrap;
	}
	
	.section-title {
		display: block;
		font-size: 32rpx;
		font-weight: bold;
		color: #fff;
		margin-bottom: 30rpx;
	}
	
	.progress-section {
		background: rgba(255, 255, 255, 0.05);
		border-radius: 20rpx;
		padding: 30rpx;
	}
	
	.progress-label {
		display: block;
		font-size: 28rpx;
		color: #fff;
		margin-bottom: 20rpx;
	}
	
	.progress-bar {
		width: 100%;
		height: 16rpx;
		background: rgba(255, 255, 255, 0.1);
		border-radius: 8rpx;
		overflow: hidden;
		margin-bottom: 20rpx;
	}
	
	.progress-fill {
		height: 100%;
		background: linear-gradient(90deg, #6c5ce7 0%, #a29bfe 100%);
		transition: width 0.3s;
	}
	
	.progress-input {
		display: flex;
		align-items: center;
		gap: 10rpx;
	}
	
	.progress-input-field {
		background: rgba(255, 255, 255, 0.1);
		border-radius: 12rpx;
		padding: 16rpx;
		color: #fff;
		font-size: 28rpx;
		width: 150rpx;
	}
	
	.progress-unit {
		font-size: 28rpx;
		color: #fff;
	}
	
	.emotion-rating {
		background: rgba(255, 255, 255, 0.05);
		border-radius: 20rpx;
		padding: 30rpx;
		text-align: center;
	}
	
	.emotion-label {
		display: block;
		font-size: 28rpx;
		color: #fff;
		margin-bottom: 30rpx;
	}
	
	.emotion-emoji {
		display: flex;
		justify-content: space-around;
		margin-bottom: 20rpx;
	}
	
	.emoji-item {
		font-size: 80rpx;
		opacity: 0.5;
		transition: all 0.3s;
	}
	
	.emoji-item.active {
		opacity: 1;
		transform: scale(1.2);
	}
	
	.emotion-desc {
		display: block;
		font-size: 28rpx;
		color: rgba(255, 255, 255, 0.6);
	}
	
	.review-textarea {
		background: rgba(255, 255, 255, 0.05);
		border-radius: 20rpx;
		padding: 30rpx;
		color: #fff;
		font-size: 32rpx;
		width: 100%;
		min-height: 300rpx;
		box-sizing: border-box;
	}
	
	.char-count {
		display: block;
		text-align: right;
		color: rgba(255, 255, 255, 0.4);
		font-size: 24rpx;
		margin-top: 10rpx;
	}
	
	.suggestion-box {
		background: rgba(108, 92, 231, 0.2);
		border-radius: 20rpx;
		padding: 30rpx;
		border: 1rpx solid rgba(108, 92, 231, 0.3);
	}
	
	.suggestion-text {
		font-size: 28rpx;
		color: #fff;
		line-height: 1.8;
	}
	
	.footer-actions {
		padding: 30rpx 40rpx;
		position: fixed;
		bottom: 0;
		left: 0;
		right: 0;
		background: linear-gradient(180deg, transparent 0%, #1a1a2e 100%);
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

