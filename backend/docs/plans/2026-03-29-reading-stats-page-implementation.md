# 阅读统计页面重新设计实施计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 重新设计阅读统计页面，提供详细的阅读信息和记录展示，包括阅读趋势图表、时段分布分析和文章阅读进度详情。

**Architecture:** 采用仪表盘式布局，使用现有数据模型（ReadingHistory、ReadingStats），新增后端聚合接口，前端使用 Recharts 实现数据可视化。

**Tech Stack:**
- 后端: FastAPI, Tortoise-ORM
- 前端: React 19, TypeScript, Recharts, Tailwind CSS

---

## 前置准备

### Task 1: 安装前端图表库

**Files:**
- Modify: `frontend/package.json`

**Step 1: 安装 Recharts 和依赖**

```bash
cd frontend
npm install recharts date-fns
```

**Step 2: 验证安装**

检查 `package.json` 包含:
```json
"recharts": "^2.x.x"
"date-fns": "^3.x.x"
```

**Step 3: 提交**

```bash
git add frontend/package.json frontend/package-lock.json
git commit -m "chore: install recharts and date-fns for reading stats visualization"
```

---

## 后端实现

### Task 2: 新增阅读趋势接口

**Files:**
- Create: `backend/controllers/reading_trends_controller.py`
- Modify: `backend/api/v1/endpoints/reading.py`

**Step 1: 创建趋势控制器**

创建 `backend/controllers/reading_trends_controller.py`:

```python
from datetime import datetime, timedelta, timezone
from typing import List, Dict
from backend.models import ReadingHistory
from tortoise import functions

def get_now():
    return datetime.now(timezone.utc).astimezone()

async def get_reading_trends(user_id: int, days: int = 7) -> List[Dict]:
    """
    获取阅读趋势数据

    Args:
        user_id: 用户ID
        days: 天数 (7, 30, 90)

    Returns:
        [{ date: "2026-03-29", minutes: 45, articles: 3 }]
    """
    start_date = get_now() - timedelta(days=days)

    # 从阅读历史聚合数据
    histories = await ReadingHistory.filter(
        user_id=user_id,
        started_at__gte=start_date
    ).annotate(
        date=functions.TruncDate('started_at')
    ).group_by('date').values(
        'date',
        minutes=functions.Sum('reading_duration') / 60,
        articles=functions.Count('article_id', distinct=True)
    )

    # 填充缺失日期
    result = []
    date_map = {h['date'].strftime('%Y-%m-%d'): h for h in histories}

    for i in range(days):
        date = (get_now() - timedelta(days=days-1-i)).strftime('%Y-%m-%d')
        if date in date_map:
            result.append({
                'date': date,
                'minutes': int(date_map[date]['minutes'] or 0),
                'articles': date_map[date]['articles']
            })
        else:
            result.append({
                'date': date,
                'minutes': 0,
                'articles': 0
            })

    return result
```

**Step 2: 添加 API 路由**

修改 `backend/api/v1/endpoints/reading.py`，添加新路由:

```python
from backend.controllers.reading_trends_controller import get_reading_trends

@router.get("/trends")
async def get_trends(
    days: int = 7,
    current_user: User = Depends(get_current_user)
):
    """获取阅读趋势数据"""
    if days not in [7, 30, 90]:
        raise HTTPException(status_code=400, detail="days must be 7, 30, or 90")

    data = await get_reading_trends(current_user.id, days)
    return {
        "items": data,
        "total": len(data)
    }
```

**Step 3: 手动测试接口**

```bash
# 获取7天趋势
curl -X 'GET' 'http://127.0.0.1:8022/api/v1/reading/trends?days=7' \
  -H 'Authorization: Bearer YOUR_TOKEN'

# 预期返回
{
  "items": [
    {"date": "2026-03-23", "minutes": 45, "articles": 2},
    {"date": "2026-03-24", "minutes": 0, "articles": 0}
  ],
  "total": 7
}
```

**Step 4: 提交**

```bash
git add backend/controllers/reading_trends_controller.py backend/api/v1/endpoints/reading.py
git commit -m "feat: add reading trends API endpoint"
```

---

### Task 3: 新增时段分布接口

**Files:**
- Create: `backend/controllers/reading_time_distribution_controller.py`
- Modify: `backend/api/v1/endpoints/reading.py`

**Step 1: 创建时段分布控制器**

创建 `backend/controllers/reading_time_distribution_controller.py`:

```python
from datetime import datetime, timezone
from typing import List, Dict
from backend.models import ReadingHistory

def get_now():
    return datetime.now(timezone.utc).astimezone()

async def get_time_distribution(user_id: int) -> Dict:
    """
    获取阅读时段分布数据

    Returns:
    {
        periods: [
            { name: "早晨", count: 12, duration: 360, percentage: 25 }
        ],
        heatmap: [
            { hour: 9, day: 1, count: 5 }
        ]
    }
    """
    histories = await ReadingHistory.filter(user_id=user_id).all()

    # 定义时段
    period_map = {
        "morning": {"name": "早晨", "hours": range(6, 12), "count": 0, "duration": 0},
        "afternoon": {"name": "下午", "hours": range(12, 18), "count": 0, "duration": 0},
        "evening": {"name": "晚上", "hours": range(18, 24), "count": 0, "duration": 0},
        "night": {"name": "深夜", "hours": range(0, 6), "count": 0, "duration": 0},
    }

    # 热力图数据 (24小时 x 7天)
    heatmap = {hour: {day: 0 for day in range(7)} for hour in range(24)}

    total_count = 0
    total_duration = 0

    for h in histories:
        hour = h.started_at.hour
        day = h.started_at.weekday()

        # 统计时段
        for key, period in period_map.items():
            if hour in period["hours"]:
                period["count"] += 1
                period["duration"] += h.reading_duration
                break

        # 统计热力图
        heatmap[hour][day] += 1

        total_count += 1
        total_duration += h.reading_duration

    # 计算百分比并格式化时段数据
    periods = []
    for period in period_map.values():
        percentage = (period["duration"] / total_duration * 100) if total_duration > 0 else 0
        periods.append({
            "name": period["name"],
            "count": period["count"],
            "duration": period["duration"] // 60,  # 转换为分钟
            "percentage": round(percentage, 1)
        })

    # 格式化热力图数据
    heatmap_list = []
    for hour in range(24):
        for day in range(7):
            if heatmap[hour][day] > 0:
                heatmap_list.append({
                    "hour": hour,
                    "day": day,
                    "count": heatmap[hour][day]
                })

    return {
        "periods": periods,
        "heatmap": heatmap_list
    }
```

**Step 2: 添加 API 路由**

修改 `backend/api/v1/endpoints/reading.py`:

```python
from backend.controllers.reading_time_distribution_controller import get_time_distribution

@router.get("/time-distribution")
async def get_distribution(
    current_user: User = Depends(get_current_user)
):
    """获取阅读时段分布数据"""
    data = await get_time_distribution(current_user.id)
    return data
```

**Step 3: 手动测试接口**

```bash
curl -X 'GET' 'http://127.0.0.1:8022/api/v1/reading/time-distribution' \
  -H 'Authorization: Bearer YOUR_TOKEN'

# 预期返回
{
  "periods": [
    {"name": "早晨", "count": 5, "duration": 120, "percentage": 20.5}
  ],
  "heatmap": [
    {"hour": 9, "day": 1, "count": 3}
  ]
}
```

**Step 4: 提交**

```bash
git add backend/controllers/reading_time_distribution_controller.py backend/api/v1/endpoints/reading.py
git commit -m "feat: add reading time distribution API endpoint"
```

---

### Task 4: 新增阅读进度接口

**Files:**
- Modify: `backend/controllers/reading_controller.py`

**Step 1: 添加进度详情函数**

在 `backend/controllers/reading_controller.py` 末尾添加:

```python
async def get_reading_progress(user_id: int, page: int = 1, size: int = 20) -> tuple[List[Dict], int]:
    """
    获取文章阅读进度详情

    Returns:
        ([{
            article_id: 1,
            article_title: "...",
            total_views: 3,
            total_duration: 2700,
            reading_progress: 75,
            last_read_at: "2026-03-29T10:00:00Z"
        }], total)
    """
    total = await ReadingStats.filter(user_id=user_id).count()

    # 获取阅读统计，按最后阅读时间排序
    stats = await ReadingStats.filter(
        user_id=user_id
    ).order_by("-last_read_at").prefetch_related("article").offset((page - 1) * size).limit(size)

    # 获取最新的阅读进度（从阅读历史中获取最后一次的进度）
    result = []
    for s in stats:
        # 获取该文章最新的阅读记录
        latest_history = await ReadingHistory.filter(
            user_id=user_id,
            article_id=s.article_id
        ).order_by("-started_at").first()

        progress = latest_history.reading_progress if latest_history else 0

        result.append({
            "article_id": s.article_id,
            "article_title": s.article.title,
            "total_views": s.total_views,
            "total_duration": s.total_duration,
            "reading_progress": progress,
            "last_read_at": s.last_read_at.isoformat() if s.last_read_at else None
        })

    return result, total
```

**Step 2: 添加 API 路由**

修改 `backend/api/v1/endpoints/reading.py`:

```python
@router.get("/progress")
async def get_progress_endpoint(
    page: int = 1,
    size: int = 20,
    current_user: User = Depends(get_current_user)
):
    """获取阅读进度详情"""
    items, total = await get_reading_progress(current_user.id, page, size)
    return {
        "items": items,
        "total": total,
        "page": page,
        "size": size
    }
```

**Step 3: 手动测试接口**

```bash
curl -X 'GET' 'http://127.0.0.1:8022/api/v1/reading/progress?page=1&size=20' \
  -H 'Authorization: Bearer YOUR_TOKEN'

# 预期返回
{
  "items": [
    {
      "article_id": 1,
      "article_title": "测试文章",
      "total_views": 3,
      "total_duration": 2700,
      "reading_progress": 75,
      "last_read_at": "2026-03-29T10:00:00+08:00"
    }
  ],
  "total": 10,
  "page": 1,
  "size": 20
}
```

**Step 4: 提交**

```bash
git add backend/controllers/reading_controller.py backend/api/v1/endpoints/reading.py
git commit -m "feat: add reading progress API endpoint"
```

---

## 前端实现

### Task 5: 添加前端 API 调用函数

**Files:**
- Modify: `frontend/src/api/reading.ts`

**Step 1: 添加新的 API 函数**

修改 `frontend/src/api/reading.ts`，添加三个新函数:

```typescript
// 阅读趋势数据类型
export interface ReadingTrend {
  date: string;
  minutes: number;
  articles: number;
}

// 时段分布类型
export interface TimePeriod {
  name: string;
  count: number;
  duration: number;
  percentage: number;
}

export interface HeatmapData {
  hour: number;
  day: number;
  count: number;
}

export interface TimeDistribution {
  periods: TimePeriod[];
  heatmap: HeatmapData[];
}

// 阅读进度类型
export interface ReadingProgress {
  article_id: number;
  article_title: string;
  total_views: number;
  total_duration: number;
  reading_progress: number;
  last_read_at: string | null;
}

// 在 readingApi 对象中添加新方法
export const readingApi = {
  // ... 现有方法 ...

  // 获取阅读趋势
  getTrends: async (days = 7): Promise<{ items: ReadingTrend[]; total: number }> => {
    const response = await apiClient.get<any>('/reading/trends', {
      params: { days },
    });
    return response.data;
  },

  // 获取时段分布
  getTimeDistribution: async (): Promise<TimeDistribution> => {
    const response = await apiClient.get<any>('/reading/time-distribution');
    return response.data;
  },

  // 获取阅读进度
  getProgress: async (page = 1, size = 20): Promise<PaginatedResponse<ReadingProgress>> => {
    const response = await apiClient.get<any>('/reading/progress', {
      params: { page, size },
    });
    return response.data;
  },
};
```

**Step 2: 更新类型定义文件**

修改 `frontend/src/types/api.ts`，添加新类型:

```typescript
// 在文件末尾添加
export interface ReadingTrend {
  date: string;
  minutes: number;
  articles: number;
}

export interface TimePeriod {
  name: string;
  count: number;
  duration: number;
  percentage: number;
}

export interface HeatmapData {
  hour: number;
  day: number;
  count: number;
}

export interface TimeDistribution {
  periods: TimePeriod[];
  heatmap: HeatmapData[];
}

export interface ReadingProgress {
  article_id: number;
  article_title: string;
  total_views: number;
  total_duration: number;
  reading_progress: number;
  last_read_at: string | null;
}
```

**Step 3: 提交**

```bash
git add frontend/src/api/reading.ts frontend/src/types/api.ts
git commit -m "feat: add reading trends, time distribution, and progress API calls"
```

---

### Task 6: 创建概览卡片组件

**Files:**
- Create: `frontend/src/components/reading/OverviewCards.tsx`

**Step 1: 创建概览卡片组件**

创建 `frontend/src/components/reading/OverviewCards.tsx`:

```typescript
import React from 'react';

interface OverviewCardProps {
  icon: React.ReactNode;
  title: string;
  value: string | number;
  unit?: string;
  change?: number;
  color: string;
}

const OverviewCard: React.FC<OverviewCardProps> = ({ icon, title, value, unit, change, color }) => {
  const gradientColors: Record<string, string> = {
    blue: 'from-blue-500 to-blue-600',
    purple: 'from-purple-500 to-purple-600',
    orange: 'from-orange-500 to-orange-600',
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-100 p-6">
      <div className="flex items-center justify-between">
        <div className={`p-3 rounded-lg bg-gradient-to-br ${gradientColors[color] || gradientColors.blue}`}>
          {icon}
        </div>
        {change !== undefined && (
          <span className={`text-sm ${change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
            {change >= 0 ? '+' : ''}{change}%
          </span>
        )}
      </div>
      <div className="mt-4">
        <p className="text-sm text-gray-600">{title}</p>
        <p className="text-2xl font-bold text-gray-900 tabular-nums">
          {value}
          {unit && <span className="text-sm font-normal text-gray-600 ml-1">{unit}</span>}
        </p>
      </div>
    </div>
  );
};

interface OverviewCardsProps {
  totalDuration: number;
  totalArticles: number;
  weeklyDuration: number;
}

const OverviewCards: React.FC<OverviewCardsProps> = ({
  totalDuration,
  totalArticles,
  weeklyDuration
}) => {
  const formatHours = (seconds: number): string => {
    const hours = Math.floor(seconds / 3600);
    return hours.toString();
  };

  const formatMinutes = (seconds: number): string => {
    const minutes = Math.floor(seconds / 60);
    return minutes.toString();
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      <OverviewCard
        icon={<svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" /></svg>}
        title="总阅读时长"
        value={formatHours(totalDuration)}
        unit="小时"
        color="blue"
      />
      <OverviewCard
        icon={<svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" /></svg>}
        title="已读文章数"
        value={totalArticles}
        unit="篇"
        color="purple"
      />
      <OverviewCard
        icon={<svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 18.657A8 8 0 016.343 7.343S7 9 9 10c0-2 .5-5 2.986-7C14 5 16.09 5.777 17.656 7.343A7.975 7.975 0 0120 13a7.975 7.975 0 01-2.343 5.657z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.879 16.121A3 3 0 1012.015 11L11 14H9c0 .768.293 1.536.879 2.121z" /></svg>}
        title="本周阅读"
        value={formatMinutes(weeklyDuration)}
        unit="分钟"
        color="orange"
      />
    </div>
  );
};

export default OverviewCards;
```

**Step 2: 提交**

```bash
git add frontend/src/components/reading/OverviewCards.tsx
git commit -m "feat: add overview cards component"
```

---

### Task 7: 创建阅读趋势图表组件

**Files:**
- Create: `frontend/src/components/reading/ReadingTrendsChart.tsx`

**Step 1: 创建趋势图表组件**

创建 `frontend/src/components/reading/ReadingTrendsChart.tsx`:

```typescript
import React, { useState } from 'react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import { readingApi } from '../../api/reading';
import type { ReadingTrend } from '../../types/api';

interface ReadingTrendsChartProps {
  userId: number;
}

const ReadingTrendsChart: React.FC<ReadingTrendsChartProps> = ({ userId }) => {
  const [days, setDays] = useState(7);
  const [data, setData] = useState<ReadingTrend[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  React.useEffect(() => {
    fetchData();
  }, [days]);

  const fetchData = async () => {
    setIsLoading(true);
    try {
      const response = await readingApi.getTrends(days);
      setData(response.items);
    } catch (error) {
      console.error('Failed to fetch trends:', error);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-100 p-6">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-100 p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-semibold text-gray-900">阅读趋势</h2>
        <div className="flex gap-2">
          {[7, 30, 90].map((d) => (
            <button
              key={d}
              onClick={() => setDays(d)}
              className={`px-3 py-1 rounded-lg text-sm transition-colors ${
                days === d
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {d}天
            </button>
          ))}
        </div>
      </div>

      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey="date"
            tickFormatter={(value) => new Date(value).toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' })}
          />
          <YAxis yAxisId="left" orientation="left" stroke="#3b82f6" />
          <YAxis yAxisId="right" orientation="right" stroke="#10b981" />
          <Tooltip
            labelFormatter={(value) => new Date(value).toLocaleDateString('zh-CN')}
            formatter={(value: number, name: string) => [
              value,
              name === 'minutes' ? '分钟' : '篇'
            ]}
          />
          <Legend />
          <Bar yAxisId="left" dataKey="minutes" fill="#3b82f6" name="阅读时长(分钟)" />
          <Bar yAxisId="right" dataKey="articles" fill="#10b981" name="阅读文章数" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default ReadingTrendsChart;
```

**Step 2: 提交**

```bash
git add frontend/src/components/reading/ReadingTrendsChart.tsx
git commit -m "feat: add reading trends chart component"
```

---

### Task 8: 创建时段分布组件

**Files:**
- Create: `frontend/src/components/reading/TimeDistributionSection.tsx`

**Step 1: 创建时段分布组件**

创建 `frontend/src/components/reading/TimeDistributionSection.tsx`:

```typescript
import React, { useState, useEffect } from 'react';
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  Legend
} from 'recharts';
import { readingApi } from '../../api/reading';
import type { TimeDistribution, TimePeriod } from '../../types/api';

interface TimeDistributionSectionProps {
  userId: number;
}

const COLORS = ['#3b82f6', '#f59e0b', '#8b5cf6', '#6b7280'];

const TimePeriodPieChart: React.FC<{ data: TimePeriod[] }> = ({ data }) => {
  const chartData = data.map(item => ({
    name: item.name,
    value: item.duration
  }));

  return (
    <div>
      <h3 className="text-sm font-medium text-gray-700 mb-4">时段分布</h3>
      <ResponsiveContainer width="100%" height={250}>
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
            outerRadius={80}
            fill="#8884d8"
            dataKey="value"
          >
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip formatter={(value: number) => [`${value}分钟`, '阅读时长']} />
        </PieChart>
      </ResponsiveContainer>
      <div className="mt-4 space-y-2">
        {data.map((item, index) => (
          <div key={item.name} className="flex items-center justify-between text-sm">
            <div className="flex items-center gap-2">
              <div className={`w-3 h-3 rounded-full bg-[${COLORS[index]}]`}></div>
              <span className="text-gray-600">{item.name}</span>
            </div>
            <span className="text-gray-900 font-medium">{item.duration}分钟 ({item.percentage}%)</span>
          </div>
        ))}
      </div>
    </div>
  );
};

const TimeDistributionSection: React.FC<TimeDistributionSectionProps> = ({ userId }) => {
  const [data, setData] = useState<TimeDistribution | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setIsLoading(true);
    try {
      const response = await readingApi.getTimeDistribution();
      setData(response);
    } catch (error) {
      console.error('Failed to fetch time distribution:', error);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-100 p-6">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div>
      </div>
    );
  }

  if (!data) return null;

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-100 p-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-6">阅读时段分布</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <TimePeriodPieChart data={data.periods} />
        <div>
          <h3 className="text-sm font-medium text-gray-700 mb-4">阅读热力图</h3>
          <div className="text-sm text-gray-600">
            <p className="mb-2">一周内各时段的阅读活跃度</p>
            <div className="grid grid-cols-7 gap-1">
              {['一', '二', '三', '四', '五', '六', '日'].map((day) => (
                <div key={day} className="text-center text-xs text-gray-500">{day}</div>
              ))}
              {Array.from({ length: 24 }).map((_, hour) => (
                <React.Fragment key={hour}>
                  {Array.from({ length: 7 }).map((_, day) => {
                    const heatData = data.heatmap.find(h => h.hour === hour && h.day === day);
                    const intensity = heatData ? Math.min(heatData.count * 20, 100) : 0;
                    return (
                      <div
                        key={`${hour}-${day}`}
                        className="w-full aspect-square rounded-sm"
                        style={{
                          backgroundColor: intensity > 0
                            ? `rgba(59, 130, 246, ${intensity / 100})`
                            : '#f3f4f6'
                        }}
                        title={`${hour}:00 - ${heatData?.count || 0}次`}
                      />
                    );
                  })}
                </React.Fragment>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TimeDistributionSection;
```

**Step 2: 提交**

```bash
git add frontend/src/components/reading/TimeDistributionSection.tsx
git commit -m "feat: add time distribution section component"
```

---

### Task 9: 创建文章进度详情组件

**Files:**
- Create: `frontend/src/components/reading/ArticleProgressList.tsx`

**Step 1: 创建进度列表组件**

创建 `frontend/src/components/reading/ArticleProgressList.tsx`:

```typescript
import React, { useState, useEffect } from 'react';
import { readingApi } from '../../api/reading';
import type { ReadingProgress } from '../../types/api';
import { useNavigate } from 'react-router-dom';

interface ArticleProgressListProps {
  userId: number;
}

const ArticleProgressList: React.FC<ArticleProgressListProps> = ({ userId }) => {
  const [progress, setProgress] = useState<ReadingProgress[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setIsLoading(true);
    try {
      const response = await readingApi.getProgress(1, 50);
      setProgress(response.items);
    } catch (error) {
      console.error('Failed to fetch progress:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const formatDuration = (seconds: number): string => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return hours > 0 ? `${hours}小时${minutes}分钟` : `${minutes}分钟`;
  };

  const formatDate = (dateString: string | null): string => {
    if (!dateString) return '从未';
    return new Date(dateString).toLocaleDateString('zh-CN', {
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getProgressColor = (progress: number): string => {
    if (progress >= 100) return 'bg-green-500';
    if (progress >= 50) return 'bg-blue-500';
    return 'bg-gray-400';
  };

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-100 p-6">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div>
      </div>
    );
  }

  if (progress.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-100 p-6">
        <div className="text-center py-12 text-gray-500">暂无阅读记录</div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-100 p-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-6">文章阅读进度</h2>
      <div className="space-y-4">
        {progress.map((item) => (
          <div
            key={item.article_id}
            className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 transition-colors cursor-pointer"
            onClick={() => navigate(`/articles/${item.article_id}`)}
          >
            <div className="flex items-start justify-between mb-3">
              <h3 className="font-medium text-gray-900 flex-1">{item.article_title}</h3>
              <span className="text-xs text-gray-500 ml-4">{formatDate(item.last_read_at)}</span>
            </div>

            <div className="mb-2">
              <div className="flex items-center justify-between text-sm mb-1">
                <span className="text-gray-600">阅读进度</span>
                <span className="font-medium text-gray-900">{item.reading_progress}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className={`h-2 rounded-full transition-all ${getProgressColor(item.reading_progress)}`}
                  style={{ width: `${Math.min(item.reading_progress, 100)}%` }}
                />
              </div>
            </div>

            <div className="flex items-center gap-6 text-sm text-gray-600">
              <div className="flex items-center gap-1">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
                <span>阅读 {item.total_views} 次</span>
              </div>
              <div className="flex items-center gap-1">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span>累计 {formatDuration(item.total_duration)}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ArticleProgressList;
```

**Step 2: 提交**

```bash
git add frontend/src/components/reading/ArticleProgressList.tsx
git commit -m "feat: add article progress list component"
```

---

### Task 10: 重构阅读统计页面

**Files:**
- Modify: `frontend/src/pages/ReadingStats.tsx`

**Step 1: 重构页面**

将 `frontend/src/pages/ReadingStats.tsx` 替换为:

```typescript
import React, { useState, useEffect } from 'react';
import { readingApi, articleApi } from '../api/reading';
import OverviewCards from '../components/reading/OverviewCards';
import ReadingTrendsChart from '../components/reading/ReadingTrendsChart';
import TimeDistributionSection from '../components/reading/TimeDistributionSection';
import ArticleProgressList from '../components/reading/ArticleProgressList';
import { useAuth } from '../contexts/AuthContext';

const ReadingStats: React.FC = () => {
  const { user } = useAuth();
  const [totalDuration, setTotalDuration] = useState(0);
  const [totalArticles, setTotalArticles] = useState(0);
  const [weeklyDuration, setWeeklyDuration] = useState(0);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchOverviewData();
  }, []);

  const fetchOverviewData = async () => {
    if (!user) return;
    setIsLoading(true);
    try {
      // 获取所有阅读进度统计
      const progressData = await readingApi.getProgress(1, 1000);

      // 计算总时长和文章数
      const totalDur = progressData.items.reduce((sum, item) => sum + item.total_duration, 0);
      const totalArts = progressData.items.length;

      // 获取本周阅读时长（通过阅读历史计算）
      const statsData = await readingApi.getStats(1, 1000);
      const weeklyDur = statsData.items
        .filter(item => {
          if (!item.last_read_at) return false;
          const lastRead = new Date(item.last_read_at);
          const now = new Date();
          const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
          return lastRead >= weekAgo;
        })
        .reduce((sum, item) => sum + item.total_duration, 0);

      setTotalDuration(totalDur);
      setTotalArticles(totalArts);
      setWeeklyDuration(weeklyDur);
    } catch (error) {
      console.error('Failed to fetch overview data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="max-w-6xl mx-auto">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">阅读统计</h1>
          <p className="text-gray-600">查看您的阅读历史和统计数据</p>
        </div>
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">阅读统计</h1>
        <p className="text-gray-600">查看您的阅读历史和统计数据</p>
      </div>

      {/* 概览卡片 */}
      <OverviewCards
        totalDuration={totalDuration}
        totalArticles={totalArticles}
        weeklyDuration={weeklyDuration}
      />

      {/* 阅读趋势图表 */}
      {user && <ReadingTrendsChart userId={user.id} />}

      {/* 阅读时段分布 */}
      {user && <TimeDistributionSection userId={user.id} />}

      {/* 文章阅读进度 */}
      {user && <ArticleProgressList userId={user.id} />}
    </div>
  );
};

export default ReadingStats;
```

**注意：** 需要修复 `reading.ts` 导出问题，创建单独的 `article.ts` API 文件或从现有位置导入。

**Step 2: 修复导入问题**

检查并确保 `frontend/src/api/reading.ts` 正确导出 `readingApi`:

```typescript
// 确保文件末尾有正确的导出
export const readingApi = {
  getStats,
  getHistory,
  getTrends,
  getTimeDistribution,
  getProgress,
};
```

**Step 3: 测试页面**

```bash
cd frontend
npm run dev
```

访问 http://localhost:5173/reading-stats 查看效果

**Step 4: 提交**

```bash
git add frontend/src/pages/ReadingStats.tsx
git commit -m "feat: redesign reading stats page with dashboard layout"
```

---

## 测试

### Task 11: 端到端测试

**Step 1: 后端接口测试**

```bash
# 测试趋势接口
curl -X 'GET' 'http://127.0.0.1:8022/api/v1/reading/trends?days=7' \
  -H 'Authorization: Bearer YOUR_TOKEN'

# 测试时段分布接口
curl -X 'GET' 'http://127.0.0.1:8022/api/v1/reading/time-distribution' \
  -H 'Authorization: Bearer YOUR_TOKEN'

# 测试进度接口
curl -X 'GET' 'http://127.0.0.1:8022/api/v1/reading/progress?page=1&size=20' \
  -H 'Authorization: Bearer YOUR_TOKEN'
```

**Step 2: 前端功能测试**

1. 启动前端: `cd frontend && npm run dev`
2. 登录系统
3. 访问阅读统计页面
4. 验证以下功能：
   - 概览卡片显示正确数据
   - 趋势图表可以切换7/30/90天
   - 时段分布饼图显示正确
   - 热力图显示正确
   - 进度列表显示所有文章
   - 点击文章可跳转到详情

**Step 3: 响应式测试**

调整浏览器窗口大小，验证移动端布局：
- 概览卡片自动换行
- 图表自适应宽度
- 时段分布和热力图上下堆叠

**Step 4: 提交测试结果**

```bash
git add .
git commit -m "test: verify reading stats page functionality"
```

---

## 完成检查清单

- [ ] Recharts 和 date-fns 已安装
- [ ] 后端三个新接口已实现并测试
- [ ] 前端 API 调用函数已添加
- [ ] 概览卡片组件已创建
- [ ] 趋势图表组件已创建
- [ ] 时段分布组件已创建
- [ ] 进度列表组件已创建
- [ ] 阅读统计页面已重构
- [ ] 所有功能已测试通过
- [ ] 响应式布局已验证

---

## 后续优化建议

1. **性能优化**: 对于大量数据，考虑添加虚拟滚动
2. **缓存**: 添加前端缓存减少 API 调用
3. **导出功能**: 添加数据导出为 CSV/Excel
4. **更多图表**: 添加文章类型分布、标签热度等
5. **目标系统**: 实现阅读目标设定和追踪
