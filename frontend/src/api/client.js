import axios from 'axios';
import DOMPurify from 'dompurify';

const api = axios.create({
    baseURL: '',
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor - add auth token
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// Response interceptor - handle auth errors
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            localStorage.removeItem('token');
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

// XSS sanitization utility
export const sanitize = (dirty) => {
    return DOMPurify.sanitize(dirty, { ALLOWED_TAGS: [] });
};

export const sanitizeHtml = (dirty) => {
    return DOMPurify.sanitize(dirty, {
        ALLOWED_TAGS: ['b', 'i', 'u', 'a', 'br'],
        ALLOWED_ATTR: ['href'],
    });
};

export default api;
