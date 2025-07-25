/**
 * SheetDB API Service
 * Handles communication with SheetDB API to store form data in Excel sheets
 */

const SHEETDB_API_URL = 'https://sheetdb.io/api/v1/atpn8mhf808aa';

export interface SheetDBRecord {
  [key: string]: string | number | boolean;
}

export interface FeedbackFormData {
  emotion: string;
  rating: number;
  issues: string[];
  improvements: string;
  wouldRecommend: boolean;
  stylePersonality?: string;
  confidenceBoost?: boolean;
  userContext?: {
    monkSkinTone?: string;
    activeTab?: string;
    sessionId?: string;
  };
  timestamp?: string;
  type?: string;
  page?: string;
}

export interface ContactFormData {
  name: string;
  email: string;
  subject: string;
  message: string;
  timestamp?: string;
  type?: string;
}

export interface AuthFormData {
  name: string;
  email: string;
  password?: string; // Note: In production, never store plain passwords
  timestamp?: string;
  type?: string;
}

/**
 * Send data to SheetDB API
 */
export const sendToSheetDB = async (data: SheetDBRecord): Promise<boolean> => {
  try {
    console.log('🚀 Sending data to SheetDB:', data);
    console.log('📡 API URL:', SHEETDB_API_URL);
    
    const payload = {
      data: [data]
    };
    
    console.log('📦 Payload:', JSON.stringify(payload, null, 2));
    
    const response = await fetch(SHEETDB_API_URL, {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload)
    });

    console.log('📊 Response status:', response.status, response.statusText);
    console.log('📋 Response headers:', Object.fromEntries(response.headers.entries()));

    if (response.ok) {
      const result = await response.json();
      console.log('✅ Data successfully sent to SheetDB:', result);
      return true;
    } else {
      const errorText = await response.text();
      console.error('❌ SheetDB API Error:', {
        status: response.status,
        statusText: response.statusText,
        body: errorText
      });
      throw new Error(`HTTP error! status: ${response.status} - ${errorText}`);
    }
  } catch (error) {
    console.error('❌ Error sending data to SheetDB:', error);
    
    // Check if it's a network error
    if (error instanceof TypeError && error.message.includes('fetch')) {
      console.error('🌐 Network error - check your internet connection');
    }
    
    return false;
  }
};

/**
 * Send feedback form data to Excel sheet
 */
export const submitFeedbackForm = async (formData: FeedbackFormData): Promise<boolean> => {
  const dataToSend: SheetDBRecord = {
    type: 'feedback',
    timestamp: new Date().toISOString(),
    page: formData.page || 'recommendations',
    emotion: formData.emotion,
    rating: formData.rating,
    issues: formData.issues.join(', '), // Convert array to comma-separated string
    improvements: formData.improvements,
    wouldRecommend: formData.wouldRecommend,
    stylePersonality: formData.stylePersonality || '',
    confidenceBoost: formData.confidenceBoost || false,
    monkSkinTone: formData.userContext?.monkSkinTone || '',
    activeTab: formData.userContext?.activeTab || '',
    sessionId: formData.userContext?.sessionId || ''
  };

  return await sendToSheetDB(dataToSend);
};

/**
 * Send contact form data to Excel sheet
 */
export const submitContactForm = async (formData: ContactFormData): Promise<boolean> => {
  const dataToSend: SheetDBRecord = {
    ...formData,
    timestamp: new Date().toISOString(),
    type: 'contact_form'
  };

  return await sendToSheetDB(dataToSend);
};

/**
 * Send auth form data to Excel sheet
 * Note: In production, handle passwords securely and never store them in plain text
 */
export const submitAuthForm = async (formData: AuthFormData, formType: 'signup' | 'login'): Promise<boolean> => {
  const dataToSend: SheetDBRecord = {
    name: formData.name,
    email: formData.email,
    // Note: Remove password from data sent to sheet for security
    // password: formData.password, // DON'T DO THIS IN PRODUCTION
    timestamp: new Date().toISOString(),
    type: formType === 'signup' ? 'user_signup' : 'user_login'
  };

  return await sendToSheetDB(dataToSend);
};

/**
 * Get all records from SheetDB (for testing purposes)
 */
export const getSheetData = async (): Promise<SheetDBRecord[] | null> => {
  try {
    const response = await fetch(SHEETDB_API_URL, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
      }
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching data from SheetDB:', error);
    return null;
  }
};
