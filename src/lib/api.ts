import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios';

// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';
const API_TIMEOUT = parseInt(import.meta.env.VITE_API_TIMEOUT || '10000');

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for debugging
apiClient.interceptors.request.use(
  (config) => {
    console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('❌ API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    console.log(`✅ API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error: AxiosError) => {
    console.error('❌ API Response Error:', error.response?.status, error.message);
    
    // Handle common errors
    if (error.response?.status === 404) {
      console.error('Resource not found');
    } else if (error.response?.status === 500) {
      console.error('Internal server error');
    } else if (error.code === 'ECONNREFUSED') {
      console.error('Backend server is not running. Please start the FastAPI server.');
    }
    
    return Promise.reject(error);
  }
);

// API Response Types
export interface ApiResponse<T = any> {
  data: T;
  message?: string;
  status: number;
}

export interface CaseQuery {
  id: number;
  case_number: string;
  court_name: string;
  case_title: string;
  case_type: string;
  filing_date: string;
  next_hearing_date: string | null;
  case_status: string;
  petitioner: string;
  respondent: string;
  judge_name: string | null;
  created_at: string;
  updated_at: string;
}

export interface CauseListEntry {
  id: number;
  court_name: string;
  date: string;
  case_number: string;
  case_title: string;
  petitioner: string;
  respondent: string;
  hearing_time: string | null;
  courtroom: string | null;
  judge_name: string | null;
  case_status: string;
  remarks: string | null;
  created_at: string;
  updated_at: string;
}

export interface DriveFile {
  id: string;
  name: string;
  type: string;
  size?: number;
  modified_time?: string;
  mime_type?: string;
  web_view_link?: string;
}

export interface DriveListResponse {
  files: DriveFile[];
  folder_path: string;
  total_files: number;
}

export interface FileSummary {
  id: number;
  file_id: string;
  file_name: string;
  summary: string;
  key_points: string[];
  created_at: string;
}

// Court API Services
export const courtApi = {
  // Get case details by case number
  async getCaseDetails(caseNumber: string): Promise<CaseQuery> {
    const response = await apiClient.get<CaseQuery>(`/api/court/query/${caseNumber}`);
    return response.data;
  },

  // Submit a new case query
  async submitCaseQuery(data: {
    case_number: string;
    court_name: string;
  }): Promise<CaseQuery> {
    const response = await apiClient.post<CaseQuery>('/api/court/query', data);
    return response.data;
  },

  // Get cause list for a specific court and date
  async getCauseList(params: {
    court_name?: string;
    date?: string;
    limit?: number;
    skip?: number;
  } = {}): Promise<CauseListEntry[]> {
    const response = await apiClient.get<CauseListEntry[]>('/api/court/cause-list', { params });
    return response.data;
  },

  // Create a new cause list entry
  async createCauseListEntry(data: {
    court_name: string;
    date: string;
    case_number: string;
    case_title: string;
    petitioner: string;
    respondent: string;
    hearing_time?: string;
    courtroom?: string;
    judge_name?: string;
    case_status: string;
    remarks?: string;
  }): Promise<CauseListEntry> {
    const response = await apiClient.post<CauseListEntry>('/api/court/cause-list', data);
    return response.data;
  },
};

// Drive API Services
export const driveApi = {
  // List files from Google Drive
  async listFiles(params: {
    query?: string;
    limit?: number;
    folder_id?: string;
  } = {}): Promise<DriveFile[]> {
    const response = await apiClient.get<DriveListResponse>('/api/drive/files', { params });
    return response.data.files; // Extract the files array from the response
  },

  // Upload file to Google Drive
  async uploadFile(file: File, folderId?: string): Promise<DriveFile> {
    const formData = new FormData();
    formData.append('file', file);
    if (folderId) {
      formData.append('folder_id', folderId);
    }

    const response = await apiClient.post<DriveFile>('/api/drive/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Download file from Google Drive
  async downloadFile(fileId: string): Promise<Blob> {
    const response = await apiClient.get(`/api/drive/download/${fileId}`, {
      responseType: 'blob',
    });
    return response.data;
  },

  // Summarize document using AI
  async summarizeDocument(fileId: string): Promise<FileSummary> {
    const response = await apiClient.post<FileSummary>('/api/drive/summarize', {
      file_id: fileId,
    });
    return response.data;
  },
};

// WhatsApp API Services
export const whatsappApi = {
  // Get available WhatsApp commands
  async getCommands(): Promise<{ commands: string[] }> {
    const response = await apiClient.get<{ commands: string[] }>('/api/whatsapp/commands');
    return response.data;
  },
};

// Integration API Services
export const integrationApi = {
  // Get Google OAuth login URL
  async getGoogleLoginUrl(): Promise<{ auth_url: string }> {
    const response = await apiClient.get<{ auth_url: string }>('/api/integrations/google/login');
    return response.data;
  },

  // Create calendar event
  async createCalendarEvent(data: {
    summary: string;
    description?: string;
    start_time: string;
    end_time: string;
    attendees?: string[];
  }): Promise<{ event_id: string; event_link: string }> {
    const response = await apiClient.post<{ event_id: string; event_link: string }>(
      '/api/integrations/calendar/events',
      data
    );
    return response.data;
  },
};

// Health check
export const healthApi = {
  async checkHealth(): Promise<{ status: string; message: string }> {
    const response = await apiClient.get<{ status: string; message: string }>('/health');
    return response.data;
  },
};

export default apiClient;