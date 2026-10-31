<template>
	<view class="create-page">
		<view class="page-header">
			<text class="back-btn" @click="goBack">←</text>
			<text class="page-title">创建胶囊</text>
		</view>
		
		<scroll-view class="form-container" scroll-y>
			<!-- 胶囊类型选择 -->
			<view class="section">
				<text class="section-title">选择胶囊类型</text>
				<view class="type-grid">
					<view 
						v-for="type in capsuleTypes" 
						:key="type.value"
						class="type-item"
						:class="{'active': form.type === type.value}"
						@click="selectType(type.value)">
						<text class="type-icon">{{type.icon}}</text>
						<text class="type-name">{{type.name}}</text>
						<text class="type-desc">{{type.desc}}</text>
					</view>
				</view>
			</view>
			
			<!-- 基本信息 -->
			<view class="section">
				<text class="section-title">基本信息</text>
				<view class="input-group">
					<view class="input-label-row">
						<text class="input-label">胶囊标题</text>
						<button 
							class="btn-ai" 
							:disabled="generatingTitle || !form.content"
							@click="handleGenerateTitle"
							v-if="form.content && form.content.length >= 10">
							<text class="btn-ai-text">{{ generatingTitle ? 'AI生成中...' : '✨ AI生成' }}</text>
						</button>
					</view>
					<input 
						class="input-field" 
						v-model="form.title" 
						@input="onTitleInput"
						placeholder="给胶囊起个名字"
						placeholder-style="color: rgba(255,255,255,0.4)"
					/>
					<text class="input-hint" v-if="form.content && form.content.length < 10 && !form.title">
						输入至少10个字符后可使用AI生成标题
					</text>
				</view>
				
				<view class="input-group">
					<text class="input-label">胶囊内容</text>
					<textarea 
						class="textarea-field" 
						v-model="form.content" 
						@input="onContentInput"
						placeholder="记录你想说的话..."
						placeholder-style="color: rgba(255,255,255,0.4)"
						:maxlength="2000"
					></textarea>
					<text class="char-count">{{form.content.length}}/2000</text>
				</view>
			</view>
			
			<!-- 目标胶囊特有 -->
			<view class="section" v-if="form.type === 'target'">
				<text class="section-title">目标设置</text>
				<view class="input-group">
					<text class="input-label">目标描述</text>
					<textarea 
						class="textarea-field" 
						v-model="form.target" 
						@input="onTargetInput"
						placeholder="描述你的目标..."
						placeholder-style="color: rgba(255,255,255,0.4)"
					></textarea>
				</view>
			</view>
			
			<!-- 解锁时间 -->
			<view class="section">
				<text class="section-title">解锁时间</text>
				<view class="input-group">
					<text class="input-label">选择日期</text>
					<picker mode="date" :value="form.date" @change="onDateChange">
						<view class="picker-field">
							<text>{{form.date || '选择日期'}}</text>
							<text class="picker-arrow">></text>
						</view>
					</picker>
				</view>
				<view class="input-group">
					<text class="input-label">选择时间</text>
					<picker mode="time" :value="form.time" @change="onTimeChange">
						<view class="picker-field">
							<text>{{form.time || '选择时间'}}</text>
							<text class="picker-arrow">></text>
						</view>
					</picker>
				</view>
			</view>
			
			<!-- 标签 -->
			<view class="section">
				<text class="section-title">标签（可选）</text>
				<view class="tags-container">
					<view 
						v-for="tag in form.tags" 
						:key="tag"
						class="tag-item">
						<text>{{tag}}</text>
						<text class="tag-close" @click="removeTag(tag)">×</text>
					</view>
					<input 
						class="tag-input" 
						v-model="newTag" 
						@input="onTagInput"
						@confirm="addTag"
						placeholder="添加标签"
						placeholder-style="color: rgba(255,255,255,0.4)"
					/>
				</view>
			</view>
			
			<!-- 共享胶囊设置 -->
			<view class="section" v-if="form.type === 'share'">
				<text class="section-title">共享设置</text>
				<view class="switch-group">
					<text class="switch-label">允许他人解锁</text>
					<switch :checked="form.allowShare" @change="onShareChange" color="#6c5ce7"/>
				</view>
			</view>
		</scroll-view>
		
		<view class="footer-actions">
			<button class="btn-primary" @click="handleCreate">创建胶囊</button>
		</view>
	</view>
</template>

<script>
	import api from '../../utils/api.js'
	import dateUtil from '../../utils/date.js'
	
	export default {
		data() {
			return {
				capsuleTypes: [
					{ value: 'target', icon: '🎯', name: '目标胶囊', desc: '设定目标，追踪进度' },
					{ value: 'emotion', icon: '💭', name: '心境胶囊', desc: '记录情感，回顾心境' },
					{ value: 'gratitude', icon: '🙏', name: '感恩胶囊', desc: '记录感恩瞬间' },
					{ value: 'share', icon: '🔗', name: '共享胶囊', desc: '分享给他人' }
				],
				form: {
					type: 'emotion',
					title: '',
					content: '',
					target: '',
					date: '',
					time: '',
					tags: [],
					allowShare: false
				},
				newTag: '',
				submitting: false,
				generatingTitle: false
			}
		},
		onLoad() {
			const today = new Date()
			this.form.date = dateUtil.formatDate(today, 'YYYY-MM-DD')
			this.form.time = dateUtil.formatDate(today, 'HH:mm')
		},
		methods: {
			onTitleInput(e) {
				this.form.title = e.detail.value
			},
			
			onContentInput(e) {
				this.form.content = e.detail.value
			},
			
			onTargetInput(e) {
				this.form.target = e.detail.value
			},
			
			onTagInput(e) {
				this.newTag = e.detail.value
			},
			
			selectType(type) {
				this.form.type = type
			},
			
			onDateChange(e) {
				this.form.date = e.detail.value
			},
			
			onTimeChange(e) {
				this.form.time = e.detail.value
			},
			
			addTag() {
				if (this.newTag && !this.form.tags.includes(this.newTag)) {
					this.form.tags.push(this.newTag)
					this.newTag = ''
				}
			},
			
			removeTag(tag) {
				this.form.tags = this.form.tags.filter(t => t !== tag)
			},
			
			onShareChange(e) {
				this.form.allowShare = e.detail.value
			},
			
			// AI生成标题
			async handleGenerateTitle() {
				if (this.generatingTitle || !this.form.content || this.form.content.length < 10) {
					return
				}
				
				this.generatingTitle = true
				uni.showLoading({ title: 'AI生成中...' })
				
				try {
					const titles = await api.generateTitle(this.form.content, 3)
					uni.hideLoading()
					
					if (titles && titles.length > 0) {
						// 如果只有一个标题，直接使用
						if (titles.length === 1) {
							this.form.title = titles[0]
							uni.showToast({
								title: '标题生成成功',
								icon: 'success',
								duration: 1500
							})
						} else {
							// 多个标题，让用户选择
							uni.showActionSheet({
								itemList: titles,
								success: (res) => {
									this.form.title = titles[res.tapIndex]
									uni.showToast({
										title: '已选择标题',
										icon: 'success',
										duration: 1000
									})
								}
							})
						}
					} else {
						uni.showToast({
							title: '未生成标题，请重试',
							icon: 'none'
						})
					}
				} catch (error) {
					uni.hideLoading()
					console.error('生成标题失败:', error)
					uni.showToast({
						title: error.message || 'AI生成标题失败，请手动输入',
						icon: 'none',
						duration: 2000
					})
				} finally {
					this.generatingTitle = false
				}
			},
			
			async handleCreate() {
				if (this.submitting) return
				
				if (!this.form.title) {
					uni.showToast({
						title: '请输入胶囊标题',
						icon: 'none'
					})
					return
				}
				
				if (!this.form.content) {
					uni.showToast({
						title: '请输入胶囊内容',
						icon: 'none'
					})
					return
				}
				
				if (!this.form.date || !this.form.time) {
					uni.showToast({
						title: '请选择解锁时间',
						icon: 'none'
					})
					return
				}
				
				// 安全解析日期时间
				const unlockDate = new Date(`${this.form.date} ${this.form.time}`)
				if (isNaN(unlockDate.getTime())) {
					uni.showToast({
						title: '日期时间格式不正确',
						icon: 'none'
					})
					return
				}
				if (unlockDate.getTime() <= Date.now()) {
					uni.showToast({
						title: '解锁时间必须晚于当前时间',
						icon: 'none'
					})
					return
				}
				
				this.submitting = true
				uni.showLoading({ title: '创建中...' })
				
				try {
					await api.createCapsule({
						type: this.form.type,
						title: this.form.title,
						content: this.form.content,
						target: this.form.target || null,
						unlockDate: unlockDate.toISOString(),
						tags: this.form.tags,
						allowShare: this.form.type === 'share' && this.form.allowShare
					})
					
					uni.hideLoading()
					uni.showToast({
						title: '创建成功',
						icon: 'success'
					})
					
					setTimeout(() => {
						uni.navigateBack()
					}, 1500)
				} catch (error) {
					uni.hideLoading()
					uni.showToast({
						title: error.message || '创建失败',
						icon: 'none'
					})
				} finally {
					this.submitting = false
				}
			},
			
			generateShareCode() {
				return Math.random().toString(36).substr(2, 8).toUpperCase()
			},
			
			goBack() {
				uni.navigateBack()
			}
		}
	}
</script>

<style scoped>
	.create-page {
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
	
	.form-container {
		height: calc(100vh - 200rpx);
		padding: 0 40rpx;
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
	
	.type-grid {
		display: grid;
		grid-template-columns: repeat(2, 1fr);
		gap: 20rpx;
	}
	
	.type-item {
		background: rgba(255, 255, 255, 0.05);
		border-radius: 20rpx;
		padding: 30rpx;
		text-align: center;
		border: 2rpx solid transparent;
		transition: all 0.3s;
	}
	
	.type-item.active {
		border-color: #6c5ce7;
		background: rgba(108, 92, 231, 0.2);
	}
	
	.type-icon {
		font-size: 60rpx;
		display: block;
		margin-bottom: 16rpx;
	}
	
	.type-name {
		display: block;
		font-size: 28rpx;
		color: #fff;
		font-weight: 500;
		margin-bottom: 8rpx;
	}
	
	.type-desc {
		display: block;
		font-size: 22rpx;
		color: rgba(255, 255, 255, 0.6);
	}
	
	.input-group {
		margin-bottom: 30rpx;
		position: relative;
		z-index: 10;
	}
	
	.input-label {
		color: rgba(255, 255, 255, 0.7);
		font-size: 28rpx;
		margin-bottom: 16rpx;
		display: block;
	}
	
	.input-label-row {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 16rpx;
	}
	
	.btn-ai {
		background: linear-gradient(135deg, #6c5ce7 0%, #a29bfe 100%);
		border-radius: 30rpx;
		padding: 8rpx 24rpx;
		border: none;
		opacity: 1;
		transition: all 0.3s;
	}
	
	.btn-ai:disabled {
		opacity: 0.5;
		background: rgba(108, 92, 231, 0.3);
	}
	
	.btn-ai-text {
		color: #fff;
		font-size: 24rpx;
		font-weight: 500;
	}
	
	.input-hint {
		display: block;
		color: rgba(255, 255, 255, 0.4);
		font-size: 22rpx;
		margin-top: 8rpx;
	}
	
	.input-field {
		width: 100%;
		height: 88rpx;
		line-height: 88rpx;
		background: rgba(255, 255, 255, 0.1);
		border-radius: 16rpx;
		padding: 0 24rpx;
		color: #fff;
		font-size: 32rpx;
		border: 1rpx solid rgba(255, 255, 255, 0.1);
		box-sizing: border-box;
	}
	
	.input-field:focus {
		border-color: rgba(108, 92, 231, 0.8);
		background: rgba(255, 255, 255, 0.15);
	}
	
	.textarea-field {
		width: 100%;
		min-height: 200rpx;
		background: rgba(255, 255, 255, 0.1);
		border-radius: 16rpx;
		padding: 24rpx;
		color: #fff;
		font-size: 32rpx;
		border: 1rpx solid rgba(255, 255, 255, 0.1);
		box-sizing: border-box;
		line-height: 1.6;
	}
	
	.textarea-field:focus {
		border-color: rgba(108, 92, 231, 0.8);
		background: rgba(255, 255, 255, 0.15);
	}
	
	.char-count {
		display: block;
		text-align: right;
		color: rgba(255, 255, 255, 0.4);
		font-size: 24rpx;
		margin-top: 10rpx;
	}
	
	.picker-field {
		background: rgba(255, 255, 255, 0.1);
		border-radius: 16rpx;
		padding: 24rpx;
		color: #fff;
		font-size: 32rpx;
		border: 1rpx solid rgba(255, 255, 255, 0.1);
		display: flex;
		justify-content: space-between;
		align-items: center;
	}
	
	.picker-arrow {
		color: rgba(255, 255, 255, 0.4);
	}
	
	.tags-container {
		display: flex;
		flex-wrap: wrap;
		gap: 16rpx;
		align-items: center;
	}
	
	.tag-item {
		background: rgba(108, 92, 231, 0.3);
		border-radius: 30rpx;
		padding: 12rpx 20rpx;
		display: flex;
		align-items: center;
		gap: 10rpx;
	}
	
	.tag-item text {
		color: #fff;
		font-size: 24rpx;
	}
	
	.tag-close {
		font-size: 32rpx;
		color: rgba(255, 255, 255, 0.6);
	}
	
	.tag-input {
		background: rgba(255, 255, 255, 0.1);
		border-radius: 30rpx;
		padding: 12rpx 20rpx;
		color: #fff;
		font-size: 24rpx;
		min-width: 150rpx;
		height: 60rpx;
		line-height: 60rpx;
		box-sizing: border-box;
	}
	
	.tag-input:focus {
		border-color: rgba(108, 92, 231, 0.8);
		background: rgba(255, 255, 255, 0.15);
	}
	
	.switch-group {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 24rpx;
		background: rgba(255, 255, 255, 0.05);
		border-radius: 16rpx;
	}
	
	.switch-label {
		color: #fff;
		font-size: 28rpx;
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

