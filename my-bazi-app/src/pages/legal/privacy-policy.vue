<template>
  <view class="legal-page">
    <!-- 顶部导航 -->
    <view class="nav-bar">
      <view class="back-btn" @click="uni.navigateBack()">
        <text class="material-symbols-outlined">arrow_back_ios</text>
      </view>
      <text class="nav-title">隐私政策</text>
      <view class="nav-placeholder"></view>
    </view>

    <!-- 正文 -->
    <scroll-view scroll-y class="scroll-body">
      <view class="content">

        <text class="update-date">最后更新日期：2026年5月</text>

        <!-- 引言 -->
        <view class="notice-box">
          <text class="notice-title">【引言】</text>
          <text class="notice-body">"云水禅心"深知个人信息对您的重要性，我们将严格遵守相关法律法规，采取业界标准的安全保护措施来保护您的个人信息安全。请您仔细阅读本政策，了解我们如何收集、使用、存储和保护您的数据。</text>
        </view>

        <!-- 第1条 -->
        <view class="section">
          <text class="section-title">1. 我们如何收集和使用您的个人信息</text>
          <text class="clause-body standalone">为了向您提供优质的排盘、测算及后续服务，我们需要在"最小必要"原则下收集以下信息：</text>

          <view class="clause">
            <text class="clause-num">1.1</text>
            <text class="clause-body"><text class="bold">账号注册信息：</text>当您注册或登录时，我们会收集您的手机号码、短信验证码，或在您主动授权下收集您的第三方公开信息（如微信昵称、头像、OpenID/UnionID），用于创建和同步您的云端账号。</text>
          </view>

          <view class="clause">
            <text class="clause-num">1.2</text>
            <text class="clause-body">
              <text class="bold">命理档案信息</text>
              <text class="clause-tag-inline">⚠️ 核心服务所需</text>
              <text class="bold">为了向您提供"八字排盘"、"流年运势"等核心服务，我们需要您主动输入并保存您或您亲友的出生日期（包含年、月、日、时）、性别、出生地等信息。这些信息是提供测算服务所必需的基础数据。</text>
            </text>
          </view>

          <view class="clause">
            <text class="clause-num">1.3</text>
            <text class="clause-body"><text class="bold">设备与日志信息：</text>为了保障软件的安全运行和排查崩溃问题，我们可能会自动收集您的设备型号、操作系统版本、唯一设备标识符（如OAID等）、IP地址及应用运行崩溃日志。</text>
          </view>

          <view class="clause">
            <text class="clause-num">1.4</text>
            <text class="clause-body">
              <text class="bold">业务扩展与功能升级声明</text>
              <text class="clause-tag-inline">🌟 面向未来的特别授权</text>
              <text>随着产品体系的丰富，我们未来可能会为您提供更多元化的泛心理与传统文化探索服务（如紫微斗数、塔罗占卜、AI智能解惑等）：</text>
            </text>
          </view>

          <!-- 1.4 子条款 -->
          <view class="sub-clause">
            <text class="sub-dot">·</text>
            <text class="clause-body"><text class="bold">基础数据复用：</text>若未来新增功能所需的基础信息与您已在档案中提供的信息一致，为了提升体验，我们可能在您开启该功能时，直接调用您现有的命理档案数据进行运算。</text>
          </view>
          <view class="sub-clause">
            <text class="sub-dot">·</text>
            <text class="clause-body bold">新增敏感数据请求：若未来新增的功能（如语音AI对话、情感合盘等）需要调用您的麦克风权限，或收集额外的个人信息（如情感状态等），我们将严格在您实际使用该功能前，通过系统弹窗或独立页面向您明确说明，并在征得您的单独授权同意后方才收集，绝不默认强制开启。</text>
          </view>
        </view>

        <!-- 第2条 -->
        <view class="section">
          <text class="section-title">2. 我们如何共享、转让、公开披露您的个人信息</text>

          <view class="clause">
            <text class="clause-num">2.1</text>
            <text class="clause-body bold">未经您的明确同意，我们不会向任何第三方共享、出售或出租您的个人身份信息及命理档案数据。</text>
          </view>

          <view class="clause">
            <text class="clause-num">2.2</text>
            <text class="clause-body"><text class="bold">第三方SDK接入：</text>为了实现一键登录、内容分享、数据统计或广告投放功能，我们集成了部分合法合规的第三方SDK（如微信开放平台SDK、腾讯/穿山甲广告SDK等）。这些第三方可能会收集您的部分基础设备信息与网络状态，具体使用目的与数据范围请查阅应用内的《第三方SDK目录》。</text>
          </view>
        </view>

        <!-- 第3条 -->
        <view class="section">
          <text class="section-title">3. 我们如何存储和保护您的个人信息</text>

          <view class="clause">
            <text class="clause-num">3.1</text>
            <text class="clause-body"><text class="bold">存储地点与期限：</text>我们在中华人民共和国境内收集和产生的个人信息，将存储在境内（阿里云/腾讯云）服务器上。我们将会在法律法规规定的最短期限内保存您的数据。</text>
          </view>

          <view class="clause">
            <text class="clause-num">3.2</text>
            <text class="clause-body"><text class="bold">数据安全技术：</text>我们使用行业标准的 <text class="bold">HTTPS 加密协议</text>在传输过程中保护您的数据，并在数据库端对登录密码等极度敏感信息采用 <text class="bold">Bcrypt 强哈希算法</text>进行不可逆加密存储，最大程度防止数据泄露。</text>
          </view>
        </view>

        <!-- 第4条 -->
        <view class="section">
          <text class="section-title">4. 您的权利</text>
          <text class="clause-body standalone">您对自己的个人信息拥有完全的控制权：</text>

          <view class="clause">
            <text class="clause-num">4.1</text>
            <text class="clause-body"><text class="bold">访问与更正：</text>您可以随时进入"我的 - 档案管理"页面，查看、修改或完善您的个人命理档案。</text>
          </view>

          <view class="clause">
            <text class="clause-num">4.2</text>
            <text class="clause-body"><text class="bold">删除档案：</text>您可以在档案列表中，随时左滑或点击删除不再需要的亲友档案数据，云端将同步抹除。</text>
          </view>

          <view class="clause">
            <text class="clause-num">4.3</text>
            <text class="clause-body bold">账号注销：您可以通过"设置 - 注销账号"功能申请注销。注销操作不可逆，注销后我们将彻底清除您在云端的所有账号信息、历史测算记录与档案数据，使其保持不可被检索和访问的状态。</text>
          </view>
        </view>

        <!-- 第5条 -->
        <view class="section">
          <text class="section-title">5. 未成年人保护</text>
          <text class="clause-body standalone bold">本应用的服务及内容（涉及命理、运势、心理深度测评）主要面向成年人提供。如您为未满18周岁的未成年人，请务必在法定监护人的陪同和指导下阅读本政策，并确保在取得监护人明确同意后方可使用我们的服务。</text>
        </view>

        <!-- 第6条 -->
        <view class="section">
          <text class="section-title">6. 隐私政策的修订与通知</text>
          <text class="clause-body standalone">我们保留随时更新本《隐私政策》的权利。当应用发生重大功能变更、收集数据类型增加或法律法规发生变化时，我们会适时对本政策进行修订。对于重大变更，我们会在新版本生效前通过应用内弹窗、红点提示等显著方式通知您。若您在收到通知后继续使用本应用，即表示您充分阅读、理解并同意受经修订的隐私政策约束。</text>
        </view>

        <!-- 第7条 -->
        <view class="section">
          <text class="section-title">7. 联系我们</text>
          <text class="clause-body standalone">如您对本隐私政策有任何疑问、意见或建议，或需要进行个人信息相关的投诉与申诉，可通过以下邮箱联系我们，我们将在收到邮件后的 <text class="bold">15 个工作日</text>内予以回复：</text>
          <view class="contact-box">
            <text class="material-symbols-outlined contact-icon">mail</text>
            <text class="contact-email">chen@jinxiangs.freeqiye.com</text>
          </view>
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

/* ── 引言框 ── */
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
}

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

/* 无编号的独立段落 */
.clause-body.standalone {
  display: block;
  padding-left: 8rpx;
  margin-bottom: 16rpx;
}

/* ── 子条款（缩进列表） ── */
.sub-clause {
  display: flex;
  align-items: flex-start;
  gap: 12rpx;
  margin-bottom: 16rpx;
  padding-left: 80rpx;
}
.sub-dot {
  flex-shrink: 0;
  font-size: 28rpx;
  color: #B23A34;
  line-height: 1.85;
}

/* ── 行内标签 ── */
.clause-tag-inline {
  display: inline;
  font-size: 22rpx;
  color: #B23A34;
  background: rgba(178, 58, 52, 0.07);
  padding: 2rpx 12rpx;
  border-radius: 16rpx;
  margin: 0 8rpx 8rpx;
}

/* ── 加粗高亮 ── */
.bold {
  font-weight: 700;
  color: #1A1A1A;
}

/* ── 联系方式 ── */
.contact-box {
  display: flex;
  align-items: center;
  gap: 16rpx;
  margin-top: 20rpx;
  padding: 24rpx 28rpx;
  background: rgba(178, 58, 52, 0.04);
  border-radius: 12rpx;
  border: 1px solid rgba(178, 58, 52, 0.12);
}
.contact-icon {
  font-family: 'Material Symbols Outlined';
  font-size: 40rpx;
  color: #B23A34;
}
.contact-email {
  font-size: 28rpx;
  color: #B23A34;
  font-weight: 600;
  letter-spacing: 1rpx;
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
