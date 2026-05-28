import Input from '../ui/Input';
import ZhipuAiSettings from './ZhipuAiSettings';

export interface UrlImportFormData {
  url: string;
  title: string;
  useAi: boolean;
  summary: string;
  keywords: string;
  apiKey: string;
  model: string;
  customModel: string;
}

interface UrlImportFieldsProps {
  data: UrlImportFormData;
  onChange: (data: Partial<UrlImportFormData>) => void;
}

const UrlImportFields: React.FC<UrlImportFieldsProps> = ({ data, onChange }) => {
  return (
    <>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">文章 URL <span className="text-blue-500">*</span></label>
        <Input type="url" value={data.url} onChange={(e) => onChange({ url: e.target.value })} placeholder="https://example.com/article" required />
        <p className="mt-1 text-xs text-gray-500">系统将自动抓取网页内容</p>
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">标题（可选）</label>
        <Input type="text" value={data.title} onChange={(e) => onChange({ title: e.target.value })} placeholder="留空则使用网页标题" />
      </div>

      <div className="border-t border-gray-100 pt-4">
        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            checked={data.useAi}
            onChange={(e) => onChange({ useAi: e.target.checked })}
            className="w-4 h-4 text-blue-500 rounded border-gray-300 focus:ring-blue-500"
          />
          <span className="text-sm font-medium text-gray-700">使用智谱 AI 提取摘要和关键词</span>
        </label>
        <p className="mt-1 ml-6 text-xs text-gray-500">API Key 只会随本次导入请求发送，不会保存在后端配置中</p>
      </div>

      {data.useAi ? (
        <ZhipuAiSettings
          apiKey={data.apiKey}
          model={data.model}
          customModel={data.customModel}
          onChange={onChange}
        />
      ) : (
        <>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">摘要 <span className="text-blue-500">*</span></label>
            <textarea value={data.summary} onChange={(e) => onChange({ summary: e.target.value })} placeholder="请输入文章摘要" rows={3} className="w-full px-3 py-2 border border-gray-200 rounded-lg bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500" required />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">关键词 <span className="text-blue-500">*</span></label>
            <Input type="text" value={data.keywords} onChange={(e) => onChange({ keywords: e.target.value })} placeholder="请输入关键词，用逗号分隔" required />
          </div>
        </>
      )}
    </>
  );
};

export default UrlImportFields;
