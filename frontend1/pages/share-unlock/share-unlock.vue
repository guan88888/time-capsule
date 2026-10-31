<template>
	<view class="share-unlock-page">
		<view class="page-header">
			<text class="back-btn" @click="goBack">←</text>
			<text class="page-title">解锁共享胶囊</text>
		</view>
		
		<view class="unlock-content" v-if="capsule">
			<view class="capsule-display">
				<text class="capsule-icon-large">{{getCapsuleIcon(capsule.type)}}</text>
				<text class="capsule-title">{{capsule.title || '未命名胶囊'}}</text>
				<text class="capsule-info">来自他人的共享胶囊</text>
			</view>
			
			<view class="unlock-section">
				<text class="unlock-label">胶囊内容</text>
				<view class="content-box">
					<text class="content-text">{{decryptedContent}}</text>
				</view>
			</view>
			
			<view class="interaction-section">
				<text class="section-title">互动</text>
				<view class="action-buttons">
					<view class="action-btn" @click="handleLike">
						<text class="action-icon">{{isLiked ? '❤️' : '🤍'}}</text>
						<text class="action-text">{{isLiked ? '已点赞' : '点赞'}}</text>
					</view>
					<view class="action-btn" @click="showComment">
						<text class="action-icon">💬</text>
						<text class="action-text">评论</text>
					</view>
				</view>
			</view>
		</view>
		
		<view class="empty-state" v-else>
			<text class="empty-icon">🔍</text>
			<text class="empty-text">未找到共享胶囊</text>
		</view>
	</view>
</template>

<script>
	import api from '../../utils/api.js'
	import storage from '../../utils/storage.js'
	
	export default {
		data() {
			return {
				capsule: null,
				isLiked: false,
				comments: [],
				showCommentInput: false,
				commentContent: '',
				shareCode: '',  // 保存共享码以便重新加载
				isLoggedIn: false  // 用户是否已登录
			}
		},
		computed: {
			decryptedContent() {
				if (!this.capsule) return ''
				return this.capsule.content
			}
		},
		onLoad(options) {
			// 检查用户是否已登录
			this.isLoggedIn = !!storage.getToken()
			
			if (options.code) {
				this.shareCode = options.code.toUpperCase()
				this.loadShareCapsule(options.code)
			}
		},
		methods: {
			async loadShareCapsule(code) {
				try {
					const capsule = await api.getSharedCapsule(code)
					this.capsule = capsule
					// 设置点赞状态
					this.isLiked = capsule.is_liked || false
					// 加载评论
					this.loadComments()
				} catch (error) {
					uni.showToast({
						title: error.message || '未找到共享胶囊',
						icon: 'none'
					})
				}
			},
			
			async loadComments() {
				if (!this.capsule) return
				try {
					this.comments = await api.getComments(this.capsule.id)
				} catch (error) {
					// 对于共享胶囊，评论应该可以正常加载
					// 如果失败，可能是网络问题或权限问题
					if (this.capsule.is_shared) {
						// 共享胶囊的评论应该可以公开查看，失败时给用户提示
						console.error('加载评论失败:', error)
						// 静默失败，不打扰用户（评论是可选的）
					} else {
						// 非共享胶囊，可能是权限问题
						console.error('加载评论失败:', error)
					}
				}
			},
			
			async handleLike() {
				if (!this.capsule) return
				// 保存原始状态，以便失败时回滚
				const originalIsLiked = this.isLiked
				const originalLikeCount = this.capsule.like_count || 0
				
				// 先更新UI状态（乐观更新）
				this.isLiked = !this.isLiked
				if (this.capsule) {
					this.capsule.like_count = this.isLiked 
						? originalLikeCount + 1 
						: Math.max(0, originalLikeCount - 1)
				}
				
				try {
					const res = await api.toggleLike(this.capsule.id)
					uni.showToast({
						title: res.message || (this.isLiked ? '已点赞' : '已取消'),
						icon: 'none'
					})
					// 成功后重新加载胶囊数据以确保状态一致
					if (this.shareCode) {
						const updated = await api.getSharedCapsule(this.shareCode)
						if (updated) {
							this.capsule.like_count = updated.like_count || 0
							this.isLiked = updated.is_liked || false
						}
					}
				} catch (error) {
					// 失败时回滚状态
					this.isLiked = originalIsLiked
					if (this.capsule) {
						this.capsule.like_count = originalLikeCount
					}
					uni.showToast({
						title: error.message || '操作失败',
						icon: 'none'
					})
				}
			},
			
			showComment() {
				// 检查用户是否已登录
				if (!this.isLoggedIn) {
					uni.showModal({
						title: '提示',
						content: '评论需要登录，是否前往登录？',
						success: (res) => {
							if (res.confirm) {
								uni.navigateTo({
									url: '/pages/login/login'
								})
							}
						}
					})
					return
				}
				this.showCommentInput = true
			},
			
			async submitComment() {
				if (!this.commentContent.trim()) {
					uni.showToast({
						title: '请输入评论内容',
						icon: 'none'
					})
					return
				}
				
				// 再次检查登录状态（防止token过期）
				if (!storage.getToken()) {
					uni.showModal({
						title: '提示',
						content: '登录已过期，请重新登录',
						success: (res) => {
							if (res.confirm) {
								uni.navigateTo({
									url: '/pages/login/login'
								})
							}
						}
					})
					return
				}
				
				try {
					await api.addComment(this.capsule.id, this.commentContent)
					uni.showToast({
						title: '评论成功',
						icon: 'success'
					})
					this.commentContent = ''
					this.showCommentInput = false
					this.loadComments()
					// 更新登录状态
					this.isLoggedIn = !!storage.getToken()
				} catch (error) {
					// 如果是401错误，提示需要登录
					if (error.statusCode === 401) {
						this.isLoggedIn = false
						uni.showModal({
							title: '提示',
							content: '登录已过期，请重新登录',
							success: (res) => {
								if (res.confirm) {
									uni.navigateTo({
										url: '/pages/login/login'
									})
								}
							}
						})
					} else {
						uni.showToast({
							title: error.message || '评论失败',
							icon: 'none'
						})
					}
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
			
			goBack() {
				uni.navigateBack()
			}
		}
	}
</script>

<style scoped>
	.share-unlock-page {
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
	
	.unlock-content {
		padding: 0 40rpx;
	}
	
	.capsule-display {
		text-align: center;
		margin: 60rpx 0;
	}
	
	.capsule-icon-large {
		font-size: 120rpx;
		display: block;
		margin-bottom: 30rpx;
	}
	
	.capsule-title {
		display: block;
		font-size: 40rpx;
		font-weight: bold;
		color: #fff;
		margin-bottom: 10rpx;
	}
	
	.capsule-info {
		display: block;
		font-size: 24rpx;
		color: rgba(255, 255, 255, 0.6);
	}
	
	.unlock-section {
		margin-bottom: 60rpx;
	}
	
	.unlock-label {
		display: block;
		font-size: 32rpx;
		font-weight: bold;
		color: #fff;
		margin-bottom: 30rpx;
	}
	
	.content-box {
		background: rgba(255, 255, 255, 0.05);
		border-radius: 20rpx;
		padding: 40rpx;
	}
	
	.content-text {
		font-size: 32rpx;
		color: #fff;
		line-height: 1.8;
		white-space: pre-wrap;
	}
	
	.interaction-section {
		margin-bottom: 60rpx;
	}
	
	.section-title {
		display: block;
		font-size: 32rpx;
		font-weight: bold;
		color: #fff;
		margin-bottom: 30rpx;
	}
	
	.action-buttons {
		display: flex;
		gap: 20rpx;
	}
	
	.action-btn {
		flex: 1;
		background: rgba(255, 255, 255, 0.05);
		border-radius: 20rpx;
		padding: 30rpx;
		text-align: center;
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 10rpx;
	}
	
	.action-icon {
		font-size: 50rpx;
	}
	
	.action-text {
		font-size: 28rpx;
		color: #fff;
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

