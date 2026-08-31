import apiClient from './client';
import type { AiProviderInfo } from '../types/api';

export const aiSettingApi = {
  /**
   * 获取服务端支持的 AI 供应商及当前用户绑定的模型
   */
  getMyAiSettings: async (): Promise<{ providers: AiProviderInfo[] }> => {
    // 拦截器已解一层返回 body 的 data 字段（即 { providers }）
    const response = await apiClient.get<any>('/users/me/ai-settings');
    return response.data;
  },

  /**
   * 保存当前用户在指定供应商上的模型绑定，可选同时更新自配密钥。
   * @param apiKey 用户自配密钥，传入则更新；不传/为空则保留已存密钥
   */
  saveMyAiSetting: async (provider: string, model: string, apiKey?: string): Promise<AiProviderInfo> => {
    const response = await apiClient.put<any>('/users/me/ai-settings', { provider, model, api_key: apiKey || undefined });
    return response.data;
  },
};
