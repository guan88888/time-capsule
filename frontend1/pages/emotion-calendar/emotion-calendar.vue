<template>
	<view class="emotion-calendar-page">
		<view class="page-header">
			<text class="back-btn" @click="goBack">←</text>
			<text class="page-title">情绪日历</text>
		</view>
		
		<view class="calendar-container">
			<view class="calendar-header">
				<text class="month-text">{{currentMonth}}</text>
			</view>
			
			<view class="calendar-grid">
				<view class="weekday-header">
					<text v-for="day in weekdays" :key="day" class="weekday">{{day}}</text>
				</view>
				<view class="days-grid">
					<view 
						v-for="(day, index) in calendarDays" 
						:key="index"
						class="day-cell"
						:class="{'other-month': day.otherMonth, 'has-emotion': day.emotion !== null}"
						@click="selectDay(day)">
						<text class="day-number">{{day.date}}</text>
						<view class="emotion-indicator" v-if="day.emotion !== null">
							<text class="emotion-emoji">{{getEmotionEmoji(day.emotion)}}</text>
						</view>
					</view>
				</view>
			</view>
		</view>
		
		<view class="emotion-stats">
			<text class="stats-title">本月情绪统计</text>
			<view class="stats-grid">
				<view class="stat-item" v-for="stat in emotionStats" :key="stat.label">
					<text class="stat-emoji">{{stat.emoji}}</text>
					<text class="stat-count">{{stat.count}}</text>
					<text class="stat-label">{{stat.label}}</text>
				</view>
			</view>
		</view>
		
		<view class="trend-section">
			<text class="section-title">情绪趋势</text>
			<view class="trend-chart">
				<view class="chart-placeholder">
					<text>情绪趋势图表</text>
					<text class="chart-desc">（图表功能开发中）</text>
				</view>
			</view>
		</view>
	</view>
</template>

<script>
	import api from '../../utils/api.js'
	import dateUtil from '../../utils/date.js'
	
	export default {
		data() {
			return {
				weekdays: ['日', '一', '二', '三', '四', '五', '六'],
				currentDate: new Date(),
				emotionCalendarData: {},  // 日历数据 { 'YYYY-MM-DD': score }
				emotionStats: [
					{ emoji: '😢', label: '非常难过', count: 0 },
					{ emoji: '😔', label: '有点低落', count: 0 },
					{ emoji: '😐', label: '平静', count: 0 },
					{ emoji: '🙂', label: '还不错', count: 0 },
					{ emoji: '😊', label: '非常开心', count: 0 }
				],
				selectedDay: null
			}
		},
		computed: {
			currentMonth() {
				const year = this.currentDate.getFullYear()
				const month = this.currentDate.getMonth() + 1
				return `${year}年${month}月`
			},
			calendarDays() {
				const year = this.currentDate.getFullYear()
				const month = this.currentDate.getMonth()
				const firstDay = new Date(year, month, 1)
				const lastDay = new Date(year, month + 1, 0)
				const firstDayWeek = firstDay.getDay()
				const daysInMonth = lastDay.getDate()
				
				const days = []
				
				// 上个月的日期
				const prevMonthLastDay = new Date(year, month, 0).getDate()
				for (let i = firstDayWeek - 1; i >= 0; i--) {
					days.push({
						date: prevMonthLastDay - i,
						otherMonth: true,
						emotion: null
					})
				}
				
				// 当前月的日期
				for (let i = 1; i <= daysInMonth; i++) {
					const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(i).padStart(2, '0')}`
					const emotion = this.emotionCalendarData[dateStr] !== undefined ? this.emotionCalendarData[dateStr] : null
					days.push({
						date: i,
						otherMonth: false,
						emotion: emotion,
						fullDate: dateStr
					})
				}
				
				// 下个月的日期
				const remainingDays = 42 - days.length
				for (let i = 1; i <= remainingDays; i++) {
					days.push({
						date: i,
						otherMonth: true,
						emotion: null
					})
				}
				
				return days
			}
		},
		onLoad() {
			this.loadCalendarData()
			this.loadStats()
		},
		methods: {
			async loadCalendarData() {
				try {
					const year = this.currentDate.getFullYear()
					const month = this.currentDate.getMonth() + 1
					const res = await api.getEmotionCalendar(year, month)
					this.emotionCalendarData = res.data || {}
				} catch (error) {
					console.error('加载情绪日历失败:', error)
					this.emotionCalendarData = {}
				}
			},
			
			async loadStats() {
				try {
					const res = await api.getEmotionStats()
					// 更新统计数据 - 后端返回的是字典格式 {score: count}
					this.emotionStats = [
						{ emoji: '😢', label: '非常难过', count: res.by_score[0] || 0 },
						{ emoji: '😔', label: '有点低落', count: res.by_score[1] || 0 },
						{ emoji: '😐', label: '平静', count: res.by_score[2] || 0 },
						{ emoji: '🙂', label: '还不错', count: res.by_score[3] || 0 },
						{ emoji: '😊', label: '非常开心', count: res.by_score[4] || 0 }
					]
				} catch (error) {
					console.error('加载情绪统计失败:', error)
					// 如果加载失败，保持默认值（全0）
				}
			},
			
			getEmotionEmoji(score) {
				const emojis = ['😢', '😔', '😐', '🙂', '😊']
				return emojis[score] || ''
			},
			
			selectDay(day) {
				if (day.otherMonth || !day.fullDate) return
				this.selectedDay = day
				// 可以显示详情或跳转
			},
			
			goBack() {
				uni.navigateBack()
			}
		}
	}
</script>

<style scoped>
	.emotion-calendar-page {
		width: 100%;
		min-height: 100vh;
		background: linear-gradient(180deg, #0f0f1e 0%, #1a1a2e 100%);
		padding-bottom: 60rpx;
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
	
	.calendar-container {
		padding: 0 40rpx;
		margin-bottom: 60rpx;
	}
	
	.calendar-header {
		text-align: center;
		margin-bottom: 30rpx;
	}
	
	.month-text {
		font-size: 36rpx;
		font-weight: bold;
		color: #fff;
	}
	
	.calendar-grid {
		background: rgba(255, 255, 255, 0.05);
		border-radius: 20rpx;
		padding: 30rpx;
	}
	
	.weekday-header {
		display: grid;
		grid-template-columns: repeat(7, 1fr);
		margin-bottom: 20rpx;
	}
	
	.weekday {
		text-align: center;
		font-size: 24rpx;
		color: rgba(255, 255, 255, 0.6);
	}
	
	.days-grid {
		display: grid;
		grid-template-columns: repeat(7, 1fr);
		gap: 10rpx;
	}
	
	.day-cell {
		aspect-ratio: 1;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		border-radius: 12rpx;
		position: relative;
	}
	
	.day-cell.other-month {
		opacity: 0.3;
	}
	
	.day-cell.has-emotion {
		background: rgba(108, 92, 231, 0.2);
	}
	
	.day-number {
		font-size: 24rpx;
		color: #fff;
	}
	
	.emotion-indicator {
		position: absolute;
		bottom: 4rpx;
	}
	
	.emotion-emoji {
		font-size: 20rpx;
	}
	
	.emotion-stats {
		padding: 0 40rpx;
		margin-bottom: 60rpx;
	}
	
	.stats-title {
		display: block;
		font-size: 32rpx;
		font-weight: bold;
		color: #fff;
		margin-bottom: 30rpx;
	}
	
	.stats-grid {
		display: grid;
		grid-template-columns: repeat(5, 1fr);
		gap: 20rpx;
	}
	
	.stat-item {
		background: rgba(255, 255, 255, 0.05);
		border-radius: 16rpx;
		padding: 20rpx;
		text-align: center;
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 10rpx;
	}
	
	.stat-emoji {
		font-size: 40rpx;
	}
	
	.stat-count {
		font-size: 32rpx;
		font-weight: bold;
		color: #fff;
	}
	
	.stat-label {
		font-size: 20rpx;
		color: rgba(255, 255, 255, 0.6);
	}
	
	.trend-section {
		padding: 0 40rpx;
	}
	
	.section-title {
		display: block;
		font-size: 32rpx;
		font-weight: bold;
		color: #fff;
		margin-bottom: 30rpx;
	}
	
	.trend-chart {
		background: rgba(255, 255, 255, 0.05);
		border-radius: 20rpx;
		padding: 60rpx;
		text-align: center;
	}
	
	.chart-placeholder {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 10rpx;
	}
	
	.chart-placeholder text {
		color: rgba(255, 255, 255, 0.6);
		font-size: 28rpx;
	}
	
	.chart-desc {
		font-size: 24rpx;
		color: rgba(255, 255, 255, 0.4);
	}
</style>

