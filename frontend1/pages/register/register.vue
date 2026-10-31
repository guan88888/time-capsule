<template>
	<view class="register-page">
		<view class="stars-bg">
			<view class="star" v-for="(star, index) in stars" :key="index"
				:style="{left: star.x + '%', top: star.y + '%', animationDelay: star.delay + 's'}">
			</view>
		</view>
		
		<view class="register-content">
			<view class="header">
				<text class="back-icon" @click="goBack">←</text>
				<text class="title">注册账号</text>
			</view>
			
			<view class="form-section">
				<view class="input-group">
					<text class="input-label">昵称</text>
					<input 
						class="input-field" 
						v-model="form.nickname" 
						@input="onNicknameInput"
						placeholder="请输入昵称"
						placeholder-style="color: rgba(255,255,255,0.4)"
						:value="form.nickname"
					/>
				</view>
				
			<view class="input-group">
				<text class="input-label">邮箱/手机号</text>
				<input 
					class="input-field" 
					v-model="form.account" 
					@input="onAccountInput"
					placeholder="请输入邮箱或手机号"
					placeholder-style="color: rgba(255,255,255,0.4)"
					:value="form.account"
				/>
			</view>
			
			<!-- 手机号注册时显示验证码输入 -->
			<view class="input-group" v-if="isPhoneAccount">
				<text class="input-label">短信验证码</text>
				<view class="sms-code-wrapper">
					<input 
						class="input-field sms-input" 
						v-model="form.smsCode" 
						@input="onSmsCodeInput"
						type="number"
						maxlength="6"
						placeholder="请输入6位验证码"
						placeholder-style="color: rgba(255,255,255,0.4)"
						:value="form.smsCode"
					/>
					<button 
						class="sms-btn" 
						:disabled="countdown > 0 || !isPhoneAccount"
						@click="handleSendSms"
						:class="{ 'disabled': countdown > 0 || !isPhoneAccount }"
					>
						{{ countdown > 0 ? `${countdown}秒` : '获取验证码' }}
					</button>
				</view>
			</view>
			
			<view class="input-group">
				<text class="input-label">密码</text>
				<input 
					class="input-field" 
					v-model="form.password" 
					@input="onPasswordInput"
					password
					placeholder="请输入密码（至少6位）"
					placeholder-style="color: rgba(255,255,255,0.4)"
					:value="form.password"
				/>
			</view>
				
				<view class="input-group">
					<text class="input-label">确认密码</text>
					<input 
						class="input-field" 
						v-model="form.confirmPassword" 
						@input="onConfirmPasswordInput"
						password
						placeholder="请再次输入密码"
						placeholder-style="color: rgba(255,255,255,0.4)"
						:value="form.confirmPassword"
					/>
				</view>
				
				<button class="btn-primary" @click="handleRegister">注册</button>
				
				<view class="login-link">
					<text>已有账号？</text>
					<text class="link" @click="goToLogin">立即登录</text>
				</view>
			</view>
		</view>
	</view>
</template>

<script>
	import api from '../../utils/api.js'
	
	export default {
		data() {
			return {
				stars: [],
				countdown: 0,
				countdownTimer: null,
				form: {
					nickname: '',
					account: '',
					password: '',
					confirmPassword: '',
					smsCode: ''
				}
			}
		},
		computed: {
			// 判断是否是手机号
			isPhoneAccount() {
				if (!this.form.account) return false
				// 简单的手机号判断（11位数字）
				return /^1[3-9]\d{9}$/.test(this.form.account)
			}
		},
		onLoad() {
			this.initStars()
		},
		onUnload() {
			// 清除倒计时
			if (this.countdownTimer) {
				clearInterval(this.countdownTimer)
				this.countdownTimer = null
			}
		},
		methods: {
			initStars() {
				const stars = []
				for (let i = 0; i < 50; i++) {
					stars.push({
						x: Math.random() * 100,
						y: Math.random() * 100,
						delay: Math.random() * 3
					})
				}
				this.stars = stars
			},
			
			onNicknameInput(e) {
				this.form.nickname = e.detail.value
			},
			
			onAccountInput(e) {
				this.form.account = e.detail.value
			},
			
			onPasswordInput(e) {
				this.form.password = e.detail.value
			},
			
			onConfirmPasswordInput(e) {
				this.form.confirmPassword = e.detail.value
			},
			
			onSmsCodeInput(e) {
				// 只允许输入数字，最多6位
				let value = e.detail.value.replace(/\D/g, '')
				if (value.length > 6) {
					value = value.substring(0, 6)
				}
				this.form.smsCode = value
			},
			
			// 发送短信验证码
			async handleSendSms() {
				if (!this.form.account) {
					uni.showToast({
						title: '请先输入手机号',
						icon: 'none'
					})
					return
				}
				
				if (!this.isPhoneAccount) {
					uni.showToast({
						title: '请输入正确的手机号',
						icon: 'none'
					})
					return
				}
				
				if (this.countdown > 0) {
					return
				}
				
				uni.showLoading({
					title: '发送中...'
				})
				
				try {
					const res = await api.sendSms(this.form.account, 'register')
					uni.hideLoading()
					uni.showToast({
						title: res.message || '验证码已发送',
						icon: 'success'
					})
					
					// 开始60秒倒计时
					this.startCountdown()
				} catch (error) {
					uni.hideLoading()
					uni.showToast({
						title: error.message || '发送验证码失败，请重试',
						icon: 'none',
						duration: 2000
					})
				}
			},
			
			// 开始倒计时
			startCountdown() {
				this.countdown = 60
				this.countdownTimer = setInterval(() => {
					this.countdown--
					if (this.countdown <= 0) {
						clearInterval(this.countdownTimer)
						this.countdownTimer = null
					}
				}, 1000)
			},
			
			async handleRegister() {
				if (!this.form.nickname || !this.form.account || !this.form.password) {
					uni.showToast({
						title: '请填写完整信息',
						icon: 'none'
					})
					return
				}
				
				if (this.form.password.length < 6) {
					uni.showToast({
						title: '密码至少6位',
						icon: 'none'
					})
					return
				}
				
				if (this.form.password !== this.form.confirmPassword) {
					uni.showToast({
						title: '两次密码不一致',
						icon: 'none'
					})
					return
				}
				
				// 如果是手机号注册，验证短信验证码
				if (this.isPhoneAccount) {
					if (!this.form.smsCode || this.form.smsCode.length !== 6) {
						uni.showToast({
							title: '请输入6位验证码',
							icon: 'none'
						})
						return
					}
				}
				
				uni.showLoading({
					title: '注册中...'
				})
				
				try {
					const registerData = {
						nickname: this.form.nickname,
						email: this.form.account.includes('@') ? this.form.account : '',
						phone: this.form.account.includes('@') ? '' : this.form.account,
						password: this.form.password
					}
					
					// 如果是手机号注册，添加短信验证码
					if (this.isPhoneAccount && this.form.smsCode) {
						registerData.sms_code = this.form.smsCode
					}
					
					const res = await api.register(registerData)
					uni.hideLoading()
					uni.showToast({
						title: '注册成功',
						icon: 'success'
					})
					
					setTimeout(() => {
						uni.reLaunch({
							url: '/pages/index/index'
						})
					}, 1500)
				} catch (error) {
					uni.hideLoading()
					uni.showToast({
						title: error.message || '注册失败，请重试',
						icon: 'none',
						duration: 2000
					})
				}
			},
			
			goBack() {
				uni.navigateBack()
			},
			
			goToLogin() {
				uni.navigateBack()
			}
		}
	}
</script>

<style scoped>
	.register-page {
		width: 100%;
		min-height: 100vh;
		position: relative;
		background: linear-gradient(180deg, #0f0f1e 0%, #1a1a2e 100%);
	}
	
	.stars-bg {
		position: fixed;
		width: 100%;
		height: 100%;
		top: 0;
		left: 0;
		z-index: 0;
		pointer-events: none;
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
	
	.register-content {
		position: relative;
		z-index: 10;
		padding: 60rpx;
		min-height: 100vh;
	}
	
	.form-section {
		width: 100%;
		position: relative;
		z-index: 20;
	}
	
	.header {
		display: flex;
		align-items: center;
		margin-bottom: 80rpx;
	}
	
	.back-icon {
		font-size: 48rpx;
		color: #fff;
		margin-right: 30rpx;
	}
	
	.title {
		font-size: 48rpx;
		font-weight: bold;
		color: #fff;
	}
	
	.form-section {
		width: 100%;
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
	
	.input-group {
		margin-bottom: 40rpx;
		position: relative;
		z-index: 30;
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
	
	.btn-primary {
		width: 100%;
		background: linear-gradient(135deg, #6c5ce7 0%, #a29bfe 100%);
		color: #fff;
		border-radius: 50rpx;
		padding: 24rpx;
		font-size: 32rpx;
		border: none;
		box-shadow: 0 8rpx 20rpx rgba(108, 92, 231, 0.3);
		margin-top: 40rpx;
		margin-bottom: 40rpx;
	}
	
	.login-link {
		text-align: center;
	}
	
	.login-link text {
		color: rgba(255, 255, 255, 0.6);
		font-size: 28rpx;
	}
	
	.login-link .link {
		color: #6c5ce7;
		margin-left: 10rpx;
	}
	
	.sms-code-wrapper {
		display: flex;
		align-items: center;
		gap: 20rpx;
	}
	
	.sms-input {
		flex: 1;
	}
	
	.sms-btn {
		background: linear-gradient(135deg, #6c5ce7 0%, #a29bfe 100%);
		color: #fff;
		border-radius: 16rpx;
		padding: 0 30rpx;
		height: 88rpx;
		line-height: 88rpx;
		font-size: 28rpx;
		border: none;
		white-space: nowrap;
		flex-shrink: 0;
	}
	
	.sms-btn.disabled {
		background: rgba(255, 255, 255, 0.2);
		color: rgba(255, 255, 255, 0.5);
	}
</style>

