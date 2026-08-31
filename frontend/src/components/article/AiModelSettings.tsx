import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Input from '../ui/Input';
import { aiSettingApi } from '../../api/aiSetting';
import type { AiProviderInfo } from '../../types/api';

interface AiModelSettingsProps {
  provider: string;
  model: string;
  onChange: (data: { provider?: string; model?: string }) => void;
}

/** AI 供应商与模型选择：仅做选择，密钥配置请到左侧「API Key 设置」页面完成。 */
const AiModelSettings: React.FC<AiModelSettingsProps> = ({ provider, model, onChange }) => {
  const navigate = useNavigate();
  const [providers, setProviders] = useState<AiProviderInfo[]>([]);
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
          {!hasAvailable && <option value="">暂无可用的 AI 供应商</option>}
          {providers.map(p => (
            <option key={p.provider} value={p.provider} disabled={!p.available}>
              {p.name}{p.available ? '' : '（暂不可用）'}
            </option>
          ))}
        </select>
        {!hasAvailable && (
          <p className="mt-1 text-xs text-blue-600">
            <button type="button" onClick={() => navigate('/ai-settings')} className="underline hover:text-blue-800">
              前往左侧「API Key 设置」配置密钥后即可使用 AI 提取
            </button>
          </p>
        )}
        {message && <p className="mt-1 text-xs text-red-500">{message}</p>}
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
        <p className="mt-1 text-xs text-gray-500">{current?.user_model ? `已绑定模型：${current.user_model}` : '保存后在「API Key 设置」页绑定，下次自动回填'}</p>
      </div>
    </>
  );
};

export default AiModelSettings;