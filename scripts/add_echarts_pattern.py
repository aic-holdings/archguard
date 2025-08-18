#!/usr/bin/env python3
"""
Add ECharts Pattern with External URLs Test

This script adds an Apache ECharts chart implementation pattern to test
the new external URL routing functionality in ArchGuard.
"""

import os
import json
import logging
import asyncio
import uuid
from datetime import datetime, timezone
from dotenv import load_dotenv

# Add src to path for imports
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from archguard.vector_search import vector_search_engine

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_echarts_pattern():
    """Return the Apache ECharts implementation pattern with external URLs"""
    
    return {
        "title": "React Dashboard Charts with Apache ECharts",
        "guidance": """# React Dashboard Charts with Apache ECharts

Complete implementation for adding interactive charts to React dashboards using Apache ECharts with TypeScript.

## 📦 Required Dependencies

```bash
npm install echarts echarts-for-react
npm install --save-dev @types/echarts
```

## 🎯 Basic Chart Component

### Line Chart Component (`components/charts/LineChart.tsx`)

```typescript
import React from 'react';
import ReactECharts from 'echarts-for-react';
import * as echarts from 'echarts';

interface LineChartProps {
  data: Array<{
    name: string;
    value: number;
  }>;
  title?: string;
  height?: string;
  color?: string;
}

export function LineChart({ 
  data, 
  title = 'Line Chart', 
  height = '400px',
  color = '#3b82f6'
}: LineChartProps) {
  const option = {
    title: {
      text: title,
      left: 'center',
      textStyle: {
        fontSize: 16,
        fontWeight: 'bold'
      }
    },
    tooltip: {
      trigger: 'axis',
      formatter: '{b}: {c}'
    },
    xAxis: {
      type: 'category',
      data: data.map(item => item.name),
      axisLabel: {
        rotate: 45
      }
    },
    yAxis: {
      type: 'value'
    },
    series: [{
      data: data.map(item => item.value),
      type: 'line',
      smooth: true,
      lineStyle: {
        color: color,
        width: 3
      },
      itemStyle: {
        color: color
      },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: color },
          { offset: 1, color: 'transparent' }
        ])
      }
    }]
  };

  return (
    <ReactECharts
      option={option}
      style={{ height }}
      opts={{ renderer: 'canvas' }}
      theme="default"
    />
  );
}
```

## 📊 Multi-Chart Dashboard

### Dashboard Component (`components/Dashboard.tsx`)

```typescript
import React, { useState, useEffect } from 'react';
import { LineChart } from './charts/LineChart';
import { BarChart } from './charts/BarChart';
import { PieChart } from './charts/PieChart';

interface DashboardData {
  sales: Array<{ name: string; value: number }>;
  users: Array<{ name: string; value: number }>;
  categories: Array<{ name: string; value: number }>;
}

export function Dashboard() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulate API call
    const fetchData = async () => {
      try {
        // Replace with your actual API call
        const response = await fetch('/api/dashboard-data');
        const dashboardData = await response.json();
        setData(dashboardData);
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error);
        // Fallback sample data
        setData({
          sales: [
            { name: 'Jan', value: 1200 },
            { name: 'Feb', value: 1900 },
            { name: 'Mar', value: 1500 },
            { name: 'Apr', value: 2100 },
            { name: 'May', value: 1800 }
          ],
          users: [
            { name: 'Active', value: 2500 },
            { name: 'Inactive', value: 800 },
            { name: 'New', value: 400 }
          ],
          categories: [
            { name: 'Electronics', value: 35 },
            { name: 'Clothing', value: 28 },
            { name: 'Books', value: 20 },
            { name: 'Home', value: 17 }
          ]
        });
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="text-center text-gray-500 py-8">
        Failed to load dashboard data
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-3xl font-bold text-gray-900">Analytics Dashboard</h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Sales Chart */}
        <div className="bg-white p-6 rounded-lg shadow-md">
          <LineChart 
            data={data.sales}
            title="Monthly Sales"
            color="#10b981"
          />
        </div>

        {/* User Stats */}
        <div className="bg-white p-6 rounded-lg shadow-md">
          <PieChart 
            data={data.users}
            title="User Distribution"
          />
        </div>

        {/* Category Performance */}
        <div className="bg-white p-6 rounded-lg shadow-md lg:col-span-2">
          <BarChart 
            data={data.categories}
            title="Category Performance (%)"
            color="#f59e0b"
          />
        </div>
      </div>
    </div>
  );
}
```

## 📈 Bar Chart Component

### Bar Chart (`components/charts/BarChart.tsx`)

```typescript
import React from 'react';
import ReactECharts from 'echarts-for-react';

interface BarChartProps {
  data: Array<{
    name: string;
    value: number;
  }>;
  title?: string;
  height?: string;
  color?: string;
}

export function BarChart({ 
  data, 
  title = 'Bar Chart', 
  height = '400px',
  color = '#8b5cf6'
}: BarChartProps) {
  const option = {
    title: {
      text: title,
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    xAxis: {
      type: 'category',
      data: data.map(item => item.name)
    },
    yAxis: {
      type: 'value'
    },
    series: [{
      data: data.map(item => item.value),
      type: 'bar',
      itemStyle: {
        color: color,
        borderRadius: [4, 4, 0, 0]
      },
      emphasis: {
        itemStyle: {
          color: '#6366f1'
        }
      }
    }]
  };

  return (
    <ReactECharts
      option={option}
      style={{ height }}
      opts={{ renderer: 'canvas' }}
    />
  );
}
```

## 🥧 Pie Chart Component

### Pie Chart (`components/charts/PieChart.tsx`)

```typescript
import React from 'react';
import ReactECharts from 'echarts-for-react';

interface PieChartProps {
  data: Array<{
    name: string;
    value: number;
  }>;
  title?: string;
  height?: string;
}

export function PieChart({ 
  data, 
  title = 'Pie Chart', 
  height = '400px'
}: PieChartProps) {
  const option = {
    title: {
      text: title,
      left: 'center',
      top: 20
    },
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      top: 'middle'
    },
    series: [{
      name: title,
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['60%', '55%'],
      data: data,
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
        }
      },
      itemStyle: {
        borderRadius: 6,
        borderColor: '#fff',
        borderWidth: 2
      }
    }]
  };

  return (
    <ReactECharts
      option={option}
      style={{ height }}
      opts={{ renderer: 'canvas' }}
    />
  );
}
```

## 🔄 Real-time Data Updates

### WebSocket Integration

```typescript
import { useEffect, useState } from 'react';

export function useRealtimeChartData(endpoint: string) {
  const [data, setData] = useState(null);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    const ws = new WebSocket(endpoint);
    
    ws.onopen = () => {
      setConnected(true);
      console.log('WebSocket connected');
    };
    
    ws.onmessage = (event) => {
      try {
        const newData = JSON.parse(event.data);
        setData(newData);
      } catch (error) {
        console.error('Failed to parse WebSocket data:', error);
      }
    };
    
    ws.onclose = () => {
      setConnected(false);
      console.log('WebSocket disconnected');
    };
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
    
    return () => {
      ws.close();
    };
  }, [endpoint]);

  return { data, connected };
}
```

## 🎨 Responsive Design

### Mobile-First Chart Container

```typescript
export function ResponsiveChartContainer({ 
  children, 
  title 
}: { 
  children: React.ReactNode;
  title: string;
}) {
  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      <div className="px-4 py-3 border-b border-gray-200">
        <h3 className="text-lg font-medium text-gray-900">{title}</h3>
      </div>
      <div className="p-4">
        <div className="w-full h-64 sm:h-80 md:h-96">
          {children}
        </div>
      </div>
    </div>
  );
}
```

## 🧪 Testing Charts

### Chart Component Tests

```typescript
// __tests__/charts/LineChart.test.tsx
import { render, screen } from '@testing-library/react';
import { LineChart } from '../../components/charts/LineChart';

const mockData = [
  { name: 'Jan', value: 100 },
  { name: 'Feb', value: 200 },
  { name: 'Mar', value: 150 }
];

describe('LineChart', () => {
  test('renders chart with data', () => {
    render(<LineChart data={mockData} title="Test Chart" />);
    
    // Chart container should be present
    const chartContainer = screen.getByTitle('Test Chart');
    expect(chartContainer).toBeInTheDocument();
  });

  test('handles empty data gracefully', () => {
    render(<LineChart data={[]} title="Empty Chart" />);
    
    expect(() => {
      screen.getByTitle('Empty Chart');
    }).not.toThrow();
  });
});
```

## 🚀 Performance Optimization

### Lazy Loading Charts

```typescript
import { lazy, Suspense } from 'react';

const LineChart = lazy(() => import('./charts/LineChart'));
const BarChart = lazy(() => import('./charts/BarChart'));
const PieChart = lazy(() => import('./charts/PieChart'));

export function OptimizedDashboard() {
  return (
    <div className="dashboard">
      <Suspense fallback={<ChartSkeleton />}>
        <LineChart data={salesData} />
      </Suspense>
      
      <Suspense fallback={<ChartSkeleton />}>
        <BarChart data={categoryData} />
      </Suspense>
    </div>
  );
}

function ChartSkeleton() {
  return (
    <div className="animate-pulse bg-gray-200 h-64 rounded-lg"></div>
  );
}
```

## 🔧 Configuration

### Chart Theme Configuration

```typescript
// themes/chartTheme.ts
import * as echarts from 'echarts';

export const customTheme = {
  color: ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'],
  backgroundColor: 'transparent',
  textStyle: {
    fontFamily: 'Inter, sans-serif',
    color: '#374151'
  },
  title: {
    textStyle: {
      color: '#111827',
      fontSize: 18,
      fontWeight: 'bold'
    }
  },
  legend: {
    textStyle: {
      color: '#6b7280'
    }
  }
};

// Register the theme
echarts.registerTheme('custom', customTheme);
```

This implementation provides a complete, production-ready chart system with Apache ECharts, including responsive design, real-time updates, performance optimization, and comprehensive testing patterns.""",
        "category": "ux",
        "priority": "medium",
        "rationale": "Complete React + Apache ECharts implementation for dashboard charts. Includes line, bar, and pie charts with responsive design, real-time updates, and performance optimization. Perfect for data visualization in modern web applications.",
        "external_urls": {
            "get_started_guide": "https://github.com/apache/echarts-handbook/blob/master/contents/en/get-started.md",
            "react_integration": "https://echarts.apache.org/handbook/en/how-to/cross-platform/react/",
            "chart_options": "https://echarts.apache.org/en/option.html",
            "examples_gallery": "https://echarts.apache.org/examples/en/index.html"
        },
        "freshness_priority": "high",
        "source": ["https://echarts.apache.org/handbook/en/", "https://github.com/hustcc/echarts-for-react"],
        "loaded_at": datetime.now(timezone.utc).isoformat(),
        "last_retrieved": None
    }

async def main():
    """Add ECharts pattern with external URLs to vector database"""
    load_dotenv()
    
    logger.info("=" * 80)
    logger.info("ADDING ECHARTS PATTERN WITH EXTERNAL URLS")
    logger.info("=" * 80)
    
    # Check if vector search is available
    if not vector_search_engine.is_available():
        logger.error("❌ Vector search engine not available. Check Supabase configuration.")
        return
    
    # Get clients
    client = vector_search_engine._get_supabase_client()
    model = vector_search_engine._get_embedding_model()
    
    if not client or not model:
        logger.error("❌ Failed to initialize Supabase client or embedding model")
        return
    
    logger.info("✅ Vector search engine initialized successfully")
    
    # First, check if we need to add the external_urls column
    logger.info("\n🔧 Checking database schema...")
    
    try:
        # Try to select external_urls column to see if it exists
        result = client.table('rules').select('external_urls').limit(1).execute()
        logger.info("✅ external_urls column exists")
    except Exception as e:
        if "column" in str(e).lower() and "external_urls" in str(e).lower():
            logger.info("⚠️ external_urls column doesn't exist, attempting to add it...")
            try:
                # Add the column using SQL
                client.rpc('exec_sql', {
                    'sql': 'ALTER TABLE rules ADD COLUMN IF NOT EXISTS external_urls JSONB, ADD COLUMN IF NOT EXISTS freshness_priority TEXT DEFAULT \'medium\''
                }).execute()
                logger.info("✅ Added external_urls and freshness_priority columns")
            except Exception as add_error:
                logger.error(f"❌ Failed to add columns: {add_error}")
                logger.info("💡 You may need to run this SQL manually:")
                logger.info("   ALTER TABLE rules ADD COLUMN external_urls JSONB;")
                logger.info("   ALTER TABLE rules ADD COLUMN freshness_priority TEXT DEFAULT 'medium';")
                return
        else:
            logger.error(f"❌ Database error: {e}")
            return
    
    # Get the ECharts pattern
    logger.info("\n📥 Loading ECharts pattern to vector database...")
    
    echarts_pattern = get_echarts_pattern()
    
    try:
        logger.info(f"   Processing: {echarts_pattern['title']}")
        
        # Generate embedding for the guidance content
        guidance_text = f"{echarts_pattern['title']} {echarts_pattern['guidance']}"
        embedding = model.encode(guidance_text).tolist()
        
        logger.info(f"   ├── Generated embedding (size: {len(embedding)})")
        
        # Insert rule into database with metadata and external URLs
        rule_id = str(uuid.uuid4())
        
        # Prepare data with external URLs
        insert_data = {
            'rule_id': rule_id,
            'title': echarts_pattern['title'],
            'guidance': echarts_pattern['guidance'],
            'category': echarts_pattern['category'],
            'priority': echarts_pattern['priority'],
            'rationale': echarts_pattern['rationale'],
            'embedding': json.dumps(embedding),
            'project_id': None,  # Global rule  
            'created_by': None,  # Use None since this field expects UUID
            'keywords': ['echarts', 'charts', 'react', 'dashboard', 'visualization', 'typescript'],
            'source': json.dumps(echarts_pattern.get('source', [])),
            'loaded_at': echarts_pattern.get('loaded_at'),
            'last_retrieved': echarts_pattern.get('last_retrieved'),
            'external_urls': json.dumps(echarts_pattern['external_urls']),
            'freshness_priority': echarts_pattern['freshness_priority']
        }
        
        result = client.table('rules').insert(insert_data).execute()
        
        if result.data:
            rule_id = result.data[0]['rule_id']
            logger.info(f"   ✅ Successfully added rule ID: {rule_id}")
            logger.info(f"   ✅ External URLs added: {list(echarts_pattern['external_urls'].keys())}")
        else:
            logger.error(f"   ❌ Failed to add ECharts pattern")
            return
            
    except Exception as e:
        logger.error(f"   ❌ Error adding ECharts pattern: {e}")
        return
    
    # Test vector search with chart-related queries
    logger.info("\n🔍 Testing vector search with chart queries...")
    
    test_queries = [
        "add charts to my dashboard",
        "implement data visualization with React",
        "create interactive charts for analytics",
        "ECharts integration with TypeScript"
    ]
    
    for i, query in enumerate(test_queries, 1):
        logger.info(f"\n   Query {i}: '{query}'")
        
        try:
            relevant_rules = vector_search_engine.search_rules(query, limit=1)
            
            if relevant_rules:
                rule = relevant_rules[0]
                logger.info(f"   ✅ Found: {rule['title']} (similarity: {rule['similarity']:.3f})")
            else:
                logger.warning(f"   ⚠️ No relevant rules found")
                
        except Exception as e:
            logger.error(f"   ❌ Search failed: {e}")
    
    # Test AI guidance integration with external URLs
    logger.info("\n🤖 Testing AI guidance with external URLs...")
    
    from archguard.ai_guidance import guidance_engine
    
    try:
        response = guidance_engine.get_guidance(
            action="add charts to my React dashboard",
            context="Building an analytics dashboard with TypeScript"
        )
        
        logger.info("   ✅ AI guidance system test:")
        logger.info(f"      - Guidance items: {len(response.guidance)}")
        logger.info(f"      - Rules applied: {response.rules_applied}")
        logger.info(f"      - Complexity score: {response.complexity_score}")
        
        # Check if external URLs are included in response
        if hasattr(response, 'external_resources'):
            logger.info(f"      - External resources: {len(response.external_resources or [])}")
        else:
            logger.info("      - External resources: Not yet implemented in response")
        
    except Exception as e:
        logger.error(f"   ❌ AI guidance test failed: {e}")
    
    logger.info("\n" + "=" * 80)
    logger.info("✅ ECHARTS PATTERN WITH EXTERNAL URLS ADDED SUCCESSFULLY")
    logger.info("=" * 80)
    logger.info("\nPattern includes external URL routing to:")
    for key, url in echarts_pattern['external_urls'].items():
        logger.info(f"   - {key}: {url}")
    logger.info("\nReady for testing with Claude Code!")

if __name__ == "__main__":
    asyncio.run(main())