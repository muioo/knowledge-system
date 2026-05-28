import Input from '../ui/Input';

export const ZHIPU_MODEL_OPTIONS = [
  { label: 'GLM-4-Flash（默认）', value: 'glm-4-flash' },
  { label: 'GLM-4-Plus', value: 'glm-4-plus' },
  { label: 'GLM-4-Air', value: 'glm-4-air' },
  { label: 'GLM-4.5-Flash', value: 'glm-4.5-flash' },
  { label: '自定义模型', value: 'custom' },
];

interface ZhipuAiSettingsProps {
  apiKey: string;
  model: string;
  customModel: string;
  onChange: (data: { apiKey?: string; model?: string; customModel?: string }) => void;
}

const ZhipuAiSettings: React.FC<ZhipuAiSettingsProps> = ({ apiKey, model, customModel, onChange }) => {
  return (
    <>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">智谱 API Key <span className="text-blue-500">*</span></label>
        <Input type="password" value={apiKey} onChange={(e) => onChange({ apiKey: e.target.value })} placeholder="输入智谱 API Key" required />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">智谱模型 <span className="text-blue-500">*</span></label>
        <select
          value={model}
          onChange={(e) => onChange({ model: e.target.value })}
          className="w-full px-3 py-2 border border-gray-200 rounded-lg bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          {ZHIPU_MODEL_OPTIONS.map(option => (
            <option key={option.value} value={option.value}>{option.label}</option>
          ))}
        </select>
      </div>
      {model === 'custom' && (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">自定义模型名称 <span className="text-blue-500">*</span></label>
          <Input type="text" value={customModel} onChange={(e) => onChange({ customModel: e.target.value })} placeholder="例如 glm-4-flash" required />
        </div>
      )}
    </>
  );
};

export default ZhipuAiSettings;
