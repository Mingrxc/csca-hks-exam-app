<template>
  <view class="timeline-preview app-shell">
    <view class="app-section">
      <view class="preview-hero app-card app-card-pad">
        <image class="preview-icon" :src="APP_ICON_PATH" mode="aspectFit" />
        <text class="preview-brand">老外一点通</text>
        <text class="preview-title">留学备考，从每一题开始</text>
        <text class="preview-description">面向 CSCA 与 HSK 备考的学习助手，结合题库练习、模拟考试和错题复习，循序渐进地积累。</text>
      </view>
    </view>

    <view class="app-section">
      <view class="app-card app-card-pad">
        <text class="app-card-title">可以怎样学习</text>
        <view class="preview-feature">
          <text class="feature-title">题库练习与模拟考试</text>
          <text class="feature-description">选择考试和科目，按自己的节奏练习，或通过限时模拟检查掌握情况。</text>
        </view>
        <view class="preview-feature">
          <text class="feature-title">错题、收藏与学习记录</text>
          <text class="feature-description">回顾答题解析，收藏需要巩固的题目，逐步整理个人学习积累。</text>
        </view>
        <view class="preview-feature">
          <text class="feature-title">AI 学习助手</text>
          <text class="feature-description">围绕题目和学习困惑提问，辅助理解思路。AI 回答可能存在错误，请结合教材核实。</text>
        </view>
      </view>
    </view>

    <view class="app-section">
      <view class="app-card app-card-pad">
        <text class="app-card-title">一道数学小练习</text>
        <text class="sample-question">若 2x + 3 = 7，求 x 的值。</text>
        <view class="sample-answer">
          <text class="feature-title">答案：x = 2</text>
          <text class="feature-description">等式两边先减去 3，得到 2x = 4；再同时除以 2，得到 x = 2。</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { APP_ICON_PATH } from '@/constants/brand'
</script>

<style lang="scss" scoped>
.timeline-preview { padding-top: 28rpx; padding-bottom: 32rpx; }
.preview-hero { text-align: center; }
.preview-icon { display: block; width: 80rpx; height: 80rpx; margin: 0 auto 16rpx; }
.preview-brand { display: block; color: var(--app-primary); font-size: 26rpx; font-weight: 600; }
.preview-title { display: block; margin-top: 16rpx; font-size: 40rpx; font-weight: 600; line-height: 1.5; }
.preview-description { display: block; margin-top: 20rpx; color: var(--app-text-weak); font-size: 27rpx; line-height: 1.9; text-align: left; }
.preview-feature { padding-top: 22rpx; margin-top: 22rpx; border-top: 1rpx solid var(--app-border); }
.feature-title { display: block; color: var(--app-text); font-size: 28rpx; font-weight: 600; }
.feature-description { display: block; margin-top: 10rpx; color: var(--app-text-weak); font-size: 26rpx; line-height: 1.9; }
.sample-question { display: block; margin-top: 24rpx; color: var(--app-text); font-size: 30rpx; line-height: 1.8; }
.sample-answer { margin-top: 22rpx; padding: 22rpx; border-radius: var(--app-radius-sm); background: var(--app-secondary-soft); }
</style>
