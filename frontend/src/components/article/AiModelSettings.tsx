import { useEffect, useState } from 'react';
import Input from '../ui/Input';
import { aiSettingApi } from '../../api/aiSetting';
import type { AiProviderInfo } from '../../types/api';

interface AiModelSettingsProps {
  provider: string;
  model: string;
  onChange: (data: { provider?: string; model?: string }) => void;
}

/** AI 供应商与模型选择：模型录入保存后即绑定当前登录用户，下次进入自动回填。 */
const AiModelSettings: React.FC<AiModelSettingsProps> = ({ provider, model, onChange }) => {
  const [providers, setProviders] = useState<AiProviderInfo[]>([]);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    // 拉取服务端供应商配置与当前用户绑定，初始化默认选择
    aiSettingApi.getMyAiSettings()
      .then((data) => {
        setProviders(data.providers);
        // 优先选已绑定模型的可用供应商，其次任一可用供应商
        const preferred = data.providers.find(p => p.available && p.user_model)
          || data.providers.find(p => p.available);
        if (preferred) {
          onChange({ provider: preferred.provider, model: preferred.user_model || preferred.default_model || '' });
        } else {
          onChange({ provider: '', model: '' });
        }
      })
      .catch((err) => {
        // 拉取失败时提示，不阻断表单
        setMessage('获取 AI 供应商配置失败');
        console.error('获取 AI 供应商配置失败:', err);
      });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  /** 切换供应商时回填该供应商的绑定模型或默认模型 */
  const handleProviderChange = (nextProvider: string) => {
    const info = providers.find(p => p.provider === nextProvider);
    onChange({ provider: nextProvider, model: info?.user_model || info?.default_model || '' });
    setMessage('');
  };

  /** 保存当前模型为该供应商的用户绑定 */
  const handleSave = async () => {
    if (!provider || !model.trim()) {
      setMessage('请先选择供应商并填写模型名称');
      return;
    }
    setSaving(true);
    setMessage('');
    try {
      await aiSettingApi.saveMyAiSetting(provider, model.trim());
      setMessage('已保存，将长期绑定您的账号');
      // 同步本地缓存的绑定值
      setProviders(prev => prev.map(p => p.provider === provider ? { ...p, user_model: model.trim() } : p));
    } catch (err) {
      // 保存失败时展示错误，不静默
      setMessage('保存失败，请稍后重试');
      console.error('保存 AI 模型绑定失败:', err);
    } finally {
      setSaving(false);
    }
  };

  const current = providers.find(p => p.provider === provider);
  const hasAvailable = providers.some(p => p.available);

  return (
    <>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">AI 供应商 <span className="text-blue-500">*</span></label>
        <select
          value={provider}
          onChange={(e) => handleProviderChange(e.target.value)}
          className="w-full px-3 py-2 border border-gray-200 rounded-lg bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          {!hasAvailable && <option value="">服务端未配置任何供应商密钥</option>}
          {providers.map(p => (
            <option key={p.provider} value={p.provider} disabled={!p.available}>
              {p.name}{p.available ? '' : '（服务端未配置密钥）'}
            </option>
          ))}
        </select>
        <p className="mt-1 text-xs text-gray-500">密钥由服务端环境变量提供，页面不采集任何密钥</p>
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">模型名称 <span className="text-blue-500">*</span></label>
        <Input
          type="text"
          value={model}
          onChange={(e) => onChange({ model: e.target.value })}
          placeholder={current?.default_model || '例如 deepseek-v4-flash-0731'}
          required
        />
        <p className="mt-1 text-xs text-gray-500">{current?.user_model ? `已绑定模型：${current.user_model}` : '保存后将绑定您的账号，下次自动回填'}</p>
      </div>
      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={handleSave}
          disabled={saving || !provider}
          className="px-3 py-1.5 text-sm bg-white border border-blue-200 text-blue-600 rounded-lg hover:bg-blue-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {saving ? '保存中...' : '保存为我的默认模型'}
        </button>
        {message && <span className={`text-xs ${message.includes('失败') || message.includes('请先') ? 'text-red-500' : 'text-green-600'}`}>{message}</span>}
      </div>
    </>
  );
};

export default AiModelSettings;
