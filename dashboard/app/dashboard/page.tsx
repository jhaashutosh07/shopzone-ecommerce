'use client';

import { useEffect, useState } from 'react';
import { api, DashboardStats } from '@/lib/api';
import {
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Clock,
  Users,
  Package
} from 'lucide-react';

function StatCard({
  title,
  value,
  subtitle,
  icon: Icon,
  trend,
  color = 'primary'
}: {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: any;
  trend?: 'up' | 'down' | null;
  color?: 'primary' | 'green' | 'red' | 'yellow';
}) {
  const colorClasses = {
    primary: 'bg-primary-50 text-primary-600',
    green: 'bg-green-50 text-green-600',
    red: 'bg-red-50 text-red-600',
    yellow: 'bg-yellow-50 text-yellow-600',
  };

  return (
    <div className="bg-white rounded-xl shadow-sm p-6">
      <div className="flex items-center justify-between">
        <div className={`p-3 rounded-lg ${colorClasses[color]}`}>
          <Icon className="h-6 w-6" />
        </div>
        {trend && (
          <div className={`flex items-center ${trend === 'up' ? 'text-green-600' : 'text-red-600'}`}>
            {trend === 'up' ? <TrendingUp className="h-4 w-4" /> : <TrendingDown className="h-4 w-4" />}
          </div>
        )}
      </div>
      <div className="mt-4">
        <h3 className="text-sm font-medium text-gray-500">{title}</h3>
        <p className="text-2xl font-bold text-gray-900 mt-1">{value}</p>
        {subtitle && <p className="text-sm text-gray-500 mt-1">{subtitle}</p>}
      </div>
    </div>
  );
}

function ScoreGauge({ score }: { score: number }) {
  const getColor = () => {
    if (score >= 70) return 'text-green-500';
    if (score >= 40) return 'text-yellow-500';
    return 'text-red-500';
  };

  return (
    <div className="relative w-32 h-32">
      <svg className="w-full h-full transform -rotate-90">
        <circle
          cx="64"
          cy="64"
          r="56"
          stroke="currentColor"
          strokeWidth="12"
          fill="none"
          className="text-gray-200"
        />
        <circle
          cx="64"
          cy="64"
          r="56"
          stroke="currentColor"
          strokeWidth="12"
          fill="none"
          strokeDasharray={`${score * 3.52} 352`}
          className={getColor()}
        />
      </svg>
      <div className="absolute inset-0 flex items-center justify-center">
        <span className="text-2xl font-bold">{score.toFixed(0)}</span>
      </div>
    </div>
  );
}

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getDashboardStats()
      .then(setStats)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!stats) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">Failed to load dashboard stats</p>
      </div>
    );
  }

  const weeklyTrend = stats.returns_this_week > stats.returns_last_week ? 'up' :
                      stats.returns_this_week < stats.returns_last_week ? 'down' : null;

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Dashboard Overview</h1>
        <p className="text-gray-500 mt-1">Monitor your return policy performance</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard
          title="Total Returns"
          value={stats.total_returns}
          subtitle={`${stats.returns_this_week} this week`}
          icon={Package}
          trend={weeklyTrend}
        />
        <StatCard
          title="Approved"
          value={stats.approved_returns}
          subtitle={`${stats.approval_rate}% approval rate`}
          icon={CheckCircle}
          color="green"
        />
        <StatCard
          title="Denied"
          value={stats.denied_returns}
          icon={XCircle}
          color="red"
        />
        <StatCard
          title="Pending Review"
          value={stats.pending_returns}
          icon={Clock}
          color="yellow"
        />
      </div>

      {/* Second Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        {/* Average Score Card */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Average Eligibility Score</h3>
          <div className="flex items-center justify-center">
            <ScoreGauge score={stats.avg_score} />
          </div>
          <p className="text-center text-sm text-gray-500 mt-4">
            {stats.avg_score >= 70 ? 'Most returns are eligible' :
             stats.avg_score >= 40 ? 'Moderate risk level' :
             'High fraud risk detected'}
          </p>
        </div>

        {/* Buyer Stats */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Buyer Analysis</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <Users className="h-5 w-5 text-gray-400 mr-3" />
                <span className="text-gray-600">Total Buyers</span>
              </div>
              <span className="font-semibold">{stats.total_buyers}</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <AlertTriangle className="h-5 w-5 text-red-400 mr-3" />
                <span className="text-gray-600">High Risk Buyers</span>
              </div>
              <span className="font-semibold text-red-600">{stats.high_risk_buyers}</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
              <div
                className="bg-red-500 h-2 rounded-full"
                style={{ width: `${stats.total_buyers > 0 ? (stats.high_risk_buyers / stats.total_buyers) * 100 : 0}%` }}
              />
            </div>
            <p className="text-sm text-gray-500">
              {stats.total_buyers > 0
                ? `${((stats.high_risk_buyers / stats.total_buyers) * 100).toFixed(1)}% of buyers flagged as high risk`
                : 'No buyer data yet'}
            </p>
          </div>
        </div>

        {/* Product Stats */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Product Analysis</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <Package className="h-5 w-5 text-gray-400 mr-3" />
                <span className="text-gray-600">Total Products</span>
              </div>
              <span className="font-semibold">{stats.total_products}</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <AlertTriangle className="h-5 w-5 text-yellow-400 mr-3" />
                <span className="text-gray-600">High Return Rate</span>
              </div>
              <span className="font-semibold text-yellow-600">{stats.high_return_products}</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
              <div
                className="bg-yellow-500 h-2 rounded-full"
                style={{ width: `${stats.total_products > 0 ? (stats.high_return_products / stats.total_products) * 100 : 0}%` }}
              />
            </div>
            <p className="text-sm text-gray-500">
              {stats.total_products > 0
                ? `${((stats.high_return_products / stats.total_products) * 100).toFixed(1)}% of products have high return rates`
                : 'No product data yet'}
            </p>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-xl shadow-sm p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <a
            href="/dashboard/returns?decision=review"
            className="flex items-center p-4 bg-yellow-50 rounded-lg hover:bg-yellow-100 transition-colors"
          >
            <Clock className="h-8 w-8 text-yellow-600 mr-4" />
            <div>
              <p className="font-medium text-gray-900">Review Pending</p>
              <p className="text-sm text-gray-500">{stats.pending_returns} returns need review</p>
            </div>
          </a>
          <a
            href="/dashboard/buyers?risk=high"
            className="flex items-center p-4 bg-red-50 rounded-lg hover:bg-red-100 transition-colors"
          >
            <AlertTriangle className="h-8 w-8 text-red-600 mr-4" />
            <div>
              <p className="font-medium text-gray-900">High Risk Buyers</p>
              <p className="text-sm text-gray-500">{stats.high_risk_buyers} buyers flagged</p>
            </div>
          </a>
          <a
            href="/dashboard/settings"
            className="flex items-center p-4 bg-primary-50 rounded-lg hover:bg-primary-100 transition-colors"
          >
            <Package className="h-8 w-8 text-primary-600 mr-4" />
            <div>
              <p className="font-medium text-gray-900">Configure Policies</p>
              <p className="text-sm text-gray-500">Adjust thresholds and windows</p>
            </div>
          </a>
        </div>
      </div>
    </div>
  );
}
