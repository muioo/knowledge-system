# 基于滚动位置的阅读进度跟踪功能

## 概述

实现了基于用户滚动位置的实时阅读进度跟踪功能，相比之前的手动输入进度，现在可以自动、准确地记录用户的真实阅读进度。

## 功能特点

### 1. 实时进度跟踪
- 📜 **自动监听滚动**：用户滚动文章时自动记录阅读位置
- 🎯 **精确计算**：基于像素位置计算阅读百分比
- ⚡ **性能优化**：使用防抖机制，减少API请求频率
- 💾 **自动保存**：页面离开时自动保存最终进度

### 2. 进度显示
- 📊 **浮动进度条**：右下角显示当前阅读进度
- 📈 **实时更新**：滚动时实时更新进度百分比
- 🎨 **视觉反馈**：蓝色进度条显示完成度

### 3. 数据模型

#### 新增字段
```python
class ReadingHistory:
    scroll_position: int          # 滚动位置（像素）
    total_content_length: int     # 总内容长度（像素）
    actual_progress: int           # 实际阅读进度（0-100）
```

### 4. API 端点

| 方法 | 端点 | 说明 |
|------|------|------|
| PUT | `/reading/articles/{id}/progress` | 更新阅读进度 |

### 5. 使用流程

```
用户进入文章详情页
    ↓
startReading() - 创建阅读记录
    ↓
用户滚动文章
    ↓
监听滚动事件（防抖500ms）
    ↓
计算：actual_progress = (scrollY / totalScrollHeight) × 100
    ↓
发送进度到后端：PUT /reading/articles/{id}/progress
    ↓
更新数据库：scroll_position, actual_progress
    ↓
页面离开时自动保存最终进度
```

## 技术实现

### 前端

**滚动监听**：
```typescript
useEffect(() => {
  const handleScroll = () => {
    // 防抖500ms
    clearTimeout(scrollTimeoutRef.current);
    scrollTimeoutRef.current = setTimeout(async () => {
      const scrollPosition = window.scrollY;
      const totalContentLength = document.documentElement.scrollHeight - window.innerHeight;
      const actualProgress = Math.round((scrollPosition / totalContentLength) * 100);

      await readingApi.updateProgress(articleId, {
        scroll_position: Math.round(scrollPosition),
        total_content_length: Math.round(totalContentLength),
        actual_progress: actualProgress
      });
    }, 500);
  };

  window.addEventListener('scroll', handleScroll, { passive: true });
}, []);
```

**页面离开保存**：
```typescript
const handleBeforeUnload = () => {
  // 使用 sendBeacon 确保数据发送
  navigator.sendBeacon(url, JSON.stringify(data));
};
```

### 后端

**更新进度函数**：
```python
async def update_reading_progress(user_id, article_id, data):
    # 获取当前活动的阅读记录
    history = await ReadingHistory.filter(
        user_id=user_id,
        article_id=article_id,
        ended_at=None  # 只更新未结束的记录
    ).order_by("-started_at").first()

    # 更新滚动位置和进度
    history.scroll_position = data.scroll_position
    history.total_content_length = data.total_content_length
    history.actual_progress = data.actual_progress
    await history.save()

    # 同步更新阅读统计
    stats.last_reading_progress = data.actual_progress
    if data.actual_progress > stats.max_reading_progress:
        stats.max_reading_progress = data.actual_progress
    await stats.save()
```

## 数据库迁移

运行迁移脚本：
```bash
cd backend
python migrate_scroll_progress.py
```

**迁移内容**：
- 添加 `scroll_position` 字段
- 添加 `total_content_length` 字段
- 添加 `actual_progress` 字段

## 优势

| 特性 | 手动输入 | 滚动跟踪 |
|------|----------|----------|
| 准确性 | ❌ 不准确 | ✅ 精确 |
| 实时性 | ❌ 需手动更新 | ✅ 实时自动 |
| 用户体验 | ❌ 需要操作 | ✅ 无感知 |
| 数据完整性 | ❌ 依赖用户 | ✅ 自动记录 |

## 注意事项

1. **防抖机制**：滚动停止500ms后才发送请求，减少API调用
2. **页面离开保存**：使用 `sendBeacon` 确保数据不丢失
3. **只更新未结束记录**：只更新 `ended_at=NULL` 的记录
4. **防止重复记录**：使用 `useRef` 防止 React StrictMode 重复调用

## 未来优化

- [ ] 支持不同设备的阅读位置同步
- [ ] 添加阅读书签功能
- [ ] 支持章节级别的进度跟踪
- [ ] 添加阅读时间预测
