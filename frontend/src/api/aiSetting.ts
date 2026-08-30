import apiClient from './client';
import type { AiProviderInfo } from '../types/api';

export const aiSettingApi = {
  /**
   * 获取服务端支持的 AI 供应商及当前用户绑定的模型
   */
  getMyAiSettings: async (): Promise<{ providers: AiProviderInfo[] }> => {
    const response = await apiClient.get<any>('/users/me/ai-settings');
    return response.data.data;
  },

  /**
   * 保存当前用户在指定供应商上的模型绑定
   */
  saveMyAiSetting: async (provider: string, model: string): Promise<AiProviderInfo> => {
    const response = await apiClient.put<any>('/users/me/ai-settings', { provider, model });
    return response.data.data;
  },
};
