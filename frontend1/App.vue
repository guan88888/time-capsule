<script>
	export default {
		onLaunch: function() {
			console.log('时空胶囊 App Launch')
			// 游客模式：不强制登录，允许预览所有页面
			const token = uni.getStorageSync('token')
			if (!token) {
				console.log('游客模式：未登录，可预览所有页面')
				// 设置游客标记
				uni.setStorageSync('isGuest', true)
			} else {
				uni.setStorageSync('isGuest', false)
			}
		},
		onShow: function() {
			console.log('App Show')
		},
		onHide: function() {
			console.log('App Hide')
		},
		methods: {
			// 全局方法：检查是否需要登录
			checkLogin(callback) {
				const token = uni.getStorageSync('token')
				if (!token) {
					uni.showModal({
						title: '需要登录',
						content: '该功能需要登录后使用，是否前往登录？',
						confirmText: '去登录',
						cancelText: '继续浏览',
						success: (res) => {
							if (res.confirm) {
								uni.navigateTo({
									url: '/pages/login/login'
								})
							}
						}
					})
					return false
				}
				if (callback) callback()
				return true
			}
		}
	}
</script>

<style>
	/*每个页面公共css */
	@import './common/common.css';
	
	/* H5模式下确保页面可以滚动 */
	html, body {
		height: auto !important;
		overflow: auto !important;
		-webkit-overflow-scrolling: touch;
	}
	
	page {
		background: linear-gradient(180deg, #0f0f1e 0%, #1a1a2e 100%);
		min-height: 100vh;
		overflow-y: auto;
		-webkit-overflow-scrolling: touch;
	}
	
	/* uni-app H5页面容器 */
	uni-page-body {
		overflow-y: auto;
		-webkit-overflow-scrolling: touch;
	}
	
	/* 全局字体 */
	* {
		font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
	}
</style>
