/**
 * 日期工具函数
 * Date utility functions using dayjs
 */

import dayjs, { type Dayjs } from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
import utc from 'dayjs/plugin/utc'
import timezone from 'dayjs/plugin/timezone'

// Load dayjs plugins
dayjs.extend(relativeTime)
dayjs.extend(utc)
dayjs.extend(timezone)

/**
 * Date format options
 */
export type DateFormat =
  | 'YYYY-MM-DD'
  | 'YYYY-MM-DD HH:mm'
  | 'YYYY-MM-DD HH:mm:ss'
  | 'MM/DD/YYYY'
  | 'MM/DD/YYYY HH:mm'
  | 'DD/MM/YYYY'
  | 'DD/MM/YYYY HH:mm'
  | 'HH:mm'
  | 'HH:mm:ss'

/**
 * Format date to string
 * @param date - Date to format (string, Date, or Dayjs)
 * @param format - Format string (default: 'YYYY-MM-DD HH:mm:ss')
 * @returns Formatted date string
 */
export function formatDate(
  date: string | Date | Dayjs,
  format: DateFormat = 'YYYY-MM-DD HH:mm:ss'
): string {
  if (!date) {
    return ''
  }

  return dayjs(date).format(format)
}

/**
 * Format date relative to now (e.g., "2 hours ago", "in 5 minutes")
 * @param date - Date to format
 * @returns Relative time string
 */
export function formatRelativeTime(date: string | Date | Dayjs): string {
  if (!date) {
    return ''
  }

  return dayjs(date).fromNow()
}

/**
 * Check if date is today
 * @param date - Date to check
 * @returns True if date is today
 */
export function isToday(date: string | Date | Dayjs): boolean {
  if (!date) {
    return false
  }

  return dayjs(date).isSame(dayjs(), 'day')
}

/**
 * Check if date is yesterday
 * @param date - Date to check
 * @returns True if date is yesterday
 */
export function isYesterday(date: string | Date | Dayjs): boolean {
  if (!date) {
    return false
  }

  return dayjs(date).isSame(dayjs().subtract(1, 'day'), 'day')
}

/**
 * Check if date is within last N days
 * @param date - Date to check
 * @param days - Number of days
 * @returns True if date is within last N days
 */
export function isWithinDays(date: string | Date | Dayjs, days: number): boolean {
  if (!date) {
    return false
  }

  return dayjs(date).isAfter(dayjs().subtract(days, 'day'))
}

/**
 * Get start of day
 * @param date - Date to get start of (default: now)
 * @returns Start of day as Dayjs object
 */
export function startOfDay(date?: string | Date | Dayjs): Dayjs {
  return dayjs(date).startOf('day')
}

/**
 * Get end of day
 * @param date - Date to get end of (default: now)
 * @returns End of day as Dayjs object
 */
export function endOfDay(date?: string | Date | Dayjs): Dayjs {
  return dayjs(date).endOf('day')
}

/**
 * Get start of month
 * @param date - Date to get start of (default: now)
 * @returns Start of month as Dayjs object
 */
export function startOfMonth(date?: string | Date | Dayjs): Dayjs {
  return dayjs(date).startOf('month')
}

/**
 * Get end of month
 * @param date - Date to get end of (default: now)
 * @returns End of month as Dayjs object
 */
export function endOfMonth(date?: string | Date | Dayjs): Dayjs {
  return dayjs(date).endOf('month')
}

/**
 * Calculate difference between two dates
 * @param date1 - First date
 * @param date2 - Second date (default: now)
 * @param unit - Unit of measurement (default: 'day')
 * @returns Difference in specified unit
 */
export function dateDiff(
  date1: string | Date | Dayjs,
  date2?: string | Date | Dayjs,
  unit: 'second' | 'minute' | 'hour' | 'day' | 'week' | 'month' | 'year' = 'day'
): number {
  return dayjs(date1).diff(dayjs(date2), unit)
}

/**
 * Format duration in seconds to human readable string
 * @param seconds - Duration in seconds
 * @returns Formatted duration string (e.g., "1h 30m")
 */
export function formatDuration(seconds: number): string {
  if (seconds < 60) {
    return `${seconds}s`
  }

  const minutes = Math.floor(seconds / 60)
  if (minutes < 60) {
    return `${minutes}m`
  }

  const hours = Math.floor(minutes / 60)
  const remainingMinutes = minutes % 60

  if (hours < 24) {
    return remainingMinutes > 0 ? `${hours}h ${remainingMinutes}m` : `${hours}h`
  }

  const days = Math.floor(hours / 24)
  const remainingHours = hours % 24

  if (remainingHours > 0) {
    return `${days}d ${remainingHours}h`
  }

  return `${days}d`
}

/**
 * Parse date string to Dayjs object
 * @param dateString - Date string to parse
 * @returns Dayjs object
 */
export function parseDate(dateString: string): Dayjs {
  return dayjs(dateString)
}

/**
 * Get current timestamp in seconds
 * @returns Current timestamp in seconds
 */
export function getCurrentTimestamp(): number {
  return Math.floor(Date.now() / 1000)
}

/**
 * Convert timestamp to date
 * @param timestamp - Timestamp in seconds
 * @returns Date object
 */
export function timestampToDate(timestamp: number): Date {
  return new Date(timestamp * 1000)
}
