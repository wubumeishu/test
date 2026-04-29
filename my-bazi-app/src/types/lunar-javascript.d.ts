/**
 * lunar-javascript 类型声明文件
 * 为没有官方类型定义的 lunar-javascript 库提供基本类型支持
 */

declare module 'lunar-javascript' {
  /**
   * 公历日期类
   */
  export class Solar {
    /**
     * 从年月日时分秒创建公历日期
     * @param year 年
     * @param month 月
     * @param day 日
     * @param hour 时
     * @param minute 分
     * @param second 秒
     */
    static fromYmdHms(
      year: number,
      month: number,
      day: number,
      hour: number,
      minute: number,
      second: number
    ): Solar

    /**
     * 从日期对象创建公历日期
     * @param date 日期对象
     */
    static fromDate(date: Date): Solar

    /**
     * 获取年份
     */
    getYear(): number

    /**
     * 获取月份
     */
    getMonth(): number

    /**
     * 获取日期
     */
    getDay(): number

    /**
     * 获取小时
     */
    getHour(): number

    /**
     * 获取分钟
     */
    getMinute(): number

    /**
     * 获取秒
     */
    getSecond(): number

    /**
     * 转换为农历
     */
    getLunar(): Lunar

    /**
     * 转换为字符串
     */
    toString(): string

    /**
     * 转换为完整字符串
     */
    toFullString(): string
  }

  /**
   * 农历日期类
   */
  export class Lunar {
    /**
     * 从年月日时分秒创建农历日期
     * @param year 年
     * @param month 月
     * @param day 日
     * @param hour 时
     * @param minute 分
     * @param second 秒
     */
    static fromYmdHms(
      year: number,
      month: number,
      day: number,
      hour: number,
      minute: number,
      second: number
    ): Lunar

    /**
     * 获取年份
     */
    getYear(): number

    /**
     * 获取月份
     */
    getMonth(): number

    /**
     * 获取日期
     */
    getDay(): number

    /**
     * 获取小时
     */
    getHour(): number

    /**
     * 获取分钟
     */
    getMinute(): number

    /**
     * 获取秒
     */
    getSecond(): number

    /**
     * 获取生肖
     */
    getYearShengXiao(): string

    /**
     * 获取年柱
     */
    getYearInGanZhi(): string

    /**
     * 获取月柱
     */
    getMonthInGanZhi(): string

    /**
     * 获取日柱
     */
    getDayInGanZhi(): string

    /**
     * 获取时柱
     */
    getTimeInGanZhi(): string

    /**
     * 获取八字
     */
    getEightChar(): EightChar

    /**
     * 转换为公历
     */
    getSolar(): Solar

    /**
     * 转换为字符串
     */
    toString(): string

    /**
     * 转换为完整字符串
     */
    toFullString(): string
  }

  /**
   * 八字类
   */
  export class EightChar {
    /**
     * 获取年柱
     */
    getYear(): string

    /**
     * 获取月柱
     */
    getMonth(): string

    /**
     * 获取日柱
     */
    getDay(): string

    /**
     * 获取时柱
     */
    getTime(): string

    /**
     * 获取年柱天干
     */
    getYearGan(): string

    /**
     * 获取年柱地支
     */
    getYearZhi(): string

    /**
     * 获取月柱天干
     */
    getMonthGan(): string

    /**
     * 获取月柱地支
     */
    getMonthZhi(): string

    /**
     * 获取日柱天干
     */
    getDayGan(): string

    /**
     * 获取日柱地支
     */
    getDayZhi(): string

    /**
     * 获取时柱天干
     */
    getTimeGan(): string

    /**
     * 获取时柱地支
     */
    getTimeZhi(): string

    /**
     * 转换为字符串
     */
    toString(): string
  }
}
