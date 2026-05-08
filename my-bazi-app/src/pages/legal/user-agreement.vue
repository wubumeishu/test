<template>
  <view class="legal-page">
    <!-- 顶部导航 -->
    <view class="nav-bar">
      <view class="back-btn" @click="uni.navigateBack()">
        <text class="material-symbols-outlined">arrow_back_ios</text>
      </view>
      <text class="nav-title">用户服务协议</text>
      <view class="nav-placeholder"></view>
    </view>

    <!-- 正文 -->
    <scroll-view scroll-y class="scroll-body">
      <view class="content">

        <text class="update-date">最后更新日期：2026年5月</text>

        <!-- 特别提示 -->
        <view class="notice-box">
          <text class="notice-title">【特别提示】</text>
          <text class="notice-body">欢迎使用"云水禅心"（以下简称"本应用"）。在您注册、登录及使用本应用提供的服务前，请务必审慎阅读、充分理解本协议的各项条款。特别是<text class="bold">免除或者限制责任的条款、对用户权利进行限制的条款、约定争议解决方式和管辖的条款</text>，我们将以加粗形式提示您注意。</text>
          <text class="notice-body">您勾选"同意"或实际使用本应用的服务，即视为您已阅读并同意接受本协议的全部内容。</text>
        </view>

        <!-- 第1条 -->
        <view class="section">
          <text class="section-title">1. 服务声明与娱乐性质提示</text>
          <text class="clause-tag">⚠️ 核心免责条款</text>

          <view class="clause">
            <text class="clause-num">1.1</text>
            <text class="clause-body">本应用提供的八字排盘、紫微斗数、MBTI测评、塔罗牌阵及未来可能上线的各类命理与心理测试内容，其算法和结果均基于传统文化典籍或特定理论模型进行程序化生成，仅供用户作为个人心理探索、传统文化研究和日常娱乐之用。</text>
          </view>

          <view class="clause">
            <text class="clause-num">1.2</text>
            <text class="clause-body bold">本应用不对任何测试结果的准确性、科学性、绝对真实性作任何承诺或保证。测算结果与分析报告不构成任何心理咨询、医疗诊断、法律、财务、投资或重大人生决策的专业建议。用户依据本应用内容作出的任何行为或决定，由用户自行承担后果与风险，本应用及开发者不承担任何直接或间接的法律责任。</text>
          </view>

          <view class="clause">
            <text class="clause-num">1.3</text>
            <text class="clause-body">本应用坚决反对利用本平台进行任何形式的封建迷信诈骗活动。请用户保持理性，切勿沉迷。</text>
          </view>
        </view>

        <!-- 第2条 -->
        <view class="section">
          <text class="section-title">2. 账号注册、使用与安全</text>

          <view class="clause">
            <text class="clause-num">2.1</text>
            <text class="clause-body">用户在注册时应当提供真实、有效的手机号码，或在您授权的情况下使用微信等第三方账号快捷登录。</text>
          </view>

          <view class="clause">
            <text class="clause-num">2.2</text>
            <text class="clause-body bold">您应对您的账号和验证码/密码的安全负全部责任。因您个人保管不善导致的账号被盗用、档案数据泄露或虚拟财产损失，本应用不承担赔偿责任。</text>
          </view>

          <view class="clause">
            <text class="clause-num">2.3</text>
            <text class="clause-body">您承诺不利用本应用从事任何违反国家法律法规、侵犯他人隐私或知识产权的活动。</text>
          </view>
        </view>

        <!-- 第3条 -->
        <view class="section">
          <text class="section-title">3. 增值服务与未来商业模式预留</text>

          <view class="clause">
            <text class="clause-num">3.1</text>
            <text class="clause-body"><text class="bold">虚拟商品与服务：</text>本应用目前或未来可能提供需要付费解锁的"AI深度精批"、"进阶测评报告"等增值服务。<text class="bold">用户在购买虚拟商品或服务前应仔细确认，虚拟商品/服务一经购买或消耗，不支持无理由退换及退款。</text></text>
          </view>

          <view class="clause">
            <text class="clause-num">3.2</text>
            <text class="clause-body"><text class="bold">商业模式的演进：</text>本应用目前可能提供免费的基础功能。在未来的版本演进中，我们保留引入新商业模式的权利，包括但不限于推出需使用"虚拟积分/禅心币"兑换的高级报告、VIP订阅制服务、或需观看激励广告解锁的深度内容等。具体规则将以功能上线时的页面公示为准。</text>
          </view>
        </view>

        <!-- 第4条 -->
        <view class="section">
          <text class="section-title">4. 服务的变更、中断与迭代免责</text>

          <view class="clause">
            <text class="clause-num">4.1</text>
            <text class="clause-body">本应用有权在提前通知或不通知的情况下，根据业务发展需要修改、中断或终止部分或全部服务。</text>
          </view>

          <view class="clause">
            <text class="clause-num">4.2</text>
            <text class="clause-body"><text class="bold">算法与模型演进免责：</text>本应用核心的排盘引擎和 AI 分析模型处于持续迭代与优化中。因此，针对同一份命理档案，未来版本生成的测试结果或解析文案可能与历史版本存在细微差异。<text class="bold">此属于产品技术正常迭代范畴，不视为本应用提供错误或虚假信息。</text></text>
          </view>

          <view class="clause">
            <text class="clause-num">4.3</text>
            <text class="clause-body"><text class="bold">服务调整：</text>为了整体用户体验及产品长远发展，本应用有权在不同版本中调整、增加、暂停或永久取消某些特定功能模块，且无需对用户承担因此产生的任何直接损失。</text>
          </view>
        </view>

        <!-- 第5条 -->
        <view class="section">
          <text class="section-title">5. 知识产权声明</text>
          <text class="clause-body standalone">本应用内的所有内容（包括但不限于算法逻辑、UI设计、文本、图片、图表、音频、视频）的知识产权均归本应用运营方所有。未经书面许可，任何人不得擅自抓取、复制、修改或用于其他商业用途。</text>
        </view>

        <!-- 第6条 -->
        <view class="section">
          <text class="section-title">6. 法律适用与管辖</text>
          <text class="clause-body standalone">本协议的订立、执行、解释及争议的解决均应适用中华人民共和国大陆地区法律。如发生争议，双方应首先友好协商；协商不成的，任何一方均有权向本应用运营方所在地有管辖权的人民法院提起诉讼。</text>
        </view>

        <view class="bottom-spacer"></view>
      </view>
    </scroll-view>
  </view>
</template>

<script setup lang="ts">
// 无需额外逻辑
</script>

<style scoped>
.legal-page {
  min-height: 100vh;
  background: #F9F6F1;
  display: flex;
  flex-direction: column;
}

/* ── 导航栏 ── */
.nav-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 100rpx 40rpx 24rpx;
  background: #F9F6F1;
  border-bottom: 0.5px solid rgba(0, 0, 0, 0.06);
}
.back-btn {
  width: 80rpx;
  display: flex;
  align-items: center;
}
.back-btn .material-symbols-outlined {
  font-family: 'Material Symbols Outlined';
  font-size: 44rpx;
  color: #1A1A1A;
}
.nav-title {
  font-size: 34rpx;
  font-weight: 600;
  color: #1A1A1A;
  letter-spacing: 2rpx;
}
.nav-placeholder { width: 80rpx; }

/* ── 滚动区域 ── */
.scroll-body {
  flex: 1;
  height: calc(100vh - 180rpx);
}

/* ── 正文容器 ── */
.content {
  padding: 36rpx 48rpx 60rpx;
}

.update-date {
  display: block;
  font-size: 22rpx;
  color: #aaa;
  margin-bottom: 36rpx;
  text-align: right;
}

/* ── 特别提示框 ── */
.notice-box {
  background: rgba(178, 58, 52, 0.04);
  border: 1px solid rgba(178, 58, 52, 0.15);
  border-radius: 12rpx;
  padding: 28rpx 32rpx;
  margin-bottom: 48rpx;
}
.notice-title {
  display: block;
  font-size: 28rpx;
  font-weight: 700;
  color: #B23A34;
  margin-bottom: 16rpx;
  letter-spacing: 2rpx;
}
.notice-body {
  display: block;
  font-size: 26rpx;
  color: #444;
  line-height: 1.85;
  text-align: justify;
  margin-bottom: 12rpx;
}
.notice-body:last-child { margin-bottom: 0; }

/* ── 条款区块 ── */
.section {
  margin-bottom: 52rpx;
}

.section-title {
  display: block;
  font-size: 30rpx;
  font-weight: 700;
  color: #1A1A1A;
  margin-bottom: 20rpx;
  padding: 0 0 16rpx 20rpx;
  border-left: 5rpx solid #B23A34;
  border-bottom: 0.5px solid rgba(0, 0, 0, 0.06);
}

.clause-tag {
  display: inline-block;
  font-size: 22rpx;
  color: #B23A34;
  background: rgba(178, 58, 52, 0.07);
  padding: 6rpx 18rpx;
  border-radius: 20rpx;
  margin-bottom: 20rpx;
  letter-spacing: 1rpx;
}

/* ── 单条条款（编号 + 正文横排） ── */
.clause {
  display: flex;
  align-items: flex-start;
  gap: 16rpx;
  margin-bottom: 20rpx;
  padding-left: 8rpx;
}

.clause-num {
  flex-shrink: 0;
  min-width: 56rpx;
  font-size: 24rpx;
  font-weight: 700;
  color: #B23A34;
  line-height: 1.85;
  padding-top: 2rpx;
}

.clause-body {
  flex: 1;
  font-size: 27rpx;
  color: #333;
  line-height: 1.85;
  letter-spacing: 0.5rpx;
  text-align: justify;
}

/* 无编号的独立段落（第5、6条） */
.clause-body.standalone {
  display: block;
  padding-left: 8rpx;
}

/* ── 加粗高亮 ── */
.bold {
  font-weight: 700;
  color: #1A1A1A;
}

/* ── 底部留白 ── */
.bottom-spacer { height: 80rpx; }

/* ── 图标字体 ── */
.material-symbols-outlined {
  font-family: 'Material Symbols Outlined';
  font-weight: normal;
  font-style: normal;
  line-height: 1;
  letter-spacing: normal;
  text-transform: none;
  display: inline-block;
  white-space: nowrap;
  -webkit-font-smoothing: antialiased;
}
</style>
