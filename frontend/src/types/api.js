/**
 * API 类型定义
 * @typedef {Object} ApiResponse
 * @property {number} code - 响应状态码
 * @property {string} message - 响应消息
 * @property {*} data - 响应数据
 */

/**
 * @typedef {Object} PaginatedResponse
 * @property {number} total - 总数
 * @property {number} page - 当前页
 * @property {number} size - 每页大小
 * @property {Array} items - 数据项
 */

/**
 * @typedef {Object} User
 * @property {number} id - 用户ID
 * @property {string} username - 用户名
 * @property {string} email - 邮箱
 * @property {'admin'|'user'} role - 角色
 * @property {boolean} is_active - 是否激活
 * @property {string} created_at - 创建时间
 */

/**
 * @typedef {Object} LoginResponse
 * @property {string} access_token - 访问令牌
 * @property {string} refresh_token - 刷新令牌
 * @property {string} token_type - 令牌类型
 * @property {User} user - 用户信息
 */

/**
 * @typedef {Object} Tag
 * @property {number} id - 标签ID
 * @property {string} name - 标签名称
 * @property {string} color - 标签颜色
 * @property {string} [created_at] - 创建时间
 */

/**
 * @typedef {Object} Article
 * @property {number} id - 文章ID
 * @property {string} title - 标题
 * @property {string|null} source_url - 来源URL
 * @property {string|null} summary - 摘要
 * @property {string|null} keywords - 关键词
 * @property {number} author_id - 作者ID
 * @property {string|null} original_filename - 原始文件名
 * @property {number} view_count - 查看次数
 * @property {string} created_at - 创建时间
 * @property {string} updated_at - 更新时间
 * @property {Tag[]} tags - 标签列表
 * @property {string|null} html_content - HTML内容
 * @property {string|null} html_path - HTML路径
 * @property {string|null} processing_status - 处理状态
 * @property {string|null} original_html_url - 原始HTML URL
 */

/**
 * @typedef {Object} ReadingStats
 * @property {number} article_id - 文章ID
 * @property {string} article_title - 文章标题
 * @property {number} total_views - 总查看次数
 * @property {number} total_duration - 总阅读时长
 * @property {string|null} last_read_at - 最后阅读时间
 */

/**
 * @typedef {Object} ReadingHistory
 * @property {number} id - 历史记录ID
 * @property {number} article_id - 文章ID
 * @property {string} article_title - 文章标题
 * @property {string} started_at - 开始时间
 * @property {string|null} ended_at - 结束时间
 * @property {number} reading_duration - 阅读时长
 * @property {number} reading_progress - 阅读进度
 */

export {};
