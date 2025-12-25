'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import { Save, Key, Copy, Check, AlertTriangle } from 'lucide-react';

export default function SettingsPage() {
  const [merchant, setMerchant] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [apiKey, setApiKey] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const [settings, setSettings] = useState({
    default_return_window: 30,
    fraud_threshold: 30,
    auto_approve_threshold: 70,
  });

  useEffect(() => {
    api.getMe()
      .then((data) => {
        setMerchant(data);
        setSettings({
          default_return_window: data.default_return_window,
          fraud_threshold: data.fraud_threshold,
          auto_approve_threshold: data.auto_approve_threshold,
        });
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const handleSave = async () => {
    setSaving(true);
    setMessage(null);
    try {
      await api.updateSettings(settings);
      setMessage({ type: 'success', text: 'Settings saved successfully' });
    } catch (error: any) {
      setMessage({ type: 'error', text: error.message || 'Failed to save settings' });
    } finally {
      setSaving(false);
    }
  };

  const handleGenerateApiKey = async () => {
    try {
      const { api_key } = await api.generateApiKey();
      setApiKey(api_key);
      setMessage({ type: 'success', text: 'New API key generated. Store it securely!' });
    } catch (error: any) {
      setMessage({ type: 'error', text: error.message || 'Failed to generate API key' });
    }
  };

  const copyApiKey = () => {
    if (apiKey) {
      navigator.clipboard.writeText(apiKey);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
        <p className="text-gray-500 mt-1">Configure your return policy and API access</p>
      </div>

      {message && (
        <div className={`mb-6 p-4 rounded-lg ${
          message.type === 'success' ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'
        }`}>
          {message.text}
        </div>
      )}

      {/* Policy Settings */}
      <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Return Policy Settings</h2>

        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Default Return Window (days)
            </label>
            <input
              type="number"
              min="1"
              max="365"
              value={settings.default_return_window}
              onChange={(e) => setSettings({ ...settings, default_return_window: parseInt(e.target.value) || 30 })}
              className="w-full max-w-xs px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
            <p className="mt-1 text-sm text-gray-500">
              Number of days after purchase that returns are accepted
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Auto-Deny Threshold (score)
            </label>
            <input
              type="number"
              min="0"
              max="100"
              value={settings.fraud_threshold}
              onChange={(e) => setSettings({ ...settings, fraud_threshold: parseInt(e.target.value) || 30 })}
              className="w-full max-w-xs px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
            <p className="mt-1 text-sm text-gray-500">
              Returns with scores below this will be automatically denied
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Auto-Approve Threshold (score)
            </label>
            <input
              type="number"
              min="0"
              max="100"
              value={settings.auto_approve_threshold}
              onChange={(e) => setSettings({ ...settings, auto_approve_threshold: parseInt(e.target.value) || 70 })}
              className="w-full max-w-xs px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
            <p className="mt-1 text-sm text-gray-500">
              Returns with scores above this will be automatically approved (no high-severity flags)
            </p>
          </div>

          {/* Threshold Visualization */}
          <div className="mt-6 p-4 bg-gray-50 rounded-lg">
            <p className="text-sm font-medium text-gray-700 mb-3">Score Zones</p>
            <div className="relative h-8 bg-gray-200 rounded-full overflow-hidden">
              <div
                className="absolute left-0 top-0 h-full bg-red-400"
                style={{ width: `${settings.fraud_threshold}%` }}
              />
              <div
                className="absolute top-0 h-full bg-yellow-400"
                style={{ left: `${settings.fraud_threshold}%`, width: `${settings.auto_approve_threshold - settings.fraud_threshold}%` }}
              />
              <div
                className="absolute right-0 top-0 h-full bg-green-400"
                style={{ width: `${100 - settings.auto_approve_threshold}%` }}
              />
            </div>
            <div className="flex justify-between mt-2 text-xs text-gray-500">
              <span>0 - Auto Deny</span>
              <span>{settings.fraud_threshold} - Manual Review - {settings.auto_approve_threshold}</span>
              <span>Auto Approve - 100</span>
            </div>
          </div>

          <button
            onClick={handleSave}
            disabled={saving}
            className="flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50"
          >
            <Save className="h-4 w-4 mr-2" />
            {saving ? 'Saving...' : 'Save Settings'}
          </button>
        </div>
      </div>

      {/* API Key Management */}
      <div className="bg-white rounded-xl shadow-sm p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">API Access</h2>

        <div className="space-y-4">
          <p className="text-sm text-gray-600">
            Use your API key to integrate the Return Policy Engine into your e-commerce platform.
            Include the key in the <code className="bg-gray-100 px-1 rounded">X-API-Key</code> header.
          </p>

          {apiKey ? (
            <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
              <div className="flex items-start">
                <AlertTriangle className="h-5 w-5 text-yellow-600 mr-2 flex-shrink-0 mt-0.5" />
                <div className="flex-1">
                  <p className="text-sm font-medium text-yellow-800">Your new API key</p>
                  <p className="text-xs text-yellow-600 mb-2">Store this securely. It won't be shown again.</p>
                  <div className="flex items-center bg-white border rounded p-2">
                    <code className="flex-1 text-sm font-mono break-all">{apiKey}</code>
                    <button
                      onClick={copyApiKey}
                      className="ml-2 p-1 hover:bg-gray-100 rounded"
                    >
                      {copied ? <Check className="h-5 w-5 text-green-600" /> : <Copy className="h-5 w-5 text-gray-500" />}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <button
              onClick={handleGenerateApiKey}
              className="flex items-center px-4 py-2 bg-gray-900 text-white rounded-lg hover:bg-gray-800"
            >
              <Key className="h-4 w-4 mr-2" />
              Generate New API Key
            </button>
          )}

          <div className="mt-6 p-4 bg-gray-50 rounded-lg">
            <p className="text-sm font-medium text-gray-700 mb-2">Example Request</p>
            <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg text-sm overflow-x-auto">
{`curl -X POST "http://localhost:8000/api/v1/score" \\
  -H "X-API-Key: your_api_key_here" \\
  -H "Content-Type: application/json" \\
  -d '{
    "buyer_id": "buyer_123",
    "product_id": "prod_456",
    "order_id": "order_789",
    "order_date": "2024-01-15T00:00:00Z",
    "order_amount": 99.99,
    "return_reason": "size_issue"
  }'`}
            </pre>
          </div>
        </div>
      </div>
    </div>
  );
}
