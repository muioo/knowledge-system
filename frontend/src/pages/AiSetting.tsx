import React, { useEffect, useState } from 'react';
import Card from '../components/ui/Card';
import Input from '../components/ui/Input';
import { aiSettingApi } from '../api/aiSetting';
import type { AiProviderInfo } from '../types/api';

// 每个供应商可独立编辑的表单项
interface RowState {
  model: string;
  apiKey: string;
}

/**
 * AiSetting 页面 - 在侧边栏即可进入的"API Key 设置"
 * 每个供应商可独立录入模型与自配密钥；密钥后端加密绑定到当前账号，不回显明文。
 */
const AiSetting: React.FC = () => {
  const [providers, setProviders] = useState<AiProviderInfo[]>([]);
  // 以 provider 为 key 保存各供应商的本地编辑态
  const [inputs, setInputs] = useState<Record<string, RowState>>({});
  const [saving, setSaving] = useState(''); // 正在保存的 provider，用于按钮 loading
  const [loading, setLoading] = useState(false);
  const [msg, setMsg] = useState<{ provider: string; text: string; ok: boolean } | null>(null);

  // 拉取供应商列表，初始化每个供应商的模型为已绑定模型或默认模型
  const load = () => {
    setLoading(true);
    setMsg(null);
    aiSettingApi.getMyAiSettings()
      .then((data) => {
        setProviders(data.providers);
        const next: Record<string, RowState> = {};
        data.providers.forEach((p) => {
          next[p.provider] = { model: p.user_model || p.default_model || '', apiKey: '' };
        });
        setInputs(next);
      })
      .catch((err) => {
        setMsg({ provider: '', text: '加载 AI 供应商配置失败，请稍后重试', ok: false });
        console.error('加载 AI 供应商配置失败:', err);
      })
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  const updateRow = (provider: string, patch: Partial<RowState>) => {
    setInputs((prev) => ({ ...prev, [provider]: { ...prev[provider], ...patch } }));
    // 编辑时清空该行之前的提示
    if (msg && msg.provider === provider) setMsg(null);
  };

  /** 保存某个供应商的模型与可选的自配密钥 */
  const save = async (provider: string) => {
    const row = inputs[provider];
    if (!row || !row.model.trim()) {
      setMsg({ provider, text: '请填写模型名称', ok: false });
      return;
    }
    setSaving(provider);
    setMsg(null);
    try {
      const updated = await aiSettingApi.saveMyAiSetting(provider, row.model.trim(), row.apiKey || undefined);
      setMsg({
        provider,
        text: row.apiKey.trim()
          ? '已保存，密钥已加密绑定到您的账号'
          : '已保存，将长期绑定您的账号',
        ok: true,
      });
      // 同步本地绑定状态（has_apikey 由后端返回）
      setProviders((prev) =>
        prev.map((p) =>
          p.provider === provider
            ? { ...p, user_model: row.model.trim(), has_apikey: updated.has_apikey }
            : p
        )
      );
      // 保存成功后清空密钥输入框，避免误重复提交
      updateRow(provider, { apiKey: '' });
    } catch (err: unknown) {
      // 展示后端返回的明确错误，不静默
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setMsg({ provider: provider, text: detail || '保存失败，请稍后重试', ok: false });
      console.error('保存 AI 配置失败:', err);
    } finally {
      setSaving('');
    }
  };

  return (
    <div className="w-full space-y-6">
      <div>
        <h1 className="text-xl font-semibold">API Key 设置</h1>
        <p className="mt-1 text-sm text-gray-500">
          在此为各 AI 供应商自配模型与密钥，保存后仅加密绑定到您的账号，明文不回显。配置后即可在"添加文章→URL 导入"中勾选"使用 AI 提取"。
        </p>
      </div>

      {msg && msg.provider === '' && (
        <div className={`p-3 rounded-lg text-sm ${msg.ok ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-600'}`}>
          {msg.text}
        </div>
      )}

      {loading ? (
        <Card><p className="text-sm text-gray-500">加载中...</p></Card>
      ) : (
        providers.map((p) => {
          const row = inputs[p.provider] || { model: '', apiKey: '' };
          const rowMsg = msg && msg.provider === p.provider ? msg : null;
          const isSaving = saving === p.provider;
          return (
            <Card key={p.provider}>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">{p.name}</p>
                    <p className="text-xs text-gray-500">
                      {p.available ? '可用' : '未配置密钥，暂不可用于 AI 提取'}
                      {p.has_apikey ? ' · 已绑定自配密钥' : ''}
                    </p>
                  </div>
                  <span className={`px-2 py-1 text-xs rounded-full ${p.available ? 'bg-green-50 text-green-700' : 'bg-gray-100 text-gray-500'}`}>
                    {p.available ? '已就绪' : '未就绪'}
                  </span>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">模型名称 <span className="text-blue-500">*</span></label>
                  <Input
                    type="text"
                    value={row.model}
                    onChange={(e) => updateRow(p.provider, { model: e.target.value })}
                    placeholder={p.default_model || '例如 deepseek-v4-flash-0731'}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">API 密钥（可选）</label>
                  <Input
                    type="password"
                    value={row.apiKey}
                    onChange={(e) => updateRow(p.provider, { apiKey: e.target.value })}
                    placeholder={p.has_apikey ? '已配置自配密钥（不回显明文），输入新值可覆盖' : '不填则使用服务端环境变量密钥'}
                    autoComplete="off"
                  />
                  <p className="mt-1 text-xs text-gray-500">
                    {p.has_apikey ? '已绑定密钥仅加密存储，不会回显' : '密钥只加密保存到您的账号，提取时优先使用'}
                  </p>
                </div>

                <div className="flex items-center gap-3">
                  <button
                    type="button"
                    onClick={() => save(p.provider)}
                    disabled={isSaving}
                    className="px-3 py-1.5 text-sm bg-white border border-blue-200 text-blue-600 rounded-lg hover:bg-blue-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    {isSaving ? '保存中...' : '保存'}
                  </button>
                  {rowMsg && (
                    <span className={`text-xs ${rowMsg.ok ? 'text-green-600' : 'text-red-500'}`}>{rowMsg.text}</span>
                  )}
                </div>
              </div>
            </Card>
          );
        })
      )}
    </div>
  );
};

export default AiSetting;