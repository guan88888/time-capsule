<template>
	<view class="login-page">
		<view class="stars-bg">
			<view class="star" v-for="(star, index) in stars" :key="index"
				:style="{left: star.x + '%', top: star.y + '%', animationDelay: star.delay + 's'}">
			</view>
		</view>
		
		<view class="login-content">
			<view class="logo-section">
				<text class="logo-icon">🌌</text>
				<text class="app-name">时空胶囊</text>
				<text class="app-desc">记录时光，遇见未来</text>
			</view>
			
			<view class="form-section">
				<!-- 登录方式切换 -->
				<view class="login-tabs">
					<view 
						class="tab-item" 
						:class="{'active': loginType === 'password'}"
						@click="switchLoginType('password')">
						<text>密码登录</text>
					</view>
					<view 
						class="tab-item" 
						:class="{'active': loginType === 'code'}"
						@click="switchLoginType('code')">
						<text>验证码登录</text>
					</view>
				</view>
				
				<!-- 密码登录 -->
				<view v-if="loginType === 'password'">
					<view class="input-group">
						<text class="input-label">账号</text>
						<input 
							class="input-field" 
							v-model="form.account" 
							@input="onAccountInput"
							placeholder="请输入邮箱或手机号"
							placeholder-style="color: rgba(255,255,255,0.4)"
						/>
					</view>
					
					<view class="input-group">
						<text class="input-label">密码</text>
						<input 
							class="input-field" 
							v-model="form.password" 
							@input="onPasswordInput"
							password
							placeholder="请输入密码"
							placeholder-style="color: rgba(255,255,255,0.4)"
						/>
					</view>
					
					<view class="forgot-password" @click="handleForgotPassword">
						<text>忘记密码？</text>
					</view>
					
					<button class="btn-primary" @click="handleLogin">登录</button>
				</view>
				
				<!-- 验证码登录 -->
				<view v-if="loginType === 'code'">
					<view class="input-group">
						<text class="input-label">手机号</text>
						<input 
							class="input-field" 
							v-model="form.phone" 
							@input="onPhoneInput"
							type="number"
							maxlength="11"
							placeholder="请输入手机号"
							placeholder-style="color: rgba(255,255,255,0.4)"
						/>
					</view>
					
					<view class="input-group">
						<text class="input-label">验证码</text>
						<view class="code-input-wrapper">
							<input 
								class="input-field code-input" 
								v-model="form.code" 
								@input="onCodeInput"
								type="number"
								maxlength="6"
								placeholder="请输入验证码"
								placeholder-style="color: rgba(255,255,255,0.4)"
							/>
							<button 
								class="send-code-btn" 
								:class="{'disabled': countdown > 0}"
								:disabled="countdown > 0"
								@click="handleSendCode">
								{{countdown > 0 ? `${countdown}秒` : '发送验证码'}}
							</button>
						</view>
					</view>
					
					<button class="btn-primary" @click="handleCodeLogin">登录</button>
				</view>
				
				<view class="divider" v-if="loginType === 'password'">
					<text>或</text>
				</view>
				
				<view class="third-party-login" v-if="loginType === 'password'">
					<view class="third-btn" @click="handleThirdLogin('wechat')">
						<text>微信登录</text>
					</view>
					<view class="third-btn" @click="handleThirdLogin('qq')">
						<text>QQ登录</text>
					</view>
				</view>
				
				<view class="register-link">
					<text>还没有账号？</text>
					<text class="link" @click="goToRegister">立即注册</text>
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
				loginType: 'password', // 'password' 或 'code'
				countdown: 0,
				countdownTimer: null,
				form: {
					account: '',
					password: '',
					phone: '',
					code: ''
				}
			}
		},
		onUnload() {
			// 清除倒计时
			if (this.countdownTimer) {
				clearInterval(this.countdownTimer)
			}
		},
		onLoad() {
			this.initStars()
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
			
			onAccountInput(e) {
				this.form.account = e.detail.value
			},
			
			onPasswordInput(e) {
				this.form.password = e.detail.value
			},
			
			onPhoneInput(e) {
				this.form.phone = e.detail.value
			},
			
			onCodeInput(e) {
				this.form.code = e.detail.value
			},
			
			switchLoginType(type) {
				this.loginType = type
				// 清除表单
				if (type === 'password') {
					this.form.phone = ''
					this.form.code = ''
				} else {
					this.form.account = ''
					this.form.password = ''
				}
			},
			
			async handleSendCode() {
				if (!this.form.phone) {
					uni.showToast({
						title: '请输入手机号',
						icon: 'none'
					})
					return
				}
				
				// 验证手机号格式
				const phoneReg = /^1[3-9]\d{9}$/
				if (!phoneReg.test(this.form.phone)) {
					uni.showToast({
						title: '手机号格式不正确',
						icon: 'none'
					})
					return
				}
				
				uni.showLoading({
					title: '发送中...'
				})
				
				try {
					await api.sendCode(this.form.phone)
					uni.hideLoading()
					uni.showToast({
						title: '验证码已发送',
						icon: 'success'
					})
					
					// 开始倒计时
					this.countdown = 60
					this.countdownTimer = setInterval(() => {
						this.countdown--
						if (this.countdown <= 0) {
							clearInterval(this.countdownTimer)
							this.countdownTimer = null
						}
					}, 1000)
				} catch (error) {
					uni.hideLoading()
					uni.showToast({
						title: error.message || '发送失败，请重试',
						icon: 'none',
						duration: 2000
					})
				}
			},
			
			async handleCodeLogin() {
				if (!this.form.phone) {
					uni.showToast({
						title: '请输入手机号',
						icon: 'none'
					})
					return
				}
				
				if (!this.form.code) {
					uni.showToast({
						title: '请输入验证码',
						icon: 'none'
					})
					return
				}
				
				uni.showLoading({
					title: '登录中...'
				})
				
				try {
					const res = await api.codeLogin(this.form.phone, this.form.code)
					uni.hideLoading()
					uni.showToast({
						title: '登录成功',
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
						title: error.message || '登录失败，请重试',
						icon: 'none',
						duration: 2000
					})
				}
			},
			
			async handleLogin() {
				if (!this.form.account || !this.form.password) {
					uni.showToast({
						title: '请填写完整信息',
						icon: 'none'
					})
					return
				}
				
				uni.showLoading({
					title: '登录中...'
				})
				
				try {
					const res = await api.login(this.form.account, this.form.password)
					uni.hideLoading()
					uni.showToast({
						title: '登录成功',
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
						title: error.message || '登录失败，请重试',
						icon: 'none',
						duration: 2000
					})
				}
			},
			
			handleForgotPassword() {
				// 跳转到重置密码页面
				uni.navigateTo({
					url: '/pages/reset-password/reset-password'
				})
			},
			
			handleThirdLogin(type) {
				uni.showToast({
					title: `${type === 'wechat' ? '微信' : 'QQ'}登录功能开发中`,
					icon: 'none'
				})
			},
			
			goToRegister() {
				uni.navigateTo({
					url: '/pages/register/register'
				})
			}
		}
	}
</script>

<style scoped>
	.login-page {
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
	
	.login-content {
		position: relative;
		z-index: 10;
		padding: 100rpx 60rpx;
		min-height: 100vh;
		display: flex;
		flex-direction: column;
		justify-content: center;
	}
	
	.logo-section {
		text-align: center;
		margin-bottom: 100rpx;
	}
	
	.logo-icon {
		font-size: 120rpx;
		display: block;
		margin-bottom: 30rpx;
	}
	
	.app-name {
		display: block;
		font-size: 56rpx;
		font-weight: bold;
		color: #fff;
		margin-bottom: 20rpx;
	}
	
	.app-desc {
		display: block;
		font-size: 28rpx;
		color: rgba(255, 255, 255, 0.6);
	}
	
	.form-section {
		width: 100%;
		position: relative;
		z-index: 20;
	}
	
	.login-tabs {
		display: flex;
		gap: 20rpx;
		margin-bottom: 40rpx;
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
	
	.code-input-wrapper {
		display: flex;
		gap: 20rpx;
		align-items: center;
	}
	
	.code-input {
		flex: 1;
	}
	
	.send-code-btn {
		background: rgba(108, 92, 231, 0.3);
		color: #fff;
		border-radius: 16rpx;
		padding: 0 30rpx;
		height: 88rpx;
		line-height: 88rpx;
		font-size: 26rpx;
		border: 1rpx solid rgba(108, 92, 231, 0.5);
		white-space: nowrap;
	}
	
	.send-code-btn.disabled {
		background: rgba(255, 255, 255, 0.1);
		color: rgba(255, 255, 255, 0.4);
		border-color: rgba(255, 255, 255, 0.1);
	}
	
	.input-group {
		margin-bottom: 40rpx;
		position: relative;
		z-index: 30;
	}
	
	.input-label {
		color: rgba(255, 255, 255, 0.7);
		font-size: 28rpx;
		margin-bottom: 16rpx;
		display: block;
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
	
	.forgot-password {
		text-align: right;
		margin-bottom: 40rpx;
	}
	
	.forgot-password text {
		color: rgba(255, 255, 255, 0.6);
		font-size: 26rpx;
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
		margin-bottom: 40rpx;
	}
	
	.divider {
		text-align: center;
		margin: 40rpx 0;
		position: relative;
	}
	
	.divider text {
		color: rgba(255, 255, 255, 0.4);
		font-size: 24rpx;
		background: linear-gradient(180deg, #0f0f1e 0%, #1a1a2e 100%);
		padding: 0 20rpx;
		position: relative;
		z-index: 1;
	}
	
	.divider::before {
		content: '';
		position: absolute;
		left: 0;
		right: 0;
		top: 50%;
		height: 1rpx;
		background: rgba(255, 255, 255, 0.1);
	}
	
	.third-party-login {
		display: flex;
		justify-content: space-between;
		gap: 20rpx;
		margin-bottom: 60rpx;
	}
	
	.third-btn {
		flex: 1;
		background: rgba(255, 255, 255, 0.1);
		border-radius: 16rpx;
		padding: 24rpx;
		text-align: center;
		border: 1rpx solid rgba(255, 255, 255, 0.1);
	}
	
	.third-btn text {
		color: #fff;
		font-size: 28rpx;
	}
	
	.register-link {
		text-align: center;
	}
	
	.register-link text {
		color: rgba(255, 255, 255, 0.6);
		font-size: 28rpx;
	}
	
	.register-link .link {
		color: #6c5ce7;
		margin-left: 10rpx;
	}
</style>

