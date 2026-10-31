<template>
	<view class="countdown">
		<text v-if="!countdown.isExpired" class="countdown-text">
			{{formatTime(countdown.days)}}天 {{formatTime(countdown.hours)}}时 {{formatTime(countdown.minutes)}}分 {{formatTime(countdown.seconds)}}秒
		</text>
		<text v-else class="expired-text">已解锁</text>
	</view>
</template>

<script>
	import dateUtil from '../../utils/date.js'
	
	export default {
		props: {
			targetDate: {
				type: String,
				required: true
			}
		},
		data() {
			return {
				countdown: {
					days: 0,
					hours: 0,
					minutes: 0,
					seconds: 0,
					isExpired: false
				},
				timer: null
			}
		},
		onLoad() {
			this.updateCountdown()
			this.startTimer()
		},
		onUnload() {
			if (this.timer) {
				clearInterval(this.timer)
			}
		},
		methods: {
			updateCountdown() {
				this.countdown = dateUtil.getCountdown(this.targetDate)
			},
			
			startTimer() {
				this.timer = setInterval(() => {
					this.updateCountdown()
					if (this.countdown.isExpired) {
						clearInterval(this.timer)
						this.$emit('expired')
					}
				}, 1000)
			},
			
			formatTime(num) {
				return String(num).padStart(2, '0')
			}
		}
	}
</script>

<style scoped>
	.countdown {
		font-size: 24rpx;
	}
	
	.countdown-text {
		color: rgba(108, 92, 231, 1);
	}
	
	.expired-text {
		color: #4ade80;
	}
</style>

